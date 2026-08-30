package com.assignment.question;

import com.assignment.question.external.MicrosoftTranslateApi;

import java.util.List;

public class MicrosoftTranslationAdapter implements TranslationProviderAdapter {
    private MicrosoftTranslateApi translateApi = new MicrosoftTranslateApi();

    @Override
    public String translate(TranslationRequest request) {
        // TODO: delegate to translateApi.translate(...), passing the individual
        // text/sourceLanguage/targetLanguage fields from the incoming request
        return null;
    }

    @Override
    public List<String> getSupportedLanguages() {
        // TODO: delegate to translateApi.getSupportedLanguages()
        return null;
    }
}
