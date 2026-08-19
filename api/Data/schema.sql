-- PostgreSQL 16 Relational Schema for StudyTracker
-- Supports dynamic hierarchy: Courses -> Modules -> Lessons -> Problems / LessonResources

-- 1. Verticals & Tasks (Base Compatibility)
CREATE TABLE IF NOT EXISTS study_verticals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS study_tasks (
    id SERIAL PRIMARY KEY,
    vertical_id INT NOT NULL REFERENCES study_verticals(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    module VARCHAR(150) NOT NULL DEFAULT 'General'
);

CREATE INDEX IF NOT EXISTS idx_tasks_vertical_id ON study_tasks(vertical_id);

-- 2. Courses
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    order_index INT NOT NULL DEFAULT 0,
    vertical_id INT REFERENCES study_verticals(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_courses_slug ON courses(slug);
CREATE INDEX IF NOT EXISTS idx_courses_vertical_id ON courses(vertical_id);

-- 3. Course Modules
CREATE TABLE IF NOT EXISTS course_modules (
    id SERIAL PRIMARY KEY,
    course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    slug VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    badge VARCHAR(50) NOT NULL DEFAULT '',
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_course_modules_course_slug UNIQUE (course_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_modules_course_id ON course_modules(course_id);
CREATE INDEX IF NOT EXISTS idx_modules_slug ON course_modules(slug);

-- 4. Lessons
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    module_id INT NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    slug VARCHAR(150) NOT NULL,
    title VARCHAR(250) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    lecture_number INT NOT NULL DEFAULT 0,
    class_date VARCHAR(50) NOT NULL DEFAULT '',
    content_body TEXT NOT NULL DEFAULT '',
    horstmann_ref VARCHAR(250) NOT NULL DEFAULT '',
    estimated_minutes INT NOT NULL DEFAULT 45,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_lessons_module_slug UNIQUE (module_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_lessons_module_id ON lessons(module_id);
CREATE INDEX IF NOT EXISTS idx_lessons_slug ON lessons(slug);
CREATE INDEX IF NOT EXISTS idx_lessons_is_completed ON lessons(is_completed);

-- 5. Problems
CREATE TABLE IF NOT EXISTS problems (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    slug VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    difficulty VARCHAR(50) NOT NULL DEFAULT 'Warm-up',
    package_name VARCHAR(100) NOT NULL DEFAULT '',
    test_class_name VARCHAR(100) NOT NULL DEFAULT '',
    problem_statement TEXT NOT NULL DEFAULT '',
    requirements_body TEXT NOT NULL DEFAULT '',
    worked_example TEXT NOT NULL DEFAULT '',
    hints TEXT NOT NULL DEFAULT '',
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_problems_lesson_slug UNIQUE (lesson_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_problems_lesson_id ON problems(lesson_id);
CREATE INDEX IF NOT EXISTS idx_problems_slug ON problems(slug);
CREATE INDEX IF NOT EXISTS idx_problems_is_completed ON problems(is_completed);

-- 6. Lesson Resources
CREATE TABLE IF NOT EXISTS lesson_resources (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL DEFAULT 'StudyGuideTopic',
    title VARCHAR(250) NOT NULL,
    content_body TEXT NOT NULL DEFAULT '',
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resources_lesson_id ON lesson_resources(lesson_id);
CREATE INDEX IF NOT EXISTS idx_resources_type ON lesson_resources(resource_type);

-- 7. Knowledge Atlas Schema
CREATE TABLE IF NOT EXISTS knowledge_domains (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    icon VARCHAR(100) NOT NULL DEFAULT 'layers',
    color_hex VARCHAR(50) NOT NULL DEFAULT '#3B82F6',
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_domains_slug ON knowledge_domains(slug);
CREATE INDEX IF NOT EXISTS idx_domains_order ON knowledge_domains(order_index);

CREATE TABLE IF NOT EXISTS knowledge_concepts (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    sub_label TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    difficulty VARCHAR(50) NOT NULL DEFAULT 'Intermediate',
    icon VARCHAR(100) NOT NULL DEFAULT 'sparkles',
    estimated_hours INT NOT NULL DEFAULT 10,
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_concepts_slug ON knowledge_concepts(slug);
CREATE INDEX IF NOT EXISTS idx_concepts_order ON knowledge_concepts(order_index);

CREATE TABLE IF NOT EXISTS domain_concept_connections (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL REFERENCES knowledge_domains(id) ON DELETE CASCADE,
    concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    relevance_weight INT NOT NULL DEFAULT 5,
    role_description VARCHAR(250) NOT NULL DEFAULT '',
    order_index INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_domain_concept UNIQUE (domain_id, concept_id)
);

CREATE INDEX IF NOT EXISTS idx_domain_concept_domain ON domain_concept_connections(domain_id);
CREATE INDEX IF NOT EXISTS idx_domain_concept_concept ON domain_concept_connections(concept_id);

CREATE TABLE IF NOT EXISTS concept_prerequisites (
    id SERIAL PRIMARY KEY,
    concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    prerequisite_concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'included',
    CONSTRAINT uq_concept_prerequisite UNIQUE (concept_id, prerequisite_concept_id)
);

CREATE INDEX IF NOT EXISTS idx_concept_prereq_concept ON concept_prerequisites(concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_prereq_target ON concept_prerequisites(prerequisite_concept_id);

CREATE TABLE IF NOT EXISTS concept_relations (
    id SERIAL PRIMARY KEY,
    source_concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    target_concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE RESTRICT,
    relationship_type VARCHAR(50) NOT NULL DEFAULT 'Related',
    CONSTRAINT uq_concept_relation UNIQUE (source_concept_id, target_concept_id)
);

CREATE INDEX IF NOT EXISTS idx_concept_rel_source ON concept_relations(source_concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_rel_target ON concept_relations(target_concept_id);

CREATE TABLE IF NOT EXISTS concept_next_lessons (
    id SERIAL PRIMARY KEY,
    concept_id INT NOT NULL REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    lesson_title VARCHAR(300) NOT NULL,
    module_name VARCHAR(200) NOT NULL DEFAULT '',
    lesson_slug VARCHAR(150) NOT NULL DEFAULT '',
    lesson_id INT REFERENCES lessons(id) ON DELETE SET NULL,
    order_index INT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_concept_lessons_concept ON concept_next_lessons(concept_id);

