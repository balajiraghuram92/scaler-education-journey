Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/rJgHH0GpMze

# Post-Read: OOP-4 Lab — Library Management System

## Overview

This document serves dual purposes: consolidating the OOP-4 lab session and providing a comprehensive revision guide for all four OOP modules. It grounds every concept taught across OOP-1 through OOP-4 in a Library Management System implementation.

## Section 1: Abstraction — The Design Principle

**Core Principle:**
"Model a complex problem/system as set of different entities working together. Show what something does. Hide how it does it."

Abstraction operates at two levels in the LMS:

- **Abstract Classes:** `User` and `Book` serve as blueprints that cannot be instantiated. They declare required behavior without providing implementation.

- **Interfaces:** `Lendable` represents a pure contract defining capabilities (`lend`, `returnItem`, `isAvailable`) without implementation details.

The distinction matters significantly: abstract classes represent "what something IS" with partial implementation, while interfaces represent "what something CAN DO" as pure contracts.

## Section 2: Encapsulation — Protecting State

Encapsulation creates a protected bundle of state and governing rules. Every class controls its own data through methods rather than direct external access.

Key implementation patterns:
- `Book` controls `isAvailable` flag through `lend()` and `returnItem()` methods
- `Member` manages `borrowedBooksCount` via dedicated increment/decrement methods
- `LibraryManagementSystem` coordinates between classes while respecting encapsulation

**Access Modifiers Table:**

| Modifier | Same Class | Same Package | Subclass | Everywhere |
|----------|------------|--------------|----------|------------|
| `private` | yes | no | no | no |
| default | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

All entity fields in the LMS remain `private`, with controlled access through public getters.

## Section 3: Inheritance — Sharing Structure

Inheritance allows one class to build upon another through the `extends` keyword. The IS-A relationship test determines appropriateness: "Member IS-A User" reads naturally, indicating valid inheritance.

**Shared code example:**
Without inheritance, `userId`, `name`, and `contactInfo` would duplicate across `Member` and `Librarian`. Inheritance places these once in `User`, automatically benefiting all subclasses.

**Constructor ordering rule:**
Parents always initialize before children. When `new Member("Asha", "asha@email.com")` executes:
1. `Member` constructor invoked
2. `super()` passes control to `User`
3. `User` generates `userId` and increments `totalUsers`
4. Control returns to `Member` for child-specific initialization

## Section 4: `static` and `final` — Class-Level Rules

**`static` keyword:** Belongs to the class, not instances. One shared copy regardless of object count.

**`final` keyword:** On variables, assigned once and never changed. On methods, cannot be overridden. On classes, cannot be subclassed.

**Practical implementations:**
- `idCounter` and `totalUsers` as `static`: shared across all `User` instances
- `getTotalUsers()` as `static method`: callable on the class itself
- `userId` as `final`: assigned exactly once in constructor
- `MAX_BORROW_LIMIT` as `static final`: shared constant policy across all `Member` instances

## Section 5: All Three Constructor Types

**Constructor patterns used throughout the LMS:**

1. **Default constructor:** Establishes object with safe starting values
2. **Parameterized constructor:** Accepts required initialization values at creation time
3. **Copy constructor:** Creates independent new object from existing instance

**Critical design point in copy constructors:**
A copied user receives a fresh unique ID via `generateUniqueId()`, not a copied ID. Copying `other.userId` directly would create duplicate IDs, violating the PRD requirement for uniqueness.

Similarly, a copied book starts with `isAvailable = true`, as a new record begins available.

## Section 6: Polymorphism — One Call, Multiple Behaviours

Polymorphism enables one interface with multiple runtime implementations. Java automatically selects the correct version based on the actual object type.

**Two forms:**

- **Runtime polymorphism:** Method overriding where child replaces parent's method. Resolved at runtime.
- **Compile-time polymorphism:** Method overloading with identical names but different parameter lists. Resolved at compile time.

**Runtime example in `Book.lend()`:**
```java
if (isAvailable && user.canBorrowBooks()) {
```
The `user` reference accepts both `Member` and `Librarian` objects. Each runs its own version:
- `Member`: checks `borrowedBooksCount < MAX_BORROW_LIMIT`
- `Librarian`: returns `true` unconditionally

No `instanceof` checks needed. One method, correct behavior for any type.

## Section 7: Interfaces — Capability Without Family

Interfaces attach capabilities across inheritance hierarchies. They answer "what can this thing do?" rather than "what type is it?"

**Design advantage:**
`TextBook` (extending `Book`) and `Magazine` (extending different parent) both implement `Lendable` despite different families. Forcing them into an artificial shared parent would violate design principles. The interface provides exactly the needed capability independently.

`Book` implements `Lendable` and provides concrete implementations for all methods. Subclasses `TextBook` and `NovelBook` inherit this lending capability while supplying their own `displayBookDetails()` implementations.

## Section 8: Complete System Integration

All OOP concepts operate simultaneously in the LMS:

- **Abstraction:** `User`, `Book`, and `Lendable`
- **Encapsulation:** Private fields throughout
- **Inheritance:** `Member`/`Librarian` extend `User`; `TextBook`/`NovelBook` extend `Book`
- **Polymorphism:** `canBorrowBooks()` within `lend()`; `displayDashboard()` on `List<User>`
- **Interfaces:** `Lendable` capability attachment
- **`static`:** Shared counters and class methods
- **`final`:** Immutable unique IDs and constants
- **Constructors:** All three types in both `User` and `Book`

