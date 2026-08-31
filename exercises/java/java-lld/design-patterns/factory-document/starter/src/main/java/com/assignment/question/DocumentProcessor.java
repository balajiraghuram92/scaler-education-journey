package com.assignment.question;

public abstract class DocumentProcessor {
    private String documentName;

    public DocumentProcessor(String documentName) {
        this.documentName = documentName;
    }

    public String getDocumentName() {
        // TODO: return the document name
        return null;
    }

    public abstract void processDocument();

    public abstract DocumentType supportsType();

}
