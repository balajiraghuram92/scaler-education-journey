# Scaler MCQ Batch 3 — Day 121: Backend LLD: UML Diagrams

## MCQ 1 (msedge_XHiByLsVuV.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** What is the primary purpose of a PRIMARY KEY in a database table?

**Options:**
1. To uniquely identify each row in the table
2. To link one table to another
3. To make queries run faster automatically
4. To enforce a fixed number of columns

**Marked/Correct answer:** none marked

---

## MCQ 2 (msedge_aiuFRnr735.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A teammate wrote this schema for a blog, where one post can have many comments:

```sql
CREATE TABLE posts (
  id INT PRIMARY KEY,
  title VARCHAR(255),
  comment_1 VARCHAR(500),
  comment_2 VARCHAR(500),
  comment_3 VARCHAR(500)
);
```

What is the main problem, and what's the correct fix?

**Options:**
1. A fixed number of comment columns caps the relationship – create a separate comments table with a post_id foreign key instead
2. id should not be declared as a primary key
3. title should be split into two columns
4. The comments should be merged into one column separated by commas

**Marked/Correct answer:** none marked

---

## MCQ 3 (msedge_e5arK0cd7f.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A hospital has a Department class and a Doctor class. A doctor belongs to one department at a time, but if a department is dissolved, doctors continue to exist and can be reassigned elsewhere. Which pair correctly identifies the relationship type AND the foreign key placement?

**Options:**
1. Aggregation, with department_id placed inside the doctors table
2. Composition, with department_id placed inside the doctors table
3. Aggregation, with doctor_id placed inside the departments table
4. Composition, with doctor_id placed inside the departments table

**Marked/Correct answer:** none marked

---

## MCQ 4 (msedge_eDenfdFVLk.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a drawing application, there is a Canvas class. The canvas class contains objects representing shapes such as circles, rectangles, and triangles. If the canvas object is destroyed, the shapes are also destroyed. What type of relationship exists between the canvas class and the shapes, where the shapes are dependent on the lifecycle of the canvas?

**Options:**
1. Composition
2. Aggregation
3. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 5 (msedge_iOaXGd4jlM.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** In a software application, there's a class called Animal with properties and methods common to all animals. You have to create classes for Dog, Cat, and Bird. What is the nature of the relationship between the Animal class and the Dog, Cat, and Bird classes?

**Options:**
1. Association
2. Composition
3. Aggregation
4. Inheritance

**Marked/Correct answer:** none marked

---

## MCQ 6 (msedge_ieZ11czNf9.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A teammate wrote this schema for an orders system:

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_name VARCHAR(255),
  customer_email VARCHAR(255),
  product VARCHAR(255)
);
```

There's already a separate customers table storing customer details. What's wrong with this design, and what's the fix?

**Options:**
1. Nothing is wrong — storing the name and email directly avoids extra joins
2. product should be split into product_name and product_price
3. id should not be declared as a primary key since orders can repeat
4. customer_name and customer_email duplicate data that already lives in customers — replace both with a single customer_id foreign key instead

**Marked/Correct answer:** none marked

---

## MCQ 7 (msedge_nRnZrDIZIB.png)

**Page/Topic header:** Day 121 - Backend LLD: UML Diagrams

**Question:** A ride-sharing app's Trip class has a List<RouteCoordinate> – the GPS points making up that specific trip's path. If the trip record is deleted, those exact coordinates have no meaning anywhere else in the system. Which combination correctly describes the relationship and its notation?

**Options:**
1. Association without ownership — plain line, no diamond
2. Inheritance — hollow triangle
3. Aggregation — hollow diamond
4. Composition — filled diamond

**Marked/Correct answer:** none marked

---

## Summary

1. **MCQ 1** — Primary Key purpose (database fundamentals)
2. **MCQ 2** — Schema design: fixed comment columns anti-pattern
3. **MCQ 3** — Doctor-Department relationship classification (Aggregation vs Composition)
4. **MCQ 4** — Canvas-Shapes lifecycle dependency (Composition)
5. **MCQ 5** — Animal-Dog/Cat/Bird inheritance relationship
6. **MCQ 6** — Duplicated customer data normalization issue
7. **MCQ 7** — Trip-RouteCoordinate composition notation (filled diamond)

**All 7 images loaded and transcribed successfully. No illegible sections or missing content.**
