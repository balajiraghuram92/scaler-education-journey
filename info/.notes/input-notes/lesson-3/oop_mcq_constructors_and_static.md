# Java OOP Practice Question: Class-Level Data Members

## Multiple Choice Question

### Question:
**Q3. OOPs in Java (Constructors and Static)**  
What keyword is used to make class level data members?

### Options:
- [ ] `const`
- [ ] `final`
- [ ] `auto`
- [x] **`static`** *(Correct Answer)*

---

## Explanation
In Java:
- The **`static`** keyword designates members (variables and methods) that belong to the **class itself** rather than to individual object instances.
- A single copy of a `static` variable is shared across all instances of the class and initialized at class loading time.
- `const` is a reserved keyword in Java but not used.
- `final` makes a variable constant (immutable value), but does not make it class-level unless paired with `static` (`static final`).
- `auto` does not exist as an access/storage modifier in Java.

---

## Example Java Program

```java
public class CompanyDirectory {
    // 1. Class-level static variable (shared among ALL employees)
    public static String companyName = "Enterprise Global Tech";
    public static int totalEmployees = 0;

    // 2. Instance-level variables (unique per employee object)
    private int employeeId;
    private String employeeName;

    // Constructor
    public CompanyDirectory(int employeeId, String employeeName) {
        this.employeeId = employeeId;
        this.employeeName = employeeName;
        // Incrementing class-level static counter
        totalEmployees++;
    }

    public void printEmployeeInfo() {
        System.out.println("ID: " + employeeId + 
                           " | Name: " + employeeName + 
                           " | Company: " + companyName);
    }

    public static void printTotalEmployees() {
        System.out.println("Total Registered Employees: " + totalEmployees);
    }

    public static void main(String[] args) {
        // Creating distinct object instances
        CompanyDirectory emp1 = new CompanyDirectory(101, "Alice");
        CompanyDirectory emp2 = new CompanyDirectory(102, "Bob");

        emp1.printEmployeeInfo();
        emp2.printEmployeeInfo();
        CompanyDirectory.printTotalEmployees();

        System.out.println("\n--- Changing Class-Level Variable ---");
        // Modifying class-level member modifies it for ALL objects
        CompanyDirectory.companyName = "Apex Solutions Corp";

        emp1.printEmployeeInfo();
        emp2.printEmployeeInfo();
    }
}
```
