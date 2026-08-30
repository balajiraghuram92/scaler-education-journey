Source: https://hackmd.io/@7ZhgEFzKSUeDhAQFDVj8mw/BJmMLbRXzl

# Post-Reads-Java-Advanced-1.md - HackMD

---

title: Post-Reads
tags: [Final]

---

| POST-READ | Java Advanced Concepts | Java Advanced Concepts-1 — Generics & Collections |
|-----------|-------------------------|-----------------------------------------------------|

This document consolidates the material covered in the session. Each section states the relevant definition, walks through the Java code built live in class, and closes with the pitfalls most commonly associated with that concept. This is the first session of the Java Advanced Concepts series; later sessions in the series build directly on the vocabulary established here.

## Section 1: What Is a Collection

### Definition

A **collection**, in plain terms, is a group of similar things stored together. Java's **Collections Framework** provides a standard, ready-made set of containers — `List`, `Set`, `Queue`, and others — so that this general idea does not need to be implemented from scratch for every program.

### Hidden Pitfalls

- **Treating "Collection" and "Collections Framework" as identical terms.** `Collection` is a specific interface within the framework; the Collections Framework is the broader hierarchy of interfaces and implementations built around it, covered fully in Section 7.

---

## Section 2: The Problem, Before Generics Existed

### Deep-Dive Theory

Before Generics, a general-purpose container had to be written to hold a type that could accommodate anything at all. Since every class in Java derives from `Object`, `Object` was that type.

```java
class Stack {
    Object[] arr;
    void push(Object x) { ... }
    Object pop() { ... }
}
```

This design is maximally flexible — any type can be pushed onto the stack — but it provides no restriction whatsoever. Nothing stops a caller from pushing an `Integer` immediately followed by a `String` into the same stack. The compiler raises no objection to this. The mistake only becomes visible when the program actually runs, typically as a `ClassCastException` when the value is later read back and cast to the wrong type.

```text
Object-based container: Flexible -> yes, holds anything Safe -> no, nothing stops mixed types When does the mistake surface -> at runtime, not compile time
```

### Hidden Pitfalls

- **Assuming a compiling program is a correct program.** An `Object`-based container compiles cleanly regardless of what is pushed into it; compilation success says nothing about type consistency in this design.

- **Underestimating where `ClassCastException` surfaces.** Because the failure only occurs when a value is read back and cast, it can appear far from the line of code that actually caused the mistake, and often only under specific runtime conditions.

---

## Section 3: Generics — The Solution

### Definition

**Generics**, introduced in Java 5, allow the caller of a class to decide the type it will hold at the point the object is created. Once decided, Java enforces that type strictly from that point onward, at compile time.

```java
class Stack<T> {
    T[] arr;
    void push(T x) { ... }
    T pop() { ... }
}
```

```java
Stack<Integer> s = new Stack<>();
```

Here, `T` is a **type parameter** — a placeholder. Writing `Stack<Integer>` fixes `T` to `Integer` for that specific object. Attempting `s.push("hello")` immediately afterward does not compile; the error is caught before the program ever runs.

### Practical Mechanics

```java
Stack<Integer> s = new Stack<>();
s.push(5); // compiles
s.push("hello"); // compile-time error: incompatible types
```

A **raw type** — a generic class used without specifying a type argument — remains legal:

```java
Stack s = new Stack(); // raw type
```

This compiles, and Java treats it exactly as it would before Generics existed: as `Object` underneath, with no type safety. Raw types exist purely for backward compatibility with code written before Java 5 and should not appear in new code.

### Hidden Pitfalls

- **Writing a raw type out of habit or convenience.** A raw type compiles without complaint but silently discards every safety guarantee Generics provide; it should be treated as legacy syntax, not a shortcut.

- **Assuming `Stack<Integer>` and `Stack<String>` share some relationship at the type level.** They do not — each parameterization is treated as an unrelated type by the compiler, a point revisited in Section 6.

---

## Section 4: Generic Methods

### Deep-Dive Theory

A method can be made generic independently of the class it belongs to. This is particularly useful for `static` methods, since a `static` method is not tied to any specific object and therefore cannot rely on a type parameter declared at the class level.

