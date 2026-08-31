package com.assignment.question.processor;

import com.assignment.question.DocumentType;

// TODO: extend DocumentProcessor and implement processDocument() and supportsType() (DocumentType.TEXT).
public class TextDocumentProcessor extends DocumentProcessor {

    public TextDocumentProcessor(String documentName) {
        super(documentName);
    }

    @Override
    public void processDocument() {

    }

    @Override
    public DocumentType supportsType() {
        return null;
    }
}
