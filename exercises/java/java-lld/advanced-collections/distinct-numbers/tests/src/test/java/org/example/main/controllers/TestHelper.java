package org.example.main.controllers;

import java.util.List;
import java.util.stream.Collectors;

public class TestHelper {
    public static List<Integer> findDistinct(List<Integer> numbers){
        return numbers.stream()
                .distinct()
                .collect(Collectors.toList());
    }
}
