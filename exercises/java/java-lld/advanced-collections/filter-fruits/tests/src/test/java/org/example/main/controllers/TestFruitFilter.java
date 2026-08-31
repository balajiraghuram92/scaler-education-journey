package org.example.main.controllers;

import org.example.FruitFilter;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestFruitFilter {

    @Test
    public void testFilterFruitsStartingWithA() {
        List<String> allFruits = Arrays.asList("Apple", "Banana", "Apricot", "Avocado", "Orange");
        List<String> expectedFilteredFruits = Arrays.asList("Apple", "Apricot", "Avocado");
        List<String> actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);


        allFruits = Arrays.asList("Almond","Asian Pear");
        expectedFilteredFruits = Arrays.asList("Almond","Asian Pear");
        actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);

        allFruits = Arrays.asList("Akebia","Ambarella","Grapes","Acerola","Guava");
        expectedFilteredFruits = Arrays.asList("Akebia","Ambarella","Acerola");
        actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);
    }

    @Test
    public void testFilterFruitsStartingWithA_NoMatchingFruits() {
        List<String> allFruits = Arrays.asList("Banana", "Orange");
        List<String> expectedFilteredFruits = Arrays.asList();
        List<String> actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);


        allFruits = Arrays.asList("Grapes", "Guava");
        expectedFilteredFruits = Arrays.asList();
        actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);

        allFruits = Arrays.asList("DragonFruit", "Lichi","Strawberry");
        expectedFilteredFruits = Arrays.asList();
        actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);
    }

    @Test
    public void testFilterFruitsStartingWithA_EmptyList() {
        List<String> allFruits = Arrays.asList();
        List<String> expectedFilteredFruits = Arrays.asList();
        List<String> actualFilteredFruits = FruitFilter.filterFruitsStartingWithA(allFruits);
        assertEquals(expectedFilteredFruits, actualFilteredFruits);
    }
}
