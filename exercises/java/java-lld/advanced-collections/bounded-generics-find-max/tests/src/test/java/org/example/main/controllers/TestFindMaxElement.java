package org.example.main.controllers;
import org.example.FindMaxElement;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class TestFindMaxElement {

    @Test
    public void testFindMax_Integer() {
        Integer[] numbers = {4, 7, 1, 9, 3, 5};
        Integer maxNumber = FindMaxElement.findMax(numbers);
        assertEquals((Integer) 9, maxNumber);
    }

    @Test
    public void testFindMax_Double() {
        Double[] decimals = {3.14, 2.71, 1.618, 2.718};
        Double maxDecimal = FindMaxElement.findMax(decimals);
        assertEquals((Double) 3.14, maxDecimal);
    }

    @Test
    public void testFindMax_String() {
        String[] words = {"Apple", "Banana", "Peach", "Orange"};
        String maxWord = FindMaxElement.findMax(words);
        assertEquals("Peach", maxWord);
    }

    @Test
    public void testFindMax_Character() {
        Character[] letters = {'a', 'e', 'i', 'o', 'u'};
        Character maxLetter = FindMaxElement.findMax(letters);
        assertEquals((Character) 'u', maxLetter);
    }

    @Test
    public void testFindMax_NegativeNumbers() {
        Integer[] numbers = {-1, -3, -7, -4};
        Integer maxNumber = FindMaxElement.findMax(numbers);
        assertEquals((Integer) (-1), maxNumber);
    }

    @Test
    public void testFindMax_Float() {
        Float[] decimals = {1.0f, 3.14f, -1.618f, 2.718f};
        Float maxDecimal = FindMaxElement.findMax(decimals);
        assertEquals((Float) 3.14f, maxDecimal);
    }

    @Test
    public void testFindMax_NullArray() {
        Integer[] numbers = null;
        Integer maxNumber = FindMaxElement.findMax(numbers);
        assertNull(maxNumber);
    }

    @Test
    public void testFindMax_EmptyArray() {
        Integer[] numbers = {};
        Integer maxNumber = FindMaxElement.findMax(numbers);
        assertNull(maxNumber);
    }
}
