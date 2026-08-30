package com.assignment.question;

import com.assignment.question.external.GoogleTranslateApi;
import com.assignment.question.external.GoogleTranslationRequest;

import java.util.List;

public class GoogleTranslationAdapter implements TranslationProviderAdapter {

    private GoogleTranslateApi googleTranslateApi = new GoogleTranslateApi();

    @Override
    public String translate(TranslationRequest request) {
        // TODO: convert the TranslationRequest into a GoogleTranslationRequest
        // and delegate to googleTranslateApi.convert(...)
        return null;
    }

    private GoogleTranslationRequest to(TranslationRequest request) {
        // TODO: build a GoogleTranslationRequest from the incoming TranslationRequest.
        // GoogleTranslationRequest requires a confidence threshold that
        // TranslationRequest does not carry — pick a sensible default.
        return null;
    }

    @Override
    public List<String> getSupportedLanguages() {
        // TODO: delegate to googleTranslateApi.getLanguages()
        return null;
    }
}