### Practical Mechanics

```java
public static <S> void doSomething(S data) { ... }
```

The type parameter `S` here is scoped to this one method. Each call determines `S` independently, based on the argument supplied, and the check happens entirely at compile time.

### Hidden Pitfalls

- **Referencing a class-level type parameter inside a `static` method.** A `static` method has no access to its enclosing class's type parameter, since `static` members are not associated with any particular instantiation of the class; the method must declare its own type parameter instead.

---

## Section 5: Storing a Pair of Values — `Pair<T, V>`

### Deep-Dive Theory

A class parameterized by a single type solves the "one type per container" problem. Some structures need to hold two related values of potentially different types at once — an attendance and a PSP score, a subject and a mark. Without Generics, each such combination would require its own hand-written class.

### Practical Mechanics

Without Generics, using plain `Object`:

```java
class Pair {
    Object first, second;
    void setFirst(Object f) { first = f; }
    void setSecond(Object s) { second = s; }
}
```

Nothing here stops `setFirst(100)` from being called even where `first` was only ever intended to hold a name. With Generics:

```java
class Pair<T, V> {
    T first;
    V second;
    void setFirst(T f) { first = f; }
    void setSecond(V s) { second = s; }
}
```

```java
Pair<String, Integer> p = new Pair<>();
p.setFirst("Rohit"); // compiles
p.setFirst(100); // compile-time error
```

`T` and `V` are arbitrary names; once real types are supplied at object creation, Java locks them in for that object. As with the single-parameter case, `Pair pair = new Pair();` remains legal as a raw type, but should be avoided in new code for the same reasons covered in Section 3.

```text
Pair<Double, Double> -> attendance, PSP
Pair<String, Integer> -> subject, marks
```

### Hidden Pitfalls

- **Writing a separate class for every type combination instead of parameterizing once.** This is precisely the duplication Generics are designed to eliminate; a single `Pair<T, V>` definition should serve every combination of types needed.

- **Forgetting that a raw `Pair` still compiles.** As in Section 3, this does not raise a warning that stops compilation, only reduced safety — a distinction worth remembering when reviewing unfamiliar code.

---

## Section 6: Generics With Inheritance — Wildcards

### Deep-Dive Theory

A common assumption is that if `Cat` extends `Animal`, then `List<Cat>` should be usable wherever `List<Animal>` is expected — reasoning that since a single `Cat` object is always usable where an `Animal` is expected, a list of them should behave the same way. This assumption is incorrect.

```java
void printAnimalNames(List<Animal> animals) {
    for (Animal a : animals) {
        System.out.println(a.getName());
    }
}
printAnimalNames(new ArrayList<Cat>()); // does not compile
```

A collection of the child type is not automatically treated as a collection of the parent type in Java's generic type system, even though this holds for a single object. `List<Cat>` and `List<Animal>` are treated as unrelated types by the compiler.

### Practical Mechanics

The fix is a **wildcard**, combined with `extends`:

```java
void printAnimalNames(List<? extends Animal> animals) { ... }
printAnimalNames(new ArrayList<Cat>()); // now compiles
```

```text
Animal
|
Mammal / \
Dog    Cat
```

`List<? extends Animal>` accepts a list of `Animal`, or a list of anything below it in this hierarchy — `Mammal`, `Dog`, `Cat`. This is an **upper-bounded wildcard**. A mirror form exists using `super`, which accepts the given type and everything above it:

```java
void insertAnimal(List<? super Dog> arr) {
    arr.add(new Dog());
}
```

The governing rule:

```text
Use extends when the list is only being READ from -> "? extends Animal"
Use super when the list is being WRITTEN, or inserted into -> "? super Dog"
PECS — Producer Extends, Consumer Super.
```

### Hidden Pitfalls

- **Applying `extends` when the intent is to write into the list.** A `List<? extends Animal>` cannot safely accept an `add()` call for a specific subtype, since the compiler cannot guarantee which exact subtype the underlying list holds; this is why `extends` is reserved for read-only ("producer") use.

