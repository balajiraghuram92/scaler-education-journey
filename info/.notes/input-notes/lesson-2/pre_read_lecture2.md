# PRE-READ: Foundations of Object-Oriented Design & Scalable Systems
## Lecture-2: OOP-1 — Classes, Objects & Encapsulation

> **Welcome:** Last session we established *why* OOP exists — the puppeteer problem, the idea of an entity, and the five Uber entities we identified together. This session is where we stop talking about entities conceptually and start writing them in Java. Every concept in this pre-read will be coded live in class, so the goal here is not to memorize syntax but to arrive with the mental models already in place. That way, when you see the code, it confirms what you already understand rather than surprising you.

---

## Why This Session Is the One You Can't Miss

Everything that follows in this course — Inheritance, Polymorphism, Design Patterns, Machine Coding — sits directly on top of what you learn today. And in LLD interviews, nobody asks you to define encapsulation. They hand you a broken class and ask you to make it production-ready. That skill starts here.

---

## What We're Covering

Abstraction (the real story) → Classes & Objects → Fields, Methods & State → Reference Variables → Constructors & `this` → `static` → Pass by Value → `toString()` → Encapsulation

---

## Before Class: Concepts to Sit With

Work through these in order — each one sets up the next.

---

### 1. The Four Pillars Problem

Your college almost certainly taught you that OOP has four pillars: **Encapsulation, Inheritance, Polymorphism, and Abstraction**.

Most textbooks say this. Most interview prep sheets say this. Here's the question worth sitting with before class:

*Is Abstraction really in the same category as the other three? Or is it something different — something higher up?*

Think about what the word "abstract" literally means. Not in a programming context — just the word. Then think about what we did at the end of last session: we looked at a system as large and complex as Uber and broke it into five ideas — Driver, Rider, Trip, Vehicle, Payment. We didn't understand Uber all at once. We distilled it.

Was that Encapsulation? Inheritance? Polymorphism?

Bring your thinking to class. We'll sort this out together.

---

### 2. Class vs Object — Can You Live in a Blueprint?

Last session we landed on the concept of an **entity** — something real in your system with its own data and its own behaviour. Driver is an entity. So is Rider. So is Trip.

Here's the question that was deliberately left unanswered: *how does Java actually represent an entity?*

Consider this: an architect designs a blueprint for a flat. It specifies exactly where the walls go, how large each room is, where the plumbing runs. From that one blueprint, a contractor builds every flat in the tower — Floor 1, Floor 7, Floor 22. Same structure, different residents, completely independent from each other.

Now ask yourself:
- Can the architect *live* in the blueprint?
- If a resident on Floor 7 repaints their walls, does Floor 1 change?
- What's the Java equivalent of the blueprint? What's the equivalent of the actual flat?

One of those two things occupies real memory when a program runs. The other is just a specification. Which is which — and why does it matter?

---

### 3. State and Behaviour

Once you have an entity in code, it has two things: data it *holds* and things it can *do*.

A Driver holds a name, a rating, a phone number, and a status (online or offline). A Driver can go online, go offline, and accept a ride.

In Java, that data becomes **fields**. That behaviour becomes **methods**. Together they are the **members** of a class.

Here's something worth thinking about: the word **state**. An object's state is the snapshot of all its field values at a particular moment. When Rahul goes online, his `isOnline` field flips from `false` to `true`. That's a state change.

State isn't fixed — it evolves as the program runs. The debugger gives you a live window into an object's state at any point. We'll use it in class to watch state change in real time.

---

### 4. A Puzzle About Memory

Look at this code:

```java
Driver d1 = new Driver();
d1.name = "Rahul";

Driver d2 = d1;
d2.name = "Suresh";

System.out.println(d1.name);
```

What does the last line print?

Most people say "Rahul". Run it mentally. Are you sure?

The answer depends on one critical question: when you write `Driver d2 = d1`, are you copying the *object* — or something else? Think about what `d1` actually *holds*. This distinction will come up again when we talk about passing objects into methods, and again next session when we cover deep vs shallow copies.

---

### 5. A Silent Bug That Compiles Fine

Here's a constructor. It looks correct. It compiles. It runs. But it doesn't work.

```java
public Driver(String name, double rating) {
    name = name;
    rating = rating;
}
```

After calling `new Driver("Rahul", 4.8)`, the object's fields are empty. Why?

The `this` keyword exists precisely to fix this. What do you think it does?

---

### 6. Rahul's Rating vs Uber's Driver Count

Two pieces of data:
- Rahul's rating: **4.8**
- Total drivers Uber has ever onboarded: **8,40,000**

Both are numbers. Both live inside the `Driver` class. But they are fundamentally different *kinds* of data.

One belongs to Rahul specifically — every Driver object has its own copy. The other belongs to the system as a whole — there should be exactly one number, no matter how many Driver objects exist.

In Java, the `static` keyword captures this distinction. Before class, just ask yourself: *what goes wrong* if you make the total count a regular field instead of a static one?

---

### 7. The Open Data Problem

This code compiles. It runs. No errors.

```java
rahul.rating = 10.0;       // Uber ratings only go up to 5
rahul.rating = -3.0;       // negative ratings don't exist
rahul.driverId = "HACKED"; // IDs should never change after creation
```

Nothing stops it. The Driver's data is completely exposed — anyone, anywhere, can reach in and set anything to any value.

This is the procedural problem from last session showing up inside a class. Having an entity doesn't automatically make it safe.

Now look at your Uber app. When you book a ride, what does the driver's phone number look like? Something like +91 98XXX XX234 — partially masked. The full number exists somewhere in the system. But you never see it. Someone designed that deliberately. *Who* should be responsible for that masking — the Driver, or whoever is displaying it?

That question has a right answer. We'll get there in class.

---

## One Thing to Revisit

Pull up the five Uber entities from last session — Driver, Rider, Trip, Vehicle, Payment. For each one, spend two minutes thinking: what data does it carry, and what can it do? We start coding them today.

---

## What You'll Build in Class

By the end of the session, you'll have a fully working `Driver` class built live from scratch — private fields, validated setters, a masked phone getter, a static driver count, and a clean `toString()`. Not a tutorial exercise. Something close to what you'd actually write in a backend role.

Homework after class: build `Rider` the same way, on your own.

---

## Self-Check

Don't look these up — just think them through before you arrive.

1. What's the difference between a class and an object? Use an analogy of your own.
2. In the memory puzzle above, what does `d1.name` actually print, and why?
3. Why does `name = name` inside a constructor silently do nothing useful?
4. Rahul's rating and Uber's total driver count — which one should be `static`, and what goes wrong if you get it wrong?
5. What's broken about direct field access like `rahul.rating = 10.0`, and what would a better design look like?

Bring your instincts. We'll pressure-test them live.

---

> Make sure IntelliJ is set up and your GitHub repository is ready before class.
