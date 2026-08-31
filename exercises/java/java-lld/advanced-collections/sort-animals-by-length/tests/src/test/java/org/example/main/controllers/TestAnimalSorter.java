package org.example.main.controllers;

import org.example.AnimalSorter;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestAnimalSorter {
    @Test
    public void testSortAnimalsByLengthDescending() {
//        TC1
        List<String> animals = Arrays.asList("zebra", "lion", "tiger", "elephant", "giraffe");
        List<String> expectedSortedAnimals = Arrays.asList("elephant", "giraffe", "zebra", "tiger", "lion");
        List<String> actualSortedAnimals = AnimalSorter.sortAnimalsByLengthDescending(animals);

        assertEquals(expectedSortedAnimals, actualSortedAnimals);

//        TC2
        animals = Arrays.asList("cat","dog","animal-x","elephant","mouse");
        expectedSortedAnimals = Arrays.asList("animal-x", "elephant", "mouse", "cat", "dog");
        actualSortedAnimals = AnimalSorter.sortAnimalsByLengthDescending(animals);

        assertEquals(expectedSortedAnimals,actualSortedAnimals);

//        TC3
        animals = Arrays.asList("a","b","d","c","a");
        expectedSortedAnimals = Arrays.asList("a","b","d","c","a");
        actualSortedAnimals = AnimalSorter.sortAnimalsByLengthDescending(animals);

        assertEquals(expectedSortedAnimals,actualSortedAnimals);
    }

    @Test
    public void testSortAnimalsByLengthDescending_EmptyList() {
        List<String> animals = Arrays.asList();
        List<String> expectedSortedAnimals = Arrays.asList();

        List<String> actualSortedAnimals = AnimalSorter.sortAnimalsByLengthDescending(animals);

        assertEquals(expectedSortedAnimals, actualSortedAnimals);
    }
}
