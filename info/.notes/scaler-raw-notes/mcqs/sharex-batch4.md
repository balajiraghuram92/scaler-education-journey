# Scaler Java LLD MCQs - Batch 4

Date: 2026-08-30
Source: Scaler Platform - Java LLD Course, Day 121

---

## MCQ 1 (msedge_pJNXfVpKpT.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q17. Composite Primary Key Definition

In a many-to-many junction table like enrollments, some teams skip a separate surrogate id column entirely and instead make the **combination of both foreign keys** (student_id + course_id together) the primary key. What is this called?

**Options:**
1. A composite primary key
2. A duplicate key
3. A foreign primary key
4. A static key

**Marked/Correct answer:** None marked

---

## MCQ 2 (msedge_pU2vm9P3LP.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q15. Counting Employees By Department

Given this schema and data:

```
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(255),
  department_id INT
);
```

Rows: (1, 'A', 1), (2, 'B', 2), (3, 'C', 2), (4, 'D', 3)

What does `SELECT COUNT(*) FROM employees WHERE department_id = 2;` return?

**Options:**
1. 1
2. 2
3. 3
4. 4

**Marked/Correct answer:** None marked

---

## MCQ 3 (msedge_qXa7v326rK.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams (Additional Problems section)

**Question:** Q3. Hibernate Join Column Mapping

Look at this Hibernate entity code:

```java
@Entity
public class Course {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  private String title;

  @ManyToOne
  @JoinColumn(name = "instructor_id")
  private Instructor instructor;
}
```

When Hibernate generates the table for this class, what column represents the relationship with Instructor?

**Options:**
1. instructor (storing the full object)
2. instructor_name
3. instructor_id
4. No column — a junction table is created instead

**Marked/Correct answer:** None marked

---

## MCQ 4 (msedge_qoSD3byKTa.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q8. SCALER QUESTION 39934 c33d

In a music streaming application, a class represents a **playlist**. The playlist class contains objects representing songs. If the playlist is deleted, the songs still exist in the system and may be part of other playlists. What type of relationship exists between the playlist class and the song objects, where the song class is independent of the lifecycle of the playlist class?

**Options:**
1. Composition
2. Aggregation
3. Inheritance

**Marked/Correct answer:** None marked

---

## MCQ 5 (msedge_vSC1iwkQ4U.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q1. SCALER QUESTION 39900 f6d0

In a car manufacturing simulation, there's a class for generic vehicle properties. You have to create classes for a car, truck and motorcycle. What is the nature of the relationship between the vehicle class and the car, truck, and motorcycle classes?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** None marked

---

## MCQ 6 (msedge_z8KQhvxgeN.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q10. SCALER QUESTION 39937 c101

In a car manufacturing simulation, a class represents a car. The car class contains objects representing the engine, wheels, and other parts. If the car object is destroyed, the engine, wheels, and other parts are also destroyed. What type of relationship exists between the car class and the engine, wheels, and other parts, where the parts are dependent on the lifecycle of the car?

**Options:**
1. Composition
2. Aggregation
3. Inheritance

**Marked/Correct answer:** None marked

---

## MCQ 7 (msedge_zNhnsswMbH.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Q6. SCALER QUESTION 39932 d121

In a social media application, there's a class for a user and a class for a post. What is the nature of the relationship between the user class and the post class?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** None marked

---
