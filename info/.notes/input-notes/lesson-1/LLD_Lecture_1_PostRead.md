| POST-READ | Foundations of Object-Oriented Design & Scalable Systems | Lecture-1: Intro to LLD for Scalable & AI-Ready Systems |
|----------|-------------------------------|------------------------------------------------------|

> **How to use this document.** This is a consolidation brief for the first session of Backend LLD. It tracks the lecture exactly: HLD versus LLD, scaling and infrastructure layers, why LLD matters on the job and in interviews, the module roadmap, the contrast between procedural and object-oriented thinking, and the core concept of an Entity. Each major topic has three parts: **Deep-Dive Theory**, **Practical Mechanics**, and **Hidden Pitfalls**. Optional **Going Deeper** callouts contain stretch material you can skip on a first pass. We will write actual Java classes next session, so any Java here is deliberately minimal and appears only inside clearly flagged preview callouts.

---

## Section 1: What Is LLD and Where It Sits (HLD vs LLD)

### Deep-Dive Theory

System design exists at different **altitudes**. The higher you stand, the less internal detail you see. The lower you go, the more concrete the implementation becomes.

The lecture built this up from a startup story. You have an idea, you write code, and you deploy it on a single cloud machine (an AWS EC2 instance, a GCP VM, it does not matter). That works until users arrive. Then a single server reveals three structural weaknesses, which we examine fully in Section 2.

The fix is to add more machines and route traffic across them, which forces you to think about **infrastructure layers**: a load balancer in front, a pool of application servers in the middle, and a shared database behind them. When you reason at this level, deciding what components exist and how they connect, you are doing **High-Level Design (HLD)**.

- **High-Level Design (HLD)** answers *what components exist* and *how they connect*. Load balancers, application servers, databases, caches, message queues, CDNs. It is a bird's-eye view. It is not about how any single component works internally.
- **Low-Level Design (LLD)** answers *how each component is actually written in code*. The crucial realization from the lecture: every infrastructure layer is just software, and all software is code.

$$\text{Load Balancer} \rightarrow \text{Software} \rightarrow \text{Code}$$
$$\text{App Server} \rightarrow \text{Software} \rightarrow \text{Code}$$
$$\text{Database} \rightarrow \text{Software} \rightarrow \text{Code}$$

A load balancer is not magic. It is a machine running code that reads requests, checks the health of downstream servers, applies a routing algorithm (round robin, least connections), and forwards the request. A database (MySQL, Postgres, MongoDB) is code that handles query parsing, storage engines, indexing, and transactions. So once HLD has decided *what* to build, **LLD is about how we actually write that code, and write it well.**

And "well" has a concrete meaning from the lecture:

- **Maintainable:** someone else can read it, understand it, and modify it without breaking things.
- **Extensible:** you can add new features without rewriting everything.
- **Reusable:** pieces of logic are not duplicated across the codebase.

The key mental model: **LLD provides guidelines for writing good code, which is code that is easy to change.** Most production cost is not in writing code once, but in modifying it repeatedly as requirements evolve.

### Practical Mechanics

The lecture's payment-gateway example makes this tangible. You are building an e-commerce platform. Today you support PhonePe. Tomorrow the business needs Razorpay, then Paytm.

If the payment logic is **tightly coupled to PhonePe**, that PhonePe-specific logic ends up baked into many places. Every new provider means rewriting a significant chunk of the application:

```text
PhonePe-specific logic scattered across 15 different places
   -> add Razorpay  -> edit all 15 places
   -> add Paytm     -> edit all 15 places again
   -> time lost, bugs introduced, codebase growing in the wrong way
```

If instead you have a **clean abstraction** around the idea of "a payment gateway", every provider plugs into the same contract, and the rest of the application does not need to know which provider it is talking to:

```text
PaymentGateway  (a common contract: "I can charge an amount")
   PhonePeGateway   plugs in
   RazorpayGateway  plugs in

The checkout code just uses some PaymentGateway.
   -> adding Razorpay is a small, isolated change
   -> adding Paytm is another small, isolated change
```

That is the difference good LLD makes: the difference between rewriting a whole module and changing one small piece.

### Hidden Pitfalls

