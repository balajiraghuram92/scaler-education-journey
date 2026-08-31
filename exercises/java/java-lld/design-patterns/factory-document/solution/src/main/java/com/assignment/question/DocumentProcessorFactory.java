package com.assignment.question;

public class DocumentProcessorFactory {

    public static DocumentProcessor createDocumentProcessor(DocumentType documentType, String documentName) {
        return switch (documentType) {
            case TEXT -> new TextDocumentProcessor(documentName);
            case PRESENTATION -> new PresentationDocumentProcessor(documentName);
            case SPREAD_SHEET -> new SpreadsheetDocumentProcessor(documentName);
            default -> throw new IllegalArgumentException("Unsupported document type: " + documentType);
        };
    }
}
