"""Translated from SurefireResultParserTests.cs."""

from __future__ import annotations

import pytest

from app.services.exercises.exercise_execution_exceptions import (
    ExerciseInfrastructureException,
)
from app.services.exercises.surefire_result_parser import SurefireResultParser

from .exercise_test_factory import create_definition


def test_parser_uses_surefire_and_maps_methods_to_stable_evidence() -> None:
    definition = create_definition("C:\\exercise")
    parser = SurefireResultParser()
    xml = """
              <testsuite name="TrustedTest" tests="2" failures="1" errors="0" skipped="0">
                <testcase name="testOne" classname="TrustedTest" time="0.010" />
                <testcase name="testTwo" classname="TrustedTest" time="0.020">
                  <failure message="expected value">stack</failure>
                </testcase>
              </testsuite>
              """

    result = parser.parse(xml, definition)

    assert result.total == 2
    assert result.passed == 1
    assert result.failed == 1
    assert result.tests[0].evidence_id == "one-evidence"
    assert result.tests[1].evidence_id == "two-evidence"
    assert result.tests[1].status == "failed"


def test_parser_rejects_xml_without_test_cases() -> None:
    definition = create_definition("C:\\exercise")
    parser = SurefireResultParser()

    with pytest.raises(ExerciseInfrastructureException):
        parser.parse("<testsuite />", definition)
