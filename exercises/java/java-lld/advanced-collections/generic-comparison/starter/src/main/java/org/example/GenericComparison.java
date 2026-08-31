package org.example;

// TODO: implement compare(...) — a generic method bounded to Comparable<T> that returns
// obj1.compareTo(obj2).
public class GenericComparison {

    public static <T extends Comparable<T>> int compare(T obj1, T obj2) {
        return 0;
    }
}
