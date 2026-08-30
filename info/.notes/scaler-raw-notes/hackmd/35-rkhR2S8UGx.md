Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/rkhR2S8UGx

# Backend LLD: UML Diagrams & Schema Design

This is the eighth and final post-read of the Design Patterns module. It introduces **UML (Unified Modelling Language)** as a standardized visual notation for communicating software designs, and **Schema Design** as the translation from class diagrams to database tables.

## Core Concepts

**UML** is "a STANDARDIZED way to represent software engineering concepts (classes, interfaces, relationships, workflows) as diagrams — so any engineer, anywhere, reads the same shapes the same way."

The session uses an **Online Learning Platform** as its running example, featuring Instructors, Students, Courses, and Enrollments, with inheritance (LiveCourse vs RecordedCourse) and many-to-many relationships (Students to Courses via Enrollment).

## Two UML Categories

1. **Structural UML**: Class, Object, Package, Component diagrams—describing the frozen codebase structure
2. **Behavioral UML**: Use Case, Sequence, Activity diagrams—describing system behavior over time

## Use Case Diagrams

Key vocabulary:
- **System Boundary**: Rectangle containing all system responsibilities
- **Use Case**: A feature/action (verb phrase), drawn as an oval
- **Actor**: A person or external system (noun), drawn as a stick figure
- **Includes**: Solid arrow—the parent *always* triggers the child
- **Extends**: Dashed arrow—the child is one *optional variant* of the parent

Example: "Enroll in Course" *includes* "Make Payment" (mandatory), while "Pay by UPI" and "Pay by Card" *extend* "Make Payment" (optional variants).

## Class Diagram Notation

A class has three sections:
```
┌───────────────────────────────┐
│ ClassName                     │
├───────────────────────────────┤
│ - privateAttribute: Type      │
│ + publicMethod(): returnType  │
└───────────────────────────────┘
```

Special notation:
- **Interface**: `<<interface>>` label, implemented via dashed line
- **Abstract class**: Name and abstract methods in *italics*, extended via solid line
- **Enum**: `<<enumeration>>` label listing constants
- **Static members**: *Underlined* (regardless of access modifier)
- Access modifiers: `-` (private), `+` (public), `#` (protected)

## Schema Design Fundamentals

Translates class diagrams into database tables. Every table needs a **Primary Key (PK)**—a column guaranteeing row uniqueness, even if not explicitly in the class diagram.

### One-to-Many Relationship

The foreign key lives on the "many" side. For Instructor (one) and Course (many):

```sql
CREATE TABLE instructors (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255)
);
CREATE TABLE courses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255),
  instructor_id INT,
  FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);
```

### Many-to-Many Relationship

Requires a junction table. For Students and Courses via Enrollments:

```sql
CREATE TABLE enrollments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  course_id INT,
  enrolled_at DATE,
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

The junction table often maps directly to a class already in the class diagram (e.g., `Enrollment`).

## Normalization

"Store each fact ONCE, in exactly one place, and reference it everywhere else via a foreign key." This prevents data from silently drifting out of sync when a value is updated in one place but not others.

## Inheritance vs Association

- **Inheritance (IS-A)**: `extends` (solid line, hollow triangle) or `implements` (dashed line, hollow triangle)
- **Association (HAS-A)**: 
  - **Aggregation**: Both objects exist independently (hollow diamond)
  - **Composition**: Child cannot exist without parent (filled diamond)

The test: "If the parent is deleted, does the child still mean anything on its own?"

## Aggregation vs Composition: The Judgment Call

No universal rule exists. A `Module` within a `Course` is composition if it's a one-off unit, but aggregation if it's reusable content shared across multiple courses. The classification depends on actual product requirements.

## ORMs and Schema Generation

Tools like Hibernate automate *mechanical* translation of annotated classes into schema:

```java
@Entity
public class Course {
  @ManyToOne
  @JoinColumn(name = "instructor_id")
  private Instructor instructor;
}
```

However, ORMs cannot make design judgments: whether a relationship is aggregation or composition, whether a junction table needs its own entity because it carries extra data, or whether a relationship was even correctly identified.

## AI in Schema Review

Rather than generating schema directly, use AI for *diagnosis*: paste a flawed schema, ask it to explain what's wrong and why, then make the fix yourself. This ensures human judgment remains on the actual design decisions.

## Common Pitfalls

1. Drawing use cases as nouns instead of verb phrases
2. Confusing Include (always) and Extend (optional variant)
3. Omitting italics for abstract classes/methods or underlines for static members
4. Forgetting every table needs a primary key
5. Placing foreign key on the "one" side instead of "many"
6. Skipping junction tables for many-to-many relationships
7. Denormalizing without a sync plan
8. Defaulting to composition for every HAS-A relationship
9. Treating aggregation vs composition as memorizable rules rather than context-dependent judgments
10. Trusting ORM defaults without verifying against class diagram decisions

## Key Terminology

| Term | Definition |
|------|-----------|
| **UML** | Standardized visual notation for software structure/behavior |
| **Structural UML** | Class, Object, Package, Component diagrams |
| **Behavioral UML** | Use Case, Sequence, Activity diagrams |
| **Primary Key** | Column uniquely identifying one row |
| **Foreign Key** | Column storing a PK value from another table |
| **Junction Table** | Third table for many-to-many relationships |
| **Normalization** | Storing each fact once, referencing elsewhere |
| **Aggregation** | HAS-A where both exist independently |
| **Composition** | HAS-A where child depends on parent |
| **ORM** | Tool generating schema from annotated classes |
| **Migration** | Versioned script altering database structure |

## Interview Questions Summary

Key distinctions covered: UML vs code, structural vs behavioral diagrams, Include vs Extend, abstract vs interface notation, PK necessity, FK placement, junction tables, normalization benefits, aggregation vs composition logic, ORM capabilities/limitations, and why design judgments remain human decisions.

## Homework

1. Draw a Use Case diagram for the platform with 3+ actors and 5 use cases
2. Create a full Class Diagram with proper relationship notation
3. Hand-write CREATE TABLE statements translating the class diagram
4. Generate the same schema via AI and compare results
5. Optional: Add JPA annotations mirroring the SQL
6. Push to GitHub branch: `uml-schema-design-lecture-complete`
