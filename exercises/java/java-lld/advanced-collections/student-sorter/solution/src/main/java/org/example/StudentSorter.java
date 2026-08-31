package org.example;
import java.util.*;

public class StudentSorter {
    public static void sortStudentsByAgeDescending(List<Student> students) {
        Comparator<Student> ageComparator = Comparator.comparingInt(Student::getAge).reversed();
        students.sort(ageComparator);
    }
}
