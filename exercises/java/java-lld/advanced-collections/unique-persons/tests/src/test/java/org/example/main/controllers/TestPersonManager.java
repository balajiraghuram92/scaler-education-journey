package org.example.main.controllers;

import org.example.Person;
import org.example.PersonManager;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestPersonManager {

    @Test
    public void testRemoveDuplicatePersons() {
        List<Person> persons = new ArrayList<>();
        persons.add(new Person("Alice", 20));
        persons.add(new Person("Bob", 25));
        persons.add(new Person("Alice", 22));
        persons.add(new Person("Charlie", 22));
        persons.add(new Person("Bob", 30));

        List<Person> expected = new ArrayList<>();
        expected.add(new Person("Alice", 20));
        expected.add(new Person("Bob", 25));
        expected.add(new Person("Charlie", 22));

        List<Person> uniquePersons = PersonManager.removeDuplicatePersons(persons);

        assertEquals(expected.size(), uniquePersons.size());
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i).getName(), uniquePersons.get(i).getName());
            assertEquals(expected.get(i).getAge(), uniquePersons.get(i).getAge());
        }
    }

    @Test
    public void testRemoveDuplicatePersons_WithEmptyList() {
        List<Person> persons = new ArrayList<>();
        List<Person> uniquePersons = PersonManager.removeDuplicatePersons(persons);
        assertTrue(uniquePersons.isEmpty());
    }

    // Additional test cases can be added to cover edge cases
    @Test
    public void noDuplicates(){
        List<Person> persons = new ArrayList<>();
        persons.add(new Person("Alice", 20));
        persons.add(new Person("Bob", 25));
        persons.add(new Person("Charlie", 22));
        persons.add(new Person("Ronny", 30));
        persons.add(new Person("Prateek", 31));

        List<Person> expected = new ArrayList<>();
        expected.add(new Person("Alice", 20));
        expected.add(new Person("Bob", 25));
        expected.add(new Person("Charlie", 22));
        expected.add(new Person("Ronny", 30));
        expected.add(new Person("Prateek", 31));

        assertEquals(expected,PersonManager.removeDuplicatePersons(persons));

    }
}
