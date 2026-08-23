using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLinkedReadingAndActivity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // 1. reading_map_items extensions
            migrationBuilder.AddColumn<int>(
                name: "lesson_id",
                table: "reading_map_items",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "task_id",
                table: "reading_map_items",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "status",
                table: "reading_map_items",
                type: "character varying(32)",
                maxLength: 32,
                nullable: false,
                defaultValue: "Planned");

            migrationBuilder.AddColumn<DateOnly>(
                name: "scheduled_for",
                table: "reading_map_items",
                type: "date",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "priority",
                table: "reading_map_items",
                type: "integer",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<bool>(
                name: "is_seeded",
                table: "reading_map_items",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<DateTime>(
                name: "archived_at",
                table: "reading_map_items",
                type: "timestamp with time zone",
                nullable: true);

            migrationBuilder.AddCheckConstraint(
                name: "ck_reading_map_status",
                table: "reading_map_items",
                sql: "status IN ('Planned', 'Reading', 'Completed', 'Revisited', 'Deferred', 'Archived')");

            migrationBuilder.AddCheckConstraint(
                name: "ck_reading_map_priority",
                table: "reading_map_items",
                sql: "priority BETWEEN 0 AND 100");

            migrationBuilder.CreateIndex(
                name: "ix_reading_map_status_schedule",
                table: "reading_map_items",
                columns: new[] { "status", "scheduled_for", "priority" });

            migrationBuilder.AddForeignKey(
                name: "FK_reading_map_items_lessons_lesson_id",
                table: "reading_map_items",
                column: "lesson_id",
                principalTable: "lessons",
                principalColumn: "id",
                onDelete: ReferentialAction.SetNull);

            migrationBuilder.AddForeignKey(
                name: "FK_reading_map_items_Tasks_task_id",
                table: "reading_map_items",
                column: "task_id",
                principalTable: "Tasks",
                principalColumn: "Id",
                onDelete: ReferentialAction.SetNull);

            // 2. learning_activity table
            migrationBuilder.CreateTable(
                name: "learning_activity",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    event_type = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    occurred_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()"),
                    lesson_id = table.Column<int>(type: "integer", nullable: true),
                    problem_id = table.Column<int>(type: "integer", nullable: true),
                    task_id = table.Column<int>(type: "integer", nullable: true),
                    reading_map_item_id = table.Column<int>(type: "integer", nullable: true),
                    correlation_id = table.Column<Guid>(type: "uuid", nullable: false),
                    metadata = table.Column<string>(type: "jsonb", nullable: false, defaultValueSql: "'{}'::jsonb")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_learning_activity", x => x.id);
                    table.CheckConstraint("ck_learning_activity_event_type", "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported')");
                    table.ForeignKey(
                        name: "FK_learning_activity_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_learning_activity_problems_problem_id",
                        column: x => x.problem_id,
                        principalTable: "problems",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_learning_activity_Tasks_task_id",
                        column: x => x.task_id,
                        principalTable: "Tasks",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_learning_activity_reading_map_items_reading_map_item_id",
                        column: x => x.reading_map_item_id,
                        principalTable: "reading_map_items",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateIndex(
                name: "ux_learning_activity_correlation_event",
                table: "learning_activity",
                columns: new[] { "correlation_id", "event_type" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_learning_activity_occurred_at",
                table: "learning_activity",
                column: "occurred_at");

            migrationBuilder.CreateIndex(
                name: "ix_learning_activity_lesson",
                table: "learning_activity",
                column: "lesson_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "learning_activity");
            migrationBuilder.DropForeignKey(name: "FK_reading_map_items_Tasks_task_id", table: "reading_map_items");
            migrationBuilder.DropForeignKey(name: "FK_reading_map_items_lessons_lesson_id", table: "reading_map_items");
            migrationBuilder.DropIndex(name: "ix_reading_map_status_schedule", table: "reading_map_items");
            migrationBuilder.DropCheckConstraint(name: "ck_reading_map_priority", table: "reading_map_items");
            migrationBuilder.DropCheckConstraint(name: "ck_reading_map_status", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "archived_at", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "is_seeded", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "priority", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "scheduled_for", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "status", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "task_id", table: "reading_map_items");
            migrationBuilder.DropColumn(name: "lesson_id", table: "reading_map_items");
        }
    }
}
