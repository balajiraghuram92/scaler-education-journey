package com.assignment.question;

import com.assignment.question.parser.DocumentParser;
import com.assignment.question.printer.DocumentPrinter;
import com.assignment.question.processor.DocumentProcessor;
import com.assignment.question.processor.TextDocumentProcessor;
import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class DocumentFactoryTest {

    @Test
    public void testAbstractFactoryClass() {
        // Define the package where your files are located
        String packageName = DocumentFactoryTest.class.getPackageName();

        // Get all subtypes of DocumentFactory using reflection
        Reflections reflections = new Reflections(packageName, new SubTypesScanner(false));
        Set<Class<? extends DocumentFactory>> subTypes = reflections.getSubTypesOf(DocumentFactory.class);

        assertEquals(2, subTypes.size(),
                "If the abstract factory is implemented correctly, it should have 2 subtypes: PresentationFactory, and SpreadsheetFactory.");

        boolean hasSupportsType = Arrays.stream(DocumentFactory.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("supportsType")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(DocumentType.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasSupportsType,
                "If the abstract factory class is implemented correctly, it should have a method called supportsType with no parameters and DocumentType return type.");

        boolean hasCreateProcessorMethod = Arrays.stream(DocumentFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(DocumentProcessor.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));
        assertTrue(hasCreateProcessorMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a document processor that takes a String parameter document name and returns a DocumentProcessor.");

        boolean hasCreateParserMethod = Arrays.stream(DocumentFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(DocumentParser.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));
        assertTrue(hasCreateParserMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a document parser that takes a String parameter document path and returns a DocumentParser.");

        boolean hasCreatePrinterMethod = Arrays.stream(DocumentFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isAbstract(method.getModifiers())
                        && method.getReturnType().equals(DocumentPrinter.class)
                        && Arrays.asList(method.getParameterTypes())
                        .contains(DocumentProcessor.class));
        assertTrue(hasCreatePrinterMethod,
                "If the abstract factory class is implemented correctly, it should have a method to create a document printer that takes a DocumentProcessor parameter and returns a DocumentPrinter.");

    }

    @Test
    public void testDocumentProcessorCreateMethodInvocation() {
        // Get all methods in TextDocumentFactory
        Method[] methods = TextDocumentFactory.class.getDeclaredMethods();

        // Check if any method is returning a DocumentProcessor
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(DocumentProcessor.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a document processor that takes a String parameter document name and returns a DocumentProcessor.");

        String docName = "test.txt";

        // Invoke the create method with parameters in different orders
        DocumentProcessor processor = null;

        try {
            processor = (DocumentProcessor) createMethod.invoke(new TextDocumentFactory(), docName);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a document processor should take a String parameter document name and return a DocumentProcessor.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(processor,
                "If the abstract factory is implemented correctly, the create method for a document processor should return a non-null DocumentProcessor.");
        assertEquals(DocumentType.TEXT, processor.supportsType(),
                "If the factory is implemented correctly, the create method should return a TextDocumentProcessor for a text document.");

    }

    @Test
    public void testDocumentParserCreateMethodInvocation() {
        // Get all methods in TextDocumentFactory
        Method[] methods = TextDocumentFactory.class.getDeclaredMethods();

        // Check if any method is returning a DocumentProcessor
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(DocumentParser.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a document parser that takes a String parameter document path and returns a DocumentParser.");

        String docName = "test.txt";

        // Invoke the create method with parameters in different orders
        DocumentParser parser = null;

        try {
            parser = (DocumentParser) createMethod.invoke(new TextDocumentFactory(), docName);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a document parser should take a String parameter document path and return a DocumentParser.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(parser,
                "If the abstract factory is implemented correctly, the create method for a document parser should return a non-null DocumentParser.");
        assertEquals(DocumentType.TEXT, parser.supportsType(),
                "If the factory is implemented correctly, the create method should return a TextDocumentParser for a text document.");

    }

    @Test
    public void testDocumentPrinterCreateMethodInvocation() {
        // Get all methods in TextDocumentFactory
        Method[] methods = TextDocumentFactory.class.getDeclaredMethods();

        // Check if any method is returning a DocumentPrinter
        Method createMethod = Arrays.stream(methods)
                .filter(method -> method.getReturnType().equals(DocumentPrinter.class)
                        && Arrays.asList(method.getParameterTypes()).contains(DocumentProcessor.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod,
                "If the abstract factory is implemented correctly, it should have a method to create a document printer that takes a DocumentProcessor parameter and returns a DocumentPrinter.");

        DocumentProcessor processor = new TextDocumentProcessor("test.txt");
        DocumentPrinter printer = null;

        try {
            printer = (DocumentPrinter) createMethod.invoke(new TextDocumentFactory(), processor);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            fail("If the abstract factory is implemented correctly, the create method for a document printer should take a DocumentProcessor parameter and return a DocumentPrinter.");
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(printer,
                "If the abstract factory is implemented correctly, the create method for a document printer should return a non-null DocumentPrinter.");
        assertEquals(DocumentType.TEXT, printer.supportsType(),
                "If the factory is implemented correctly, the create method should take a TextDocumentProcessor and return a TextDocumentPrinter.");

    }

}
