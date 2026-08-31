# Prompt: Redesign the lesson list on LearningPathDetail as a card grid

Paste everything below into the Local LLM verbatim. Read the whole prompt before
making any change.

---

## Strict rules — read first

- Touch **exactly one file**: `app/src/pages/LearningPath/LearningPathDetail.jsx`.
  Do not create any new file, do not create a new `.css` file, do not add any import,
  do not add any npm package. This component already uses inline `style={{...}}`
  objects for everything (no CSS classes) — keep using that exact same convention for
  anything new; do not introduce CSS classes or a stylesheet.
- Do not change anything outside the one block identified below — not the imports,
  not the state/fetch logic, not the breadcrumb, not the hero card with the overall
  progress percentage. Leave all of that character-for-character identical.
- Do not rename, add, or remove any data field. The lesson/module objects only have
  the fields already used in the code below (`module.id`, `module.slug`,
  `module.title`, `module.lessons`, `lesson.id`, `lesson.slug`, `lesson.title`,
  `lesson.isCompleted`, `lesson.estimatedMinutes`, `lesson.difficulty`,
  `lesson.contentStatus`) and `path.slug`. Do not invent new fields (no
  `lesson.description`, no `lesson.icon`, nothing not in this list) — none of that
  data exists in the API response and referencing it will silently render `undefined`.
- **Before editing**: open the file and confirm the block below, under "Find this
  exact block", is present verbatim (whitespace can differ slightly, but the JSX
  structure, prop names, and field references must match). If it does not match —
  if the file has already been edited, or looks structurally different from what's
  quoted here — STOP and report exactly what's different instead of guessing or
  improvising a replacement. Do not proceed on a best-effort basis.

## Context

This page is `LearningPathDetail`, mounted at the route `/chapters/:slug`. It is a
**single shared component used for every vertical/course** — the `slug` is a route
parameter, and the component fetches whatever course that slug resolves to via
`api.v2.getLearningPath(slug)`. It contains no course-specific logic anywhere (no
`if (slug === 'java-spring-lld')` branching, nothing hardcoded to one course), and the
backend's response shape (module/lesson fields) is identical for every course. So this
one change automatically applies to **all** of the following URLs — do not scope the
change to just one of them, and do not add any per-course special-casing:

- `/chapters/java-spring-lld`
- `/chapters/fde-curriculum`
- `/chapters/databases-sql`
- `/chapters/high-level-design`
- `/chapters/data-engineering`

(and any other course slug added later — the whole point of editing this one shared
component is that it covers every current and future vertical without per-course
changes).

This page currently renders each
look like the card-grid style already used on `/chapters` (`ChaptersIndex.jsx` /
`ChaptersIndex.css` — you do not need to open that file, it's just context for why
this direction was chosen), but with smaller cards so ~5-6 fit per row on a desktop
screen, since there are far more lessons than there are courses.

Requirements for the new design, all of which are already fully written out in the
"Replace with" block below — you do not need to invent any of this, just transcribe it
exactly:

1. Keep the per-module grouping and the module header row exactly as before (Module
   N, module title, on the right side of the header).
2. Change the header's right-side text from `"{count} Lessons"` to
   `"{completedCount} of {totalCount} lessons completed"` — computed from
   `module.lessons` by filtering `lesson.isCompleted`.
3. Replace the vertical divided-row list of lessons with a CSS grid:
   `display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))'`.
4. Each lesson becomes one grid cell: the **entire cell is the `<Link>`** to
   `` `/chapter/${path.slug}/${module.slug}/${lesson.slug}` `` (same URL pattern
   already used) — there is no separate "Read" button anymore, remove it.
5. Each lesson card keeps the same small completion badge (checkbox-style square,
   filled sage green with a ✓ when `lesson.isCompleted`, otherwise an empty
   outlined square) — same colors/sizing as today, just reused inside the card.
