-- ============================================================================
-- Neuralascent Production Migration Inventory Script
-- Phase: PHASE-0 (Discovery, Production Inventory, and Recovery Proof)
-- Safety: READ-ONLY (SELECT queries only. No DDL, DML, or side-effect functions)
-- Target: PostgreSQL 16
-- ============================================================================

-- Section 1: Database & Environment Identity Check
-- Purpose: Verify target database, version, connected user, and transaction state.
SELECT 
    current_database() AS database_name,
    current_schema() AS schema_name,
    current_user AS connected_user,
    version() AS postgres_version,
    pg_is_in_recovery() AS is_read_only_replica,
    now() AS execution_timestamp;

-- ============================================================================
-- Section 2: EF Core Migration History
-- Purpose: Inspect applied EF migrations in order.
SELECT 
    "MigrationId",
    "ProductVersion"
FROM "__EFMigrationsHistory"
ORDER BY "MigrationId" ASC;

-- ============================================================================
-- Section 3: Schema & Column Inventory (Information Schema)
-- Purpose: Map all tables, column names, casing, types, nullability, and defaults.
SELECT 
    table_schema,
    table_name,
    column_name,
    ordinal_position,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- Summary of table casing and quoting requirements
SELECT 
    table_name,
    CASE 
        WHEN table_name ~ '^[a-z0-9_]+$' THEN 'lower_snake_case (unquoted)'
        ELSE 'Quoted Identifier Required ("' || table_name || '")'
    END AS naming_convention
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ============================================================================
-- Section 4: Application Table Row Counts
-- Purpose: Capture exact row counts across all 19 application tables.
SELECT 'Verticals' AS table_name, COUNT(*) AS row_count FROM "Verticals"
UNION ALL
SELECT 'Tasks', COUNT(*) FROM "Tasks"
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'course_modules', COUNT(*) FROM course_modules
UNION ALL
SELECT 'lessons', COUNT(*) FROM lessons
UNION ALL
SELECT 'problems', COUNT(*) FROM problems
UNION ALL
SELECT 'lesson_resources', COUNT(*) FROM lesson_resources
UNION ALL
SELECT 'knowledge_domains', COUNT(*) FROM knowledge_domains
UNION ALL
SELECT 'knowledge_concepts', COUNT(*) FROM knowledge_concepts
UNION ALL
SELECT 'domain_concept_connections', COUNT(*) FROM domain_concept_connections
UNION ALL
SELECT 'concept_prerequisites', COUNT(*) FROM concept_prerequisites
UNION ALL
SELECT 'concept_relations', COUNT(*) FROM concept_relations
UNION ALL
SELECT 'concept_next_lessons', COUNT(*) FROM concept_next_lessons
UNION ALL
SELECT 'reading_map_items', COUNT(*) FROM reading_map_items
UNION ALL
SELECT 'reading_activity_logs', COUNT(*) FROM reading_activity_logs
UNION ALL
SELECT 'knowledge_threads', COUNT(*) FROM knowledge_threads
UNION ALL
SELECT 'lesson_code_comparisons', COUNT(*) FROM lesson_code_comparisons
UNION ALL
SELECT 'lesson_diagrams', COUNT(*) FROM lesson_diagrams
UNION ALL
SELECT 'lesson_notes', COUNT(*) FROM lesson_notes
ORDER BY table_name;

-- ============================================================================
-- Section 5: Study Verticals and Tasks Inventory
-- Purpose: Verify vertical titles, task counts, and completion status.
SELECT 
    v."Id" AS vertical_id,
    v."Name" AS vertical_name,
    v."Description" AS vertical_description,
    COUNT(t."Id") AS total_tasks,
    COUNT(CASE WHEN t."IsCompleted" = true THEN 1 END) AS completed_tasks,
    ROUND(
        CASE 
            WHEN COUNT(t."Id") = 0 THEN 0.0 
            ELSE (COUNT(CASE WHEN t."IsCompleted" = true THEN 1 END)::numeric / COUNT(t."Id")::numeric) * 100.0 
        END, 2
    ) AS completion_percentage
