# Day 95 - Backend LLD: Intro to LLD for Scalable & AI-Ready Systems
## Assignment Questions

### Q1. LLD Fundamentals
**Question:** What does LLD stand for, and what is its primary focus?

* [ ] Large Level Design — designing the overall system architecture
* [x] Low Level Design — designing how the actual code is written well
* [ ] Low Level Design — designing the network infrastructure
* [ ] Logical Level Design — designing database schemas

---

### Q2. HLD Overview
**Question:** Which of the following best describes High Level Design (HLD)?

* [ ] Writing clean, maintainable code inside individual components
* [x] Defining what components exist in a system and how they connect
* [ ] Designing the internal logic of a single class
* [ ] Writing unit tests for backend services

---

### Q3. Load Balancing Role
**Question:** In a horizontally scaled system, what is the primary role of a Load Balancer?

* [ ] To store user session data across multiple servers
* [ ] To upgrade the existing server to a more powerful machine
* [x] To decide which server handles each incoming request
* [ ] To encrypt all incoming user requests before processing

---

### Q4. Procedural Limitations
**Question:** Which of the following is the core problem with Procedural Programming as the codebase scales?

* [ ] Procedures cannot call other procedures
* [x] Entities are passive — any procedure can read or modify any entity's data freely
* [ ] Procedural code does not support functions
* [ ] Procedural code cannot work with databases

---

### Q5. OOP Entities
**Question:** In Object-Oriented Programming, what does an Entity own?

* [ ] Only its attributes (data)
* [ ] Only the functions that act on it
* [x] Both its data (what it IS) and its behaviour (what it DOES)
* [ ] References to all other entities in the system

---

### Q6. OOP Thinking
**Question:** Which of the following code snippets represents the OOP style of thinking?

* [ ] `printStudent(student)`
* [ ] `processPayment(trip, driver, rider)`
* [x] `driver.acceptRide(trip)`
* [ ] `calculateFare(source, destination, vehicle)`

---

## Additional Problems

### Q1. Data Encapsulation
**Question:** A developer is building a food delivery app. The `OrderManager` function directly accesses and modifies the `Rider` struct's `currentLocation`, `availabilityStatus`, and `rating` fields whenever needed. Six months later, a bug is reported — rider ratings are being incorrectly updated. Which of the following best explains why this is difficult to debug, and what OOP principle would fix it?

* [ ] The bug is hard to find because procedural code doesn't support debugging tools; OOP fixes this by adding more functions
* [x] The bug is hard to find because any of the many functions across the codebase could have modified the rating; OOP fixes this by enclosing the rider's data and behaviour within the Rider entity itself
* [ ] The bug is hard to find because structs don't store data properly; OOP fixes this by using classes instead of structs
* [ ] The bug is hard to find because the OrderManager function is too large; OOP fixes this by splitting it into smaller functions

---

### Q2. Extensible Design
**Question:** A startup is building a payment platform. Initially, they only support PhonePe. Their payment logic is written as a set of procedural functions tightly coupled to PhonePe's API — `initiatePhonePePayment()`, `verifyPhonePeTransaction()`, etc. — and this logic is used in 20 different places across the codebase. The business team now wants to add Razorpay and Paytm. What is the most accurate consequence of their current design, and what does this illustrate about LLD?

* [ ] They will need to rewrite their database layer to support new payment providers; this illustrates why HLD matters more than LLD
* [x] They will need to duplicate or heavily modify logic in 20 places for each new provider, leading to high risk of bugs and wasted effort; this illustrates why extensibility is a core goal of good LLD
* [ ] They will only need to change one configuration file; this shows the current design is already good
* [ ] They will need to change the load balancer configuration to support new payment gateways; this illustrates why HLD and LLD are the same thing

---

### Q3. Trading vs Ecommerce
**Question:** Consider the following two systems:
* **System A:** A real-time trading engine processing millions of transactions per second, written in C, where every microsecond of latency matters and the team of 5 engineers maintains it full-time.
* **System B:** An e-commerce platform with 200+ engineers, frequent feature additions, complex business logic, and new payment/shipping integrations every quarter.

Which paradigm is most appropriate for each, and why?

* [ ] System A → OOP, because it has a small team; System B → Procedural, because it has more engineers
* [x] System A → Procedural, because performance is the critical constraint and the team is small enough to manage it; System B → OOP, because maintainability, extensibility, and team collaboration are the critical constraints
* [ ] Both systems should use OOP because OOP is always better than procedural
* [ ] Both systems should use procedural because it performs better in all cases

---

### Q4. OOP Debate
**Question:** A junior engineer argues: "OOP and Procedural are basically the same thing — in both, you have data and functions. OOP just puts them together in a class. It is just a syntactic difference." Which response most accurately addresses this argument?

* [ ] The junior engineer is correct — OOP and Procedural are functionally identical, just with different syntax
* [ ] The junior engineer is wrong — OOP does not use functions at all, whereas Procedural does
* [x] The junior engineer is partially right about grouping, but misses the fundamental shift: in Procedural, procedures are the core active concept and entities are passive data; in OOP, entities become the core active concept, owning both their data and their behaviour, and controlling what can be done to them — this is a philosophical shift in how you structure and reason about an entire system
* [ ] The junior engineer is wrong — OOP is only about inheritance and polymorphism, not about grouping data and functions

---

### Q5. Hospital Entities
**Question:** You are designing a hospital management system. Which of the following is the most complete and accurate set of entities you would identify, and what is your reasoning?

* [ ] Database, Server, API, Cache — because these are the technical components of any system
* [x] Doctor, Patient, Appointment, Prescription, Department — because these are real-world concepts meaningful to the hospital domain, each with their own data and behaviour
* [ ] CreateDoctor(), BookAppointment(), GeneratePrescription() — because these represent the main operations the system needs to perform
* [ ] HospitalManager, SystemAdmin — because only human actors are entities in OOP
