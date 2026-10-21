# UML Diagrams for Design Interviews

In a low-level design round, the first artefact you produce is rarely code; it is a sketch on a whiteboard or a shared document. A clean class diagram with correct relationships and multiplicities shows the interviewer that you can model a domain, and a short sequence diagram shows that you understand who calls whom and when. The goal is not UML ceremony. It is a small, correct, fast picture that you can code from and defend, and that you can later translate into tables.

## Concepts Covered

### What UML is for, and the two families

UML is a shared visual vocabulary with two families: **structural** diagrams (what exists: class diagrams, and by extension schema design) and **behavioural** diagrams (what happens over time: sequence and use-case diagrams). A use-case diagram only scopes actors and features; its two relationships are **includes**, a mandatory sub-step (withdrawing cash always includes verifying the PIN), and **extends**, an optional addition (printing a receipt).

### Anatomy of a class box

A class is a rectangle with name, attribute and operation compartments. Visibility markers are `+` public, `-` private and `#` protected; in Python `-` means the leading-underscore convention. Interfaces carry a stereotype such as `<<interface>>`. List only the members that carry the design.

```text
+--------------------------+
| <<interface>>            |
| Embedder                 |
|--------------------------|
| +embed(text) list[float] |
+--------------------------+

+--------------------------+
| Index                    |
|--------------------------|
| -rows: list              |
| -embedder: Embedder      |
|--------------------------|
| +add(doc: Document)      |
+--------------------------+
```

### The relationships, in one table

```text
Parent    <|--  Child        inheritance (generalisation): solid line, hollow triangle
Interface <|..  Impl         realization: dashed line, hollow triangle
A         -->   B            association: solid line with open arrow
Whole     o--   Part         aggregation: hollow diamond at the whole
Whole     *--   Part         composition: filled diamond at the whole
A         ..>   B            dependency: dashed line with open arrow
```

| Relationship | Meaning | Python shape |
|---|---|---|
| Inheritance | Child **is a** Parent | `class Child(Parent)` |
| Realization | Impl implements an interface | Implements a `Protocol` or ABC |
| Association | A holds a long-lived reference to B | `self._b = b` |
| Aggregation | Whole/part, but the part has an independent life | Part is injected and shared |
| Composition | Whole/part, the part cannot outlive the whole | Part is created and owned inside the whole |
| Dependency | A merely uses B (parameter, local, return) | Appears in a method signature or body only |

The decisive test for aggregation versus composition is a lifecycle question: **if the container is deleted, does the part still make sense elsewhere in the system?** A playlist deleted, the songs survive: aggregation. A notebook destroyed, its pages go with it: composition. The distinction is a domain judgement, not a syntax fact, so say your assumption out loud. Menu items meaningless outside their restaurant are composition; doctors who outlive a dissolved department are aggregation. If a class only receives another class as a method argument, draw a dependency, not an association.

### Multiplicity

Put multiplicities at both ends: `1`, `0..1`, `0..*`, `1..*`. They become your collection types and foreign keys: a `Trip` with `1 *-- 0..*` `RouteCoordinate` is a list inside `Trip` and a table with a `trip_id` column.

### From diagram to Python

Here is a small RAG indexing slice, using all five relationships. The diagram first:

```text
Embedder  <|..  LengthEmbedder          realization
Index     o--   Embedder                aggregation: embedder is injected and shared
SearchService --> Index                 association: long-lived reference
Document  "1" *-- "0..*" Chunk         composition: chunks die with the document
Index     ..>   Document                dependency: used only as a parameter
```

Then the code, where every line of the diagram is visible in how the objects are created and passed:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


class Embedder(Protocol):                       # <<interface>>
    def embed(self, text: str) -> list[float]: ...


class LengthEmbedder:                           # realization: implements Embedder
    def embed(self, text: str) -> list[float]:
        return [float(len(text))]


@dataclass(frozen=True)
class Chunk:
    text: str


class Document:
    def __init__(self, doc_id: str, texts: list[str]) -> None:
        self.doc_id = doc_id
        self.chunks = [Chunk(t) for t in texts]      # composition: created and owned here


