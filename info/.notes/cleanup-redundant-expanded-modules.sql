-- Cleanup: remove the "Expanded Modules" pollution described in
-- remove-redundant-expanded-modules-prompt.md
--
-- Run the DIAGNOSTIC block first and read the output before running CLEANUP.
-- Safe order: WSL2/local DB first, verify the app looks right, then production.

-- =========================================================================
-- STEP 1 — DIAGNOSTIC (read-only, run this first)
-- =========================================================================

-- 1a. Confirm Module 4 currently contains both the real lessons and the
--     generic "patterns-XX" pollution.
SELECT l.id, l.slug, l.title, l.order_index, l.content_status
FROM lessons l
JOIN course_modules m ON m.id = l.module_id
WHERE m.slug = 'design-principles-patterns'
ORDER BY l.order_index;

-- 1b. Confirm the two extra redundant modules exist in the java-spring-lld course.
SELECT m.id, m.slug, m.title, m.badge, m.order_index
FROM course_modules m
JOIN courses c ON c.id = m.course_id
WHERE c.slug = 'java-spring-lld'
  AND m.slug IN ('applied-design-machine-coding', 'ai-first-backend-capstone-primer');

-- 1c. IMPORTANT: check whether any real user activity/progress already touched
--     the polluted lessons before deleting anything. If this returns rows,
--     stop and review them manually instead of deleting blindly.
SELECT 'learning_activity' AS source, la.id, la.lesson_id, l.slug
FROM learning_activity la
JOIN lessons l ON l.id = la.lesson_id
JOIN course_modules m ON m.id = l.module_id
WHERE (m.slug = 'design-principles-patterns' AND l.slug LIKE 'patterns-%')
   OR m.slug IN ('applied-design-machine-coding', 'ai-first-backend-capstone-primer')
UNION ALL
SELECT 'lesson_notes', ln.id, ln.lesson_id, l.slug
FROM lesson_notes ln
JOIN lessons l ON l.id = ln.lesson_id
JOIN course_modules m ON m.id = l.module_id
WHERE (m.slug = 'design-principles-patterns' AND l.slug LIKE 'patterns-%')
   OR m.slug IN ('applied-design-machine-coding', 'ai-first-backend-capstone-primer');

-- =========================================================================
-- STEP 2 — CLEANUP (only run after reviewing Step 1 output)
-- =========================================================================
-- Wrapped in a transaction so it can be rolled back if anything looks wrong
-- before COMMIT.

BEGIN;

-- 2a. Delete the 10 generic "patterns-XX" lessons that were merged into the
--     real Module 4 (design-principles-patterns). Cascades clean up
--     dependent Problems, LessonResources, LessonDiagrams,
--     LessonCodeComparisons, and outgoing LessonRelations automatically.
DELETE FROM lessons l
USING course_modules m
WHERE l.module_id = m.id
  AND m.slug = 'design-principles-patterns'
  AND l.slug LIKE 'patterns-%';

-- 2b. Delete the two entirely-redundant modules and their lessons.
--     Module -> Course is Cascade, and Lesson -> Module cascade removes the
--     lessons; Lesson-child tables cascade from there as in 2a.
DELETE FROM course_modules m
USING courses c
WHERE m.course_id = c.id
  AND c.slug = 'java-spring-lld'
  AND m.slug IN ('applied-design-machine-coding', 'ai-first-backend-capstone-primer');

-- 2c. Verify: Module 4 should now show only the 4 authored lessons, and the
--     two extra modules should be gone.
SELECT l.slug, l.title, l.order_index
FROM lessons l
JOIN course_modules m ON m.id = l.module_id
WHERE m.slug = 'design-principles-patterns'
ORDER BY l.order_index;

SELECT m.slug
FROM course_modules m
JOIN courses c ON c.id = m.course_id
WHERE c.slug = 'java-spring-lld';

-- If both results look correct, commit. Otherwise ROLLBACK;
COMMIT;
