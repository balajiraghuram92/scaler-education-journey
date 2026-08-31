package org.example;

// TODO: extend User with studentId and course fields; override displayInfo() to call
// super.displayInfo() first, then print "Student ID: <id>" and "Course: <course>" on
// their own lines.
public class Student extends User {
    private final int studentId;
    private final String course;

    public Student(String username, String email, int studentId, String course) {
        super(username, email);
        this.studentId = studentId;
        this.course = course;
    }

    public int getStudentId() {
        return studentId;
    }

    public String getCourse() {
        return course;
    }
}