FROM "Verticals" v
LEFT JOIN "Tasks" t ON v."Id" = t."VerticalId"
GROUP BY v."Id", v."Name", v."Description"
ORDER BY v."Id";

-- Tasks grouped by Vertical and Module
SELECT 
    v."Id" AS vertical_id,
    v."Name" AS vertical_name,
    t."Module" AS module_name,
    COUNT(t."Id") AS task_count,
    COUNT(CASE WHEN t."IsCompleted" = true THEN 1 END) AS completed_count
FROM "Verticals" v
JOIN "Tasks" t ON v."Id" = t."VerticalId"
GROUP BY v."Id", v."Name", t."Module"
ORDER BY v."Id", t."Module";

-- ============================================================================
-- Section 6: Courses, Modules, Lessons, and Problems Inventory
-- Purpose: Verify canonical hierarchy row counts, order indexes, and completions.
SELECT 
    c.id AS course_id,
    c.slug AS course_slug,
    c.title AS course_title,
    c.order_index AS course_order,
    c.vertical_id AS linked_vertical_id,
    COUNT(DISTINCT cm.id) AS module_count,
    COUNT(DISTINCT l.id) AS lesson_count,
    COUNT(DISTINCT CASE WHEN l.is_completed = true THEN l.id END) AS completed_lessons,
    COUNT(DISTINCT p.id) AS problem_count,
    COUNT(DISTINCT CASE WHEN p.is_completed = true THEN p.id END) AS completed_problems
FROM courses c
LEFT JOIN course_modules cm ON c.id = cm.course_id
LEFT JOIN lessons l ON cm.id = l.module_id
LEFT JOIN problems p ON l.id = p.lesson_id
GROUP BY c.id, c.slug, c.title, c.order_index, c.vertical_id
ORDER BY c.order_index, c.id;

-- Detailed Course Module Breakdown
SELECT 
    c.slug AS course_slug,
    cm.id AS module_id,
    cm.slug AS module_slug,
    cm.title AS module_title,
    cm.badge AS module_badge,
    cm.order_index AS module_order,
    COUNT(DISTINCT l.id) AS lesson_count,
    COUNT(DISTINCT p.id) AS problem_count
FROM courses c
JOIN course_modules cm ON c.id = cm.course_id
LEFT JOIN lessons l ON cm.id = l.module_id
LEFT JOIN problems p ON l.id = p.lesson_id
GROUP BY c.slug, cm.id, cm.slug, cm.title, cm.badge, cm.order_index
ORDER BY c.slug, cm.order_index;

-- Detailed Lesson Content Breakdown (Notes, Diagrams, Comparisons, Resources)
SELECT 
    l.id AS lesson_id,
    l.slug AS lesson_slug,
    l.title AS lesson_title,
    l.difficulty AS lesson_difficulty,
    l.is_completed AS is_completed,
    LENGTH(COALESCE(l.content_body, '')) AS content_body_length,
    COUNT(DISTINCT r.id) AS resource_count,
    COUNT(DISTINCT c.id) AS comparison_count,
    COUNT(DISTINCT d.id) AS diagram_count,
    COUNT(DISTINCT n.id) AS note_count,
    COUNT(DISTINCT p.id) AS problem_count
FROM lessons l
LEFT JOIN lesson_resources r ON l.id = r.lesson_id
LEFT JOIN lesson_code_comparisons c ON l.id = c.lesson_id
LEFT JOIN lesson_diagrams d ON l.id = d.lesson_id
LEFT JOIN lesson_notes n ON l.id = n.lesson_id
LEFT JOIN problems p ON l.id = p.lesson_id
GROUP BY l.id, l.slug, l.title, l.difficulty, l.is_completed, l.content_body
ORDER BY l.id;

