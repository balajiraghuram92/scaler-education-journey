# Scaler Java LLD Course - MCQ Batch 1

## MCQ 1 (msedge_106mii7rgo.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A banking app allows joint accounts — one account can have multiple owners, and one person can be an owner on multiple accounts. How should this be modeled in the schema?

**Options:**
1. Add an owner_id column directly inside accounts
2. Create a separate junction table (e.g. account_owners) holding account_id and owner_id
3. Add an account_id column directly inside owners
4. Store all owner names as a comma-separated list inside accounts

**Marked/Correct answer:** none marked

---

## MCQ 2 (msedge_1u75JDDNaW.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a Class Diagram, what does a dashed line with a hollow triangle arrowhead represent?

**Options:**
1. A class implementing an interface
2. A class extending another class
3. Aggregation between two classes
4. Composition between two classes

**Marked/Correct answer:** none marked

---

## MCQ 3 (msedge_4ihj6gTVlZ.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** One instructor teaches many courses, but each course has only one instructor. Where should the foreign key go?

**Options:**
1. In the instructors table
2. In the courses table
3. In both tables at once
4. In a separate junction table

**Marked/Correct answer:** none marked

---

## MCQ 4 (msedge_8OxXy7AbNs.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a library management system, there's a class for a library and a class for a book. What is the nature of the relationship between the library class and the book class?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 5 (msedge_C7fTjl8WUC.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a Use Case Diagram, "Enroll in Course" always triggers "Make Payment" — there's no scenario where enrollment happens without it. What relationship connects these two use cases?

**Options:**
1. Extends
2. Actor
3. System Boundary
4. Includes

**Marked/Correct answer:** none marked

---

## MCQ 6 (msedge_DpM3Y1W1Ar.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Given this SQL:

```sql
CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(255));
CREATE TABLE courses (id INT PRIMARY KEY, title VARCHAR(255));

CREATE TABLE enrollments (
  id INT PRIMARY KEY,
  student_id INT,
  course_id INT,
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

Current rows in enrollments: {(1, 1, 1), (2, 1, 2), (3, 2, 1)} (columns: id, student_id, course_id)

How many courses is the student with id = 1 enrolled in?

**Options:**
1. 3
2. 0
3. 2
4. 1

**Marked/Correct answer:** none marked

---

## MCQ 7 (msedge_E2Kc8GZoXb.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** What is the main purpose of normalization in database schema design?

**Options:**
1. To duplicate frequently-used data across tables for faster reads
2. To store each fact only once and reference it elsewhere with a foreign key, avoiding out-of-sync copies
3. To ensure every table has exactly the same number of columns
4. To turn every relationship into a many-to-many relationship

**Marked/Correct answer:** none marked

---

## MCQ 8 (msedge_HrAeMM6Qzt.png)
**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** [Page appears to be loading - content not fully rendered; text and answer options visible as placeholder/skeleton state only]

**Options:** [illegible]

**Marked/Correct answer:** none marked

---

## Summary

| # | Filename | Topic | Question |
|---|----------|-------|----------|
| 1 | msedge_106mii7rgo.png | UML Diagrams | Modeling Joint Account Ownership (many-to-many relationship) |
| 2 | msedge_1u75JDDNaW.png | UML Diagrams | Dashed Hollow Triangle Meaning in Class Diagram |
| 3 | msedge_4ihj6gTVlZ.png | UML Diagrams | Foreign Key Placement - One-to-Many (Instructor-Course) |
| 4 | msedge_8OxXy7AbNs.png | UML Diagrams | Library-Book Relationship Type (Association/Composition/Aggregation) |
| 5 | msedge_C7fTjl8WUC.png | UML Diagrams | Use Case Diagram: Includes vs Extends (Enroll Course + Make Payment) |
| 6 | msedge_DpM3Y1W1Ar.png | UML Diagrams | Junction Table Query: Count Enrolled Courses (SQL exercise) |
| 7 | msedge_E2Kc8GZoXb.png | UML Diagrams | Purpose of Database Normalization |
| 8 | msedge_HrAeMM6Qzt.png | UML Diagrams | [Content loading - illegible] |

**Note:** Image 8 (msedge_HrAeMM6Qzt.png) was captured during a page load state and contains only placeholder skeleton content; the actual MCQ text is not visible.
