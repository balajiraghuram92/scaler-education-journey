using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddCurriculumBridgeSchema : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. StudyVerticals & StudyTasks compatibility columns
            migrationBuilder.AddColumn<int>(
                name: "canonical_vertical_id",
                table: "Verticals",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "archived_at",
                table: "Verticals",
                type: "timestamp with time zone",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "updated_at",
                table: "Verticals",
                type: "timestamp with time zone",
                nullable: false,
                defaultValueSql: "now()");

            migrationBuilder.AddColumn<DateTime>(
                name: "updated_at",
                table: "Tasks",
                type: "timestamp with time zone",
                nullable: false,
                defaultValueSql: "now()");

            migrationBuilder.CreateIndex(
                name: "ix_verticals_canonical_vertical_id",
                table: "Verticals",
                column: "canonical_vertical_id");

            migrationBuilder.AddForeignKey(
                name: "FK_Verticals_Verticals_canonical_vertical_id",
                table: "Verticals",
                column: "canonical_vertical_id",
                principalTable: "Verticals",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);

            // 2. Courses PathType & IsPublished
            migrationBuilder.AddColumn<string>(
                name: "path_type",
                table: "courses",
                type: "character varying(32)",
                maxLength: 32,
                nullable: false,
                defaultValue: "Course");

            migrationBuilder.AddColumn<bool>(
                name: "is_published",
                table: "courses",
                type: "boolean",
                nullable: false,
                defaultValue: true);

            migrationBuilder.AddCheckConstraint(
                name: "ck_courses_path_type",
                table: "courses",
                sql: "path_type IN ('Course', 'Certification', 'Project')");

            // 3. Lessons ContentStatus
            migrationBuilder.AddColumn<string>(
                name: "content_status",
                table: "lessons",
                type: "character varying(32)",
                maxLength: 32,
                nullable: false,
                defaultValue: "Published");

            migrationBuilder.AddCheckConstraint(
                name: "ck_lessons_content_status",
                table: "lessons",
                sql: "content_status IN ('Outline', 'Draft', 'Published', 'Archived')");

            // 4. course_domain_links table
            migrationBuilder.CreateTable(
                name: "course_domain_links",
                columns: table => new
                {
                    course_id = table.Column<int>(type: "integer", nullable: false),
                    domain_id = table.Column<int>(type: "integer", nullable: false),
                    is_primary = table.Column<bool>(type: "boolean", nullable: false, defaultValue: false),
                    order_index = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_course_domain_links", x => new { x.course_id, x.domain_id });
                    table.ForeignKey(
                        name: "FK_course_domain_links_courses_course_id",
                        column: x => x.course_id,
                        principalTable: "courses",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_course_domain_links_knowledge_domains_domain_id",
                        column: x => x.domain_id,
                        principalTable: "knowledge_domains",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_course_domain_links_domain_id",
                table: "course_domain_links",
                columns: new[] { "domain_id", "order_index" });

            // 5. lesson_concept_links table
            migrationBuilder.CreateTable(
                name: "lesson_concept_links",
                columns: table => new
                {
                    lesson_id = table.Column<int>(type: "integer", nullable: false),
                    concept_id = table.Column<int>(type: "integer", nullable: false),
                    relationship_type = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false, defaultValue: "Related"),
                    order_index = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_lesson_concept_links", x => new { x.lesson_id, x.concept_id, x.relationship_type });
                    table.CheckConstraint("ck_lesson_concept_relationship", "relationship_type IN ('Primary', 'Related', 'PrerequisiteContext')");
                    table.ForeignKey(
                        name: "FK_lesson_concept_links_knowledge_concepts_concept_id",
                        column: x => x.concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_lesson_concept_links_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_lesson_concept_links_concept",
                table: "lesson_concept_links",
                columns: new[] { "concept_id", "relationship_type", "order_index" });

            // 6. lesson_relations table
            migrationBuilder.CreateTable(
                name: "lesson_relations",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    source_lesson_id = table.Column<int>(type: "integer", nullable: false),
                    target_lesson_id = table.Column<int>(type: "integer", nullable: true),
                    target_title = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    target_slug = table.Column<string>(type: "character varying(150)", maxLength: 150, nullable: true),
                    relationship_type = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false),
                    resolution_status = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false, defaultValue: "Unresolved"),
                    order_index = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()"),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_lesson_relations", x => x.id);
                    table.CheckConstraint("ck_lesson_relation_type", "relationship_type IN ('Prerequisite', 'Related', 'Next')");
                    table.CheckConstraint("ck_lesson_relation_resolution", "resolution_status IN ('Unresolved', 'Resolved', 'External')");
                    table.CheckConstraint("ck_lesson_relation_target", "target_lesson_id IS NOT NULL OR length(trim(target_title)) > 0");
                    table.ForeignKey(
                        name: "FK_lesson_relations_lessons_source_lesson_id",
                        column: x => x.source_lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_lesson_relations_lessons_target_lesson_id",
                        column: x => x.target_lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateIndex(
                name: "ux_lesson_relations_identity",
                table: "lesson_relations",
                columns: new[] { "source_lesson_id", "relationship_type", "target_title" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_lesson_relations_target_lesson",
                table: "lesson_relations",
                column: "target_lesson_id");

            // 7. study_task_content_links table
            migrationBuilder.CreateTable(
                name: "study_task_content_links",
                columns: table => new
                {
                    task_id = table.Column<int>(type: "integer", nullable: false),
                    lesson_id = table.Column<int>(type: "integer", nullable: true),
                    problem_id = table.Column<int>(type: "integer", nullable: true),
                    mapping_type = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false, defaultValue: "TitleAndModule"),
                    mapping_status = table.Column<string>(type: "character varying(32)", maxLength: 32, nullable: false, defaultValue: "Proposed"),
                    confidence = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: false, defaultValue: 1.0000m),
                    source_checksum = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    verified_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()"),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_study_task_content_links", x => x.task_id);
                    table.CheckConstraint("ck_task_content_exactly_one_target", "num_nonnulls(lesson_id, problem_id) = 1");
                    table.CheckConstraint("ck_task_content_mapping_type", "mapping_type IN ('Exact', 'TitleAndModule', 'Manual', 'DuplicateAlias')");
                    table.CheckConstraint("ck_task_content_mapping_status", "mapping_status IN ('Proposed', 'Verified', 'Rejected')");
                    table.CheckConstraint("ck_task_content_confidence", "confidence >= 0 AND confidence <= 1");
                    table.ForeignKey(
                        name: "FK_study_task_content_links_Tasks_task_id",
                        column: x => x.task_id,
                        principalTable: "Tasks",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_study_task_content_links_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_study_task_content_links_problems_problem_id",
                        column: x => x.problem_id,
                        principalTable: "problems",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "ix_task_content_links_lesson",
                table: "study_task_content_links",
                column: "lesson_id");

            migrationBuilder.CreateIndex(
                name: "ix_task_content_links_problem",
                table: "study_task_content_links",
                column: "problem_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "study_task_content_links");
            migrationBuilder.DropTable(name: "lesson_relations");
            migrationBuilder.DropTable(name: "lesson_concept_links");
            migrationBuilder.DropTable(name: "course_domain_links");
            migrationBuilder.DropCheckConstraint(name: "ck_lessons_content_status", table: "lessons");
            migrationBuilder.DropColumn(name: "content_status", table: "lessons");
            migrationBuilder.DropCheckConstraint(name: "ck_courses_path_type", table: "courses");
            migrationBuilder.DropColumn(name: "is_published", table: "courses");
            migrationBuilder.DropColumn(name: "path_type", table: "courses");
            migrationBuilder.DropForeignKey(name: "FK_Verticals_Verticals_canonical_vertical_id", table: "Verticals");
            migrationBuilder.DropIndex(name: "ix_verticals_canonical_vertical_id", table: "Verticals");
            migrationBuilder.DropColumn(name: "updated_at", table: "Tasks");
            migrationBuilder.DropColumn(name: "updated_at", table: "Verticals");
            migrationBuilder.DropColumn(name: "archived_at", table: "Verticals");
            migrationBuilder.DropColumn(name: "canonical_vertical_id", table: "Verticals");
        }
    }
}
