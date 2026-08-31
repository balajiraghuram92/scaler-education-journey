package com.assignment.question.printer;

import com.assignment.question.DocumentType;
import com.assignment.question.processor.DocumentProcessor;

// TODO: extend DocumentPrinter and implement printDocument() and supportsType() (DocumentType.SPREAD_SHEET).
public class SpreadsheetDocumentPrinter extends DocumentPrinter {

    public SpreadsheetDocumentPrinter(DocumentProcessor processor) {
        super(processor);
    }

    public void printDocument() {

    }

    @Override
    public DocumentType supportsType() {
        return null;
    }
}
