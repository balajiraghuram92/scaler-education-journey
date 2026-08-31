# Prompt for Local LLM — Fix pre-answered concept check in Java LLD Lesson 4

Paste everything below this line into the local LLM as-is. This is a small, surgical bugfix —
no new content is being authored, just removing two banned fields from one existing object.

---

## 1. What's wrong

In `app/src/data/lessonInteractions.js`, the entry for key
`'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces'` has a `conceptChecks` array
containing exactly one object (`id: 'lesson-4-concept-check-01'`). That object has two fields
that must never appear on a concept check in this codebase:

```js
initialSelectedOption: 'b',
initialSubmitted: true
```

These make the question render as already answered (option B pre-selected, already submitted)
the moment the lesson page loads, instead of waiting for the learner to actually answer it. This
is a known-banned pattern in this codebase — no other concept check anywhere in the file has
these fields, and they should not exist here either.

## 2. The fix

Find the object with `id: 'lesson-4-concept-check-01'` inside the `conceptChecks` array for
`'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces'`. Delete exactly these two
lines from it:

```js
        initialSelectedOption: 'b',
        initialSubmitted: true
```

The object's last real field before this deletion is `hint: 'PaymentService → capability contract
→ provider adapters',` — after deleting the two banned lines, that `hint` line must be the last
property in the object (no trailing comma after it), immediately followed by the closing `}` of
the object and `]` of the `conceptChecks` array.

Do not change `id`, `eyebrow`, `question`, `options`, `correctOptionId`, `explanation`,
`incorrectExplanation`, or `hint` — only remove the two banned lines.

## 3. A second issue to flag, not fix in this prompt

This lesson's `conceptChecks` array has only 1 entry. Every other lesson in this file (both the
`java-spring-lld/...` and `fde-curriculum/...` entries) has exactly 2. This may be intentional
(an old lesson authored before the "exactly 2" convention was established) or it may be a real
gap. **Do not add a second concept check in this prompt** — that would require authoring new
lesson-accurate content, which is out of scope here. Just note in your output whether you see
any indication (a comment, a TODO, adjacent code) of why this lesson only has one, so a human can
decide whether to author a second one separately.

## 4. Constraints

Do NOT touch:
- Any other key in `lessonInteractions.js` — this includes every other `java-spring-lld/...` key
  and every `fde-curriculum/...` key
- The `architecture` object that follows this lesson's `conceptChecks` array (leave it exactly
  as-is)
- Any `.cs` file
- Any other `.js` file

## 5. Output format

Show a small before/after diff of just the affected object (a few lines of context on each side
is enough — do not print the whole file). Confirm no trailing comma was left after `hint`, and
report your finding from Section 3 above.

## 6. Operational note

This is a pure frontend data change — no database reset or content-status change is needed. After
applying, restart the frontend dev server if it doesn't hot-reload automatically, and verify by
opening the Java LLD "Polymorphism & Interfaces" lesson page (module `oop-foundations`, lesson
`04-oop-3-polymorphism-interfaces`) and confirming concept check 01 shows as unanswered on a
fresh page load, not pre-filled with option B already selected and submitted.
