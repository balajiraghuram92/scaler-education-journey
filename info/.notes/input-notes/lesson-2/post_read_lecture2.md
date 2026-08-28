# POST-READ: Foundations of Object-Oriented Design & Scalable Systems
## Lecture-2: OOP-1 — Classes, Objects & Encapsulation

> **How to use this document.** This is a consolidation brief for the second session of Backend LLD. It tracks the session exactly: the abstraction principle and its three pillars, the class-object relationship and memory model, fields, methods and state, constructors and the `this` keyword, the `static` keyword, pass by value, `toString()`, and encapsulation. Each major topic has three parts: **Deep-Dive Theory**, **Practical Mechanics**, and **Hidden Pitfalls**. Optional **Going Deeper** callouts contain stretch material you can skip on a first pass.

---

## Section 1: Abstraction — Principle vs Pillar

### Deep-Dive Theory

Most textbooks and college curricula present four pillars of OOP: Encapsulation, Inheritance, Polymorphism, and Abstraction. This is not wrong, but it obscures an important relationship. The more precise framing — and the one that *Java: The Complete Reference* (Schildt, Ch. 2) articulates — is that Abstraction is the **overarching principle** of OOP, and Encapsulation, Inheritance, and Polymorphism are the three **mechanisms** that implement it.

**Abstraction** means representing a complex system as a set of simpler, clearly-bounded ideas working together. When we broke Uber down into Driver, Rider, Trip, Vehicle, and Payment in Lecture 1, we were practising abstraction: rather than trying to grasp Uber as one monolithic thing, we identified the distinct ideas inside it, each with its own clearly defined responsibilities.

The key insight is that a principle tells you the *destination*, not the route. "Represent your system as ideas working together" is a goal. How you achieve that goal in Java code is through the three pillars:

| Mechanism | What it contributes to Abstraction |
|-----------|-----------------------------------|
| **Encapsulation** | Each idea (class) controls what it exposes. The outside world sees a clean interface, not the internal complexity. |
| **Inheritance** | Common ideas can be generalized. `Car` and `Bike` both express what a `Vehicle` is, without repeating every vehicle concept. |
| **Polymorphism** | The same action (`startRide()`) can mean different things for different types, without the caller needing to know which type it is dealing with. |

Abstraction appears again as a concrete coding mechanism in Lecture 4 — through `interface` and `abstract class`. At that point, the principle becomes a tool, and the two senses of the word "abstraction" converge.

### Practical Mechanics

Knowing the distinction between three pillars and a principle is practically useful in interviews. An interviewer who says "explain the four pillars of OOP" is testing vocabulary. An interviewer who asks "how does encapsulation contribute to abstraction?" is testing understanding. The correct answer to the second question is: by hiding the internal state and behaviour of a class behind a controlled interface, encapsulation ensures that the user of a class interacts only with the idea it represents, not with its implementation details. That is abstraction in practice.

### Hidden Pitfalls

- **Treating the three pillars as independent.** Encapsulation, Inheritance, and Polymorphism are not separate tools you pick from a menu. They work together to implement the same principle. A class that uses encapsulation to hide its fields but exposes mutable internal objects through its getters is partially encapsulated and therefore partially abstracts its internals. The implementation detail is still leaking — just through a method instead of a direct field access.
- **Confusing "abstraction" the principle with `abstract` the keyword.** In Java, the keyword `abstract` applies to classes and methods in a very specific way. That is the *mechanism* covered in Lecture 4. Using `abstract` in code does not automatically mean you are practising the principle of abstraction well.

---

## Section 2: Class and Object — Blueprint and Real Instance

### Deep-Dive Theory

A **class** is a template — it defines the structure and behaviour of a category of objects. It specifies what fields exist and what methods exist. The class definition itself occupies minimal memory (just the bytecode loaded by the JVM).

An **object** is a concrete instance created from a class template. When `new Driver(...)` is called, the JVM allocates a block of memory on the **heap** — a region dedicated to dynamically allocated objects — and initializes all the fields of the new Driver there. The object exists independently of all other Driver objects. Modifying one object's state has no effect on any other.

$$\text{Class} \rightarrow \text{definition (no per-instance memory)}$$
$$\text{Object} \rightarrow \text{instance allocated on the heap}$$

Every time you call `new`, you get a distinct object at a distinct memory address. Uber's backend conceptually has one `Driver` class and millions of `Driver` objects — each with its own `driverId`, `name`, `rating`, and `isOnline` value, all completely independent.

### Practical Mechanics

Understanding that classes and objects are different things resolves a common confusion:

```java
Driver d;             // declares a reference variable — no object created yet
d = new Driver(...);  // NOW an object is created on the heap
```

The declaration `Driver d` does not create a Driver. It creates a reference variable capable of holding the address of a Driver. Until `new` is called, `d` is `null` — it points to nothing. Attempting to call a method on a null reference (`d.goOnline()`) throws a `NullPointerException`, one of the most common runtime errors in Java. The fix is always the same: ensure the reference actually points to an object before you use it.

