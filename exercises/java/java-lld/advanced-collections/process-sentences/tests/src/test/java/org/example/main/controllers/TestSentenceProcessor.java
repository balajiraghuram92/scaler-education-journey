package org.example.main.controllers;

import org.example.SentenceProcessor;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestSentenceProcessor {

    @Test
    public void testProcessSentences() {
        List<String> sentences = Arrays.asList(
                "Java is a programming language.",
                "Python is also a good language.",
                "Java stream processing is powerful.",
                "C++ is not as popular as Java."
        );

        int averageLength = SentenceProcessor.processSentences(sentences);
        assertEquals(32, averageLength);
    }

    @Test
    public void testProcessSentences_NoJava() {
        List<String> sentences = Arrays.asList(
                "Python is a programming language.",
                "JS is used for web development.",
                "Ruby is known for its simplicity.",
                "java is good"
        );

        int averageLength = SentenceProcessor.processSentences(sentences);
        assertEquals(0, averageLength);
    }

    @Test
    public void testProcessSentences_EmptyList() {
        List<String> sentences = Arrays.asList();
        int averageLength = SentenceProcessor.processSentences(sentences);
        assertEquals(0, averageLength);
    }
}
