package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.parser.TextDocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.printer.TextDocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;
import com.assignment.question.processor.TextDocumentProcessor;

// TODO: extend DocumentFactory, wiring up the Text family: TextDocumentProcessor,
// TextDocumentParser, TextDocumentPrinter.
public class TextDocumentFactory extends DocumentFactory {

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
