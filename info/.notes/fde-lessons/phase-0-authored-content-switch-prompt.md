# Prompt for Local LLM — FDE Phase 0: Add authored-content override switch

Paste everything below this line into the local LLM as-is. This is an infrastructure change
only — it adds an empty, working mechanism. No lesson content is added in this step. If any
step below doesn't match what you find in the actual file, STOP and report the discrepancy
instead of guessing.

---

## 0. Why this change

`api/Data/JavaVerticalSeedData.cs` has a hand-authored content override:
`GetAuthoredLessonContent(string slug)` — a switch checked before the generic template
fallback, used to inject real per-lesson content for the Java/Spring LLD vertical.

`api/Data/FdeCurriculumSeedData.cs` has **no equivalent**. Every FDE lesson currently gets its
`ContentBody` from `BuildLessonContent(title, guide)` (core lessons) or
`BuildSupplementalLessonContent(lessonDefinition, definition)` (elective lessons) — both are
generic, title-keyword-driven template generators, not real authored content. This prompt adds
the same override mechanism Java already has, so later prompts can drop in real content
lesson-by-lesson without touching the generic fallback (which stays in place for any lesson
not yet authored).

---

## 1. Read this file in full first

`api/Data/FdeCurriculumSeedData.cs`

Confirm these exact locations exist before editing (report back if line numbers have drifted,
but proceed using the method/variable names, which are authoritative):

- Line ~301-303, inside `EnsureFdeCourse` (or the method containing the `foreach (var task in
  group.Group)` loop): a local variable `lessonSlug` is computed, then
  `var content = BuildLessonContent(task.Title, guide);`
- Line ~391-394, inside `EnsureSupplementalModules`: a local variable `lessonSlug` is computed
  inside the `for (var lessonIndex = 0; lessonIndex < definition.Lessons.Count; lessonIndex++)`
  loop, then `var content = BuildSupplementalLessonContent(lessonDefinition, definition);`
- A method `private static string BuildLessonDescription(string title, ModuleGuide guide)` —
  the new method should be added immediately before this one.

---

## 2. Add the new method

Add this new private static method to the `FdeCurriculumSeedData` class, immediately before
`private static string BuildLessonDescription(string title, ModuleGuide guide)`:

```csharp
    /// <summary>
    /// Hand-authored, high-quality content for specific FDE lesson slugs, checked before the
    /// generic template fallback (BuildLessonContent / BuildSupplementalLessonContent). Mirrors
    /// GetAuthoredLessonContent in JavaVerticalSeedData.cs. Add one case per authored lesson;
    /// leave every other lesson on the generic fallback until it is authored.
    /// </summary>
    private static string? GetAuthoredFdeLessonContent(string slug) => slug switch
    {
        _ => null
    };

```

Do not add any case to the switch in this step — it must contain only `_ => null`. Later
prompts will add one `"[lesson-slug]" => @"...",` case at a time, immediately before `_ =>
null`, exactly the way `JavaVerticalSeedData.cs`'s `GetAuthoredLessonContent` is extended.

---

## 3. Wire the override into both content call sites

### 3a. Core lessons (inside the loop that builds `content` from `BuildLessonContent`)

Find:
```csharp
                var content = BuildLessonContent(task.Title, guide);
```

Replace with:
```csharp
                var content = GetAuthoredFdeLessonContent(lessonSlug) ?? BuildLessonContent(task.Title, guide);
```

### 3b. Supplemental/elective lessons (inside `EnsureSupplementalModules`)

Find:
```csharp
                var content = BuildSupplementalLessonContent(lessonDefinition, definition);
```

Replace with:
```csharp
                var content = GetAuthoredFdeLessonContent(lessonSlug) ?? BuildSupplementalLessonContent(lessonDefinition, definition);
```

Both replacements rely on `lessonSlug` already being in scope at that point in each loop — do
not introduce a new variable name; use the existing `lessonSlug` local exactly as-is. If either
site's `content` line does not match verbatim (e.g. different variable name currently in use),
STOP and report the actual line instead of guessing.

---

## 4. What must NOT change

- Do not change `BuildLessonContent`, `BuildSupplementalLessonContent`,
  `BuildLessonDescription`, `ResolveTopicBrief`, `ResolveCoreConcepts`, `ResolveModuleGuide`,
  `ModuleGuides`, `SupplementalModules`, `Slugify`, or any other existing method.
- Do not change the "populate only empty scaffold fields" logic in the `else` branches (the
  `if (string.IsNullOrWhiteSpace(lesson.ContentBody)) lesson.ContentBody = content;` lines) —
  leave that exactly as it is. It already works correctly with the new override: on a fresh
  insert `content` is always used; on an update it only backfills empty content either way.
- Do not touch `JavaVerticalSeedData.cs`, `lessonInteractions.js`, or any other file.
- Do not add any authored lesson content in this step.

Match code style exactly: 4-space indent, existing brace style, `private static` ordering
consistent with the surrounding methods.

---

## 5. Output format

Output, clearly labeled:

### OUTPUT A: The new `GetAuthoredFdeLessonContent` method
Full method as it should appear in the file.

### OUTPUT B: The two modified lines
Show before/after for both 3a and 3b, with enough surrounding context (2-3 lines each side) to
locate them unambiguously.

### OUTPUT C: Confirmation
State that no other method was touched, and that the switch contains only `_ => null` (no
lesson cases added yet).

---

## 6. Operational note (for the human running this)

This step alone changes no visible lesson content — every lesson still falls through to
`_ => null` and gets the same generic template as before. It only prepares the mechanism.

After applying, restart the API:
```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

No database reset is needed for this step. Database resets (`UPDATE lessons SET
content_body = '', content_status = 'Outline' WHERE slug = '...'`) will be needed per lesson
slug starting from Phase 1, when actual authored cases are added — each phase's own prompt will
include the exact reset SQL for the lesson slugs it authors, since those lessons already have
non-empty `ContentBody` from the generic seeder run and the "only fill if empty" scaffold rule
will otherwise silently keep the old generic content.