-- ============================================================================
-- Section 7: Duplicate Candidate Identification
-- Purpose: Find duplicate normalized titles across verticals, modules, and lessons.

-- Duplicate Task Titles across all Verticals
SELECT 
    LOWER(TRIM(t."Title")) AS normalized_task_title,
    COUNT(*) AS occurrence_count,
    ARRAY_AGG(DISTINCT v."Name") AS verticals,
    ARRAY_AGG(t."Id") AS task_ids,
    ARRAY_AGG(DISTINCT t."IsCompleted") AS completion_states
FROM "Tasks" t
JOIN "Verticals" v ON t."VerticalId" = v."Id"
GROUP BY LOWER(TRIM(t."Title"))
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC, normalized_task_title;

-- Duplicate Lesson Titles
SELECT 
    LOWER(TRIM(l.title)) AS normalized_lesson_title,
    COUNT(*) AS occurrence_count,
    ARRAY_AGG(l.id) AS lesson_ids,
    ARRAY_AGG(l.slug) AS lesson_slugs
FROM lessons l
GROUP BY LOWER(TRIM(l.title))
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;

-- Duplicate Module Slugs/Titles per Course
SELECT 
    cm.course_id,
    c.slug AS course_slug,
    LOWER(TRIM(cm.title)) AS normalized_module_title,
    COUNT(*) AS occurrence_count,
    ARRAY_AGG(cm.id) AS module_ids
FROM course_modules cm
JOIN courses c ON cm.course_id = c.id
GROUP BY cm.course_id, c.slug, LOWER(TRIM(cm.title))
HAVING COUNT(*) > 1;

-- ============================================================================
-- Section 8: Foreign Key Integrity & Orphan Candidate Analysis
-- Purpose: Verify no dangling references exist across any tables.

-- Orphan Tasks (Tasks without a valid Vertical)
SELECT 'Orphan Tasks' AS issue_type, t."Id" AS entity_id, t."Title" AS entity_title, t."VerticalId" AS foreign_id
FROM "Tasks" t
LEFT JOIN "Verticals" v ON t."VerticalId" = v."Id"
WHERE v."Id" IS NULL

UNION ALL

-- Orphan Course Modules
SELECT 'Orphan Course Modules', cm.id, cm.title, cm.course_id
FROM course_modules cm
LEFT JOIN courses c ON cm.course_id = c.id
WHERE c.id IS NULL

UNION ALL

-- Orphan Lessons
SELECT 'Orphan Lessons', l.id, l.title, l.module_id
FROM lessons l
LEFT JOIN course_modules cm ON l.module_id = cm.id
WHERE cm.id IS NULL

UNION ALL

-- Orphan Problems
SELECT 'Orphan Problems', p.id, p.title, p.lesson_id
FROM problems p
LEFT JOIN lessons l ON p.lesson_id = l.id
WHERE l.id IS NULL

UNION ALL

-- Orphan Lesson Resources
SELECT 'Orphan Lesson Resources', r.id, r.title, r.lesson_id
FROM lesson_resources r
LEFT JOIN lessons l ON r.lesson_id = l.id
WHERE l.id IS NULL

UNION ALL

-- Orphan Code Comparisons
SELECT 'Orphan Code Comparisons', c.id, c.title, c.lesson_id
FROM lesson_code_comparisons c
LEFT JOIN lessons l ON c.lesson_id = l.id
WHERE l.id IS NULL

UNION ALL

-- Orphan Diagrams
SELECT 'Orphan Diagrams', d.id, d.title, d.lesson_id
FROM lesson_diagrams d
LEFT JOIN lessons l ON d.lesson_id = l.id
WHERE l.id IS NULL

UNION ALL

-- Orphan Notes
SELECT 'Orphan Notes', n.id, n.title, n.lesson_id
FROM lesson_notes n
LEFT JOIN lessons l ON n.lesson_id = l.id
WHERE l.id IS NULL

UNION ALL

