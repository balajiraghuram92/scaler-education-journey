package org.example;

import java.util.Arrays;
import java.util.List;

public class WordCounter {
    public static long countWords(List<String> sentences) {
        long wordCount = sentences.stream()
                .filter(sentence -> !sentence.contains("Java"))
                .map(sentence -> sentence.split("\\s+"))
                .flatMap(Arrays::stream)
                .distinct()
                .count();

        return wordCount;
    }
}
