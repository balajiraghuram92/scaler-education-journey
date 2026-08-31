package com.assignment.question;

public class PresentationDocumentProcessor extends DocumentProcessor {

    public PresentationDocumentProcessor(String documentName) {
        super(documentName);
    }

    @Override
    public void processDocument() {
        // TODO: implement presentation-document-specific processing logic
    }

    @Override
    public DocumentType supportsType() {
        // TODO: return DocumentType.PRESENTATION
        return null;
    }

    public void addSlide() {
        System.out.println("Adding a slide to the presentation.");
    }
}
