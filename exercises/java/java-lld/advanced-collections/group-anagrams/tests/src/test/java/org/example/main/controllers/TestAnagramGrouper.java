package org.example.main.controllers;

import org.example.AnagramGrouper;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestAnagramGrouper {

    @Test
    public void testGroupAnagrams_WithMultipleAnagrams() {
        String[] input = {"eat", "tea", "tan", "ate", "nat", "bat"};
        List<List<String>> result = AnagramGrouper.groupAnagrams(input);
        List<List<String>> expected = Arrays.asList(
                Arrays.asList("eat", "tea", "ate"),
                Arrays.asList("tan", "nat"),
                Arrays.asList("bat")

        );
        assertEquals(expected, result);
    }

    @Test
    public void testGroupAnagrams_WithNoAnagrams() {
        String[] input = {"abc", "def", "ghi"};
        List<List<String>> result = AnagramGrouper.groupAnagrams(input);
        List<List<String>> expected = Arrays.asList(
                Arrays.asList("abc"),
                Arrays.asList("def"),
                Arrays.asList("ghi")
        );
        assertEquals(expected, result);
    }

    @Test
    public void testGroupAnagrams_WithSomeAnagrams() {
        String[] input = {"eat", "tan", "bat", "ate", "nat", "cat"};
        List<List<String>> result = AnagramGrouper.groupAnagrams(input);
        List<List<String>> expected = Arrays.asList(
                Arrays.asList("eat", "ate"),
                Arrays.asList("tan", "nat"),
                Arrays.asList("bat"),
                Arrays.asList("cat")
        );
        assertEquals(expected, result);
    }

    @Test
    public void emptyAndNullStrings(){
        String[] input = {};
        List<List<String>> result = AnagramGrouper.groupAnagrams(input);
        assertEquals(new ArrayList<>(), result);

        input = null;
        result = AnagramGrouper.groupAnagrams(input);
        assertEquals(new ArrayList<>(),result);
    }
}
