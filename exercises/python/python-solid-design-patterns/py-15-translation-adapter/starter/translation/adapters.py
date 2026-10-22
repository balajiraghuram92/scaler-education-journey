from typing import List

from .model import GoogleTranslationRequest, TranslationRequest
from .services import GoogleTranslateApi, MicrosoftTranslateApi


class TranslationAdapter:
    """Target interface the translation tool codes against.

    Declare exactly two public operations:
    - translate(request: TranslationRequest) -> str
    - get_supported_languages() -> List[str]
    """

    def translate(self, request: TranslationRequest) -> str:
        raise NotImplementedError("Declare the interface method")

    def get_supported_languages(self) -> List[str]:
        raise NotImplementedError("Declare the interface method")


class MicrosoftTranslationAdapter(TranslationAdapter):
    """Wraps MicrosoftTranslateApi (composition).

    Create the client in __init__ and store it in ``self.translate_api``.
    """

    def __init__(self):
        raise NotImplementedError("Create self.translate_api")

    def translate(self, request: TranslationRequest) -> str:
        raise NotImplementedError("Delegate to the Microsoft client")

    def get_supported_languages(self) -> List[str]:
        raise NotImplementedError("Delegate to the Microsoft client")


class GoogleTranslationAdapter(TranslationAdapter):
    """Wraps GoogleTranslateApi (composition).

    Create the client in __init__ and store it in ``self.google_translate_api``.
    Google needs a GoogleTranslationRequest, so convert the application request first
    (the confidence threshold travels with it).
    """

    def __init__(self):
        raise NotImplementedError("Create self.google_translate_api")

    def translate(self, request: TranslationRequest) -> str:
        raise NotImplementedError("Convert the request, then call convert()")

    def get_supported_languages(self) -> List[str]:
        raise NotImplementedError("Delegate to the Google client")
