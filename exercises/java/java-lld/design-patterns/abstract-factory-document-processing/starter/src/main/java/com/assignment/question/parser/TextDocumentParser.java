package com.assignment.question.parser;

import com.assignment.question.DocumentType;

// TODO: extend DocumentParser and implement parseDocument() and supportsType() (DocumentType.TEXT).
public class TextDocumentParser extends DocumentParser {

    public TextDocumentParser(String path) {
        super(path);
    }

    public void parseDocument() {

    }

    @Override
    public DocumentType supportsType() {
        return null;
    }
}