- **Confusing HLD concerns with LLD concerns.** "Should we add a caching layer or shard the database?" is HLD. "Should `Trip` hold a reference to the whole `Driver` or just a `driverId`?" is LLD. Mixing these signals weak fundamentals.
- **Premature abstraction.** Do not build a five-layer plugin architecture for a feature that has exactly one implementation and will never change. Abstract where change is *likely* (new payment providers), not everywhere.

> **Going Deeper: how Java expresses the "clean abstraction".** The `PaymentGateway` contract above is, in Java, expressed using an `interface` or an `abstract class`. You will study these properly in Module 2 (Design Principles and Patterns). For now, just hold on to the idea: the "clean abstraction" the lecture described is a real Java language feature, not hand-waving.

---

## Section 2: Scaling Fundamentals and Infrastructure Layers

### Deep-Dive Theory

A single-server deployment has three structural weaknesses, exactly the ones the class brainstormed:

1. **Single Point of Failure:** you have exactly one machine. One hardware hiccup, one memory spike, one bad deployment, and your entire application is down. Every single user sees an error.
2. **High latency under load:** that one machine handles everything (application logic, every incoming request, every database query). As more users hit it, it gets slower and slower until it buckles.
3. **Poor user experience at scale:** users do not care why your app is slow or down. They just leave.

There are two ways to get a single server more help:

- **Vertical scaling:** upgrade to a bigger, more powerful machine (more memory, more processing power). It is easier and simpler, but it has a hard ceiling (you can only make one machine so powerful), the cost spikes sharply as the machine gets beefier, and it still leaves the Single Point of Failure intact.
- **Horizontal scaling:** instead of one expensive giant machine, add multiple smaller machines and distribute the load across them. This is the more flexible, resilient, sustainable, industry-standard approach.

Once you go horizontal, a new question appears immediately: if you have five servers and a request arrives, who decides which server handles it? That is the job of a **load balancer**, a machine that sits in front of your servers and routes each request so no single server gets overwhelmed.

This gives the layered picture from the board:

$$\text{User Request} \rightarrow \text{Load Balancer} \rightarrow \text{Application Servers} \rightarrow \text{Database}$$

Each layer has its own purpose:

- **Load Balancer layer:** decides where each request goes.
- **Application Server layer:** processes business logic, replicated across many machines.
- **Database layer:** persists and serves data, shared so every app server sees the same data.

As the system grows, more layers appear (caches, message queues, CDNs), but the principle stays the same: define what pieces exist and how they connect.

### Practical Mechanics

Why must the data move out into its own dedicated layer? Recall the question from the lecture: a user logs in, their session lands on Server 1, and the very next request gets routed to Server 2. Server 2 has no idea who this user is. Chaos. And worse, if a server goes down, the data stored only on it is gone.

So we make an important decision: **the application servers will not store user data themselves.** All user data lives in a dedicated database (or a cache) that every app server can reach. Now it does not matter which server handles the next request, because they all read the same source of truth.

```text
Bad:  user session lives on one specific app server
      -> works on one machine, breaks the moment a different server gets the next request

Good: user data lives in a dedicated shared layer (Database) every app server can reach
      -> any server can serve any request for any user
```

### Hidden Pitfalls

- **Storing session in a single server's memory.** This is exactly the trap the lecture flagged: it works fine on one machine and silently breaks the moment you scale out. The fix is to externalize that data into the shared database layer.
- **Assuming horizontal scaling is free.** Distributing load solves availability and throughput, but it introduces new concerns (keeping data consistent across machines and coordination overhead). Scaling buys you a lot, but it is not without cost.

> **Going Deeper: why statelessness already touches LLD.** "App servers should not store user data" sounds like a pure HLD decision, but it constrains how you write code: your objects must not quietly stash per-user data in places that outlive a single request. How you organize state inside your entities (Section 5) is part of what determines whether the system can scale horizontally at all. Decisions at one altitude constrain the other.

---

## Section 3: Why LLD Matters (On the Job and in Interviews)

### Deep-Dive Theory

LLD matters from two perspectives, exactly as the lecture framed it: your on-the-job performance and career progression, and your ability to clear interviews.

**On the job.** The lecture opened with a surprising figure: only about **12%** of a software engineer's day-to-day time is actually spent writing code (less than one hour out of every eight). The other **88%** goes to activities that are all, fundamentally, about *understanding code*:

