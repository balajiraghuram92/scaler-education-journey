package org.example;

import java.util.List;
import java.util.stream.Collectors;

public class DistinctNumbers {

    public static List<Integer> getDistinctNumbers(List<Integer> numbers) {
        return numbers.stream()
                .distinct()
                .collect(Collectors.toList());
    }
}
