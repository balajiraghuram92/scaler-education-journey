package org.example;

// TODO: extend User with employeeId and department fields; override displayInfo() to
// call super.displayInfo() first, then print "Employee ID: <id>" and
// "Department: <department>" on their own lines.
public class Employee extends User {
    private final int employeeId;
    private final String department;

    public Employee(String username, String email, int employeeId, String department) {
        super(username, email);
        this.employeeId = employeeId;
        this.department = department;
    }

    public int getEmployeeId() {
        return employeeId;
    }

    public String getDepartment() {
        return department;
    }
}