-- Orphan Domain-Concept Connections (invalid domain)
SELECT 'Orphan Domain-Concept (Domain)', dc.id, 'Connection ID ' || dc.id, dc.domain_id
FROM domain_concept_connections dc
LEFT JOIN knowledge_domains kd ON dc.domain_id = kd.id
WHERE kd.id IS NULL

UNION ALL

-- Orphan Domain-Concept Connections (invalid concept)
SELECT 'Orphan Domain-Concept (Concept)', dc.id, 'Connection ID ' || dc.id, dc.concept_id
FROM domain_concept_connections dc
LEFT JOIN knowledge_concepts kc ON dc.concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Orphan Concept Prerequisites (invalid concept)
SELECT 'Orphan Concept Prerequisite (Concept)', cp.id, 'Prereq ID ' || cp.id, cp.concept_id
FROM concept_prerequisites cp
LEFT JOIN knowledge_concepts kc ON cp.concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Orphan Concept Prerequisites (invalid prerequisite concept)
SELECT 'Orphan Concept Prerequisite (Target Prereq)', cp.id, 'Prereq ID ' || cp.id, cp.prerequisite_concept_id
FROM concept_prerequisites cp
LEFT JOIN knowledge_concepts kc ON cp.prerequisite_concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Orphan Concept Relations (invalid source)
SELECT 'Orphan Concept Relation (Source)', cr.id, 'Relation ID ' || cr.id, cr.source_concept_id
FROM concept_relations cr
LEFT JOIN knowledge_concepts kc ON cr.source_concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Orphan Concept Relations (invalid target)
SELECT 'Orphan Concept Relation (Target)', cr.id, 'Relation ID ' || cr.id, cr.target_concept_id
FROM concept_relations cr
LEFT JOIN knowledge_concepts kc ON cr.target_concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Orphan Concept Next Lessons (invalid concept)
SELECT 'Orphan Concept Next Lesson (Concept)', cnl.id, cnl.lesson_title, cnl.concept_id
FROM concept_next_lessons cnl
LEFT JOIN knowledge_concepts kc ON cnl.concept_id = kc.id
WHERE kc.id IS NULL

UNION ALL

-- Dangling Concept Next Lessons (non-null lesson_id pointing to non-existent lesson)
SELECT 'Dangling Concept Next Lesson (LessonId)', cnl.id, cnl.lesson_title, cnl.lesson_id
FROM concept_next_lessons cnl
LEFT JOIN lessons l ON cnl.lesson_id = l.id
WHERE cnl.lesson_id IS NOT NULL AND l.id IS NULL;

-- ============================================================================
-- Section 9: FDE Curriculum vs. FDE Self-Study Row-Level Reconciliation
-- Purpose: Analyze row-level differences, duplicate titles, modules, and completion.
WITH fde_curriculum_tasks AS (
    SELECT 
        t."Id" AS task_id,
        t."Title" AS title,
        LOWER(TRIM(t."Title")) AS norm_title,
        t."Module" AS module,
        t."IsCompleted" AS is_completed
    FROM "Tasks" t
    JOIN "Verticals" v ON t."VerticalId" = v."Id"
    WHERE v."Name" = 'FDE Curriculum'
),
fde_self_study_tasks AS (
    SELECT 
        t."Id" AS task_id,
        t."Title" AS title,
        LOWER(TRIM(t."Title")) AS norm_title,
        t."Module" AS module,
        t."IsCompleted" AS is_completed
    FROM "Tasks" t
    JOIN "Verticals" v ON t."VerticalId" = v."Id"
    WHERE v."Name" = 'FDE Self-Study'
)
SELECT 
    COALESCE(c.norm_title, s.norm_title) AS normalized_title,
    c.task_id AS fde_curriculum_task_id,
    c.module AS fde_curriculum_module,
    c.is_completed AS fde_curriculum_completed,
    s.task_id AS fde_self_study_task_id,
    s.module AS fde_self_study_module,
    s.is_completed AS fde_self_study_completed,
    CASE 
        WHEN c.task_id IS NOT NULL AND s.task_id IS NOT NULL AND c.is_completed = s.is_completed THEN 'EXACT_MATCH'
        WHEN c.task_id IS NOT NULL AND s.task_id IS NOT NULL AND c.is_completed <> s.is_completed THEN 'COMPLETION_MISMATCH'
        WHEN c.task_id IS NOT NULL AND s.task_id IS NULL THEN 'ONLY_IN_CURRICULUM'
        WHEN c.task_id IS NULL AND s.task_id IS NOT NULL THEN 'ONLY_IN_SELF_STUDY'
    END AS comparison_status
