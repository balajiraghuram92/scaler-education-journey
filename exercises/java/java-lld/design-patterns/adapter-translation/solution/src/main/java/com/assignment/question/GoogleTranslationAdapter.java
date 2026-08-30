package com.assignment.question;

import com.assignment.question.external.GoogleTranslateApi;
import com.assignment.question.external.GoogleTranslationRequest;

import java.util.List;

public class GoogleTranslationAdapter implements TranslationProviderAdapter {

    private GoogleTranslateApi googleTranslateApi = new GoogleTranslateApi();

    @Override
    public String translate(TranslationRequest request) {
        return googleTranslateApi.convert(to(request));
    }

    private GoogleTranslationRequest to(TranslationRequest request) {
        return new GoogleTranslationRequest(request.getText(), request.getSourceLanguage(), request.getTargetLanguage(), 0.8);
    }

    @Override
    public List<String> getSupportedLanguages() {
        return googleTranslateApi.getLanguages();
    }
}