class Index:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder                    # aggregation: injected, can outlive this Index
        self._rows: list[tuple[str, list[float]]] = []

    def add(self, doc: Document) -> None:            # dependency on Document: parameter only
        for ch in doc.chunks:
            self._rows.append((doc.doc_id, self._embedder.embed(ch.text)))

    def __len__(self) -> int:
        return len(self._rows)


class SearchService:
    def __init__(self, index: Index) -> None:
        self._index = index                          # association: long-lived reference

    def ingest(self, doc: Document) -> int:
        self._index.add(doc)
        return len(self._index)


shared = LengthEmbedder()
svc = SearchService(Index(shared))
print(svc.ingest(Document("d1", ["alpha", "beta gamma"])))
print(shared.embed("x"))                             # the embedder outlives the index
```

```text
2
[1.0]
```

The tell for composition in code is construction inside the owner (`Chunk(t)` in `Document.__init__`); the tell for aggregation is injection through a constructor parameter.

### From class diagram to schema

A class diagram with multiplicities translates mechanically into tables. Every table gets a primary key; in a one-to-many relationship the **foreign key lives on the many side**; a many-to-many relationship needs a **junction table** holding both foreign keys (the pair can be a **composite primary key**). Normalisation stores each fact once and references it by key, so copies cannot drift. Columns `comment_1`, `comment_2`, `comment_3` cap a one-to-many relationship at three; use a `comments` table with a `post_id`.

```sql
CREATE TABLE instructors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    instructor_id INTEGER NOT NULL REFERENCES instructors(id)   -- FK on the many side
);
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE enrollments (                                      -- junction table
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id  INTEGER NOT NULL REFERENCES courses(id),
    enrolled_on TEXT NOT NULL,
    PRIMARY KEY (student_id, course_id)                         -- composite key, no duplicates
);

-- with rows (1,1),(1,2),(2,1) in enrollments:
SELECT COUNT(*) FROM enrollments WHERE student_id = 1;          -- 2
```

Against SQLite, that data gives `2`, and inserting a duplicate `(1, 1)` raises `UNIQUE constraint failed`, which is what the composite key buys you. Composition maps to a foreign key with `ON DELETE CASCADE`; aggregation to a plain, often nullable, foreign key.

### Sequence diagrams: behaviour over time

A sequence diagram has participants across the top, a dashed lifeline under each, and arrows for messages in time order from top to bottom: solid for calls, dashed for returns. Fragments such as `alt` (if/else), `opt` and `loop` wrap groups of messages. Use one when the question is "who talks to whom, in what order, and where can it fail?", as in an AI request path with a cache.

```text
Client       API        Cache      Retriever      LLM
  |  ask(q)   |           |            |           |
  |---------->|  get(q)   |            |           |
  |           |---------->|            |           |
  |           |  miss     |            |           |
  |           |<- - - - - |            |           |
  |           |  search(q)             |           |
  |           |----------------------->|           |
  |           |  chunks                |           |
  |           |<- - - - - - - - - - - -|           |
  |           |  generate(q, chunks)               |
  |           |----------------------------------->|
  |           |  answer                            |
  |           |<- - - - - - - - - - - - - - - - - -|
  |           |  put(q, answer)                    |
  |           |---------->|            |           |
  |  answer   |           |            |           |
  |<- - - - - |           |            |           |
