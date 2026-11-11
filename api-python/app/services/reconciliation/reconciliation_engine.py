"""Ported from api/Services/Reconciliation/ReconciliationEngine.cs."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .atlas_reading_reconciler import AtlasReadingReconciler
from .azure_labs_reconciler import AzureLabsReconciler
from .fde_reconciler import FdeReconciler
from .java_reconciler import JavaReconciler
from .reconciliation_models import ReconciliationOptions, ReconciliationReport

logger = logging.getLogger(__name__)


class ReconciliationEngine:
    def __init__(
        self,
        session: AsyncSession,
        java_reconciler: JavaReconciler | None = None,
        fde_reconciler: FdeReconciler | None = None,
        azure_labs_reconciler: AzureLabsReconciler | None = None,
        atlas_reading_reconciler: AtlasReadingReconciler | None = None,
    ) -> None:
        self._session = session
        self._java_reconciler = java_reconciler or JavaReconciler(session)
        self._fde_reconciler = fde_reconciler or FdeReconciler(session)
        self._azure_labs_reconciler = azure_labs_reconciler or AzureLabsReconciler(session)
        self._atlas_reading_reconciler = atlas_reading_reconciler or AtlasReadingReconciler(
            session
        )

    async def execute_async(
        self, options: ReconciliationOptions
    ) -> list[ReconciliationReport]:
        reports: list[ReconciliationReport] = []
        scope = options.scope.lower()

        logger.info(
            "Executing ReconciliationEngine for scope '%s' in '%s' mode.",
            scope,
            options.mode.value,
        )

        if scope in ("java", "all"):
            reports.append(await self._java_reconciler.reconcile_java(options.mode))
            await self._session.commit()

        if scope in ("fde", "all"):
            reports.append(await self._fde_reconciler.reconcile_fde(options.mode))
            await self._session.commit()

        if scope in ("azure", "labs", "azure-labs", "all"):
            reports.append(
                await self._azure_labs_reconciler.reconcile_azure_and_labs(options.mode)
            )
            await self._session.commit()

        if scope in ("atlas", "reading-map", "knowledge-threads", "all"):
            reports.append(
                await self._atlas_reading_reconciler.reconcile_atlas_and_reading(options.mode)
            )
            await self._session.commit()

        return reports
