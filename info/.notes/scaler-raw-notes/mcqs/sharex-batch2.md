# Scaler MCQ Transcriptions - Batch 2

All questions from **Day 121 - Backend LLD: UML Diagrams** (Wed, 12 Aug 2026)

---

## MCQ 1 (msedge_IWsExLY6X4.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a university system, there's a class for a department and a class for a professor. What is the nature of the relationship between the department class and the professor class?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 2 (msedge_IcgY0xzEoe.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A library system has Book and Author. One book can have multiple authors, and one author can write multiple books — but this relationship doesn't need to store any extra data (no dates, no royalty percentage, nothing beyond just "who wrote what"). Which Hibernate approach fits best?

**Options:**
1. Manually create a BookAuthor entity class, similar to how Enrollment was modeled
2. Use a plain @ManyToMany annotation directly between Book and Author, since no extra data needs to be stored
3. Use @OneToMany on both sides
4. Store author names as a comma-separated column inside books

**Marked/Correct answer:** none marked

---

## MCQ 3 (msedge_KpSO5my6vU.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a social media application, a class represents a user. The user class contains objects representing posts. If the user account is deleted, the posts still exist in the system. What type of relationship exists between the user class and the post objects, where the post class is independent of the lifecycle of the user class?

**Options:**
1. Composition
2. Aggregation
3. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 4 (msedge_MJNaxhkwuQ.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams (Additional Problems)

**Question:** Given this Hibernate mapping, which also stores extra data (enrolledAt):

```java
@Entity
public class Enrollment {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne
  @JoinColumn(name = "student_id")
  private Student student;

  @ManyToOne
  @JoinColumn(name = "course_id")
  private Course course;

  private LocalDate enrolledAt;
}
```

Why was Enrollment modeled as its own full entity instead of using a plain @ManyToMany between Student and Course?

**Options:**
1. @ManyToMany doesn't exist in Hibernate
2. @ManyToOne runs faster than @ManyToMany in every case
3. The relationship itself carries extra data (enrolledAt), which a plain @ManyToMany junction table can't hold — so it needs to be a real entity
4. Student and Course cannot have a many-to-many relationship

**Marked/Correct answer:** none marked

---

## MCQ 5 (msedge_NTGJbnLpgW.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a drawing application, there's a class for a generic shape called Shape. You have to create classes for Circle, Rectangle, and Triangle. What is the nature of the relationship between the Shape class and the Circle, Rectangle, and Triangle classes?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 6 (msedge_RSbbjimbjZ.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams (Additional Problems)

**Question:** A Restaurant class has a List<MenuItem>. If the restaurant shuts down permanently, its menu items (like "Paneer Butter Masala") have no meaning anywhere else in the system — they only existed as part of that restaurant's menu. What relationship is this?

**Options:**
1. Inheritance
2. Composition
3. Aggregation
4. An interface implementation

**Marked/Correct answer:** none marked

---

## MCQ 7 (msedge_U5AsH6hyDI.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams (Additional Problems)

**Question:** A junior developer wanted to model aggregation between Car and Driver (a driver should be able to exist independently of any car). Here's what they wrote:

```java
public class Car {
  private final Driver driver;

  public Car() {
    this.driver = new Driver(); // Car creates its own Driver internally
  }
}
```

What's wrong, and what's the fix?

**Options:**
1. Nothing is wrong — this already models aggregation correctly
2. Driver should be marked static
3. final should be removed from the field
4. The Car constructor creates and owns the Driver internally, which is composition-like behavior — fix it by passing an existing Driver object into the constructor instead

**Marked/Correct answer:** none marked

---

## MCQ 8 (msedge_UwixaS4gG5.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** Imagine a class for a notebook. The notebook class contains objects representing pages. If the notebook object is destroyed, the pages are also destroyed. What type of relationship exists between the notebook class and the pages, where the pages are dependent on the lifecycle of the notebook?

**Options:**
1. Composition
2. Aggregation
3. Inheritance

**Marked/Correct answer:** none marked

---

## Summary

| # | Topic | Question Focus |
|---|-------|-----------------|
| 1 | UML Relationships | Department–Professor relationship type |
| 2 | Hibernate | @ManyToMany vs. entity modeling for Book–Author |
| 3 | UML Relationships | User–Post lifecycle independence (Aggregation vs. Composition) |
| 4 | Hibernate | Enrollment as full entity with extra data (enrolledAt) |
| 5 | Inheritance | Shape–Circle/Rectangle/Triangle relationship |
| 6 | Composition | Restaurant–MenuItem lifecycle dependency |
| 7 | Aggregation | Car–Driver vs. Composition (constructor dependency) |
| 8 | Composition | Notebook–Page lifecycle dependency |

**Notes:**
- All 8 images loaded successfully
- All questions cover UML relationships (Association, Composition, Aggregation, Inheritance) and Hibernate modeling patterns
- Lesson context: Day 121 Backend LLD on UML Diagrams; includes both Assignment and Additional Problems sections
- No answers were visibly marked/highlighted in any of the screenshots
