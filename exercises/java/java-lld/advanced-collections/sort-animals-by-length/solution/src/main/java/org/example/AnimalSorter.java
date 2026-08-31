package org.example;

import java.util.List;
import java.util.stream.Collectors;

public class AnimalSorter {

    public static List<String> sortAnimalsByLengthDescending(List<String> animals) {
        return animals.stream()
                .sorted((animal1, animal2) -> Integer.compare(animal2.length(), animal1.length()))
                .collect(Collectors.toList());
    }
}
