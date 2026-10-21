from dataclasses import dataclass


@dataclass
class GoogleTranslationRequest:
    text: str
    source_language: str
    target_language: str
    confidence_threshold: float

@dataclass
class TranslationRequest:
    text: str
    source_language: str
    target_language: str
    confidence_threshold: float = 0.8