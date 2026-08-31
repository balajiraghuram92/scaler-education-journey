package org.example.main.controllers;
import org.example.PrintArrayElements;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestPrintArrayElements {

    @Test
    public void testPrintArray_Integer() {
        Integer[] numbers = {1, 2, 3, 4, 5};
        String expectedOutput = "1 2 3 4 5 ";
        assertEquals(expectedOutput, getPrintedOutput(numbers));
    }

    @Test
    public void testPrintArray_String() {
        String[] words = {"apple", "banana", "orange"};
        String expectedOutput = "apple banana orange ";
        assertEquals(expectedOutput, getPrintedOutput(words));
    }

    @Test
    public void testPrintArray_Empty() {
        Integer[] emptyArray = {};
        String expectedOutput = "";
        assertEquals(expectedOutput, getPrintedOutput(emptyArray));
    }

    @Test
    public void testPrintArray_SingleElement() {
        Integer[] singleElement = {42};
        String expectedOutput = "42 ";
        assertEquals(expectedOutput, getPrintedOutput(singleElement));
    }

    @Test
    public void testPrintArray_Double() {
        Double[] doubles = {1.1, 2.2, 3.3};
        String expectedOutput = "1.1 2.2 3.3 ";
        assertEquals(expectedOutput, getPrintedOutput(doubles));
    }

    @Test
    public void testPrintArray_Character() {
        Character[] characters = {'a', 'b', 'c'};
        String expectedOutput = "a b c ";
        assertEquals(expectedOutput, getPrintedOutput(characters));
    }

    @Test
    public void testPrintArray_NullElements() {
        Integer[] arrayWithNulls = {1, null, 3};
        String expectedOutput = "1 null 3 ";
        assertEquals(expectedOutput, getPrintedOutput(arrayWithNulls));
    }

    private String getPrintedOutput(Object[] array) {
        // Redirect System.out to a ByteArrayOutputStream to capture printed output
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        PrintStream originalOut = System.out;
        System.setOut(new PrintStream(outputStream));

        // Call the printArray method
        PrintArrayElements.printArray(array);

        // Reset System.out
        System.setOut(originalOut);

        // Return the captured output
        return outputStream.toString();
    }
}
