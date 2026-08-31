package org.example.main.controllers;

import org.example.FrequencyCounter;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestFrequencyCounter {

    @Test
    public void testCountFrequencies() {
        int[] nums1 = {1, 2, 3, 4, 1, 2, 3, 1, 2, 1};
        Map<Integer, Integer> result1 = FrequencyCounter.countFrequencies(nums1);
        Map<Integer, Integer> expected1 = new HashMap<>();
        expected1.put(1, 4);
        expected1.put(2, 3);
        expected1.put(3, 2);
        expected1.put(4, 1);
        assertEquals(expected1, result1);

        int[] nums2 = {5, 5, 5, 5, 5};
        Map<Integer, Integer> result2 = FrequencyCounter.countFrequencies(nums2);
        Map<Integer, Integer> expected2 = new HashMap<>();
        expected2.put(5, 5);
        assertEquals(expected2, result2);

        int[] nums3 = {1, 2, 3, 4, 5};
        Map<Integer, Integer> result3 = FrequencyCounter.countFrequencies(nums3);
        Map<Integer, Integer> expected3 = new HashMap<>();
        expected3.put(1, 1);
        expected3.put(2, 1);
        expected3.put(3, 1);
        expected3.put(4, 1);
        expected3.put(5, 1);
        assertEquals(expected3, result3);
    }

    @Test
    public void empty_testCountFrequencies() {
        int[] nums1 = {};
        Map<Integer, Integer> result1 = FrequencyCounter.countFrequencies(nums1);
        Map<Integer, Integer> expected1 = new HashMap<>();
        assertEquals(expected1, result1);
    }
}
