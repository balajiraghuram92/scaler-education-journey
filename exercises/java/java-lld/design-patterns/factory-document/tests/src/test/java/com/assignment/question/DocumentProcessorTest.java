package com.assignment.question;

import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class DocumentProcessorTest {

    @Test
    public void testParentClass() {
        // Define the package where your processors are located
        String packageName = DocumentProcessorTest.class.getPackageName();

        // Get all subtypes of DocumentProcessor using reflection
        Reflections reflections = new Reflections(packageName, new SubTypesScanner(false));
        Set<Class<? extends DocumentProcessor>> subTypes = reflections.getSubTypesOf(DocumentProcessor.class);

        // Ensure there is at least one subclass
        assertEquals(3, subTypes.size(),
                "If the factory is implemented correctly, there should be 3 concrete product classes of DocumentProcessor.");

        // Check if DocumentProcessor has the required methods and fields
        boolean hasDocumentName = Arrays.stream(DocumentProcessor.class.getDeclaredFields())
                .anyMatch(field -> field.getType().equals(String.class));
        assertTrue(hasDocumentName,
                "If the parent class is implemented correctly, it should have a field of type String for the document name.");

        boolean hasSupportsType = Arrays.stream(DocumentProcessor.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("supportsType")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(DocumentType.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasSupportsType,
                "If the parent class is implemented correctly, it should have a method called supportsType with no parameters and DocumentType return type.");


        boolean hasProcessDocument = Arrays.stream(DocumentProcessor.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("processDocument")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(void.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasProcessDocument,
                "If the parent class is implemented correctly, it should have a method called processDocument with no parameters and void return type.");

    }

    @Test
    public void testDocumentProcessorFactory() {

        // Check if the DocumentProcessorFactory class has a static method to create the
        // document processor
        boolean hasCreateMethod = Arrays.stream(DocumentProcessorFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(DocumentProcessor.class)
                        && Arrays.asList(method.getParameterTypes()).contains(DocumentType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));

        assertTrue(hasCreateMethod,
                "If the factory is implemented correctly, it should have a static method to create a document process that takes two parameters: DocumentType and String documentName.");
    }

    @Test
    public void testDocumentProcessorFactoryCreateMethodInvocation() {
        // Get all methods in DocumentProcessorFactory
        Method[] methods = DocumentProcessorFactory.class.getDeclaredMethods();

        // Check if any method is a static method that returns DocumentProcessor
        Method createMethod = Arrays.stream(methods)
                .filter(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(DocumentProcessor.class)
                        && Arrays.asList(method.getParameterTypes()).contains(DocumentType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createMethod, "If the factory is implemented correctly, it should have a static method to create a document process that takes two parameters: DocumentType and String documentName.");

        // Create a DocumentType and a document name
        DocumentType docType = DocumentType.PRESENTATION;
        String docName = "SamplePresentation.pptx";

        // Invoke the create method with parameters in different orders
        DocumentProcessor processor = null;

        try {
            processor = (DocumentProcessor) createMethod.invoke(null, docType, docName);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            // Swallow the exception and try again with parameters in the reversed order
        }

        if (processor == null) {
            try {
                processor = (DocumentProcessor) createMethod.invoke(null, docName, docType);
            } catch (IllegalAccessException | InvocationTargetException ignored) {

            }
        }

        // Verify that the returned processors are not null and match the expected type
        assertNotNull(processor, "If the factory is implemented correctly, the create method should return a non-null DocumentProcessor.");
        assertEquals(DocumentType.PRESENTATION, processor.supportsType(), "If the factory is implemented correctly, the create method should return a PresentationProcessor for DocumentType.PRESENTATION.");

    }

}
