package org.example;

public class PrintArrayElements {
    // Generic method to print elements of an array
    // Hint for the learner - print space after each element,don't print newline after the last element.

    public static <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.print(element + " ");
        }
    }
}