6. Each card shows the lesson title, clamped to 2 lines with an ellipsis
   (`WebkitLineClamp: 2` etc., exactly as written below), and the same meta line
   (estimated minutes, difficulty, and the content-status flag when not
   `'Published'`) as today, just restyled smaller to fit the card.
7. Within each module, find the **first lesson where `isCompleted` is false** — that
   is "the next lesson to continue." Give that one card's grid cell a highlighted
   border (`2px solid var(--color-sage, #2C5E55)`) and a small "Continue" badge in
   its top-right corner. If every lesson in the module is already completed, no card
   in that module gets this treatment (there is no "next" one).

## The change

### Find this exact block:

```jsx
      {/* Modules & Lessons List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {path.modules?.map((module, idx) => (
          <div key={module.id} style={{
            backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
            border: '1px solid var(--color-border-subtle, #E2DDD5)',
            borderRadius: '10px',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '1.25rem 1.5rem',
              backgroundColor: 'rgba(0,0,0,0.015)',
              borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>
                  Module {idx + 1}
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: 'var(--color-ink, #1F2937)' }}>
                  {module.title}
                </h3>
              </div>
              <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                {module.lessons?.length || 0} Lessons
              </span>
            </div>

            <div style={{ divideY: '1px solid var(--color-border-subtle, #E2DDD5)' }}>
              {module.lessons?.map((lesson) => (
                <div key={lesson.id} style={{
                  padding: '1rem 1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderBottom: '1px solid #F3F4F6'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '4px',
                      border: lesson.isCompleted ? 'none' : '2px solid #D1D5DB',
                      backgroundColor: lesson.isCompleted ? 'var(--color-sage, #2C5E55)' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#FFF',
                      fontSize: '12px'
                    }}>
                      {lesson.isCompleted ? '✓' : ''}
                    </div>
                    <div>
                      <Link
                        to={`/chapter/${path.slug}/${module.slug}/${lesson.slug}`}
                        style={{
                          color: 'var(--color-ink, #1F2937)',
                          fontWeight: '600',
                          textDecoration: 'none',
                          fontSize: '1rem'
                        }}
                      >
                        {lesson.title}
                      </Link>
                      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem', fontSize: '0.75rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                        <span>⏱ {lesson.estimatedMinutes} min</span>
                        <span>•</span>
                        <span>{lesson.difficulty}</span>
                        {lesson.contentStatus !== 'Published' && (
                          <>
                            <span>•</span>
                            <span style={{ color: '#D97706', fontWeight: '600' }}>{lesson.contentStatus}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <Link
                    to={`/chapter/${path.slug}/${module.slug}/${lesson.slug}`}
                    style={{
                      padding: '0.4rem 0.9rem',
                      borderRadius: '6px',
                      backgroundColor: 'transparent',
                      border: '1px solid var(--color-sage, #2C5E55)',
                      color: 'var(--color-sage, #2C5E55)',
                      fontWeight: '600',
                      fontSize: '0.85rem',
                      textDecoration: 'none'
                    }}
                  >
                    Read
                  </Link>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
```

### Replace with exactly this:

