package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.parser.SpreadsheetDocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.printer.SpreadsheetDocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;
import com.assignment.question.processor.SpreadsheetDocumentProcessor;

// TODO: extend DocumentFactory, wiring up the Spreadsheet family:
// SpreadsheetDocumentProcessor, SpreadsheetDocumentParser, SpreadsheetDocumentPrinter.
public class SpreadsheetDocumentFactory extends DocumentFactory {

    @Override
    public DocumentProcessor createProcessor(String name) {
        return null;
    }

    @Override
    public DocumentParser createParser(String path) {
        return null;
    }

    @Override
    public DocumentPrinter createPrinter(DocumentProcessor documentProcessor) {
        return null;
    }

    @Override
    public DocumentType supportsType() {
        return null;
    }
}
