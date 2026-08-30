# Prompt for Local LLM — Fix 3 Duplicate Self-Check Questions

Paste everything below this line into the local LLM as-is. This is a small, precise
correction to `api/Data/JavaVerticalSeedData.cs` fixing 3 duplicate MCQs that were
introduced by mistake in the previous round. Do not touch anything else in the file.

---

## Bug: 3 duplicate MCQs across the lesson content

An earlier edit accidentally added the same question twice in two places, and the same
question across two different lessons. Fix all three as follows.

### Fix 1 — Lesson 9 (`09-concurrency-4-semaphores`)

Find the existing **Q4** in this lesson's `## Self-Check (From Class Material)` section —
it currently reads "Which of the following methods in a Semaphore is a blocking method?"
This is a verbatim duplicate of this same lesson's own **Q2**. Replace Q4's entire content
(question, options, answer, and citation) with:

```
**Q4.** Consider the following two statements:
a. If the value of a Semaphore is greater than 0, `acquire()` reduces the permit count by 1 but allows the thread to enter the critical section.
b. If the value of a Semaphore is 0, `acquire()` blocks the thread.
Which of the following is true?
- A. Only a is true
- B. Only b is true
- C. Both a and b are true
- D. Both a and b are false

**Answer: C** — Both statements correctly describe `acquire()`'s behavior: when permits
remain, it decrements the count and lets the thread proceed immediately; when the permit
count has reached zero, it blocks the calling thread until another thread calls
`release()`.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/78-88.md, MCQ 1; answer determined from source material, not marked in original)*
```

### Fix 2 — Lesson 10 (`10-java-adv-1-generics`)

Find the existing **Q4** in this lesson's `## Self-Check (From Class Material)` section —
it currently reads "When is it appropriate to use wildcards with an upper bound in Java
generics?" This is a verbatim duplicate of this same lesson's own **Q3**. Replace Q4's
entire content with:

```
**Q4.** Suppose you are writing a generic method to return the first element of a list.
What is the correct method declaration?
- A. `public static <T> T getFirstElement(List<T> list)`
- B. `public static T getFirstElement(List<T> list)`
- C. `public static void getFirstElement(List<T> list)`
- D. `public static <T> void getFirstElement(List<T> list)`

**Answer: A** — A generic static method must declare its own type parameter `<T>`
immediately before the return type, since static members have no access to a class-level
type parameter. The return type must also be `T`, not `void`, since the method returns the
first element.
*(SOURCE_TYPE: FROM_MATERIAL — mcqs/45-55.md, MCQ 49; answer determined from source material, not marked in original)*
```

### Fix 3 — Lesson 13 (`13-java-adv-4-streams-exceptions`)

Find the existing **Q4** in this lesson's `## Self-Check (From Class Material)` section —
it currently reads "What is the output of the following code?" with the `IntFunction`
square/`BinaryOperator` addition/`Function` increment example. This is a verbatim duplicate
of Lesson 12's own **Q1**. There is no other unused, clean Streams/Lambdas MCQ left in the
source bank to replace it with (the remaining ones in that topic are either already used
elsewhere or are coding-challenge stubs with no real answer options).

**Delete this Q4 entirely** (question, options, answer, and citation — all of it), and
renumber the current **Q5** ("Which of the following is NOT a way of creating a stream?")
to **Q4** in its place. After this fix, Lesson 13 will have exactly 4 self-check questions
(Q1, Q2, Q3, Q4), not 5 — this is correct and expected.

---

## What must NOT change

- Do not touch any other content in any lesson.
- Do not change Q1–Q3 in any of the three lessons.
- Every replacement block above already uses correct C# verbatim-string escaping — copy it
  exactly as given.

## Output format

Output the complete, updated `GetAuthoredLessonContent` method body, ready to paste over
the existing method in `api/Data/JavaVerticalSeedData.cs`.

After the code block, confirm:
- Lesson 9's Q4 no longer duplicates its Q2.
- Lesson 10's Q4 no longer duplicates its Q3.
- Lesson 13 now has exactly 4 self-check questions, with the old Q5 renumbered to Q4, and
  no question in Lesson 13 duplicates any question in Lesson 12.

## Self-check before you output

1. Search the entire 10-lesson block for the exact string "Which of the following methods
   in a Semaphore is a blocking method?" — it must appear exactly once (in Lesson 9's Q2),
   not twice.
2. Search for "When is it appropriate to use wildcards with an upper bound" — it must
   appear exactly once (in Lesson 10's Q3), not twice.
3. Search for "IntFunction<Integer> square" — it must appear exactly once (in Lesson 12),
   not in Lesson 13 anymore.
4. Lesson 13 has exactly 4 self-check questions numbered Q1–Q4 with no gap.

## Operational note (same as before)

If you haven't already reset these lessons in the database since the last content change,
run this before restarting the API:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN ('09-concurrency-4-semaphores', '10-java-adv-1-generics', '13-java-adv-4-streams-exceptions');
```
