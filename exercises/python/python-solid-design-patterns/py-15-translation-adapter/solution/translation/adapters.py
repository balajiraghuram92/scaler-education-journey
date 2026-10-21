from typing import List

from .model import GoogleTranslationRequest, TranslationRequest
from .services import GoogleTranslateApi, MicrosoftTranslateApi


class TranslationAdapter:
    def translate(self, request: TranslationRequest) -> str:
        raise NotImplementedError

    def get_supported_languages(self) -> List[str]:
        raise NotImplementedError


class MicrosoftTranslationAdapter(TranslationAdapter):
    def __init__(self):
        self.translate_api = MicrosoftTranslateApi()

    def translate(self, request: TranslationRequest) -> str:
        return self.translate_api.translate(
            request.text, request.source_language, request.target_language
        )

    def get_supported_languages(self) -> List[str]:
        return self.translate_api.get_supported_languages()


class GoogleTranslationAdapter(TranslationAdapter):
    def __init__(self):
        self.google_translate_api = GoogleTranslateApi()

    def translate(self, request: TranslationRequest) -> str:
        return self.google_translate_api.convert(self._to_google_request(request))

    def get_supported_languages(self) -> List[str]:
        return self.google_translate_api.get_languages()

    @staticmethod
    def _to_google_request(request: TranslationRequest) -> GoogleTranslationRequest:
        return GoogleTranslationRequest(
            request.text,
            request.source_language,
            request.target_language,
            request.confidence_threshold,
        )
