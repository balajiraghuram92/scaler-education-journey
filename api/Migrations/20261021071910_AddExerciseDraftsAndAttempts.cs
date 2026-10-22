using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddExerciseDraftsAndAttempts : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity");

            migrationBuilder.CreateTable(
                name: "user_exercise_attempts",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    exercise_id = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    status = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    tests_total = table.Column<int>(type: "integer", nullable: false),
                    tests_passed = table.Column<int>(type: "integer", nullable: false),
                    duration_ms = table.Column<long>(type: "bigint", nullable: false),
                    files = table.Column<string>(type: "jsonb", nullable: false),
                    summary = table.Column<string>(type: "jsonb", nullable: false),
                    submitted_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_exercise_attempts", x => x.id);
                    table.CheckConstraint("ck_user_exercise_attempts_status", "status IN ('success', 'testFailure', 'compilationFailure', 'timeout')");
                    table.ForeignKey(
                        name: "FK_user_exercise_attempts_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_exercise_drafts",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    exercise_id = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: false),
                    files = table.Column<string>(type: "jsonb", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_exercise_drafts", x => x.id);
                    table.ForeignKey(
                        name: "FK_user_exercise_drafts_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.AddCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity",
                sql: "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported', 'LessonOpened', 'McqAnswered', 'ProblemAttempted', 'SolutionRevealed', 'ExerciseRun')");

            migrationBuilder.CreateIndex(
                name: "ix_user_exercise_attempts_user_exercise_time",
                table: "user_exercise_attempts",
                columns: new[] { "user_id", "exercise_id", "submitted_at" });

            migrationBuilder.CreateIndex(
                name: "ux_user_exercise_drafts_user_exercise",
                table: "user_exercise_drafts",
                columns: new[] { "user_id", "exercise_id" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "user_exercise_attempts");

            migrationBuilder.DropTable(
                name: "user_exercise_drafts");

            migrationBuilder.DropCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity");

            migrationBuilder.Sql("DELETE FROM learning_activity WHERE event_type = 'ExerciseRun';");

            migrationBuilder.AddCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity",
                sql: "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported', 'LessonOpened', 'McqAnswered', 'ProblemAttempted', 'SolutionRevealed')");
        }
    }
}