```

On a cache hit, the diagram would have an `alt` fragment: if `get(q)` returns an answer, return immediately and skip the retriever and the model entirely. Drawing that branch shows you thought about the cheap path.

### How to sketch fast in an interview

1. **Nouns first:** list candidate classes; discard those that are only attributes.
2. **Boxes with names only**, then the two or three members that carry the design.
3. **Relationships with multiplicities**, asking the lifecycle question for each whole/part pair and saying your assumption.
4. **Mark interfaces and extension points**, where a new provider or rule would plug in.
5. **One sequence diagram** for the main flow, then one failure branch.
6. **Stop when the code is obvious.**

> **Interview tip:** Narrate while you draw: "A Trip has many route coordinates and they mean nothing without the trip, so that is composition, one to many." The reasoning is the signal; the arrowheads are only notation.

> **Pitfall:** Drawing everything as a plain association. If every line is the same, the diagram carries no information about ownership, lifecycle or substitutability.

## Practical Backend Scenario

An interviewer says: "Design the backend for a RAG-based support assistant that answers from company documents and supports multiple LLM providers." A weak answer starts typing classes. A strong answer sketches in five minutes: a `ChatModel` interface realised by provider adapters; `Document` composed of `Chunk`s; an `Index` holding an injected `Embedder`; an `AnswerService` associated with the index and the model; a `Conversation` composing `0..*` `Message`s. Then one sequence diagram for "ask" with the cache-hit branch. Code, tables and tests fall out of that picture, and follow-ups ("how do I add a provider?", "what if the document is deleted?") each have a place on it.

## Practice Loop

1. Take the RAG example above and redraw the class diagram from memory in text notation. Check every relationship against the code.
2. For each pair, decide composition or aggregation and write the lifecycle sentence that justifies it: playlist and songs, car and engine, department and doctors, canvas and shapes, user and posts.
3. Write the schema for `Course`, `Student`, `Instructor` and `Enrollment`. Add `enrolled_on` to the junction table and explain why it cannot live on either side.
4. Convert the `comment_1..3` schema into a proper one-to-many design and write the `SELECT` that lists a post with its comments.
5. Draw a sequence diagram for "ask a question" with an `alt` fragment for the cache hit, and a second diagram where the LLM call times out and a fallback model is used.
6. Time yourself: sketch classes plus one sequence for a ride-hailing booking in ten minutes, then code the skeleton from the sketch alone.

## Evidence of Understanding

- I can name the six relationships, draw each in text notation, and give the Python shape of each.
- I can decide between aggregation and composition with the lifecycle test, and say the assumption aloud.
- I can read and write multiplicities and turn them into collection types and foreign keys.
- I can place a foreign key correctly and justify a junction table with a composite primary key.
- I can sketch a sequence diagram with a branch for the cheap path and a failure.
- I can complete a useful class sketch in a few minutes and stop at the right point.

## Interview Questions to Rehearse

### Q: What is the difference between aggregation and composition?

Both are whole/part associations. In composition the part's lifetime is bound to the whole, which creates and owns it. In aggregation the part is independent and may be shared, so it is injected and outlives the container. It is a domain judgement, so I state my assumption: playlist and songs is aggregation, notebook and pages is composition.

### Q: How does a class diagram become a database schema?

Each entity becomes a table with a primary key. One-to-many puts the foreign key on the many side; many-to-many gets a junction table holding both keys plus any relationship attributes. Composition suggests a cascading delete, aggregation a plain or nullable reference. I normalise so each fact is stored once.

### Q: When do you use a sequence diagram instead of a class diagram?

When the question is about order, responsibility and failure across collaborators: who calls whom, what comes back, and where branches or timeouts occur. A class diagram shows structure that is always true; a sequence diagram shows one scenario over time.

### Q: What is the difference between association and dependency?

Association is a lasting structural link, usually a field holding a reference. Dependency is transient use: a parameter, local variable or return type. Drawing a dependency as an association overstates coupling.

## Common Pitfalls

- Using only plain lines, so ownership and lifecycle information is missing.
- Drawing aggregation where the part clearly cannot exist alone, or composition for shared objects.
- Omitting multiplicities, then guessing at foreign keys later.
- Placing the foreign key on the one side of a one-to-many relationship.
- Skipping the junction table by comma-separating IDs or adding numbered columns.
- Overdrawing every attribute, or showing only the happy path in the sequence diagram.

## Suggested Extension

Pick a system you have built (the localisation API or a chatbot) and draw, from the code, its class diagram with correct relationships and multiplicities, then a sequence diagram for its main request. Compare the diagram with what you remember designing: note any relationship you drew as aggregation that the code actually implements as composition, and what that implies about object lifetimes and deletion behaviour.