| Activity | What it is really about |
| --- | --- |
| Meetings | Planning and clarifying requirements |
| Code reviews | Reading code others wrote and catching bugs early |
| Giving KTs | Making others understand code |
| Designing | Structuring code before writing it |
| Debugging | Understanding code well enough to trace failures |
| Testing | Verifying code behaves correctly |
| Talking to Product Managers | Clarifying requirements |

Good LLD makes your 88% easier. Meetings get shorter because you can articulate your design decisions clearly. Code reviews go faster because your structure speaks for itself. Debugging shrinks because well-designed code fails in predictable, traceable ways. And you ask product managers sharper questions, because you know exactly what is ambiguous.

**In interviews.** LLD rounds have become a deciding factor in whether a candidate gets hired, because well-designed code lets companies build related features faster, which saves real money. It used to be evaluated only for senior engineers. That is no longer true. Today even mid-level roles face LLD rounds, and at startups you may hit an LLD round right after a single DSA round, even as a beginner. As experience grows this becomes more prominent, because senior engineers spend most of their time reviewing and designing code rather than just writing it.

### Practical Mechanics

Experience maps roughly to roles, and the kind of LLD interview you face shifts accordingly:

```text
0 to 2 years   -> SDE-1
2 to 5 years   -> SDE-2
5 to 10 years  -> SDE-3 / Senior Software Engineer
10+ years      -> Staff / Principal Engineer
```

**The LLD Interview Matrix:**

| Level | Startups | Product MNCs | FAANG |
| --- | --- | --- | --- |
| SDE-1 | Machine Coding Round | Usually none | Usually none |
| SDE-2 | Machine Coding + LLD | Dedicated LLD Round | May appear in some teams |
| SDE-3 / Senior | Advanced Machine Coding + LLD | Strong LLD Round | LLD + System Design expected |
| Staff / Principal | Architecture + Design Deep Dive | Multiple design discussions | Extensive design interviews |

LLD shows up in three formats, each testing a different competency:

| Format | Where it appears | What it tests |
| --- | --- | --- |
| **Theoretical Rounds** | Consulting and service firms (Deloitte, Cognizant, Infosys, Capgemini) | Foundational vocabulary and theory: what is a design pattern, what is SOLID, explain encapsulation, explain polymorphism |
| **LLD Design Rounds** | Product MNCs (Oracle, Adobe, VISA, Goldman Sachs), MAANG | Design thinking under ambiguity: clarifying a vague problem, identifying entities and relationships, choosing applicable patterns, sketching a class structure. Often little or no coding |
| **Machine Coding Rounds** | Startups (CRED, Cult.fit), even at SDE-1 | End-to-end execution: design the solution *and* write running, compilable, clean code within a limited time window |

At startups, the machine coding round is often the *first* round for an SDE-1: do well and you move forward, do poorly and you are out of the process. So it carries a lot of weight.

### Hidden Pitfalls

- **Theoretical rounds:** reciting a pattern name without explaining *when* and *why* you would use it. Interviewers immediately spot rote memorization.
- **Machine coding rounds:** getting bogged down trying to write a complete, perfect database layer or multi-threaded setup, instead of focusing on clean class design, working business logic, and clear separation of concerns.

> **Going Deeper: the hidden economics of code.** Software engineering is fundamentally an economic activity. Code that takes four times longer to modify than necessary is costing the company real money. That is why companies invest in LLD: good design is risk management and cost control wrapped in syntax.

---

## Section 4: Module Overview and LLD Roadmap

### Deep-Dive Theory

The LLD module is structured as a three-part journey that moves you from basic syntax to enterprise-grade system design. The roadmap looks like this:

```text
Module 1: Foundations of OOP & Entities
   - Classes, Objects, Constructors, Methods
   - Access Modifiers & Encapsulation
   - Association, Aggregation, and Composition

Module 2: Design Principles & Patterns
   - SOLID Principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
   - Creational Patterns (Singleton, Factory, Builder)
   - Structural Patterns (Adapter, Decorator, Facade)
   - Behavioral Patterns (Strategy, Observer, Command)

Module 3: Machine Coding & Real-World LLD Problems
   - Splitwise / Expense Sharing Application
   - Tic-Tac-Toe / Snake and Ladder
   - Parking Lot Design
   - BookMyShow / Movie Ticket Booking
   - Elevator System
```

