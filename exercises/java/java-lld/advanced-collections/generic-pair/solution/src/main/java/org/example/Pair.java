package org.example;

public class Pair<T, U> {
    private T first;
    private U second;

    // Constructor to initialize the Pair with two values
    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    // Method to get the first value of the Pair
    public T getFirst() {
        return first;
    }

    // Method to get the second value of the Pair
    public U getSecond() {
        return second;
    }
}