- **Applying `super` when the intent is only to read.** Reading from a `List<? super Dog>` only guarantees an `Object` in return, not a `Dog`, since the underlying list could be of `Dog`, `Mammal`, or `Animal`.

- **Forgetting that the wildcard rule applies to the collection type, not the element type.** A single `Cat` is always assignable to an `Animal` variable; it is specifically `List<Cat>` versus `List<Animal>` that breaks the intuitive subtype relationship.

---

## Section 7: The Collections Framework

### Deep-Dive Theory

Without a standard framework, every developer building a `Stack`, a `Queue`, or a `HashMap` from scratch would produce implementations that differ in correctness, edge-case handling, and performance. The Collections Framework exists to provide one standard, well-tested set of data structures instead. The framework is organized as a set of interfaces — which define what operations are possible — with concrete implementations underneath providing the actual behaviour. `Collection.java` in the JDK source defines the baseline methods, such as `size()` and `isEmpty()`, that every implementation must support.

### Practical Mechanics

```text
List -> a sequence of elements, one after another.
ArrayList -> dynamic-size array. Grows/shrinks on its own. Insertion order preserved. Indexed access. (derived from the List interface)
LinkedList -> doubly linked list. Insertion from both ends. Good for lots of insertions/deletions.
Vector -> same as ArrayList, but synchronized/thread-safe. Largely outdated now — concurrent package does this better.
Queue -> holds elements waiting, first-come first-served.
PriorityQueue -> insertion in order, but extraction follows priority, not insertion order.
Set -> stores only unique data. Very fast search.
HashSet -> like Set, but no ordering guarantee.
LinkedHashSet -> HashSet + doubly linked list. Keeps insertion order.
TreeSet -> backed by a balanced BST. Sorted order.
```

```java
List<Integer> list = new ArrayList<>(List.of(3, 1, 2));
System.out.println(list); // [3, 1, 2] -> insertion order preserved
Set<Integer> set = new HashSet<>(List.of(3, 1, 2));
System.out.println(set); // no guaranteed order
```

`Map` is part of the Collections family but does not extend the `Collection` interface, because `Collection` operates on a single type per element, while `Map` operates on key-value pairs.

```text
Map -> part of the Collections family, but does NOT come under the Collection interface. Search is excellent — close to O(1).
HashMap -> no ordering
LinkedHashMap -> insertion order
TreeMap -> sorted order
```

`Map` is covered in full detail in the next session, which examines the internal hashing mechanism behind `HashMap`.

### Hidden Pitfalls

- **Assuming any `Set` or `Map` preserves insertion order.** Only `LinkedHashSet` and `LinkedHashMap` guarantee this; `HashSet` and `HashMap` make no such guarantee, and their apparent order should never be relied upon.

- **Choosing `ArrayList` or `LinkedList` without considering the access pattern.** `ArrayList` offers fast indexed access but costlier insertion/deletion in the middle; `LinkedList` offers the reverse trade-off. The choice should follow from how the collection is actually used, not from habit.

- **Assuming `Map` is a `Collection`.** It is a related but structurally separate interface in the framework, for the reason stated above.

---

## Section 8: Common Generics Pitfalls

### Deep-Dive Theory

Beyond the individual pitfalls noted above, a small number of mistakes recur across most first exposure to Generics:

```text
1. Using a raw type in new code -> compiles, but silently discards all type safety. Should never appear in code written after this session.
2. Assuming subtype relationships carry over to generic types -> List<Cat> is not a List<Animal>, even though Cat is an Animal. Requires a wildcard to express the intended flexibility.
3. Using extends where write access is needed, or super where only read access is needed -> violates PECS and either fails to compile or compiles but cannot be used as intended.
4. Referencing a class's type parameter inside a static method -> does not compile; a static method must declare its own type parameter if it needs one.
```

### Hidden Pitfalls

- **Treating a raw-type compile success as validation.** As emphasized throughout this document, compiling is not the same as being type-safe; raw types are the clearest example of this gap.

