package org.example.main.controllers;

import org.example.Student;
import org.example.StudentSorter;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestStudentSorter {

    @Test
    public void testSortStudentsByAgeDescending() {
        List<Student> students = new ArrayList<>();
        students.add(new Student("Alice", 20));
        students.add(new Student("Bob", 25));
        students.add(new Student("Charlie", 22));

        List<Student> expected = new ArrayList<>();
        expected.add(new Student("Bob", 25));
        expected.add(new Student("Charlie", 22));
        expected.add(new Student("Alice", 20));

        StudentSorter.sortStudentsByAgeDescending(students);
        assertEquals(expected.size(), students.size());
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i).getName(), students.get(i).getName());
            assertEquals(expected.get(i).getAge(), students.get(i).getAge());
        }
    }

    @Test
    public void testSortStudentsByAgeDescending_WithEmptyList() {
        List<Student> students = new ArrayList<>();
        StudentSorter.sortStudentsByAgeDescending(students);
        assertTrue(students.isEmpty());
    }

    @Test
    public void testSortStudentsByAgeDescending_WithSingleElement() {
        List<Student> students = new ArrayList<>();
        students.add(new Student("Alice", 20));
        StudentSorter.sortStudentsByAgeDescending(students);
        assertEquals(20, students.get(0).getAge());
    }

    @Test
    public void testSortStudentsByAgeDescending_WithAlreadySorted() {
        List<Student> students = new ArrayList<>();
        students.add(new Student("Alice", 25));
        students.add(new Student("Bob", 22));
        students.add(new Student("Charlie", 20));
        StudentSorter.sortStudentsByAgeDescending(students);
        assertEquals(25, students.get(0).getAge());
        assertEquals(22, students.get(1).getAge());
        assertEquals(20, students.get(2).getAge());
    }
}
