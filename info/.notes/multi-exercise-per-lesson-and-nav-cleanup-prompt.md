# Prompt: Support multiple exercises per lesson + drop the redundant Chapters nav link

Paste everything below into the Local LLM verbatim.

---

You are editing a React app. Make exactly three changes, described below with exact
before/after content. Do not touch any other file, and do not change anything else in
the files you do touch beyond what's specified.

## Background

`app/src/data/lessonExerciseAssociations.js` maps `courseSlug/moduleSlug/lessonSlug` to
a coding exercise shown on that lesson's page. It currently only supports **one**
exercise per lesson (`{ exerciseId: '...' }`), and only has 4 lessons registered. Many
lessons now have multiple exercises attached (e.g. 13 for Creational Patterns), so the
data shape and the rendering code both need to support a list.

## File 1: `app/src/data/lessonExerciseAssociations.js`

Replace the entire file contents with:

```js
const lessonExerciseAssociations = {
  'java-spring-lld/oop-foundations/01-intro-to-lld': {
    exerciseIds: [
      'java-lld-oop1-trip-state-management'
    ]
  },
  'java-spring-lld/oop-foundations/02-oop-1-intro-lab': {
    exerciseIds: [
      'java-lld-oop2-rider-entity'
    ]
  },
  'java-spring-lld/oop-foundations/03-oop-2-access-modifiers-encapsulation': {
    exerciseIds: [
      'java-lld-oop2-point-rectangle',
      'java-lld-shape-hierarchy'
    ]
  },
  'java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces': {
    exerciseIds: [
      'java-lld-media-file-player',
      'java-lld-oop3-point-threedpoint',
      'java-lld-vehicle-renting'
    ]
  },
  'java-spring-lld/oop-foundations/05-oop-4-lms-lab': {
    exerciseIds: [
      'java-lld-scaler-learning-platform-users'
    ]
  },
  'java-spring-lld/concurrency-multithreading/06-concurrency-1-threads': {
    exerciseIds: [
      'java-lld-big-factorial-thread',
      'java-lld-thread-basics-adder-subtractor'
    ]
  },
  'java-spring-lld/concurrency-multithreading/07-concurrency-2-executors': {
    exerciseIds: [
      'java-lld-image-painter-executors'
    ]
  },
  'java-spring-lld/concurrency-multithreading/08-concurrency-3-synchronization': {
    exerciseIds: [
      'java-lld-movie-ticket-reservation',
      'java-lld-synchronized-counter',
      'java-lld-train-reservation-per-class-locks'
    ]
  },
  'java-spring-lld/advanced-java-collections/10-java-adv-1-generics': {
    exerciseIds: [
      'java-lld-bounded-generics-find-max',
      'java-lld-generic-comparison',
      'java-lld-generic-linked-list',
      'java-lld-generic-pair',
      'java-lld-generic-print-array'
    ]
  },
  'java-spring-lld/advanced-java-collections/11-java-adv-2-collections-lab': {
    exerciseIds: [
      'java-lld-frequency-counter',
      'java-lld-group-anagrams',
      'java-lld-unique-persons'
    ]
  },
  'java-spring-lld/advanced-java-collections/12-java-adv-3-lambdas-streams': {
    exerciseIds: [
      'java-lld-count-unique-words',
      'java-lld-distinct-numbers',
      'java-lld-filter-fruits',
      'java-lld-process-sentences',
      'java-lld-sort-animals-by-length',
      'java-lld-student-sorter'
    ]
  },
  'java-spring-lld/design-principles-patterns/14-solid-principles': {
    exerciseIds: [
      'java-lld-cloud-provider-adapter-integration'
    ]
  },
  'java-spring-lld/design-principles-patterns/15-creational-patterns': {
    exerciseIds: [
      'java-lld-abstract-factory-audio',
      'java-lld-abstract-factory-document-processing',
      'java-lld-abstract-factory-notifications',
      'java-lld-builder-database-configuration',
      'java-lld-builder-message',
      'java-lld-builder-query',
      'java-lld-factory-board-game',
      'java-lld-factory-database-connection',
      'java-lld-factory-document',
      'java-lld-prototype-configuration',
      'java-lld-prototype-invoice',
      'java-lld-prototype-user',
      'java-lld-singleton-file-config'
    ]
  },
  'java-spring-lld/design-principles-patterns/16-structural-patterns': {
    exerciseIds: [
      'java-lld-adapter-insurance',
      'java-lld-adapter-social-media',
      'java-lld-adapter-translation',
      'java-lld-decorator-api',
      'java-lld-decorator-file-storage',
      'java-lld-decorator-image',
      'java-lld-facade-booking',
      'java-lld-facade-data-analysis',
      'java-lld-facade-image-editing',
      'java-lld-flyweight-chess-user',
      'java-lld-flyweight-graphics'
    ]
  },
  'java-spring-lld/design-principles-patterns/17-behavioural-patterns-uml': {
    exerciseIds: [
      'java-lld-observer-stock-price-alerts',
      'java-lld-observer-task-assignment',
      'java-lld-observer-weather-monitoring',
      'java-lld-strategy-pricing',
      'java-lld-strategy-stock-trading',
      'java-lld-strategy-video-streaming'
    ]
  },
  'java-spring-lld/applied-machine-coding/19-machine-coding-tictactoe': {
    exerciseIds: [
      'java-lld-tictactoe-undo-and-win-check',
      'java-lld-tictactoe-win-check'
    ]
  },
  'java-spring-lld/applied-machine-coding/24-machine-coding-hotel-management': {
    exerciseIds: [
      'java-lld-hotel-add-rooms',
      'java-lld-hotel-book-rooms',
      'java-lld-hotel-generate-invoice',
      'java-lld-hotel-get-rooms'
    ]
  }
};

export function getLessonExerciseAssociation(courseSlug, moduleSlug, lessonSlug) {
  return lessonExerciseAssociations[`${courseSlug}/${moduleSlug}/${lessonSlug}`] || null;
}

export default lessonExerciseAssociations;
```

