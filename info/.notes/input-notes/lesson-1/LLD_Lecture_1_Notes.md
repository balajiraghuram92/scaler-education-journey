# Lecture Notes: Introduction to LLD for Scalable & AI-Ready Systems

## Agenda
* Introduction to LLD (What & Why)
* Importance of LLD
* Overview & Module Roadmap
* Procedural vs. Object-Oriented Programming

---

## 1. Introduction to LLD

* **High-Level Design (HLD):** Gives the overall bird's-eye picture of a system.
  * *Example:* Building a startup like Flipkart.
  * *Architecture Flow:* User request (`flipkart.com`) $ightarrow$ **Load Balancer** $ightarrow$ Application Servers (`S1`, `S2`, `S3`) $ightarrow$ **Database (`DB`)**.
* **Low-Level Design (LLD):** Focuses on low-level details, clean code, and implementation specifics inside each component.

---

## 2. Importance of LLD

1. **Interviews:** Essential for clearing technical rounds across various company tiers.
2. **Day-to-Day Life as an SWE:** Improves code quality, maintainability, debugging, and team communication during technical meetings.

### LLD Interview Breakdown & Matrix

* **Theoretical Interviews:** Common in service-based companies (TCS, Infosys, Philips, JP Morgan). Duration: 40–45 minutes. Focuses on foundational concepts.
* **LLD Design Rounds:** Common in Product MNCs and FAANG. Focuses on system design (e.g., Netflix design, Scaler). Very little code expected. Duration: 50–55 minutes.
* **Machine Coding Rounds:** Common in startups (e.g., CRED, Cult.fit). Duration: 2-hour hands-on coding round.

#### Experience & Role Matrix

| Experience | Startups | Product MNC | FAANG |
| :--- | :--- | :--- | :--- |
| **0–3 years (SDE-1)** | Machine Coding Round | Usually None | Usually None |
| **3–6 years (SDE-2)** | Machine Coding + LLD | Dedicated LLD Round | Dedicated LLD Round |
| **6–9 years (SDE-3)** | Advanced Machine Coding + LLD | Strong LLD Round | Strong LLD Round |
| **9+ years (Staff / Principal)** | Architecture + Design Deep Dive | Multiple Design Discussions | Multiple Design Interviews |

---

## 3. Module Overview

The LLD curriculum is divided into three core parts:

### 1. Foundations of OOP & Scalable Systems
* Classes and Objects, Constructors
* 4 Pillars of OOP: Abstraction, Encapsulation, Polymorphism, Inheritance
* Deep vs. Shallow Copy
* Concurrency, Threading, Generics, Collections, Exceptions

### 2. Design Principles & Patterns
* SOLID Principles
* Design Patterns
* UML Diagrams

### 3. Applied Design & Machine Coding
* Design Tic-Tac-Toe
* Design BookMyShow (BMS)
* Design Splitwise
* Design Parking Lot

---

## 4. Programming Paradigms

Programming paradigms represent different ways of structuring and organizing code:

1. **Procedural Programming** (e.g., C)
2. **Object-Oriented Programming (OOP)** (e.g., Java)
3. **Functional Programming** (e.g., Scala, Golang)
4. **Reactive Programming** (e.g., JavaFX, JavaScript, Kotlin)

### Procedural Programming
* Built on a set of instructions coded together where a function acts as a procedure.
* Data and behavior are separated (e.g., structs holding passive data manipulated by external functions).
* *Example structure:*
  ```c
  struct student {
      string name;
      int age;
      float psp;
  }
  
  void printStudent(struct student st) {
      print(st.name);
      print(st.age);
      print(st.psp);
  }
  ```

### Object-Oriented Programming (OOP)
* Shift in perspective: **The entity/subject performs the action** (e.g., *"Uber driver accepted my request"*).
* Data and behavior are bundled together inside classes/objects.
* *Example structure:*
  ```java
  class Driver {
      String name;
      boolean isRideAccepted() {
          // behavior encapsulated within the entity
      }
  }
  ```
