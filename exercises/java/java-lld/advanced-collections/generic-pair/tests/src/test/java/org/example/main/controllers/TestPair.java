package org.example.main.controllers;
import org.example.Pair;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class TestPair {

    @Test
    public void testGetFirst_IntegerStringPair() {
        Pair<Integer, String> pair = new Pair<>(10, "Hello");
        assertEquals((Integer) 10, pair.getFirst());
    }

    @Test
    public void testGetSecond_IntegerStringPair() {
        Pair<Integer, String> pair = new Pair<>(10, "Hello");
        assertEquals("Hello", pair.getSecond());
    }

    @Test
    public void testGetFirst_StringDoublePair() {
        Pair<String, Double> pair = new Pair<>("Pi", 3.14);
        assertEquals("Pi", pair.getFirst());
    }

    @Test
    public void testGetSecond_StringDoublePair() {
        Pair<String, Double> pair = new Pair<>("Pi", 3.14);
        assertEquals((Double) 3.14, pair.getSecond());
    }

    @Test
    public void testBooleanPair() {
        Pair<Boolean, Boolean> pair = new Pair<>(true, false);
        assertEquals(Boolean.TRUE, pair.getFirst());
        assertEquals(Boolean.FALSE, pair.getSecond());
    }

    @Test
    public void testWithNullValues() {
        Pair<String, String> pair = new Pair<>(null, null);
        assertNull(pair.getFirst());
        assertNull(pair.getSecond());
    }

    @Test
    public void testIntegerBoundaryValues() {
        Pair<Integer, Integer> pair = new Pair<>(Integer.MIN_VALUE, Integer.MAX_VALUE);
        assertEquals((Integer)Integer.MIN_VALUE, pair.getFirst());
        assertEquals((Integer)Integer.MAX_VALUE, pair.getSecond());
    }
}