(`getLessonExerciseAssociation`'s signature and behavior are unchanged — same three
arguments, same lookup key format, still returns `null` for an unregistered lesson. Only
the shape of what it returns changed: `exerciseIds` array instead of a single
`exerciseId` string.)

## File 2: `app/src/pages/ChapterReader.jsx`

This file currently renders exactly one `<ImplementationExercise>` per lesson, tracked
by a single boolean (`isExerciseExpanded`). Change it to render one
`<ImplementationExercise>` per entry in `exerciseIds`, tracking which ones are expanded
in a `Set`.

### 2a. `ChapterMarkdown` — accept a list and render one widget per id

Find:
```jsx
function ChapterMarkdown({ sections, interactions, exerciseId, isExerciseExpanded, onToggleExerciseExpanded }) {
```
Replace with:
```jsx
function ChapterMarkdown({ sections, interactions, exerciseIds, expandedExerciseIds, onToggleExerciseExpanded }) {
```

Find:
```jsx
      {section.id === 'practice-loop' && exerciseId && (
        <ImplementationExercise
          key={exerciseId}
          exerciseId={exerciseId}
          isExpanded={isExerciseExpanded}
          onToggleExpand={onToggleExerciseExpanded}
        />
      )}
```
Replace with:
```jsx
      {section.id === 'practice-loop' && exerciseIds?.map((exerciseId) => (
        <ImplementationExercise
          key={exerciseId}
          exerciseId={exerciseId}
          isExpanded={expandedExerciseIds.has(exerciseId)}
          onToggleExpand={() => onToggleExerciseExpanded(exerciseId)}
        />
      ))}
```

### 2b. Replace the boolean state with a Set of expanded exercise ids

Find:
```jsx
  const [isExerciseExpanded, setIsExerciseExpanded] = useState(false);
```
Replace with:
```jsx
  const [expandedExerciseIds, setExpandedExerciseIds] = useState(() => new Set());
```

