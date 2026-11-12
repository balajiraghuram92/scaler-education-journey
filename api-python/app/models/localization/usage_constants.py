"""Ported from api/Models/Localization/UsageConstants.cs."""

from __future__ import annotations


class UsageMeters:
    MACHINE_TRANSLATION = "machine-translation"
    LLM_OPTIMIZE = "llm-optimize"
    LLM_SCORE = "llm-score"


class UsageOperations:
    MT_DRAFT = "mt-draft"
    MT_OPTIMIZE = "mt-optimize"
    QPS_SCORE = "qps-score"


class UsageUnitKinds:
    CHAR = "char"
    INPUT_TOKEN = "input-token"
    OUTPUT_TOKEN = "output-token"


class UsageCapKinds:
    MACHINE_TRANSLATION = "machine-translation"
    LLM = "llm"
