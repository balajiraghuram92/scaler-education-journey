# Abstract Factory Pattern for Document Processing

Source folder: `1773391288_de667c89d2a2fb11 / Abstract_Factory-solution`

## Problem Statement

You are designing a document processing application. Depending on the type of document (e.g., text, spreadsheet, presentation), different processing routines are required. These routines involve multiple steps, such as parsing, formatting, and exporting, which need to be coordinated to ensure correct document processing. You want to create instances of these processing steps without explicitly specifying their classes and ensure that the steps within the same family are compatible.

## Detailed Requirements

Your task is to implement the Abstract Factory pattern to create document processors in the document processing application. The Abstract Factory pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes, allowing for easy addition of new document processor types and ensuring compatibility within families.

### Task 1 - Adding the factory methods to the abstract factory

The abstract factory class has been created for you. You will need to add the factory methods to create document processors, parsers, and printers to the abstract factory class. The method `supportsType` has already been abstracted out for you as an example. You will need to implement the `DocumentFactory` class as a common parent class for all the document factories.

### Task 2 - Implementing the Abstract Factory

Now that you have the abstract factory class, you will need to implement the abstract factory for text and spreadsheet documents. Two classes have been created for you: `TextDocumentFactory` and `SpreadsheetDocumentFactory`. You will need to implement the methods to create compatible document processors, parsers, and printers. Ensure that the created processors, parsers, and printers are compatible within the same family.

### Instructions

1. Implement the `DocumentFactory` interface with methods to create document processors, parsers, and printers.
2. Create concrete implementations of the `DocumentFactory` interface for text and spreadsheet documents. Implement the methods to create compatible document processors, parsers, and printers.
3. Run the provided test cases in the `DocumentFactoryTest` class to verify the correctness of your implementation. The tests will check if all document processors have a common parent class, and if the factory classes can correctly create document processors, parsers, and printers based on the document type and name.

## Graded Contract (from tests)

- `DocumentFactory` must be an abstract class (or interface) with 4 abstract methods:
  - `DocumentProcessor createProcessor(String documentName)` - returns DocumentProcessor
  - `DocumentParser createParser(String path)` - returns DocumentParser
  - `DocumentPrinter createPrinter(DocumentProcessor processor)` - returns DocumentPrinter
  - `DocumentType supportsType()` - returns DocumentType
- `TextDocumentFactory` and `SpreadsheetDocumentFactory` must extend `DocumentFactory` (exactly 2 subtypes)
- Each concrete factory's `createProcessor()` must return a processor with matching `supportsType()` value
- Each concrete factory's `createParser()` must return a parser with matching `supportsType()` value
- Each concrete factory's `createPrinter()` must return a printer with matching `supportsType()` value
- Reflection tests verify method signatures and return types via getDeclaredMethods()
- Tests invoke create methods via reflection and verify the returned objects are not null and have correct types

## Learner Template

```java
package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;

public abstract class DocumentFactory {
    
    public abstract DocumentProcessor createProcessor(String documentName);
    public abstract DocumentParser createParser(String path);
    public abstract DocumentPrinter createPrinter(DocumentProcessor processor);

    public abstract DocumentType supportsType();
}
```

```java
package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;

public class TextDocumentFactory extends DocumentFactory {

    @Override
    public DocumentProcessor createProcessor(String name) {
        // TODO: Implement
    }

    @Override
    public DocumentParser createParser(String path) {
        // TODO: Implement
    }

    @Override
    public DocumentPrinter createPrinter(DocumentProcessor documentProcessor) {
        // TODO: Implement
    }

    @Override
    public DocumentType supportsType() {
        // TODO: Implement
    }
}
```

```java
package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;

public class SpreadsheetDocumentFactory extends DocumentFactory {

    @Override
    public DocumentProcessor createProcessor(String name) {
        // TODO: Implement
    }

    @Override
    public DocumentParser createParser(String path) {
        // TODO: Implement
    }

    @Override
    public DocumentPrinter createPrinter(DocumentProcessor documentProcessor) {
        // TODO: Implement
    }

    @Override
    public DocumentType supportsType() {
        // TODO: Implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- The concrete implementations of `DocumentProcessor`, `DocumentParser`, and `DocumentPrinter` (these are provided as base classes with abstract methods)
- The specific logic to instantiate the correct concrete processor/parser/printer types (e.g., `new TextDocumentProcessor(name)`)
- The correct return value for `supportsType()` (e.g., `DocumentType.TEXT` vs `DocumentType.SPREAD_SHEET`)
