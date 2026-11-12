"""Ported from api/Services/Localization/WorkflowService.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.glossary_term import GlossaryTerm
from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...models.localization.usage_constants import (
    UsageCapKinds,
    UsageMeters,
    UsageOperations,
)
from ...models.localization.workflow_step import WorkflowStep
from ...schemas.localization_dtos import (
    AddWorkflowStepRequest,
    UpdateWorkflowStepRequest,
    WorkflowStepDto,
)
from ...settings import LocalizationAiSettings
from .auto_routing_service import AutoRoutingService
from .i_quality_scorer import IQualityScorer
from .i_translation_provider import ITranslationProvider
from .localization_ai_client import (
    NOT_CONFIGURED_MESSAGE,
    AiGlossaryTermDto,
    LocalizationAiException,
)
from .localization_exceptions import (
    InvalidJobStateException,
    LocalizationAiDisabledException,
    LocalizationProjectNotFoundException,
    LocalizationUsageCapReachedException,
    WorkflowStepBoundaryException,
    WorkflowStepNotFoundException,
)
from .mt_optimize_service import MtOptimizeService
from .translation_job_service import TranslationJobService
from .usage_metering_service import UsageBudget, UsageCallRecord, UsageMeteringService


class WorkflowActions:
    MARK_TRANSLATED = "Mark Translated"
    SEND_TO_REVIEW = "Send to Review"
    APPROVE = "Approve"
    AUTO_TRANSLATE_VIA_AZURE_TRANSLATOR = "Auto-Translate via Azure Translator"
    CREATE_TRANSLATION_JOBS = "Create Translation Jobs"
    RUN_MT_OPTIMIZE = "Run MT Optimize"
    SCORE_QUALITY = "Score Quality"
    AUTO_ROUTE = "Auto-Route"

    ALL = frozenset(
        {
            MARK_TRANSLATED,
            SEND_TO_REVIEW,
            APPROVE,
            AUTO_TRANSLATE_VIA_AZURE_TRANSLATOR,
            CREATE_TRANSLATION_JOBS,
            RUN_MT_OPTIMIZE,
            SCORE_QUALITY,
            AUTO_ROUTE,
        }
    )


class WorkflowTriggers:
    ON_MANUAL_CLICK = "On Manual Click"

    ALL = frozenset({ON_MANUAL_CLICK})


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


class WorkflowService:
    def __init__(
        self,
        session: AsyncSession,
        translation_provider: ITranslationProvider,
        mt_optimize_service: MtOptimizeService,
        quality_scorer: IQualityScorer,
        auto_routing_service: AutoRoutingService,
        translation_job_service: TranslationJobService,
        ai_options: LocalizationAiSettings | None = None,
        usage: UsageMeteringService | None = None,
    ) -> None:
        self._session = session
        self._translation_provider = translation_provider
        self._mt_optimize_service = mt_optimize_service
        self._quality_scorer = quality_scorer
        self._auto_routing_service = auto_routing_service
        self._translation_job_service = translation_job_service
        # Kept for signature parity with the C# constructor; R3 removed the
        # ledger writes that used these rates.
        self._ai_options = ai_options
        self._usage = usage

    async def get_steps_async(self, project_slug: str) -> list[WorkflowStepDto]:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        steps = (
            await self._session.execute(
                select(WorkflowStep)
                .where(WorkflowStep.project_id == project.id)
                .order_by(WorkflowStep.order)
            )
        ).scalars().all()
        return [_step_dto(step) for step in steps]

    async def add_step_async(
        self, project_slug: str, request: AddWorkflowStepRequest
    ) -> WorkflowStepDto:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        _validate_action_and_trigger(request.action, request.trigger)
        max_order = (
            await self._session.execute(
                select(func.coalesce(func.max(WorkflowStep.order), 0)).where(
                    WorkflowStep.project_id == project.id
                )
            )
        ).scalar_one()
        step = WorkflowStep(
            project_id=project.id,
            order=max_order + 1,
            trigger=request.trigger
            if request.trigger and request.trigger.strip()
            else WorkflowTriggers.ON_MANUAL_CLICK,
            action=cast(str, request.action),
            condition_expression=request.condition_expression,
            last_run_at=None,
            last_run_outcome=None,
        )
        self._session.add(step)
        await self._session.flush()
        return _step_dto(step)

    async def update_step_async(
        self, project_slug: str, step_id: int, request: UpdateWorkflowStepRequest
    ) -> WorkflowStepDto:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        step = (
            await self._session.execute(
                select(WorkflowStep).where(
                    WorkflowStep.id == step_id,
                    WorkflowStep.project_id == project.id,
                )
            )
        ).scalar_one_or_none()
        if step is None:
            raise WorkflowStepNotFoundException(step_id)
        _validate_action_and_trigger(request.action, request.trigger)
        step.trigger = (
            request.trigger
            if request.trigger and request.trigger.strip()
            else WorkflowTriggers.ON_MANUAL_CLICK
        )
        step.action = cast(str, request.action)
        step.condition_expression = request.condition_expression
        await self._session.flush()
        return _step_dto(step)

    async def reorder_step_async(
        self, project_slug: str, step_id: int, direction: str | None
    ) -> None:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        steps = (
            await self._session.execute(
                select(WorkflowStep)
                .where(WorkflowStep.project_id == project.id)
                .order_by(WorkflowStep.order)
            )
        ).scalars().all()
        index = next(
            (position for position, step in enumerate(steps) if step.id == step_id),
            -1,
        )
        if index == -1:
            raise WorkflowStepNotFoundException(step_id)
        # C# calls direction.Trim() directly: a null direction throws
        # NullReferenceException (500), not a validation error. The cast keeps
        # that behavior (AttributeError -> 500) instead of a 400.
        normalized_dir = cast(str, direction).strip().lower()
        if normalized_dir == "up":
            if index == 0:
                raise WorkflowStepBoundaryException(
                    "Cannot move the first workflow step up."
                )
            prev = steps[index - 1]
            steps[index].order, prev.order = prev.order, steps[index].order
        elif normalized_dir == "down":
            if index == len(steps) - 1:
                raise WorkflowStepBoundaryException(
                    "Cannot move the last workflow step down."
                )
            nxt = steps[index + 1]
            steps[index].order, nxt.order = nxt.order, steps[index].order
        else:
            raise ValueError(
                "Direction must be either 'up' or 'down'. (Parameter 'direction')"
            )
        await self._session.flush()

    async def delete_step_async(self, project_slug: str, step_id: int) -> None:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        step = (
            await self._session.execute(
                select(WorkflowStep).where(
                    WorkflowStep.id == step_id,
                    WorkflowStep.project_id == project.id,
                )
            )
        ).scalar_one_or_none()
        if step is None:
            raise WorkflowStepNotFoundException(step_id)
        await self._session.delete(step)
        await self._session.flush()

    async def run_step_async(
        self, project_slug: str, step_id: int
    ) -> WorkflowStepDto:
        project = (
            await self._session.execute(
                select(LocalizationProject)
                .options(
                    selectinload(LocalizationProject.locales),
                    selectinload(LocalizationProject.strings).selectinload(
                        LocalizationString.translations
                    ),
                )
                .where(LocalizationProject.slug == project_slug)
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        step = (
            await self._session.execute(
                select(WorkflowStep).where(
                    WorkflowStep.id == step_id,
                    WorkflowStep.project_id == project.id,
                )
            )
        ).scalar_one_or_none()
        if step is None:
            raise WorkflowStepNotFoundException(step_id)
        now = datetime.now(UTC)

        if step.action == WorkflowActions.MARK_TRANSLATED:
            affected = 0
            for item in project.strings:
                for trans in item.translations:
                    if trans.stage == "New" and not _is_blank(trans.target_text):
                        trans.stage = "Translated"
                        trans.updated_at = now
                        affected += 1
            outcome = f"{affected} strings affected"
        elif step.action == WorkflowActions.SEND_TO_REVIEW:
            affected = 0
            for item in project.strings:
                for trans in item.translations:
                    if trans.stage == "Translated":
                        trans.stage = "Reviewed"
                        trans.updated_at = now
                        affected += 1
            outcome = f"{affected} strings affected"
        elif step.action == WorkflowActions.APPROVE:
            affected = 0
            for item in project.strings:
                for trans in item.translations:
                    if trans.stage == "Reviewed":
                        trans.stage = "Approved"
                        trans.updated_at = now
                        affected += 1
            outcome = f"{affected} strings affected"
        elif step.action == WorkflowActions.AUTO_TRANSLATE_VIA_AZURE_TRANSLATOR:
            if not project.ai_enabled:
                raise LocalizationAiDisabledException(project.slug)
            mt_budget = await self._start_budget_async(
                project.id, UsageCapKinds.MACHINE_TRANSLATION, now
            )
            translated_count = 0
            skipped = 0
            for locale in project.locales:
                for item in project.strings:
                    existing: LocalizationTranslation | None = next(
                        (
                            t
                            for t in item.translations
                            if t.locale_code == locale.locale_code
                        ),
                        None,
                    )
                    # C# measures the call in UTF-16 code units
                    # (string.Length); len() counts code points. Identical
                    # for BMP text; astral characters differ by one unit
                    # per surrogate pair (Finding).
                    call_units = len(item.source_text)
                    if existing is None:
                        if mt_budget is not None and not mt_budget.can_spend(
                            UsageCapKinds.MACHINE_TRANSLATION, call_units
                        ):
                            skipped += 1
                            continue
                        translated_text = (
                            await self._translation_provider.translate_async(
                                item.source_text,
                                project.source_locale,
                                locale.locale_code,
                            )
                        )
                        await self._record_usage_async(
                            UsageCallRecord(
                                project.id,
                                step.id,
                                UsageMeters.MACHINE_TRANSLATION,
                                UsageOperations.MT_DRAFT,
                                locale.locale_code,
                                call_units,
                                None,
                                False,
                                True,
                            ),
                            now,
                        )
                        if mt_budget is not None:
                            mt_budget.spent(
                                UsageCapKinds.MACHINE_TRANSLATION, call_units
                            )
                        new_trans = LocalizationTranslation(
                            string_id=item.id,
                            locale_code=locale.locale_code,
                            target_text=translated_text,
                            raw_mt_text=translated_text,
                            stage="Translated",
                            translation_source="AI",
                            needs_review=False,
                            updated_at=now,
                        )
                        self._session.add(new_trans)
                        # EF Core fixes up the navigation by itself;
                        # without the append the next step in this
                        # session never sees the new row (the
                        # identity-map collection is already loaded).
                        item.translations.append(new_trans)
                        translated_count += 1
                    elif _is_blank(existing.target_text):
                        if mt_budget is not None and not mt_budget.can_spend(
                            UsageCapKinds.MACHINE_TRANSLATION, call_units
                        ):
                            skipped += 1
                            continue
                        translated_text = (
                            await self._translation_provider.translate_async(
                                item.source_text,
                                project.source_locale,
                                locale.locale_code,
                            )
                        )
                        await self._record_usage_async(
                            UsageCallRecord(
                                project.id,
                                step.id,
                                UsageMeters.MACHINE_TRANSLATION,
                                UsageOperations.MT_DRAFT,
                                locale.locale_code,
                                call_units,
                                None,
                                False,
                                True,
                            ),
                            now,
                        )
                        if mt_budget is not None:
                            mt_budget.spent(
                                UsageCapKinds.MACHINE_TRANSLATION, call_units
                            )
                        existing.target_text = translated_text
                        existing.raw_mt_text = translated_text
                        existing.stage = "Translated"
                        existing.translation_source = "AI"
                        existing.updated_at = now
                        translated_count += 1
            outcome = _with_skipped_clause(
                f"{translated_count} strings translated via Azure Translator",
                mt_budget,
                UsageCapKinds.MACHINE_TRANSLATION,
                skipped,
            )
        elif step.action == WorkflowActions.CREATE_TRANSLATION_JOBS:
            created_count = 0
            skipped_count = 0
            for locale in project.locales:
                try:
                    await self._translation_job_service.create_job_async(
                        project.slug, locale.locale_code
                    )
                    created_count += 1
                except InvalidJobStateException:
                    skipped_count += 1
            outcome = f"{created_count} jobs created, {skipped_count} skipped"
        # Phase 3 AI actions — thin orchestration over the localization-ai service.
        # A per-string AI failure is counted and the run continues; only
        # NotImplementedError (service not configured) aborts into HTTP 501.
        elif step.action == WorkflowActions.RUN_MT_OPTIMIZE:
            if not project.ai_enabled:
                raise LocalizationAiDisabledException(project.slug)
            _throw_if_ai_not_configured(self._mt_optimize_service.is_configured)
            llm_budget = await self._start_budget_async(
                project.id, UsageCapKinds.LLM, now
            )
            glossary = (
                await self._session.execute(
                    select(GlossaryTerm).where(
                        GlossaryTerm.project_id == project.id
                    )
                )
            ).scalars().all()
            optimized_count = 0
            failed_count = 0
            skipped = 0
            for item in project.strings:
                for trans in item.translations:
                    if trans.translation_source != "AI" or trans.stage == "Approved":
                        continue
                    raw_mt = trans.raw_mt_text
                    if _is_blank(raw_mt):
                        continue
                    if llm_budget is not None and not llm_budget.can_spend(
                        UsageCapKinds.LLM, 0
                    ):
                        skipped += 1
                        continue
                    terms = [
                        AiGlossaryTermDto(
                            source=term.source_term, target=term.target_term
                        )
                        for term in glossary
                        if term.locale_code == trans.locale_code
                    ]
                    try:
                        result = await self._mt_optimize_service.optimize_detailed_async(
                            item.source_text,
                            cast(str, raw_mt),
                            project.slug,
                            trans.locale_code,
                            terms,
                        )
                        await self._record_usage_async(
                            UsageCallRecord(
                                project.id,
                                step.id,
                                UsageMeters.LLM_OPTIMIZE,
                                UsageOperations.MT_OPTIMIZE,
                                trans.locale_code,
                                result.input_tokens,
                                result.output_tokens,
                                result.cache_hit,
                                True,
                            ),
                            now,
                        )
                        if llm_budget is not None:
                            llm_budget.spent(
                                UsageCapKinds.LLM,
                                0
                                if result.cache_hit
                                else result.input_tokens + result.output_tokens,
                            )
                        trans.target_text = result.optimized_translation
                        trans.updated_at = now
                        optimized_count += 1
                    except LocalizationAiException:
                        failed_count += 1
            outcome = _with_skipped_clause(
                f"{optimized_count} strings optimized"
                if failed_count == 0
                else f"{optimized_count} strings optimized, {failed_count} failed",
                llm_budget,
                UsageCapKinds.LLM,
                skipped,
            )
        elif step.action == WorkflowActions.SCORE_QUALITY:
            if not project.ai_enabled:
                raise LocalizationAiDisabledException(project.slug)
            _throw_if_ai_not_configured(self._quality_scorer.is_configured)
            llm_budget = await self._start_budget_async(
                project.id, UsageCapKinds.LLM, now
            )
            scored_count = 0
            failed_count = 0
            skipped = 0
            for item in project.strings:
                for trans in item.translations:
                    if trans.translation_source != "AI" or trans.stage == "Approved":
                        continue
                    if llm_budget is not None and not llm_budget.can_spend(
                        UsageCapKinds.LLM, 0
                    ):
                        skipped += 1
                        continue
                    try:
                        score_result = await self._quality_scorer.score_async(
                            item.source_text,
                            trans.target_text if trans.target_text is not None else "",
                            trans.locale_code,
                        )
                        if score_result.score < 1 or score_result.score > 5:
                            await self._record_usage_async(
                                UsageCallRecord(
                                    project.id,
                                    step.id,
                                    UsageMeters.LLM_SCORE,
                                    UsageOperations.QPS_SCORE,
                                    trans.locale_code,
                                    score_result.input_tokens,
                                    score_result.output_tokens,
                                    False,
                                    False,
                                ),
                                now,
                            )
                            if llm_budget is not None:
                                llm_budget.spent(
                                    UsageCapKinds.LLM,
                                    score_result.input_tokens
                                    + score_result.output_tokens,
                                )
                            failed_count += 1
                            continue
                        await self._record_usage_async(
                            UsageCallRecord(
                                project.id,
                                step.id,
                                UsageMeters.LLM_SCORE,
                                UsageOperations.QPS_SCORE,
                                trans.locale_code,
                                score_result.input_tokens,
                                score_result.output_tokens,
                                False,
                                True,
                            ),
                            now,
                        )
                        if llm_budget is not None:
                            llm_budget.spent(
                                UsageCapKinds.LLM,
                                score_result.input_tokens + score_result.output_tokens,
                            )
                        trans.qps_score = score_result.score
                        trans.updated_at = now
                        scored_count += 1
                    except LocalizationAiException as exc:
                        if exc.input_tokens + exc.output_tokens > 0:
                            await self._record_usage_async(
                                UsageCallRecord(
                                    project.id,
                                    step.id,
                                    UsageMeters.LLM_SCORE,
                                    UsageOperations.QPS_SCORE,
                                    trans.locale_code,
                                    exc.input_tokens,
                                    exc.output_tokens,
                                    False,
                                    False,
                                ),
                                now,
                            )
                            if llm_budget is not None:
                                llm_budget.spent(
                                    UsageCapKinds.LLM,
                                    exc.input_tokens + exc.output_tokens,
                                )
                        failed_count += 1
                        continue
                    raw_mt = trans.raw_mt_text
                    if not _is_blank(raw_mt) and trans.raw_mt_qps_score is None:
                        if llm_budget is not None and not llm_budget.can_spend(
                            UsageCapKinds.LLM, 0
                        ):
                            skipped += 1
                        else:
                            try:
                                raw_result = await self._quality_scorer.score_async(
                                    item.source_text,
                                    cast(str, raw_mt),
                                    trans.locale_code,
                                )
                                if raw_result.score < 1 or raw_result.score > 5:
                                    await self._record_usage_async(
                                        UsageCallRecord(
                                            project.id,
                                            step.id,
                                            UsageMeters.LLM_SCORE,
                                            UsageOperations.QPS_SCORE,
                                            trans.locale_code,
                                            raw_result.input_tokens,
                                            raw_result.output_tokens,
                                            False,
                                            False,
                                        ),
                                        now,
                                    )
                                    if llm_budget is not None:
                                        llm_budget.spent(
                                            UsageCapKinds.LLM,
                                            raw_result.input_tokens
                                            + raw_result.output_tokens,
                                        )
                                    failed_count += 1
                                else:
                                    await self._record_usage_async(
                                        UsageCallRecord(
                                            project.id,
                                            step.id,
                                            UsageMeters.LLM_SCORE,
                                            UsageOperations.QPS_SCORE,
                                            trans.locale_code,
                                            raw_result.input_tokens,
                                            raw_result.output_tokens,
                                            False,
                                            True,
                                        ),
                                        now,
                                    )
                                    if llm_budget is not None:
                                        llm_budget.spent(
                                            UsageCapKinds.LLM,
                                            raw_result.input_tokens
                                            + raw_result.output_tokens,
                                        )
                                    trans.raw_mt_qps_score = raw_result.score
                            except LocalizationAiException as exc:
                                if exc.input_tokens + exc.output_tokens > 0:
                                    await self._record_usage_async(
                                        UsageCallRecord(
                                            project.id,
                                            step.id,
                                            UsageMeters.LLM_SCORE,
                                            UsageOperations.QPS_SCORE,
                                            trans.locale_code,
                                            exc.input_tokens,
                                            exc.output_tokens,
                                            False,
                                            False,
                                        ),
                                        now,
                                    )
                                    if llm_budget is not None:
                                        llm_budget.spent(
                                            UsageCapKinds.LLM,
                                            exc.input_tokens + exc.output_tokens,
                                        )
                                failed_count += 1
            outcome = _with_skipped_clause(
                f"{scored_count} strings scored"
                if failed_count == 0
                else f"{scored_count} strings scored, {failed_count} failed",
                llm_budget,
                UsageCapKinds.LLM,
                skipped,
            )
        elif step.action == WorkflowActions.AUTO_ROUTE:
            if not project.ai_enabled:
                raise LocalizationAiDisabledException(project.slug)
            _throw_if_ai_not_configured(self._auto_routing_service.is_configured)
            processed_count = 0
            flagged_count = 0
            failed_count = 0
            for item in project.strings:
                for trans in item.translations:
                    if (
                        trans.translation_source != "AI"
                        or trans.stage == "Approved"
                        or trans.qps_score is None
                    ):
                        continue
                    try:
                        needs_review = await self._auto_routing_service.should_route_to_review_async(
                            trans.qps_score,
                            project.qps_threshold,
                        )
                        trans.needs_review = needs_review
                        trans.updated_at = now
                        processed_count += 1
                        if needs_review:
                            flagged_count += 1
                    except LocalizationAiException:
                        failed_count += 1
            outcome = (
                f"{processed_count} strings processed, {flagged_count} flagged for review"
                if failed_count == 0
                else (
                    f"{processed_count} strings processed, {flagged_count} flagged "
                    f"for review, {failed_count} failed"
                )
            )
        else:
            raise RuntimeError(f"Unknown workflow action '{step.action}'.")

        step.last_run_at = now
        step.last_run_outcome = outcome
        await self._session.flush()
        return _step_dto(step)

    async def _record_usage_async(
        self, call: UsageCallRecord, occurred_at: datetime
    ) -> None:
        if self._usage is not None:
            await self._usage.record_async(call, occurred_at)

    async def _start_budget_async(
        self, project_id: int, cap_kind: str, now: datetime
    ) -> UsageBudget | None:
        if self._usage is None:
            return None
        budget = await self._usage.begin_run_async(project_id, now)
        limit = budget.limit(cap_kind)
        if limit is not None and budget.used(cap_kind) >= limit:
            raise LocalizationUsageCapReachedException(
                cap_kind, budget.used(cap_kind), limit
            )
        return budget


def _step_dto(step: WorkflowStep) -> WorkflowStepDto:
    return WorkflowStepDto(
        id=step.id,
        project_id=step.project_id,
        order=step.order,
        trigger=step.trigger,
        action=step.action,
        condition_expression=step.condition_expression,
        last_run_at=step.last_run_at,
        last_run_outcome=step.last_run_outcome,
    )


def _with_skipped_clause(
    outcome: str, budget: UsageBudget | None, cap_kind: str, skipped: int
) -> str:
    if skipped <= 0 or budget is None:
        return outcome
    return (
        f"{outcome}, {skipped} skipped: monthly {cap_kind} cap reached "
        f"({budget.used(cap_kind)} of {budget.limit(cap_kind)})"
    )


def _validate_action_and_trigger(
    action: str | None, trigger: str | None
) -> None:
    if action not in WorkflowActions.ALL:
        # The detail embeds .NET's ArgumentException Message suffix verbatim
        # (" (Parameter 'action')") so error bodies match.
        raise ValueError(
            f"Unknown workflow action '{action or ''}'. (Parameter 'action')"
        )
    effective_trigger = (
        trigger
        if trigger is not None and trigger.strip()
        else WorkflowTriggers.ON_MANUAL_CLICK
    )
    if effective_trigger not in WorkflowTriggers.ALL:
        raise ValueError(
            f"Unknown workflow trigger '{effective_trigger}'. (Parameter 'trigger')"
        )


def _throw_if_ai_not_configured(configured: bool) -> None:
    """Port of WorkflowService.ThrowIfAiNotConfigured: call before any loop
    and before any database write."""
    if not configured:
        raise NotImplementedError(NOT_CONFIGURED_MESSAGE)