Find (inside `fetchChapter`, resetting state on lesson change):
```jsx
    setIsExerciseExpanded(false);
```
Replace with:
```jsx
    setExpandedExerciseIds(new Set());
```

Find (the page-level CSS class toggle that widens the layout while an exercise editor
is open — now true when *any* exercise is expanded):
```jsx
    <div className={`chapter-reader-page${isExerciseExpanded ? ' chapter-reader-page--exercise-expanded' : ''}`}>
```
Replace with:
```jsx
    <div className={`chapter-reader-page${expandedExerciseIds.size > 0 ? ' chapter-reader-page--exercise-expanded' : ''}`}>
```

### 2c. Update the `<ChapterMarkdown>` call site

Find:
```jsx
          <ChapterMarkdown
            sections={contentSections}
            interactions={lessonInteractions}
            exerciseId={lessonExercise?.exerciseId}
            isExerciseExpanded={isExerciseExpanded}
            onToggleExerciseExpanded={() => setIsExerciseExpanded((current) => !current)}
          />
```
Replace with:
```jsx
          <ChapterMarkdown
            sections={contentSections}
            interactions={lessonInteractions}
            exerciseIds={lessonExercise?.exerciseIds}
            expandedExerciseIds={expandedExerciseIds}
            onToggleExerciseExpanded={(exerciseId) => setExpandedExerciseIds((current) => {
              const next = new Set(current);
              if (next.has(exerciseId)) {
                next.delete(exerciseId);
              } else {
                next.add(exerciseId);
              }
              return next;
            })}
          />
```

Nothing else in `ChapterReader.jsx` changes — `getLessonExerciseAssociation(...)` is
still called the same way (three arguments), it just now returns `{ exerciseIds: [...] }`
instead of `{ exerciseId: '...' }`, which is exactly what the changes above account for.

## File 3: `app/src/components/Navbar.jsx` — drop the Chapters link entirely

Chapters is now the default/home page (root `/` redirects to `/chapters`), so a nav
link to it is redundant — same reasoning as most sites not linking "Home" from their
own home page. Remove the link entirely; the brand logo (already linking to `/`) is
the way back.

Find:
```jsx
          {/* Center: Navigation Links */}
          <div className="navbar-section navbar-center">
            <Link
              to="/chapters"
              className={`navbar-nav-link ${location.pathname.startsWith('/chapters') || location.pathname.startsWith('/chapter') || location.pathname.startsWith('/learning-paths') ? 'active' : ''}`}
            >
              Chapters
            </Link>
          </div>

```
Delete this whole block (including the blank line after it). The center nav section is
now empty, so remove it entirely rather than leaving an empty `<div>`.

After this change, `useLocation()` (`const location = useLocation();` near the top of
the component) is no longer used anywhere in the file — remove that line and the
`useLocation` import too:

Find:
```jsx
import { Link, useLocation } from 'react-router-dom';
```
Replace with:
```jsx
import { Link } from 'react-router-dom';
```

Find:
```jsx
export default function Navbar() {
  const location = useLocation();

  return (
```
Replace with:
```jsx
export default function Navbar() {
  return (
```

Nothing else in `Navbar.jsx` changes — the brand logo section and the profile section
on the right stay exactly as they are.

## Output expected

The full, updated contents of:
- `app/src/data/lessonExerciseAssociations.js`
- `app/src/pages/ChapterReader.jsx`
- `app/src/components/Navbar.jsx`

## Verification

- Run `npm run lint` and `npm run build` inside `app/` — should be clean (no unused
  `useLocation` import, no unused `location` variable, no lint errors).
- Visit a lesson with multiple exercises, e.g. the Creational Patterns lesson
  (`/chapter/java-spring-lld/design-principles-patterns/15-creational-patterns`) — all
  13 exercise widgets should render, each independently expandable/collapsible.
- Visit a lesson with one exercise (e.g. Lesson 1) — behavior is unchanged, one widget
  renders.
- The nav bar should now show only the brand logo (left) and the profile pill (right) —
  no center links at all.
