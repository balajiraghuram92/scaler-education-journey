package org.example.main.controllers;

import org.example.GenericComparison;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestGenericComparison {
    // Unit test for comparing Integer objects
    @Test
    public void testCompareIntegers1() {
        int result = GenericComparison.compare(5, 10);
        assertEquals(-1, result);
    }

    @Test
    public void testCompareIntegers2() {
        int result = GenericComparison.compare(-33, -33);
        assertEquals(0, result);
    }

    // Unit test for comparing String objects
    @Test
    public void testCompareStrings1() {
        int result = GenericComparison.compare("apple", "banana");
        assertEquals(-1, result);
    }

    @Test
    public void testCompareStrings2() {
        int result = GenericComparison.compare("mango", "banana");
        assertEquals(11, result);
    }
    @Test
    public void testCompareStrings3() {
        int result = GenericComparison.compare("mango", "mango");
        assertEquals(0, result);
    }

    @Test
    public void testCompareDoubles() {
        int result = GenericComparison.compare(10.5, 10.5);
        assertEquals(0, result);
    }

    @Test
    public void testCompareCharacters() {
        int result = GenericComparison.compare('a', 'b');
        assertEquals(-1, result);
    }


}