```jsx
      {/* Modules & Lessons Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {path.modules?.map((module, idx) => {
          const totalCount = module.lessons?.length || 0;
          const completedCount = module.lessons?.filter((lesson) => lesson.isCompleted).length || 0;
          const nextLesson = module.lessons?.find((lesson) => !lesson.isCompleted) || null;

          return (
            <div key={module.id} style={{
              backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
              border: '1px solid var(--color-border-subtle, #E2DDD5)',
              borderRadius: '10px',
              overflow: 'hidden'
            }}>
              <div style={{
                padding: '1.25rem 1.5rem',
                backgroundColor: 'rgba(0,0,0,0.015)',
                borderBottom: '1px solid var(--color-border-subtle, #E2DDD5)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--color-ink-muted, #6B7280)', textTransform: 'uppercase' }}>
                    Module {idx + 1}
                  </span>
                  <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: 'var(--color-ink, #1F2937)' }}>
                    {module.title}
                  </h3>
                </div>
                <span style={{ fontSize: '0.85rem', color: 'var(--color-ink-muted, #6B7280)' }}>
                  {completedCount} of {totalCount} lessons completed
                </span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
                gap: '1rem',
                padding: '1.5rem'
              }}>
                {module.lessons?.map((lesson) => {
                  const isNextUp = nextLesson !== null && lesson.id === nextLesson.id;

                  return (
                    <Link
                      key={lesson.id}
                      to={`/chapter/${path.slug}/${module.slug}/${lesson.slug}`}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem',
                        padding: '1rem',
                        minHeight: '140px',
                        borderRadius: '10px',
                        border: isNextUp ? '2px solid var(--color-sage, #2C5E55)' : '1px solid var(--color-border-subtle, #E2DDD5)',
                        backgroundColor: 'var(--color-parchment-card, #FFFFFF)',
                        color: 'inherit',
                        textDecoration: 'none'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '4px',
                          border: lesson.isCompleted ? 'none' : '2px solid #D1D5DB',
                          backgroundColor: lesson.isCompleted ? 'var(--color-sage, #2C5E55)' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#FFF',
                          fontSize: '12px',
                          flexShrink: 0
                        }}>
                          {lesson.isCompleted ? '✓' : ''}
                        </div>
                        {isNextUp && (
                          <span style={{
                            fontSize: '0.65rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            color: 'var(--color-sage, #2C5E55)',
                            backgroundColor: 'rgba(44, 94, 85, 0.1)',
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px'
                          }}>
                            Continue
                          </span>
                        )}
                      </div>

                      <span style={{
                        fontWeight: '600',
                        fontSize: '0.95rem',
                        color: 'var(--color-ink, #1F2937)',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}>
                        {lesson.title}
                      </span>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', fontSize: '0.7rem', color: 'var(--color-ink-muted, #6B7280)', marginTop: 'auto' }}>
                        <span>⏱ {lesson.estimatedMinutes} min</span>
                        <span>•</span>
                        <span>{lesson.difficulty}</span>
                        {lesson.contentStatus !== 'Published' && (
                          <>
                            <span>•</span>
                            <span style={{ color: '#D97706', fontWeight: '600' }}>{lesson.contentStatus}</span>
                          </>
                        )}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
```

Note the `.map()` callback body changed from an implicit-return arrow
(`(module, idx) => ( ... )`) to an explicit-return arrow with a `{ return ( ... ); }`
body, because it now needs to compute `totalCount`/`completedCount`/`nextLesson`
before returning JSX. This is intentional — keep it exactly as written above.

## Output expected

The full, updated contents of `app/src/pages/LearningPath/LearningPathDetail.jsx`.

## Verification (do this yourself after applying, don't just trust the diff)

- Run `npm run lint` and `npm run build` inside `app/` — must be clean. In particular
  check there are no "unused variable" or "missing key prop" warnings.
- Visit **all five** of `/chapters/java-spring-lld`, `/chapters/fde-curriculum`,
  `/chapters/databases-sql`, `/chapters/high-level-design`, `/chapters/data-engineering`:
  on every one of them, each module should show a grid of small lesson cards (roughly
  5-6 per row on a desktop-width window), not a vertical list. Since this is one shared
  component, if it works on one course it should work on all of them — but check more
  than one to be sure nothing was scoped too narrowly.
- Confirm clicking anywhere on a card (not just the title) navigates to that lesson.
- Confirm the module header now reads "X of Y lessons completed" instead of
  "Y Lessons".
- Confirm exactly one card per module (the first incomplete one, if any) has the
  green "Continue" badge and highlighted border; modules where every lesson is
  completed should have no such card.
- Confirm the hero card at the top of the page (overall progress %, title,
  description) is completely unchanged.
