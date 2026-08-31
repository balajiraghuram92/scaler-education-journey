package com.assignment.question;

public class TextDocumentProcessor extends DocumentProcessor {

    public TextDocumentProcessor(String documentName) {
        super(documentName);
    }

    @Override
    public void processDocument() {
        // TODO: implement text-document-specific processing logic
    }

    @Override
    public DocumentType supportsType() {
        // TODO: return DocumentType.TEXT
        return null;
    }
}
