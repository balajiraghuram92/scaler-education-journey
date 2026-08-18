using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddCoursesAndLessonsHierarchy : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "courses",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    slug = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    description = table.Column<string>(type: "text", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    vertical_id = table.Column<int>(type: "integer", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_courses", x => x.id);
                    table.ForeignKey(
                        name: "FK_courses_Verticals_vertical_id",
                        column: x => x.vertical_id,
                        principalTable: "Verticals",
                        principalColumn: "Id");
                });

            migrationBuilder.CreateTable(
                name: "course_modules",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    course_id = table.Column<int>(type: "integer", nullable: false),
                    slug = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    description = table.Column<string>(type: "text", nullable: false),
                    badge = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_course_modules", x => x.id);
                    table.ForeignKey(
                        name: "FK_course_modules_courses_course_id",
                        column: x => x.course_id,
                        principalTable: "courses",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "lessons",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    module_id = table.Column<int>(type: "integer", nullable: false),
                    slug = table.Column<string>(type: "character varying(150)", maxLength: 150, nullable: false),
                    title = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    description = table.Column<string>(type: "text", nullable: false),
                    lecture_number = table.Column<int>(type: "integer", nullable: false),
                    class_date = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    content_body = table.Column<string>(type: "text", nullable: false),
                    horstmann_ref = table.Column<string>(type: "text", nullable: false),
                    estimated_minutes = table.Column<int>(type: "integer", nullable: false),
                    is_completed = table.Column<bool>(type: "boolean", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_lessons", x => x.id);
                    table.ForeignKey(
                        name: "FK_lessons_course_modules_module_id",
                        column: x => x.module_id,
                        principalTable: "course_modules",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "lesson_resources",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    lesson_id = table.Column<int>(type: "integer", nullable: false),
                    resource_type = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    title = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    content_body = table.Column<string>(type: "text", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_lesson_resources", x => x.id);
                    table.ForeignKey(
                        name: "FK_lesson_resources_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "problems",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    lesson_id = table.Column<int>(type: "integer", nullable: false),
                    slug = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    difficulty = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    package_name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    test_class_name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    problem_statement = table.Column<string>(type: "text", nullable: false),
                    requirements_body = table.Column<string>(type: "text", nullable: false),
                    worked_example = table.Column<string>(type: "text", nullable: false),
                    hints = table.Column<string>(type: "text", nullable: false),
                    is_completed = table.Column<bool>(type: "boolean", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_problems", x => x.id);
                    table.ForeignKey(
                        name: "FK_problems_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_course_modules_course_id_slug",
                table: "course_modules",
                columns: new[] { "course_id", "slug" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_courses_slug",
                table: "courses",
                column: "slug",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_courses_vertical_id",
                table: "courses",
                column: "vertical_id");

            migrationBuilder.CreateIndex(
                name: "IX_lesson_resources_lesson_id",
                table: "lesson_resources",
                column: "lesson_id");

            migrationBuilder.CreateIndex(
                name: "IX_lessons_module_id_slug",
                table: "lessons",
                columns: new[] { "module_id", "slug" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_problems_lesson_id_slug",
                table: "problems",
                columns: new[] { "lesson_id", "slug" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "lesson_resources");

            migrationBuilder.DropTable(
                name: "problems");

            migrationBuilder.DropTable(
                name: "lessons");

            migrationBuilder.DropTable(
                name: "course_modules");

            migrationBuilder.DropTable(
                name: "courses");
        }
    }
}
