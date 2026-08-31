package com.assignment.question.parser;

import com.assignment.question.DocumentType;

// TODO: extend DocumentParser and implement parseDocument() and supportsType() (DocumentType.SPREAD_SHEET).
public class SpreadsheetDocumentParser extends DocumentParser {

    public SpreadsheetDocumentParser(String path) {
        super(path);
    }

    public void parseDocument() {

    }

    @Override
    public DocumentType supportsType() {
        return null;
    }
}
