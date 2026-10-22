from typing import List

from .model import *


class GoogleTranslateApi:
    def convert(self, request: GoogleTranslationRequest) -> str:
        return "Translated text"

    def get_languages(self) -> List[str]:
        return ["hindi", "marathi", "kannada"]


class MicrosoftTranslateApi:
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        return "Translated text"

    def get_supported_languages(self) -> List[str]:
        return ["hindi", "marathi", "kannada"]
