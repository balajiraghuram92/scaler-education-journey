# Prompt: Update lessonExerciseAssociations test for the new array shape

Paste everything below into the Local LLM verbatim.

---

## Context

`app/src/data/lessonExerciseAssociations.js` was intentionally changed so each lesson
maps to a **list** of exercise ids (`{ exerciseIds: [...] }`) instead of a single one
(`{ exerciseId: '...' }`), because several lessons now have multiple exercises
attached. `app/src/__tests__/data/lessonExerciseAssociations.test.js` was not updated
to match, and now fails with:

```
AssertionError: expected { Object (exerciseIds) } to deeply equal { Object (exerciseId) }
```

on 3 of its 4 tests.

## The fix

File: `app/src/__tests__/data/lessonExerciseAssociations.test.js`

Replace the entire file contents with:

```js
import { describe, expect, it } from 'vitest';
import { getLessonExerciseAssociation } from '../../data/lessonExerciseAssociations';

describe('lesson exercise associations', () => {
  it('associates the intro to lld lesson with the trip state management exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '01-intro-to-lld'
    )).toEqual({ exerciseIds: ['java-lld-oop1-trip-state-management'] });
  });

  it('associates the oop 1 lab lesson with the rider entity exercise', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '02-oop-1-intro-lab'
    )).toEqual({ exerciseIds: ['java-lld-oop2-rider-entity'] });
  });

  it('associates the polymorphism lesson with all three attached exercises', () => {
    expect(getLessonExerciseAssociation(
      'java-spring-lld',
      'oop-foundations',
      '04-oop-3-polymorphism-interfaces'
    )).toEqual({
      exerciseIds: [
        'java-lld-media-file-player',
        'java-lld-oop3-point-threedpoint',
        'java-lld-vehicle-renting'
      ]
    });
  });

  it('does not associate unrelated lessons', () => {
    expect(getLessonExerciseAssociation('java-spring-lld', 'oop-foundations', 'other-lesson')).toBeNull();
  });
});
```

Only two things changed from the original: the expected object shape (`exerciseIds`
array instead of `exerciseId` string) in the first three tests, the array now
containing all three exercises actually registered for the polymorphism lesson (not
just one), and that third test's description was reworded to say "all three attached
exercises" instead of "the canonical exercise" since it now checks more than one. The
fourth test (`does not associate unrelated lessons`) is completely unchanged.

Do not touch any other file.

## Verification

```bash
cd app && npm run test
```

Expect `4 passed (4)` in `lessonExerciseAssociations.test.js`, and the full suite
back to all green (previously: `3 failed | 31 passed (34)`).
