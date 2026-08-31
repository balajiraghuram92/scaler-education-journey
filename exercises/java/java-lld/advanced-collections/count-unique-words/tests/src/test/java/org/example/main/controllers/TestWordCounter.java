package org.example.main.controllers;

import org.example.WordCounter;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestWordCounter {

    @Test
    public void testProcessSentences() {
        List<String> sentences = Arrays.asList(
                "Java is a programming language.",
                "Python is also a good language.",
                "Java stream processing is powerful.",
                "C++ is not as popular as Java."
        );

        long wordCount = WordCounter.countWords(sentences);
        assertEquals(6, wordCount);
    }

    @Test
    public void testProcessSentences_NoJava() {
        List<String> sentences = Arrays.asList(
                "Python is a programming language.",
                "JavaScript is used for web development.",
                "Ruby is known for its simplicity."
        );

        long wordCount = WordCounter.countWords(sentences);
        assertEquals(10, wordCount);
    }

    @Test
    public void testProcessSentences_EmptyList() {
        List<String> sentences = Arrays.asList();
        long wordCount = WordCounter.countWords(sentences);
        assertEquals(0, wordCount);
    }
}
