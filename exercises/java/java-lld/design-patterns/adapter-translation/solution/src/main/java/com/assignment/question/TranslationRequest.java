package com.assignment.question;

public class TranslationRequest {
    private String text;
    private String sourceLanguage;
    private String targetLanguage;
    private Double confidenceThreshold;

    public TranslationRequest() {
    }

    public String getText() {
        return text;
    }

    public String getSourceLanguage() {
        return sourceLanguage;
    }

    public String getTargetLanguage() {
        return targetLanguage;
    }

    public Double getConfidenceThreshold() {
        return confidenceThreshold;
    }
}
