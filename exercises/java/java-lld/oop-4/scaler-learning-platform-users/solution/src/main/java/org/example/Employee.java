package org.example;

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

    @Override
    public void displayInfo() {
        super.displayInfo();
        System.out.println("Employee ID: " + employeeId);
        System.out.println("Department: " + department);
    }
}