- **Memorizing PECS without the underlying reasoning.** The mnemonic is useful for quick recall, but the reasoning — that a producer-only wildcard cannot guarantee safe insertion, while a consumer-only wildcard cannot guarantee a specific read type — is what actually generalizes to unfamiliar situations.

---

## Section 9: Key Terminology

| Term | Definition |
|------|------------|
| **Generics** | A language feature allowing a class, interface, or method to be parameterized by one or more types, enforced at compile time |
| **Type parameter** | A placeholder, such as `T` or `V`, standing in for an actual type to be supplied at the point of use |
| **Raw type** | A generic class used without a type argument; legal for backward compatibility, but without any type safety |
| **Wildcard** | The `?` symbol, denoting an unknown type within a bounded range |
| **Upper-bounded wildcard** | `? extends Type` — accepts the given type and any of its subtypes; read-only |
| **Lower-bounded wildcard** | `? super Type` — accepts the given type and any of its supertypes; write-capable |
| **PECS** | Producer Extends, Consumer Super — the rule governing when to use `extends` versus `super` |
| **Collection** | The root interface in the Collections Framework representing a group of elements |
| **Collections Framework** | Java's standard library of container interfaces and implementations, including `List`, `Set`, `Queue`, and `Map` |
| **`ClassCastException`** | A runtime exception raised when an object is cast to a type it is not actually an instance of |

---

## Section 10: Extra Read — Type Erasure

This topic was not covered live in the session but is closely related and frequently raised in follow-up discussion and interviews. Java implements Generics through a mechanism called **type erasure**: type parameter information exists only at compile time, for the purpose of type checking, and is removed from the actual bytecode. At runtime, `Stack<Integer>` and `Stack<String>` are represented by the exact same class, `Stack`, with its type parameter erased to `Object` (or to its bound, if one was declared).

```text
Compile time: Stack<Integer>, Stack<String> -> distinct, type-checked
Runtime: Stack, Stack -> identical, no type info remains
```

This has several practical consequences worth being aware of:

- `stack1.getClass() == stack2.getClass()` returns `true` for a `Stack<Integer>` and a `Stack<String>`, since both share the same runtime class.

- A generic array cannot be created directly (`new T[]` does not compile), because the runtime has no way to know what `T` actually is at the point of array creation.

- Overloading two methods that differ only in their type parameter, such as `void process(List<Integer> list)` and `void process(List<String> list)`, is not permitted, since both erase to the identical signature `process(List list)`.

Type erasure is the reason raw types exist at all: pre-Generics bytecode and Generics-aware bytecode are, at the JVM level, indistinguishable, which is precisely what allows old and new code to interoperate.

---

## Section 11: Frequently Asked Interview Questions

**1. Why does Java use type erasure instead of retaining generic type information at runtime?**

Generics were introduced in Java 5, after a large body of code already existed. Type erasure was chosen specifically so that existing bytecode and libraries would remain compatible with code written using Generics, without requiring the JVM itself to change. The trade-off is that type information is unavailable at runtime, which is why raw types, certain overloads, and generic array creation behave the way they do.

**2. Why is `List<String>` not a subtype of `List<Object>`, even though `String` is a subtype of `Object`?**

If this were allowed, a `List<Object>` reference pointing to an actual `List<String>` could have a non-`String` object inserted into it through the `Object`-typed reference, silently corrupting the underlying `List<String>`. Disallowing the relationship at compile time closes this hole entirely; wildcards exist precisely to allow the specific, safe subset of this flexibility that is actually needed.

**3. What is the practical difference between `? extends T` and `? super T`, beyond the PECS mnemonic?**

With `? extends T`, the compiler only knows the elements are "some subtype of `T`," so it cannot allow inserting a specific type without risking a mismatch — only reading, as a `T`, is safe. With `? super T`, the compiler only knows the elements are "some supertype of `T`," so inserting a `T` (or a subtype of `T`) is always safe, but reading only guarantees an `Object`.

**4. Can a primitive type be used as a generic type argument, such as `List<int>`?**

No. Generics operate only on reference types, because type erasure ultimately treats the type parameter as `Object`, and primitives are not objects. This is why `List<Integer>` is used instead of `List<int>`, with autoboxing handling the conversion between `int` and `Integer` at the call site.

