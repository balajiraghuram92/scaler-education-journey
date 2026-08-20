using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLessonDifficultyAndChapterTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                ALTER TABLE lessons ADD COLUMN IF NOT EXISTS difficulty VARCHAR(50) DEFAULT 'Intermediate';
                ALTER TABLE lessons ADD COLUMN IF NOT EXISTS content_body TEXT DEFAULT '';
                ALTER TABLE lessons ADD COLUMN IF NOT EXISTS horstmann_ref VARCHAR(255) DEFAULT '';
                ALTER TABLE lessons ADD COLUMN IF NOT EXISTS class_date VARCHAR(50) DEFAULT '';
                ALTER TABLE lessons ADD COLUMN IF NOT EXISTS estimated_minutes INT DEFAULT 45;

                CREATE TABLE IF NOT EXISTS lesson_code_comparisons (
                    id SERIAL PRIMARY KEY,
                    lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    before_label VARCHAR(100) NOT NULL,
                    before_language VARCHAR(50) NOT NULL,
                    before_code TEXT NOT NULL,
                    after_label VARCHAR(100) NOT NULL,
                    after_language VARCHAR(50) NOT NULL,
                    after_code TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    order_index INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS lesson_diagrams (
                    id SERIAL PRIMARY KEY,
                    lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                    title VARCHAR(200) NOT NULL,
                    caption VARCHAR(300) NOT NULL,
                    diagram_type VARCHAR(50) NOT NULL DEFAULT 'svg-inline',
                    svg_content TEXT NOT NULL,
                    diagram_spec_json TEXT,
                    order_index INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS lesson_notes (
                    id SERIAL PRIMARY KEY,
                    lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                    note_type VARCHAR(50) NOT NULL DEFAULT 'FieldNote',
                    anchor_section VARCHAR(150),
                    title VARCHAR(250) NOT NULL,
                    content_body TEXT NOT NULL,
                    order_index INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS ix_lesson_code_comparisons_lesson_id ON lesson_code_comparisons(lesson_id);
                CREATE INDEX IF NOT EXISTS ix_lesson_diagrams_lesson_id ON lesson_diagrams(lesson_id);
                CREATE INDEX IF NOT EXISTS ix_lesson_notes_lesson_id_note_type ON lesson_notes(lesson_id, note_type);
            ");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "lesson_code_comparisons");
            migrationBuilder.DropTable(name: "lesson_diagrams");
            migrationBuilder.DropTable(name: "lesson_notes");
            migrationBuilder.DropColumn(name: "difficulty", table: "lessons");
        }
    }
}
