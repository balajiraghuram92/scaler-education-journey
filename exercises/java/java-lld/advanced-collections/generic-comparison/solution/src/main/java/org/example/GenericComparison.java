package org.example;

public class GenericComparison {

    // Generic method to compare two objects of any comparable type
    public static <T extends Comparable<T>> int compare(T obj1, T obj2) {
        return obj1.compareTo(obj2);
    }
}
