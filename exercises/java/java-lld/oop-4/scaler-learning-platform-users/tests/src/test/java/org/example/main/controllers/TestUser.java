package org.example.main.controllers;

import org.example.Employee;
import org.example.Student;
import org.example.User;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class TestUser {

    @Test
    public void testUser() {
        User user = new User("john_doe", "john@example.com");
        assertEquals("john_doe", user.getUsername());
        assertEquals("john@example.com", user.getEmail());
    }

    @Test
    public void testStudent() {
        Student student = new Student("jane_smith", "jane@example.com", 1001, "Computer Science");
        assertEquals("jane_smith", student.getUsername());
        assertEquals("jane@example.com", student.getEmail());
        assertEquals(1001, student.getStudentId());
        assertEquals("Computer Science", student.getCourse());
    }

    @Test
    public void testEmployee() {
        Employee employee = new Employee("jack_jones", "jack@example.com", 2001, "Human Resources");
        assertEquals("jack_jones", employee.getUsername());
        assertEquals("jack@example.com", employee.getEmail());
        assertEquals(2001, employee.getEmployeeId());
        assertEquals("Human Resources", employee.getDepartment());
    }

    @Test
    public void testDisplayUserInfo() {
        final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        final PrintStream originalOut = System.out;
        System.setOut(new PrintStream(outContent));

        User user = new User("john_doe", "john@example.com");
        user.displayInfo();
        String expectedOutput = String.format("Username: john_doe%sEmail: john@example.com%s", System.lineSeparator(), System.lineSeparator());
        assertEquals(expectedOutput, outContent.toString());

        System.setOut(originalOut);
    }

    @Test
    public void testDisplayStudentInfo() {
        final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        final PrintStream originalOut = System.out;
        System.setOut(new PrintStream(outContent));

        Student student = new Student("jane_smith", "jane@example.com", 1001, "Computer Science");
        student.displayInfo();

        String expectedOutput = String.format("Username: jane_smith%sEmail: jane@example.com%sStudent ID: 1001%sCourse: Computer Science%s",
                System.lineSeparator(), System.lineSeparator(), System.lineSeparator(), System.lineSeparator());

        assertEquals(expectedOutput, outContent.toString());

        System.setOut(originalOut);
    }

    @Test
    public void testDisplayEmployeeInfo() {
        final ByteArrayOutputStream outContent = new ByteArrayOutputStream();
        final PrintStream originalOut = System.out;
        System.setOut(new PrintStream(outContent));

        Employee employee = new Employee("jack_jones", "jack@example.com", 2001, "Human Resources");
        employee.displayInfo();

        String expectedOutput = String.format("Username: jack_jones%sEmail: jack@example.com%sEmployee ID: 2001%sDepartment: Human Resources%s",
                System.lineSeparator(), System.lineSeparator(), System.lineSeparator(), System.lineSeparator());

        assertEquals(expectedOutput, outContent.toString());

        System.setOut(originalOut);
    }

    @Test
    public void testUserWithNullValues() {
        User user = new User(null, null);
        assertNull(user.getUsername());
        assertNull(user.getEmail());
    }

    @Test
    public void testUserSpecialCharacters() {
        User user = new User("john_doe@2024", "john@example.com");
        assertEquals("john_doe@2024", user.getUsername());
        assertEquals("john@example.com", user.getEmail());
    }

}