### Hidden Pitfalls

- **Thinking the class "contains" the objects.** A class does not contain its instances. The class is a definition; the objects live independently on the heap. There is no parent-child containment relationship.
- **One object, multiple references.** It is easy to assume that if you have one variable, you have one object. But multiple reference variables can point to the same object (as the next section covers). The number of objects in memory is determined by the number of `new` calls, not the number of variable declarations.

> **Going Deeper: the JVM's memory model.** The heap is one of several memory regions the JVM manages. The **stack** holds method call frames — local variables and references for the currently executing methods. When a method returns, its stack frame is popped and its local variables are gone. Objects on the heap, however, persist until the JVM's garbage collector determines nothing refers to them anymore. This is why an object can outlive the method that created it: the object is on the heap, but the reference (on the stack) was just a pointer to it.

---

## Section 3: Fields, Methods, Members, and State

### Deep-Dive Theory

Every class in Java is made up of **members**: fields and methods.

- **Fields** (also called instance variables or attributes) represent the data an object holds. Each object gets its own copy of every non-static field.
- **Methods** represent the behaviour — the actions an object can perform. Methods may read or modify the object's fields, take inputs as parameters, and return results.

The collective term for fields and methods is the **members** of a class.

The **state** of an object is the set of values its fields hold at a particular moment. State is not a fixed snapshot — it changes continuously as the program runs. When `rahul.goOnline()` executes, `rahul`'s `isOnline` field changes from `false` to `true`. That is a state transition. A debugger, set at a breakpoint, shows you the exact state of every object in scope at that instant — which is why learning to use the debugger from day one dramatically accelerates your ability to understand object-oriented programs.

### Practical Mechanics

Java initializes fields to default values if no explicit assignment is given:

| Field type | Default value |
|-----------|--------------|
| `int`, `long`, `short`, `byte` | `0` |
| `double`, `float` | `0.0` |
| `boolean` | `false` |
| Any reference type (objects, `String`) | `null` |

This means a `Driver` created with `new Driver()` and no constructor assignments has `driverId = null`, `name = null`, `rating = 0.0`, and `isOnline = false`. This is a valid, if incomplete, state. It is the programmer's responsibility to set fields to meaningful values — which is exactly what constructors are for.

### Hidden Pitfalls

- **Confusing local variables with fields.** A local variable declared inside a method exists only for the duration of that method call. It does not retain its value between calls, is not shared between objects, and is not initialized to a default (you must assign it before reading it, or the compiler will refuse to compile). Fields, by contrast, belong to the object, persist for the object's lifetime, and receive defaults.
- **Treating state as read-only.** State changes constantly. A common mistake is assuming that an object's field value at one point in the program will still hold at a later point. If multiple methods, or multiple threads, can modify a field, the state at any given moment depends on execution order — which is why concurrency (covered later in this module) is non-trivial.

---

## Section 4: Reference Variables and the Memory Model

### Deep-Dive Theory

In Java, variables of a class type do not hold objects. They hold **references** — memory addresses pointing to where an object lives on the heap. This is the single most important low-level detail to internalize about Java.

```java
Driver d1 = new Driver("D001", "Rahul", 4.8);
Driver d2 = d1;
```

After the first line, the heap contains one Driver object, and `d1` holds its address. After the second line, `d2` holds the same address. There is still only one object. Assigning `d2 = d1` copies the address, not the object.

```
Stack             Heap
─────             ────
d1  ────────────► [ Driver object ]
d2  ────────────► { name: "Suresh" }   ← same object
```

So `d2.name = "Suresh"` modifies the single shared object — and reading `d1.name` afterwards returns "Suresh", not "Rahul".

To get two independent objects, you need two separate `new` calls:

```java
Driver d1 = new Driver("D001", "Rahul", 4.8);
Driver d2 = new Driver("D002", "Suresh", 4.2);
```

Now the heap contains two distinct Driver objects at two distinct addresses. Modifying `d2` has no effect on `d1`.

### Practical Mechanics

The reference model explains a subtle but important behaviour: setting a reference to `null` does not destroy the object.

```java
Driver d1 = new Driver("D001", "Rahul", 4.8);
Driver d2 = d1;
d1 = null;  // d1 no longer points to the Driver object
            // but d2 still does — the object is alive
```

The object is only eligible for garbage collection when *no* reference anywhere in the program still points to it. This matters in larger programs where objects should be released to free memory — keeping an unintentional reference alive (for example, in a list that is never cleared) is a common source of memory leaks in Java.

### Hidden Pitfalls

- **Equality confusion.** `d1 == d2` checks whether `d1` and `d2` hold the same address — whether they point to the same object. It does not check whether the two objects have equal field values. To compare two Driver objects by their content, you override the `equals()` method. This distinction will matter when you work with collections.
- **Returning references from methods.** If a method returns a reference to an internal field (particularly a mutable object), the caller can modify what should be private state. Encapsulation requires care here — returning a copy, or returning an immutable view, rather than the internal reference itself.
