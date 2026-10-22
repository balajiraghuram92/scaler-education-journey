import copy

from translation.adapters import (
    GoogleTranslationAdapter,
    MicrosoftTranslationAdapter,
    TranslationAdapter,
)
from translation.model import GoogleTranslationRequest, TranslationRequest
from translation.services import GoogleTranslateApi, MicrosoftTranslateApi


class SpyMicrosoft:
    def __init__(self):
        self.calls = []

    def translate(self, text, source_language, target_language):
        self.calls.append((text, source_language, target_language))
        return "ms:" + text

    def get_supported_languages(self):
        return ["ms-fr", "ms-de"]


class SpyGoogle:
    def __init__(self):
        self.requests = []

    def convert(self, request):
        self.requests.append(request)
        return "g:" + request.text

    def get_languages(self):
        return ["g-fr", "g-es"]


def microsoft(spy=None):
    adapter = MicrosoftTranslationAdapter()
    adapter.translate_api = spy or SpyMicrosoft()
    return adapter


def google(spy=None):
    adapter = GoogleTranslationAdapter()
    adapter.google_translate_api = spy or SpyGoogle()
    return adapter


def test_interface_declares_exactly_two_operations():
    public = {n for n in vars(TranslationAdapter) if not n.startswith("_")}
    assert public == {"translate", "get_supported_languages"}, (
        f"TranslationAdapter must declare exactly translate and get_supported_languages, found {sorted(public)}"
    )


def test_adapters_are_translation_adapters_built_by_composition():
    ms, g = MicrosoftTranslationAdapter(), GoogleTranslationAdapter()
    assert isinstance(ms, TranslationAdapter) and isinstance(g, TranslationAdapter)
    assert isinstance(ms.translate_api, MicrosoftTranslateApi), "translate_api must hold a MicrosoftTranslateApi"
    assert isinstance(g.google_translate_api, GoogleTranslateApi), "google_translate_api must hold a GoogleTranslateApi"
    assert not isinstance(ms, MicrosoftTranslateApi), "wrap the vendor client, do not subclass it"
    assert not isinstance(g, GoogleTranslateApi), "wrap the vendor client, do not subclass it"


def test_microsoft_translate_delegates_with_unpacked_arguments():
    spy = SpyMicrosoft()
    result = microsoft(spy).translate(TranslationRequest("Hello", "en", "fr"))
    assert spy.calls == [("Hello", "en", "fr")], f"vendor must receive (text, source, target), got {spy.calls}"
    assert result == "ms:Hello", "return the vendor's string unchanged"


def test_google_translate_converts_request_to_google_shape():
    spy = SpyGoogle()
    result = google(spy).translate(TranslationRequest("Hello", "en", "fr"))
    assert len(spy.requests) == 1, "convert() must be called exactly once"
    sent = spy.requests[0]
    assert isinstance(sent, GoogleTranslationRequest), "Google must receive a GoogleTranslationRequest"
    assert (sent.text, sent.source_language, sent.target_language) == ("Hello", "en", "fr")
    assert result == "g:Hello", "return the vendor's string unchanged"


def test_google_translate_carries_confidence_threshold():
    spy = SpyGoogle()
    google(spy).translate(TranslationRequest("Hi", "en", "de", confidence_threshold=0.55))
    assert spy.requests[0].confidence_threshold == 0.55, "the request's threshold must be forwarded, not a hard-coded 0.8"
    google(spy).translate(TranslationRequest("Hi", "en", "de"))
    assert spy.requests[1].confidence_threshold == 0.8, "default threshold is 0.8"


def test_supported_languages_pass_through_unchanged():
    assert microsoft().get_supported_languages() == ["ms-fr", "ms-de"]
    assert google().get_supported_languages() == ["g-fr", "g-es"]


def test_application_request_is_not_mutated():
    request = TranslationRequest("Hello", "en", "fr", 0.9)
    before = copy.deepcopy(request)
    microsoft().translate(request)
    google().translate(request)
    assert request == before, "adapters must not modify the caller's TranslationRequest"
    assert type(request) is TranslationRequest


def test_client_code_works_against_the_interface_only():
    def translate_all(adapters, request):
        return [a.translate(request) for a in adapters]

    out = translate_all([microsoft(), google()], TranslationRequest("Yo", "en", "es"))
    assert out == ["ms:Yo", "g:Yo"], "both vendors must be usable interchangeably through TranslationAdapter"
