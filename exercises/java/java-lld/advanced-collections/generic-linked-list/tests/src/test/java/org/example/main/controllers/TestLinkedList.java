package org.example.main.controllers;
import org.example.LinkedList;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.jupiter.api.Assertions.*;

public class TestLinkedList {

    @Test
    public void testAdd() {
        LinkedList<Integer> list = new LinkedList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);

        assertEquals(5, list.size());
    }

    @Test
    public void testDisplay() {
        LinkedList<String> list = new LinkedList<>();
        list.add("apple");
        list.add("banana");
        list.add("orange");

        assertEquals("apple banana orange ", getPrintedOutput(list));
    }

    @Test
    public void testIsEmpty() {
        LinkedList<Double> list = new LinkedList<>();
        assertTrue(list.isEmpty());

        list.add(3.14);
        assertFalse(list.isEmpty());
    }

    @Test
    public void testSize() {
        LinkedList<Character> list = new LinkedList<>();
        assertEquals(0, list.size());

        list.add('a');
        list.add('b');
        list.add('c');
        assertEquals(3, list.size());
    }

    @Test
    public void testAddNull() {
        LinkedList<String> list = new LinkedList<>();
        list.add(null);
        list.add("test");
        assertEquals(2, list.size());
    }

    @Test
    public void testDisplayEmptyList() {
        LinkedList<String> list = new LinkedList<>();
        assertEquals("", getPrintedOutput(list));
    }

    private String getPrintedOutput(LinkedList<String> list) {
        // Redirect System.out to a ByteArrayOutputStream to capture printed output
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        PrintStream originalOut = System.out;
        System.setOut(new PrintStream(outputStream));

        // Call the display method
        list.display();

        // Reset System.out
        System.setOut(originalOut);

        // Return the captured output
        return outputStream.toString();
    }
}