## Section 9: Key Terminology

| Term | Definition |
|------|------------|
| **Abstraction** | Showing *what* while hiding *how* |
| **Abstract class** | Cannot instantiate; serves as blueprint with partial implementation |
| **Abstract method** | Declared without body; every concrete subclass provides implementation |
| **Interface** | Pure contract with method signatures only; models capabilities |
| **`implements`** | Declares class fulfils interface contract |
| **Encapsulation** | Private fields plus controlled access through methods |
| **Inheritance** | One class building on another via `extends`; IS-A relationship |
| **`extends`** | Makes one class child of another |
| **`super(...)`** | Calls parent constructor; must be first line |
| **Polymorphism** | One interface, multiple forms at runtime |
| **Method overriding** | Child replaces parent's method; resolved at runtime |
| **Method overloading** | Same name, different parameters in same class; compile-time resolution |
| **`@Override`** | Signals intentional method replacement; catches signature errors |
| **`static` field** | One shared copy per class, not per instance |
| **`static` method** | Called on class; requires no object instance |
| **`final` field** | Assigned once, compiler enforces immutability |
| **`final` method** | Cannot be overridden by subclasses |
| **`final` class** | Cannot be subclassed |
| **`static final`** | Constant: shared and fixed in value |
| **Default constructor** | No arguments; creates object with safe defaults |
| **Parameterized constructor** | Takes specific arguments for full initialization |
| **Copy constructor** | Creates new independent object from existing instance |
| **`this(...)`** | Calls another constructor in same class; first line |
| **Constructor order** | Parent always runs before child |
| **Shallow copy** | Copies field values; reference fields share inner objects |
| **Deep copy** | Copies recursively; nested objects get independent memory |
| **IS-A test** | Intuition check: does "Child IS-A Parent" read naturally? |

## Section 10: Self-Check Questions

1. Why should plain `User` and `Book` objects never exist? Explain each in one sentence.

2. The copy constructor in `User` calls `generateUniqueId()` instead of copying `other.userId`. What requirement would be violated if it copied the ID directly?

3. `totalUsers` increments in all three `User` constructors. Why must the copy constructor also increment it? What would undercount without it?

4. `Book.lend()` calls `user.canBorrowBooks()`. Predict outcomes with a `Member` at the 5-book limit versus a `Librarian`. Which mechanism creates different behaviors from one method call?

5. Is `searchBooks` overloading runtime or compile-time polymorphism? How does Java pick the correct version?

6. `Librarian.canBorrowBooks()` always returns `true` with no counting. Is this a bug or deliberate design? Argue both perspectives and explain what would change if requirements shifted.

7. `TextBook` uses `getTitle()` and `getAuthor()` rather than direct field access in `displayBookDetails()`. Why? Would `this.title` compile? Explain using encapsulation and access modifiers.

8. Draw the memory picture for this sequence. How many objects? How many unique IDs?
```java
Member asha = new Member("Asha", "asha@email.com");
User copy = new Member(asha);
System.out.println(asha.getUserId().equals(copy.getUserId()));
```

9. `LibraryManagementSystem.lendBook()` delegates to `book.lend()` then calls `member.incrementBorrowCount()`. Why doesn't `Book.lend()` call `incrementBorrowCount()` directly? Which design principle protects this separation?

10. List every OOP concept in this code block and explain each:
```java
List<User> users = new ArrayList<>();
users.add(new Member("Asha", "asha@email.com"));
for (User u : users) { u.displayDashboard(); }
```

## Section 11: The Four-Pillar Summary

**ENCAPSULATION:** Protects state through private fields and controlled method access. Each class governs its own data exclusively.

**INHERITANCE:** Shares structure. Common code lives once in parent; children extend and specialize. Updates to parent automatically benefit all descendants.

**POLYMORPHISM:** Enables flexibility. One call executes correct behavior for any concrete type without `instanceof` checks. Runtime overriding and compile-time overloading are both forms.

**ABSTRACTION:** Hides complexity. Exposes what something does while hiding implementation. Abstract classes provide partial blueprints enforcing contracts; interfaces provide pure capability contracts across hierarchies.

These four reinforce each other: inheritance enables polymorphism, abstraction specifies polymorphic dispatch targets, and encapsulation protects all underlying state.

## Section 12: Further Reading

- **Java: The Complete Reference (Herbert Schildt):** Canonical treatment of `extends`, `abstract`, and `implements`
- **Effective Java (Joshua Bloch):** "Prefer interfaces to abstract classes" and "Design and document for inheritance or else prohibit it"
- **The Java Tutorials (Oracle):** Official walkthroughs of abstraction tools
- **Head First Design Patterns:** Introduces programming to interface rather than implementation

## Section 13: Homework

**Milestone C — LibraryManagementSystem Implementation:**

1. Wire `registerUser`, `addBook`, `lendBook`, `returnBook`
2. `lendBook` must delegate to `book.lend(member)` then call `member.incrementBorrowCount()`
3. `returnBook` must delegate to `book.returnItem(member)` then call `member.decrementBorrowCount()`
4. Implement both `searchBooks` overloads (by criteria only, and by criteria + type)
5. Implement `displayAllBooks` and `displayRegisteredUsers`

Revise all OOP-1 through OOP-4 material using this document as reference. Push complete code to GitHub branch: `oop-4-lab-complete`.