Each module builds directly on the previous one. You cannot design a Parking Lot (Module 3) without clean entities (Module 1) and proper use of SOLID principles and design patterns (Module 2).

### Practical Mechanics

How to study this module effectively:
1. **Do not skip Module 1.** Even if you have written OOP code, make sure your mental model of encapsulation and state ownership is solid.
2. **Focus on the "Why" for SOLID.** Do not memorize definitions; understand what pain point each principle solves.
3. **Practice machine coding.** Design is a muscle. Reading about patterns is not enough; you must write the code from scratch, refactor it, and see where your abstractions break.

### Hidden Pitfalls

- **Jumping straight to Module 3.** Trying to code a complex system like Parking Lot or Splitwise without mastering core OOP and design principles leads to spaghetti code and frustration.

---

## Section 5: Programming Paradigms (Procedural vs Object-Oriented)

### Deep-Dive Theory

How do we structure our code? Throughout programming history, many paradigms have emerged, but two matter most for our journey: **Procedural** and **Object-Oriented**.

- **Procedural Programming:** Code is organized around *procedures* (functions or routines) that operate on passive data structures. Data and behavior are completely separated. A struct holds data (like a record in a database), and functions elsewhere manipulate that data.
- **Object-Oriented Programming (OOP):** Code is organized around *objects* (entities) that bundle both their data (attributes) and their behavior (methods) together. The entity controls what happens to its data.

Think of Procedural as a **puppeteer and puppets**: the functions are the active puppeteer pulling strings, and the data structs are passive puppets that have no say in what happens to them. Any function anywhere in the codebase can reach into a data struct and modify its fields. As the codebase grows, tracking which function modified which field becomes nearly impossible.

Think of Object-Oriented as **autonomous entities**: an object owns its state and exposes controlled methods to interact with it. You don't arbitrarily reach into a driver's state to accept a ride; you call `driver.acceptRide()`, and the driver object handles its own state transition.

### Practical Mechanics

Consider an Uber-like ride-sharing application:

**Procedural approach:**
```text
TripStruct { driverId, passengerId, status }
Function updateTripStatus(TripStruct trip, String newStatus) {
    trip.status = newStatus;
}
```
Any function anywhere can call `updateTripStatus` or directly mutate `trip.status = "CANCELLED"`.

**Object-Oriented approach:**
```text
class Trip {
    private String status;
    
    public void cancelTrip() {
        if (this.status.equals("COMPLETED")) {
            throw new RuntimeException("Cannot cancel a completed trip!");
        }
        this.status = "CANCELLED";
    }
}
```
The `Trip` entity protects its own invariants. It enforces business rules (you cannot cancel a completed trip) right where the data lives.

### Hidden Pitfalls

- **Anemic Domain Models.** Writing classes that contain *only* getters and setters with zero behavior, and putting all business logic in massive "Service" or "Manager" classes. This is procedural programming disguised in Java syntax. Real OOP keeps behavior close to data.

---

## Section 6: The Concept of Entity

### Deep-Dive Theory

At the heart of OOP lies the **Entity**. An entity is a representation of a real-world concept (like a User, a Driver, a Ride, a Payment) inside your software system.

An entity is defined by three things:
1. **Identity:** It has a unique identifier (like an ID or UUID) that distinguishes it from other instances even if their attributes are identical.
2. **State (Attributes):** The data it holds at any given moment (e.g., driver name, rating, location).
3. **Behavior (Methods):** The actions it can perform or have performed on it, governed by business rules.

When designing any system in LLD, your very first step is always **Entity Identification**. You read the problem statement, identify the nouns (which become your entities), define their attributes, and determine how they collaborate.

### Practical Mechanics

When designing a system like BookMyShow:
- Nouns identified: `User`, `Movie`, `Theater`, `Screen`, `Show`, `Seat`, `Booking`, `Payment`.
- Relationships: A `Theater` has multiple `Screen`s. A `Screen` has multiple `Show`s. A `Show` has multiple `Seat`s.
- Each entity encapsulates its own data and behavior.

### Hidden Pitfalls

- **Creating God Classes.** Putting all system logic into a single massive class (e.g., a `SystemManager` class that handles users, bookings, payments, and notifications). Break responsibilities down into distinct, focused entities.

---
