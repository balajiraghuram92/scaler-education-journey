# Stage 1 UI Prompt for a Local Coding LLM

Use this prompt from the root of the React/Vite frontend project. It is intentionally limited to the UI. The Java/Spring backend will be implemented manually in IntelliJ.

## Copy-paste prompt

```text
You are implementing the Stage 1 frontend for NeuralAscent, a learning platform.

## Reference

Use this public page as the visual reference when browser access is available:
https://neuralascent.top/chapters/java-spring-lld

Also use the general curriculum landing page:
https://neuralascent.top/chapters

If you cannot access the URLs, follow the visual specification below.

## Scope

Build only the React/Vite UI for the first local vertical slice:

1. `/chapters` — curriculum landing page.
2. `/chapters/java-spring-lld` — Java/Spring course index.
3. Lesson links may navigate to a placeholder route or remain visibly disabled.

Do not implement Java, Spring Boot, PostgreSQL, authentication, AI, RAG, or backend API calls in this task.
Do not modify files outside the frontend project.
Do not add a new framework. Use the existing React, Vite, and router setup if present.

## Product intent

The UI should feel like a quiet, editorial engineering-learning library: focused, spacious, readable, and serious. It is not a dashboard full of dense widgets and it is not a generic SaaS admin template.

## Visual direction

- Warm off-white page background.
- White or slightly warm header with a thin bottom border.
- Near-black text with muted gray supporting text.
- Deep desaturated teal/green for progress, accents, and active states.
- Large editorial serif headings, similar in feeling to Newsreader or Playfair Display.
- Clean sans-serif UI text, similar to Plus Jakarta Sans or Outfit.
- Monospace only for small technical labels when useful.
- Thin rules, restrained shadows, generous whitespace, and moderate rounded corners.
- Desktop-first layout that remains usable on mobile.
- Do not use gradients, neon colors, oversized rounded cards, glassmorphism, or decorative stock imagery.

## Header

Create a reusable site header:

- Left: small geometric Neuralascent mark and the word `Neuralascent`.
- Right: `By Raghuram Balaji` and a small circular profile icon.
- Keep the header approximately 60–64px tall.
- Add a subtle bottom border.
- The logo should be a simple local CSS/SVG shape if no existing asset is available; do not hotlink an image.

## `/chapters` landing page

Create:

- A small uppercase eyebrow: `CURRICULUM LIBRARY`.
- Large serif heading: `Learning pathways`.
- Supporting text: `Follow a complete engineering path, or return to the precise lesson that moves your work forward today.`
- A right-side callout with a vertical teal rule and the ideas `Designed for deliberate progress` and `Your completed chapters travel with you across related pathways.`
- Divider line.
- Section eyebrow: `READY TO EXPLORE`.
- Section title: `Active pathways`.
- A compact count badge: `5 active`.
- Responsive pathway cards. Include Java/Spring first, followed by realistic placeholder cards for FDE, Databases & SQL, High-Level Design, and Data Engineering.
- Each active card should show type, progress percentage, title, description, completion count, module count, and a clear action such as `Continue pathway` or `Open pathway`.
- Add a quieter `Planned pathways` section lower on the page with muted cards and `Coming soon` labels.

## `/chapters/java-spring-lld` course index

Create:

- Breadcrumb: `Chapters / Java Low-Level Design & Spring Architecture`.
- Course label: `Course`.
- Title: `Java Low-Level Design & Spring Architecture`.
- Description: `Mastering Object-Oriented Design, Concurrency, JVM Internals, and Spring Boot Enterprise Architecture.`
- Progress display: `3%` and `3 of 88 lessons completed`.
- A visible but restrained progress bar.
- A vertical list of module sections.

Use these module names and high-level lesson data:

1. `OOP Foundations & Design Principles` — 5 lessons, 3 completed.
2. `Concurrency & Multithreading` — 5 lessons.
3. `Advanced Java, Collections & Streams` — 4 lessons.
4. `Design Principles & Patterns for Extensible Systems` — 14 lessons.
5. `Applied Design & Machine Coding` — 7 lessons.
6. `Spring Boot & Enterprise Architecture` — 4 lessons.
7. `Applied Design & Machine Coding` — 14 lessons.
8. `AI-First Backend Capstone Project - Primer` — 12 lessons.
9. `AI-First Backend Capstone Project - Advance` — 15 lessons.
10. `Build a Production-Ready AI-Enabled System` — 8 lessons.

For the first module, show these lesson titles:

- `Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems`
- `Lesson 2 — OOP-1: Intro to OOP Lab`
- `Lesson 3 — OOP-2: Access Modifiers, Encapsulation & Inheritance`
- `Lesson 4 — OOP-3: Polymorphism & Interfaces`
- `Lesson 5 — OOP-4: Library Management System Lab`

For later modules, use concise representative lesson names from the reference page. Do not hardcode a huge 88-lesson page if a reusable data structure can render it.

Each module should have:

- module number;
- module title;
- completion count;
- collapsible or clearly grouped lesson rows;
- lesson status such as completed, current, or not started;
- duration and difficulty metadata;
- a clear hover/focus state;
- a `Continue` action for the current lesson.

## React learning requirements

Keep the implementation easy for a beginner to follow:

- Use small components such as `SiteHeader`, `PathwayCard`, `ProgressBar`, `ModuleSection`, and `LessonRow`.
- Keep display data in plain arrays/objects in a separate data file.
- Render repeated cards and lessons with `.map()`.
- Use props for reusable component data.
- Use one small piece of state for expanded/collapsed modules.
- Use normal React Router links for navigation.
- Avoid global state, Redux, complex hooks, TypeScript migration, animation libraries, and premature abstraction.
- Use semantic HTML and accessible labels/buttons.
- Support keyboard navigation and visible focus styles.

## Data/backend boundary

For this stage, use local mock data only. Put it behind a small module such as `src/data/curriculum.js` so it can later be replaced by:

`React component -> fetch('/api/v2/learning-paths') -> Spring Boot controller -> service -> repository -> PostgreSQL`

Do not put Java/Spring code in the frontend. Do not put lesson content or permissions in browser state as if they were authoritative.

## Required output

Before editing, inspect the existing project and reuse its established styling and routing where practical.

After editing:

1. List every file created or changed.
2. Explain the purpose of each file in one sentence.
3. State the command used to run the frontend locally.
4. State any assumptions or remaining placeholders.
5. Run the existing frontend lint/test/build command if available and report the result.
6. Do not claim pixel-perfect reproduction; identify any areas that still need visual tuning.
```

## What I will explain after the local model finishes

Once the local LLM has implemented the UI, share its changed-file summary or let me inspect the files. I will explain:

- how the page is split into React components;
- how props carry pathway/module/lesson data;
- how `.map()` renders repeated UI;
- how state controls expanded modules;
- how links prepare us for the Java API;
- what is currently mock data and what will later come from Spring Boot;
- how each visual section corresponds to the live website.

