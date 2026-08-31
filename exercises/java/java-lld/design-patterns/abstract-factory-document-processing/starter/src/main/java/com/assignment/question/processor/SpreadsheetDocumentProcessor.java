package com.assignment.question.processor;

import com.assignment.question.DocumentType;

// TODO: extend DocumentProcessor and implement processDocument() and supportsType() (DocumentType.SPREAD_SHEET).
public class SpreadsheetDocumentProcessor extends DocumentProcessor {

    public SpreadsheetDocumentProcessor(String documentName) {
        super(documentName);
    }

    @Override
    public void processDocument() {

    }

    @Override
    public DocumentType supportsType() {
        return null;
    }

    public void performDataAnalysis() {
        System.out.println("Performing data analysis on the spreadsheet.");
    }
}