FROM fde_curriculum_tasks c
FULL OUTER JOIN fde_self_study_tasks s ON c.norm_title = s.norm_title
ORDER BY comparison_status, normalized_title;

-- ============================================================================
-- Section 10: Reading Map Seed Candidates & Activity Log Analysis
-- Purpose: Inventory seeded reading items, synthetic activity bars, and threads.

-- Reading Map Items Inventory
SELECT 
    "Id" AS reading_item_id,
    "Category" AS category,
    "Title" AS title,
    "SubText" AS sub_text,
    "OrderIndex" AS order_index,
    "IsCompleted" AS is_completed,
    CASE 
        WHEN "Title" ~ '\([0-9]+\)' THEN 'List-like Prototype ("(N)")'
        WHEN "Title" IN ('Structured Concurrency & Virtual Threads in Java 21', 'OOP-2: Access Modifiers, Constructor Chaining & Immutability', 'The equals/hashCode Contract & Memory Symmetry') THEN 'Canonical Java Candidate'
        WHEN "SubText" ILIKE '%deferred%' OR "SubText" ILIKE '%next%' THEN 'Placeholder SubText'
        ELSE 'Manual / Standard Item'
    END AS seed_classification
FROM reading_map_items
ORDER BY "Category", "OrderIndex", "Id";

-- Reading Activity Logs Inventory
SELECT 
    "Id" AS log_id,
    "DayLabel" AS day_label,
    "ActivityCount" AS activity_count,
    "OrderIndex" AS order_index,
    "LogDate" AS log_date
FROM reading_activity_logs
ORDER BY "OrderIndex" ASC;

-- Knowledge Threads Inventory
SELECT 
    "Id" AS thread_id,
    "Domain" AS domain,
    "RawPath" AS raw_path,
    "OrderIndex" AS order_index
FROM knowledge_threads
ORDER BY "OrderIndex" ASC;

-- ============================================================================
-- Section 11: ConceptNextLesson Resolution Status
-- Purpose: Evaluate how many ConceptNextLesson records have LessonId vs string only.
SELECT 
    cnl.id AS concept_next_lesson_id,
    kc.title AS concept_title,
    cnl.lesson_title AS candidate_lesson_title,
    cnl.module_name AS candidate_module_name,
    cnl.lesson_slug AS candidate_lesson_slug,
    cnl.lesson_id AS existing_lesson_id,
    l.id AS resolved_matching_lesson_id,
    l.title AS resolved_matching_lesson_title,
    CASE 
        WHEN cnl.lesson_id IS NOT NULL THEN 'LINKED_EXPLICITLY'
        WHEN l.id IS NOT NULL THEN 'RESOLVABLE_BY_SLUG_OR_TITLE'
        ELSE 'UNRESOLVED_EXTERNAL_OR_UNAUTHORED'
    END AS resolution_status
FROM concept_next_lessons cnl
JOIN knowledge_concepts kc ON cnl.concept_id = kc.id
LEFT JOIN lessons l ON (cnl.lesson_slug = l.slug OR LOWER(TRIM(cnl.lesson_title)) = LOWER(TRIM(l.title)))
ORDER BY resolution_status, kc.title, cnl.order_index;
