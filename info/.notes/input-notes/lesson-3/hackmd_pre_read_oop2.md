# Pre-Read: Foundations of Object-Oriented Design & Scalable Systems

**Topic:** Backend LLD: OOP-2: Access Modifiers, Encapsulation Complete, and Inheritance  
**Source:** [HackMD Pre-Read (rJycNy_Mfl)](https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/rJycNy_Mfl)

---

## 1. Overview & Session Map
In this session, we complete the second pillar of Object-Oriented Programming (OOP) and establish foundations for scalable system design:
1. **Pillar 1 Complete (Encapsulation)**: Sealing entities using access modifiers, immutability, and copy semantics.
2. **Pillar 2 (Inheritance)**: Reusing structure and behavior across entities without code duplication.
3. **Core Java Integration (`java.lang.Object`)**: Understanding `toString()`, `equals()`, and `hashCode()`.

### Session Breakdown
| Topic | Description |
| :--- | :--- |
| **Access Modifiers** | The complete visibility matrix: `private`, `default`, `protected`, and `public`. |
| **Constructor Overloading & Chaining** | Constructing entities in multiple configurations while keeping initialization DRY using `this(...)`. |
| **`final` on Methods & Classes** | Locking method behavior against overrides and sealing classes against subclassing. |
| **Immutability (The `Fare` Class)** | Creating immutable value objects to prevent silent state mutation bugs in multi-threaded workflows. |
| **Copy Semantics (Trip & Route)** | Differentiating shallow vs. deep copy and implementing safe copy constructors. |
| **Inheritance (`extends`, `super`)** | Factoring common fields and behavior into parent classes (`Vehicle` $\rightarrow$ `Car`, `Auto`, `Bike`). |
| **The `Object` Class** | Why every class inherits `toString()`, `equals()`, and `hashCode()`, and preventing HashMap lookup failures. |

---

## 2. Real-World Domain Use Cases (Uber System Design)

- **Constructor Overloading (`Driver` Entity)**:
  - When a driver signs up with full details (phone, license, rating), use a fully parameterized constructor.
  - When minimal info is known initially (id and name), use a minimal constructor.
  - Use `this(...)` constructor chaining so onboarding metrics and default flags are maintained in a single place.
- **`final` Modifier**:
  - `getDriverId()` is made `final` to ensure identity retrieval cannot be maliciously altered by subclasses.
  - The `Fare` class is declared `final` to guarantee price immutability.
- **Immutability (`Fare` Object)**:
  - If a `Fare` object were mutable, downstream pricing engines could mutate an accepted fare of `1.2x` to `2.5x`.
  - Marking fields `final`, omitting setters, and sealing the class makes this bug impossible at compile time.
- **Copy Semantics (`Trip` & `Route`)**:
  - Copying a `Trip` containing a mutable `Route` object via shallow copy shares the inner `Route` reference.
  - Mutating the destination on the copy alters the original trip. Deep copy avoids this memory aliasing.
- **Inheritance (`Vehicle` Hierarchy)**:
  - `Car`, `Auto`, and `Bike` share `vehicleId`, `licensePlate`, and `seatingCapacity`.
  - Factoring shared logic into `Vehicle` eliminates code duplication across concrete vehicle types.

---

## 3. Key Concepts & Principles

### Shallow Copy vs. Deep Copy
- **Shallow Copy**: Copies field values directly. Object reference fields continue pointing to the same underlying heap object.
- **Deep Copy**: Recursively creates new instances of all nested mutable objects, ensuring complete state independence.

> **Design Rule**: If a nested object is immutable (e.g., `String`, `Fare`), sharing its reference is safe and memory-efficient. If mutable (e.g., `Route`), deep copying is required for isolation.

---

## 4. Learning Checklist
- [x] Analyze the complete 4-tier Access Modifier matrix.
- [x] Chain constructors using `this(...)` without repeating boilerplate.
- [x] Apply `final` to variables, methods, and classes.
- [x] Design thread-safe immutable classes.
- [x] Prevent reference leakage via deep copy constructors.
- [x] Implement inheritance with `extends` and `super(...)`.
- [x] Understand the contract between `equals()` and `hashCode()`.
