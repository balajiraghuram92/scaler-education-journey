# Prompt: Remove the domain-tags row from the LearningPathDetail hero card

Paste everything below into the Local LLM verbatim.

---

## Strict rules

- Touch **exactly one file**: `app/src/pages/LearningPath/LearningPathDetail.jsx`.
- Do not change anything else in the file — not the `path.pathType` badge right next
  to what you're removing, not the `<h1>` title, not the description, not anything
  above or below this block.
- Do not add any new file, import, or npm package.

## Context

The hero card's top badge row currently renders the course's `pathType` badge
("Course") followed by one blue pill per entry in `path.domains`. This is fine for
courses with 0-1 domains, but `fde-curriculum` has 8 domains (Agentic AI Core, FDE
Foundations, Backend Engineering & Data Systems, Full-Stack FDE, Cloud DevOps &
Infrastructure, Enterprise LLM Engineering, Agent Systems & Integrations, Application
Engineering & Reliability), and the row has no wrapping, so it overflows/clips instead
of degrading gracefully. Since this component is shared across every course
(`java-spring-lld`, `fde-curriculum`, `databases-sql`, `high-level-design`,
`data-engineering`), the fix must not special-case any one course.

The agreed fix: remove the domain-tags row entirely. Keep only the `pathType` badge.

## The change

Find this exact block:

```jsx
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span style={{
                backgroundColor: 'rgba(44, 94, 85, 0.1)',
                color: 'var(--color-sage, #2C5E55)',
                padding: '0.2rem 0.6rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '700',
                textTransform: 'uppercase'
              }}>
                {path.pathType}
              </span>
              {path.domains?.map((d) => (
                <span key={d} style={{
                  backgroundColor: '#EFF6FF',
                  color: '#1D4ED8',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600'
                }}>
                  {d}
                </span>
              ))}
            </div>
```

Replace it with exactly this (the `pathType` badge kept as-is, the `path.domains` map
removed):

```jsx
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span style={{
                backgroundColor: 'rgba(44, 94, 85, 0.1)',
                color: 'var(--color-sage, #2C5E55)',
                padding: '0.2rem 0.6rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '700',
                textTransform: 'uppercase'
              }}>
                {path.pathType}
              </span>
            </div>
```

## Output expected

The full, updated contents of `app/src/pages/LearningPath/LearningPathDetail.jsx`.

## Verification

- Run `npm run lint && npm run test && npm run build` inside `app/` — must be clean.
- Visit `/chapters/fde-curriculum`: the hero card should show only a single "Course"
  badge above the title, no domain pills, no overflow/clipping.
- Visit `/chapters/java-spring-lld` (or any other course): unaffected, since it likely
  had 0-1 domains anyway — confirm the hero still looks correct there too.
