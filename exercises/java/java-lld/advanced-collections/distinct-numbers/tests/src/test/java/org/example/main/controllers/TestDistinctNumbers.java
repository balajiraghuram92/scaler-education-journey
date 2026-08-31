package org.example.main.controllers;

import org.example.DistinctNumbers;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class TestDistinctNumbers {

    @Test
    public void testGetDistinctNumbers() {

        //        TC1
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 2, 3, 5, 6, 1, 7, 8, 9, 7);
        List<Integer> expectedDistinctNumbers = TestHelper.findDistinct(numbers);
        List<Integer> actualDistinctNumbers = DistinctNumbers.getDistinctNumbers(numbers);

        assertEquals(expectedDistinctNumbers, actualDistinctNumbers);

        //        TC2
        numbers = Arrays.asList(5,5,5,6,6,6,4,4,4);
        expectedDistinctNumbers = TestHelper.findDistinct(numbers);
        actualDistinctNumbers = DistinctNumbers.getDistinctNumbers(numbers);

        assertEquals(expectedDistinctNumbers, actualDistinctNumbers);

        //        TC3
        numbers = Arrays.asList(1,1,1,1,1,1);
        expectedDistinctNumbers = TestHelper.findDistinct(numbers);
        actualDistinctNumbers = DistinctNumbers.getDistinctNumbers(numbers);

        assertEquals(expectedDistinctNumbers, actualDistinctNumbers);

//        TC4
        numbers = Arrays.asList(-1,-2,-3,-4,-1,-2,-2,-3,-4,5,1,0,(int)1e9);
        expectedDistinctNumbers = TestHelper.findDistinct(numbers);
        actualDistinctNumbers = DistinctNumbers.getDistinctNumbers(numbers);

        assertEquals(expectedDistinctNumbers, actualDistinctNumbers);
    }

    @Test
    public void testGetDistinctNumbers_EmptyList() {
        List<Integer> numbers = Arrays.asList();
        List<Integer> expectedDistinctNumbers = Arrays.asList();

        List<Integer> actualDistinctNumbers = DistinctNumbers.getDistinctNumbers(numbers);

        assertEquals(expectedDistinctNumbers, actualDistinctNumbers);
    }
}
