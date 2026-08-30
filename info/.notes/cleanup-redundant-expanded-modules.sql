-- Cleanup: remove ALL "Expanded Modules" pollution from the java-spring-lld
-- course — the auto-templated modules/lessons that predate the curated
-- Modules 1-6, described in:
--   remove-redundant-expanded-modules-prompt.md         (first 3 removed)
--   fix-idempotent-module4-seeding-prompt.md             (2 more removed)
--
-- The seed code is additive-only and never deletes rows, so removing a
-- definition from GetExpandedModules() only stops FUTURE creation — it does
-- not retroactively clean up rows already inserted by an earlier run. This
-- script is safe to run against ANY environment regardless of which subset
-- of the pollution it actually has: every slug below either matches real
-- rows (which get removed) or matches nothing (no-op), so run it as-is on
-- both local and production without needing to check which case applies.
--
-- Run the DIAGNOSTIC block first and read the output before running CLEANUP.
-- Safe order: WSL2/local DB first, verify the app looks right, then production.

-- =========================================================================
-- STEP 1 — DIAGNOSTIC (read-only, run this first)
-- =========================================================================

-- 1a. Confirm Module 4 currently contains only real lessons (no leftover
--     generic "patterns-XX" rows merged in from the old shared-slug bug).
SELECT l.id, l.slug, l.title, l.order_index, l.content_status
FROM lessons l
JOIN course_modules m ON m.id = l.module_id
WHERE m.slug = 'design-principles-patterns'
ORDER BY l.order_index;

-- 1b. List every redundant module still present in the java-spring-lld course.
SELECT m.id, m.slug, m.title, m.badge, m.order_index,
       (SELECT count(*) FROM lessons l WHERE l.module_id = m.id) AS lesson_count
FROM course_modules m
JOIN courses c ON c.id = m.course_id
WHERE c.slug = 'java-spring-lld'
  AND m.slug IN (
    'applied-design-machine-coding',
    'ai-first-backend-capstone-primer',
    'ai-first-backend-capstone-advanced',
    'production-ai-enabled-system'
  );

-- 1c. IMPORTANT: check whether any real user activity/progress already touched
--     the polluted lessons before deleting anything. If this returns rows,
--     stop and review them manually instead of deleting blindly.
SELECT 'learning_activity' AS source, la.id, la.lesson_id, l.slug
FROM learning_activity la
JOIN lessons l ON l.id = la.lesson_id
JOIN course_modules m ON m.id = l.module_id
WHERE (m.slug = 'design-principles-patterns' AND l.slug LIKE 'patterns-%')
   OR m.slug IN (
        'applied-design-machine-coding',
        'ai-first-backend-capstone-primer',
        'ai-first-backend-capstone-advanced',
        'production-ai-enabled-system'
      )
UNION ALL
SELECT 'lesson_notes', ln.id, ln.lesson_id, l.slug
FROM lesson_notes ln
JOIN lessons l ON l.id = ln.lesson_id
JOIN course_modules m ON m.id = l.module_id
WHERE (m.slug = 'design-principles-patterns' AND l.slug LIKE 'patterns-%')
   OR m.slug IN (
        'applied-design-machine-coding',
        'ai-first-backend-capstone-primer',
        'ai-first-backend-capstone-advanced',
        'production-ai-enabled-system'
      );

-- =========================================================================
-- STEP 2 — CLEANUP (only run after reviewing Step 1 output)
-- =========================================================================
-- Wrapped in a transaction so it can be rolled back if anything looks wrong
-- before COMMIT.

BEGIN;

-- 2a. Delete any generic "patterns-XX" lessons still merged into the real
--     Module 4 (design-principles-patterns), if present. Cascades clean up
--     dependent Problems, LessonResources, LessonDiagrams,
--     LessonCodeComparisons, and outgoing LessonRelations automatically.
DELETE FROM lessons l
USING course_modules m
WHERE l.module_id = m.id
  AND m.slug = 'design-principles-patterns'
  AND l.slug LIKE 'patterns-%';

-- 2b. Delete every entirely-redundant module and its lessons, if present.
--     Module -> Course is Cascade, and Lesson -> Module cascade removes the
--     lessons; Lesson-child tables cascade from there as in 2a.
DELETE FROM course_modules m
USING courses c
WHERE m.course_id = c.id
  AND c.slug = 'java-spring-lld'
  AND m.slug IN (
    'applied-design-machine-coding',
    'ai-first-backend-capstone-primer',
    'ai-first-backend-capstone-advanced',
    'production-ai-enabled-system'
  );

-- 2c. Verify: Module 4 should now show only the 4 authored lessons, and none
--     of the redundant modules should remain in the course's module list.
SELECT l.slug, l.title, l.order_index
FROM lessons l
JOIN course_modules m ON m.id = l.module_id
WHERE m.slug = 'design-principles-patterns'
ORDER BY l.order_index;

SELECT m.slug, m.badge, m.order_index
FROM course_modules m
JOIN courses c ON c.id = m.course_id
WHERE c.slug = 'java-spring-lld'
ORDER BY m.order_index;

-- If both results look correct (6 modules total, Module 4 has exactly the
-- 4 real lessons), commit. Otherwise ROLLBACK;
COMMIT;
