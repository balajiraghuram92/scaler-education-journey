"""Ported from api/Services/Exercises/SurefireResultParser.cs."""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from datetime import timedelta

from .exercise_execution_exceptions import ExerciseInfrastructureException
from .exercise_execution_models import ParsedSurefireResult, ParsedSurefireTest
from .exercise_manifest_models import ExerciseDefinition

_MAX_DOCUMENT_CHARS = 1_000_000
_MAX_DIAGNOSTIC_CHARS = 4096


class SurefireResultParser:
    def parse(self, xml: str, definition: ExerciseDefinition) -> ParsedSurefireResult:
        if not xml or not xml.strip():
            raise ExerciseInfrastructureException("Surefire XML was empty.")
        try:
            # Mirrors XmlReaderSettings: DTD prohibited, 1M char cap.
            if "<!DOCTYPE" in xml:
                raise ExerciseInfrastructureException("Surefire XML could not be parsed.")
            if len(xml) > _MAX_DOCUMENT_CHARS:
                raise ExerciseInfrastructureException("Surefire XML could not be parsed.")
            root = ET.fromstring(xml)
            test_cases = [
                _parse_test_case(element, definition)
                for element in root.iter("testcase")
            ]
            if not test_cases:
                raise ExerciseInfrastructureException(
                    "Surefire XML did not contain any test cases."
                )
            return ParsedSurefireResult(
                total=len(test_cases),
                passed=sum(1 for t in test_cases if t.status == "passed"),
                failed=sum(1 for t in test_cases if t.status == "failed"),
                errors=sum(1 for t in test_cases if t.status == "error"),
                skipped=sum(1 for t in test_cases if t.status == "skipped"),
                tests=test_cases,
            )
        except ExerciseInfrastructureException:
            raise
        except ET.ParseError as exc:
            raise ExerciseInfrastructureException(
                "Surefire XML could not be parsed.", exc
            ) from exc


def _parse_test_case(element: ET.Element, definition: ExerciseDefinition) -> ParsedSurefireTest:
    method = element.get("name") or ""
    evidence = definition.evidence_by_test_method.get(method)

    # pytest parametrized cases are reported as "test_name[case]": map them to the
    # function's evidence and keep the case id visible in the label.
    case_suffix: str | None = None
    bracket = method.find("[")
    if (
        evidence is None
        and bracket > 0
        and method.endswith("]")
        and method[:bracket] in definition.evidence_by_test_method
    ):
        evidence = definition.evidence_by_test_method[method[:bracket]]
        case_suffix = method[bracket:]

    failure = element.find("failure")
    error = element.find("error")
    skipped = element.find("skipped")
    if failure is not None:
        status = "failed"
    elif error is not None:
        status = "error"
    elif skipped is not None:
        status = "skipped"
    else:
        status = "passed"
    diagnostic = failure if failure is not None else error

    if evidence is None:
        evidence_id = None
        label = None
    elif case_suffix is None:
        evidence_id = evidence.id
        label = evidence.label
    else:
        evidence_id = evidence.id + case_suffix
        label = f"{evidence.label} {case_suffix}"

    message = None
    if diagnostic is not None:
        raw = diagnostic.get("message")
        if raw is None:
            raw = "".join(diagnostic.itertext())
        message = _truncate(raw)

    return ParsedSurefireTest(
        test_method=method,
        evidence_id=evidence_id,
        label=label,
        status=status,
        duration=_parse_duration(element.get("time")),
        message=message,
    )


def _parse_duration(value: str | None) -> timedelta:
    if value is None or "_" in value:
        return timedelta(0)
    try:
        seconds = float(value)
    except ValueError:
        return timedelta(0)
    if math.isnan(seconds) or seconds < 0:
        return timedelta(0)
    if math.isinf(seconds):
        # Mirrors TimeSpan.FromSeconds throwing on infinity (not caught by the parser).
        raise OverflowError("Surefire duration is infinite.")
    return timedelta(seconds=seconds)


def _truncate(value: str | None) -> str | None:
    if not value or len(value) <= _MAX_DIAGNOSTIC_CHARS:
        return value
    return value[:_MAX_DIAGNOSTIC_CHARS] + "\n[diagnostic truncated]"
