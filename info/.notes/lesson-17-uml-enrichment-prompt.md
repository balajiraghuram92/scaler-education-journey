# Prompt for Local LLM — Enrich Lesson 17's UML Section with Real Assessed Content

Paste everything below this line into the local LLM as-is. All content below was authored by
hand from real Scaler assessment material (30 screenshots from the live "Day 121: UML
Diagrams" class, 29 of them legible) — you are NOT being asked to write new prose or invent
examples. Your job is to insert the given blocks verbatim. If anything below doesn't match
what you find in the file, STOP and report the discrepancy instead of guessing.

---

## 0. Prerequisite check

This prompt modifies the existing `"17-behavioural-patterns-uml"` case inside
`GetAuthoredLessonContent`. That case must already exist (added by
`info/.notes/lesson-17-behavioural-patterns-uml-prompt.md`). If you don't find it, apply
that prompt first, then come back to this one.

## 1. What to do

Two edits to the existing `"17-behavioural-patterns-uml"` lesson content:

### 1a. Expand the UML paragraph in `## Concepts Covered`

Find the existing paragraph starting with `**UML — A Shared Notation for Communicating
Design:**`. Insert the following two new sentences at the **end** of that paragraph (after
the existing final sentence about ORMs and judgment calls, still inside the same paragraph,
same `**UML —...**` block — do not start a new paragraph):

```
 A composite primary key is the alternative to a surrogate `id` column on a junction table: instead of adding a new auto-incrementing column, the combination of both foreign keys together (e.g. `student_id` + `course_id`) serves as the primary key, since that pair is already guaranteed unique. In Hibernate, a plain `@ManyToMany` is sufficient only when the relationship itself carries no extra data; the moment the relationship needs its own fields (e.g. an `enrolledAt` timestamp on an enrollment), it must be modeled as its own full `@Entity` with two `@ManyToOne` sides instead, because a plain many-to-many junction table has nowhere to store that extra column. The most reliable way to tell aggregation from composition is a lifecycle-dependency test, not intuition: if the contained object continues to exist and make sense after the container is deleted (a post surviving its author's account deletion, a song surviving its playlist's deletion), it's aggregation; if the contained object stops making sense the moment the container is gone (a notebook's pages, a car's engine and wheels, a GPS trip's route coordinates), it's composition — and a common implementation bug is a class that claims aggregation but actually constructs its dependency internally in its own constructor (e.g. `this.driver = new Driver();` inside `Car`'s constructor) rather than receiving an already-existing object from outside, which silently turns it into composition-like ownership regardless of what the diagram says.
```

### 1b. Add 16 new self-check questions

Find the existing `## Self-Check (From Class Material)` section, which currently ends after
**Q12** with its citation line, immediately before the closing `",`. Insert the following as
**Q13** through **Q28**, in this exact order, right after Q12's citation line:

```

**Q13.** What is the primary purpose of a PRIMARY KEY in a database table?
- A. To uniquely identify each row in the table
- B. To link one table to another
- C. To make queries run faster automatically
- D. To enforce a fixed number of columns

**Answer: A** — A primary key's core job is guaranteeing every row is uniquely identifiable; foreign keys (not primary keys) are what link tables together.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q14.** In a Class Diagram, what does a dashed line with a hollow triangle arrowhead represent?
- A. A class implementing an interface
- B. A class extending another class
- C. Aggregation between two classes
- D. Composition between two classes

**Answer: A** — A dashed line with a hollow triangle is realization (implements an interface). A solid line with a hollow triangle is generalization (extends a class).
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q15.** One instructor teaches many courses, but each course has only one instructor. Where should the foreign key go?
- A. In the instructors table
- B. In the courses table
- C. In both tables at once
- D. In a separate junction table

**Answer: B** — The foreign key always lives on the ""many"" side of a one-to-many relationship, so `instructor_id` belongs in the `courses` table.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q16.** In a Use Case Diagram, ""Enroll in Course"" always triggers ""Make Payment"" — there's no scenario where enrollment happens without it. What relationship connects these two use cases?
- A. Extends
- B. Actor
- C. System Boundary
- D. Includes

**Answer: D** — A solid **includes** arrow means the parent use case always triggers the child. **Extends** (dashed) would be for an optional variant, like ""Pay by UPI"" extending ""Make Payment"".
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q17.** 
```sql
CREATE TABLE enrollments (
  id INT PRIMARY KEY, student_id INT, course_id INT,
  FOREIGN KEY (student_id) REFERENCES students(id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);
```
Current rows (id, student_id, course_id): (1, 1, 1), (2, 1, 2), (3, 2, 1). How many courses is the student with id = 1 enrolled in?
- A. 3
- B. 0
- C. 2
- D. 1

**Answer: C** — Rows with `student_id = 1` are (1,1,1) and (2,1,2), referencing `course_id` 1 and 2 — two distinct courses.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q18.** What is the main purpose of normalization in database schema design?
- A. To duplicate frequently-used data across tables for faster reads
- B. To store each fact only once and reference it elsewhere with a foreign key, avoiding out-of-sync copies
- C. To ensure every table has exactly the same number of columns
- D. To turn every relationship into a many-to-many relationship

**Answer: B** — Normalization's goal is eliminating duplicate, potentially-inconsistent copies of the same fact by storing it once and referencing it via foreign key.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q19.** A library system has `Book` and `Author`. One book can have multiple authors, one author can write multiple books, and the relationship needs no extra data (no dates, no royalty percentage). Which Hibernate approach fits best?
- A. Manually create a `BookAuthor` entity class, similar to how `Enrollment` was modeled
- B. Use a plain `@ManyToMany` annotation directly between `Book` and `Author`, since no extra data needs to be stored
- C. Use `@OneToMany` on both sides
- D. Store author names as a comma-separated column inside books

**Answer: B** — A plain `@ManyToMany` is exactly right when the relationship itself carries no additional data — a full entity is only needed once the relationship needs its own fields.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q20.** Given a Hibernate `Enrollment` entity with `@ManyToOne` to both `Student` and `Course`, plus its own `enrolledAt` field, why was `Enrollment` modeled as its own full entity instead of a plain `@ManyToMany` between `Student` and `Course`?
- A. `@ManyToMany` doesn't exist in Hibernate
- B. `@ManyToOne` runs faster than `@ManyToMany` in every case
- C. The relationship itself carries extra data (`enrolledAt`), which a plain `@ManyToMany` junction table can't hold — so it needs to be a real entity
- D. Student and Course cannot have a many-to-many relationship

**Answer: C** — The moment a many-to-many relationship needs to carry its own data, a plain `@ManyToMany` junction table (which only holds the two foreign keys) is insufficient — the relationship must be promoted to its own entity.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q21.** A junior developer wanted to model aggregation between `Car` and `Driver` (a driver should exist independently of any car):
```java
public class Car {
  private final Driver driver;
  public Car() {
    this.driver = new Driver(); // Car creates its own Driver internally
  }
}
```
What's wrong, and what's the fix?
- A. Nothing is wrong — this already models aggregation correctly
- B. `Driver` should be marked `static`
- C. `final` should be removed from the field
- D. The `Car` constructor creates and owns the `Driver` internally, which is composition-like behavior — fix it by passing an existing `Driver` object into the constructor instead

**Answer: D** — Constructing the dependency internally makes the `Car` own the `Driver`'s lifecycle (composition-like), which contradicts the stated goal of aggregation. Passing an already-existing `Driver` in via the constructor (dependency injection) is what actually models independent lifecycles.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q22.** A hospital has a `Department` class and a `Doctor` class. A doctor belongs to one department at a time, but if a department is dissolved, doctors continue to exist and can be reassigned elsewhere. Which pair correctly identifies the relationship type AND the foreign key placement?
- A. Aggregation, with `department_id` placed inside the `doctors` table
- B. Composition, with `department_id` placed inside the `doctors` table
- C. Aggregation, with `doctor_id` placed inside the `departments` table
- D. Composition, with `doctor_id` placed inside the `departments` table

**Answer: A** — Doctors outliving their department's dissolution is the definition of aggregation (independent lifecycles). The foreign key still follows the standard one-to-many rule: it lives on the ""many"" side (`doctors`), pointing back to the one `department`.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q23.** A teammate wrote this schema for a blog, where one post can have many comments:
```sql
CREATE TABLE posts (
  id INT PRIMARY KEY, title VARCHAR(255),
  comment_1 VARCHAR(500), comment_2 VARCHAR(500), comment_3 VARCHAR(500)
);
```
What is the main problem, and what's the correct fix?
- A. A fixed number of comment columns caps the relationship — create a separate `comments` table with a `post_id` foreign key instead
- B. `id` should not be declared as a primary key
- C. `title` should be split into two columns
- D. The comments should be merged into one column separated by commas

**Answer: A** — Hardcoding a fixed number of columns for what is really a one-to-many relationship caps it artificially (a 4th comment has nowhere to go) and wastes space for posts with fewer comments. The fix is a proper `comments` table with a foreign key back to `posts`.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q24.** A teammate wrote this schema for an orders system, where a separate `customers` table already stores customer details:
```sql
CREATE TABLE orders (
  id INT PRIMARY KEY, customer_name VARCHAR(255),
  customer_email VARCHAR(255), product VARCHAR(255)
);
```
What's wrong with this design, and what's the fix?
- A. Nothing is wrong — storing the name and email directly avoids extra joins
- B. `product` should be split into `product_name` and `product_price`
- C. `id` should not be declared as a primary key since orders can repeat
- D. `customer_name` and `customer_email` duplicate data that already lives in `customers` — replace both with a single `customer_id` foreign key instead

**Answer: D** — This is a direct normalization violation: customer data is duplicated into every order row instead of referenced once via foreign key, risking the two copies going out of sync if a customer updates their email.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q25.** A ride-sharing app's `Trip` class has a `List<RouteCoordinate>` — the GPS points making up that specific trip's path. If the trip record is deleted, those exact coordinates have no meaning anywhere else in the system. Which combination correctly describes the relationship and its notation?
- A. Association without ownership — plain line, no diamond
- B. Inheritance — hollow triangle
- C. Aggregation — hollow diamond
- D. Composition — filled diamond

**Answer: D** — The route coordinates cannot outlive the trip they belong to (they have no independent meaning), which is composition, notated with a filled diamond on the `Trip` end.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q26.** In a many-to-many junction table like `enrollments`, some teams skip a separate surrogate `id` column entirely and instead make the combination of both foreign keys (`student_id` + `course_id` together) the primary key. What is this called?
- A. A composite primary key
- B. A duplicate key
- C. A foreign primary key
- D. A static key

**Answer: A** — A primary key made of more than one column is a composite primary key; it works here because the pairing of the two foreign keys is already guaranteed unique.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q27.** 
```java
@Entity
public class Course {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  private String title;
  @ManyToOne
  @JoinColumn(name = ""instructor_id"")
  private Instructor instructor;
}
```
When Hibernate generates the table for this class, what column represents the relationship with `Instructor`?
- A. `instructor` (storing the full object)
- B. `instructor_name`
- C. `instructor_id`
- D. No column — a junction table is created instead

**Answer: C** — `@JoinColumn(name = ""instructor_id"")` tells Hibernate to store the relationship as a plain foreign-key column named `instructor_id` on the `Course` table, matching the standard one-to-many FK placement rule.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*

**Q28.** A banking app allows joint accounts — one account can have multiple owners, and one person can be an owner on multiple accounts. How should this be modeled in the schema?
- A. Add an `owner_id` column directly inside `accounts`
- B. Create a separate junction table (e.g. `account_owners`) holding `account_id` and `owner_id`
- C. Add an `account_id` column directly inside `owners`
- D. Store all owner names as a comma-separated list inside `accounts`

**Answer: B** — A many-to-many relationship (many accounts to many owners) requires a junction table holding both foreign keys; a single column on either side cannot represent a many-to-many link.
*(SOURCE_TYPE: FROM_MATERIAL — Scaler Additional Problems, Day 121, UML Diagrams)*
```

---

## 2. What must NOT change

- Do not touch Q1–Q12 or any other part of the lesson.
- Do not touch any lesson other than `17-behavioural-patterns-uml`.
- Every quote inside the content above is already correctly doubled (`""`) for C# verbatim
  strings — copy it exactly.
- Do not renumber Q1–Q12; the new questions are strictly appended as Q13–Q28.

## 3. Output format

Output the complete, updated `GetAuthoredLessonContent` method body, ready to paste over the
existing method in `api/Data/JavaVerticalSeedData.cs`.

After the code block, report:
- Confirmation the UML paragraph was extended (not replaced) with the two new sentences.
- Confirmation Q13–Q28 were added in order, with none dropped or duplicated.
- Any discrepancy encountered.

## 4. Self-check before you output

1. Search for ""composite primary key"" and ""lifecycle-dependency test"" — both phrases
   should now appear in the Concepts Covered UML paragraph.
2. Count self-check questions in this lesson: should be exactly 28 (was 12, +16).
3. Every `"` inside the new content is doubled (`""`), not single or backslash-escaped.
4. No other lesson's content was touched.

## 5. Operational note

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug = '17-behavioural-patterns-uml';
```

Then rebuild/restart the API.
