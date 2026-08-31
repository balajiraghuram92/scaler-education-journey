package org.example;

import java.util.List;

public class SentenceProcessor {
    public static int processSentences(List<String> sentences) {
        int averageLength = (int) sentences.stream()
                .filter(sentence -> sentence.contains("Java"))
                .mapToInt(String::length)
                .average()
                .orElse(0);

        return averageLength;
    }
}