**5. When should `ArrayList` be preferred over `LinkedList`, and vice versa?**

`ArrayList` is generally preferred when indexed access or iteration dominates, since it offers constant-time access by index and better cache locality. `LinkedList` is preferred when insertions and deletions at arbitrary positions — particularly at both ends — dominate, since these do not require shifting subsequent elements. In most everyday backend code, `ArrayList` is the default choice unless the access pattern specifically favours `LinkedList`.

**6. Why does `HashSet` not guarantee any particular iteration order, while `LinkedHashSet` does?**

`HashSet` stores elements based on their hash code, bucketed internally for fast lookup; the resulting iteration order reflects bucket placement, not insertion sequence, and is not part of its contract. `LinkedHashSet` additionally maintains a doubly linked list threading through the entries in insertion order, at the cost of slightly higher memory overhead, specifically to provide that guarantee.

**7. Is a raw type the same as using `Object` explicitly, such as `List` versus `List<Object>`?**

No, and this distinction is a common trap. `List<Object>` is a fully parameterized generic type — it is type-checked, and only `Object` (or any type, since everything is an `Object`) may be inserted, with the compiler aware of this. A raw `List` bypasses generic type checking altogether, and produces unchecked warnings when mixed with generic code, whereas `List<Object>` does not.

**8. Why can a static method not use its enclosing generic class's type parameter?**

A class-level type parameter, such as `T` in `Stack<T>`, is bound to a specific instance the moment that instance is created. A `static` method exists independently of any instance and is not associated with a particular `T`, so referencing the class's `T` inside a `static` context has no meaningful value to resolve to. A `static` method that needs a type parameter must declare its own, as covered in Section 4.

---

## Section 12: Self-Check Questions

1. Explain, using a concrete example, why an `Object`-based `Stack` compiles without error even when a type mismatch is pushed into it, and precisely when that mistake becomes visible.

2. What is the difference between `Stack<T>` and a raw `Stack`, and why should the latter be avoided in new code?

3. Write the signature of a generic method that accepts a single argument of any type and returns that same type, declared independently of any enclosing class's type parameter.

4. Why does `List<Cat>` fail to compile where `List<Animal>` is expected, even though `Cat extends Animal`? What single change to the method signature resolves this?

5. State the PECS rule in your own words, and give one example each of a correct use of `? extends` and a correct use of `? super`.

6. Why does `Map` not extend the `Collection` interface, despite being part of the Collections Framework?

7. Give one situation where `ArrayList` is clearly the better choice over `LinkedList`, and one where the reverse is true.

8. Explain why `HashSet` provides no ordering guarantee, while `LinkedHashSet` does, in terms of their underlying implementation.

9. What is type erasure, and why does it prevent two overloaded methods that differ only in their generic type parameter?

10. Why is `List pair = new List();` legal Java, and what specifically is lost by writing code this way instead of `List<String> pair = new ArrayList<>();`?

---

## Section 13: Further Reading

- **Official Java documentation — Generics (The Java Tutorials):** the canonical reference for type parameters, bounded types, and wildcards.

- **Official Java documentation — `java.util.Collection` and `java.util.Map`:** the interface definitions underlying every implementation discussed in this session.

- **Effective Java, Item 26–31 (Joshua Bloch):** widely referenced treatment of Generics best practices, including why raw types should be avoided and the reasoning behind PECS.

- General reading on **type erasure** and its consequences for generic array creation and method overloading, previewed in Section 10.

---

## Section 14: Homework

```text
1. Write a small Box<T> class — store one item, return it. On purpose, try to break the type safety. Watch the compiler stop you.
2. Write a Pair<T, V> class from scratch, independently of the version built in class, and use it to store two different type combinations in a short test program.
3. Write a method that accepts a List<? extends Number> and computes the sum of its elements. Confirm it compiles for List<Integer>, List<Double>, and List<Long>.
4. Create an ArrayList<Integer> and a HashSet<Integer> with the same five elements, print both, and write one line explaining the difference in observed order.
5. Push all code to GitHub.
```
