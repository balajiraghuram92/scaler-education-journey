package com.assignment.question;

public class SpreadsheetDocumentProcessor extends DocumentProcessor {

    public SpreadsheetDocumentProcessor(String documentName) {
        super(documentName);
    }

    @Override
    public void processDocument() {
        // TODO: implement spreadsheet-document-specific processing logic
    }

    @Override
    public DocumentType supportsType() {
        // TODO: return DocumentType.SPREAD_SHEET
        return null;
    }

    public void performDataAnalysis() {
        System.out.println("Performing data analysis on the spreadsheet.");
    }
}
