using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <summary>
    /// Session management (user_sessions) and per-learner state (user_lesson_progress,
    /// user_problem_progress, owner columns on lesson_notes / learning_activity), plus
    /// MCQ categories and Python assignment fields on problems.
    ///
    /// Hand-trimmed: earlier migrations did not keep the model snapshot in sync, so the
    /// scaffolded version also tried to re-create mcq_* tables and drop unrelated column
    /// defaults. Only this change set is applied here; the snapshot is now current.
    /// </summary>
    public partial class AddSessionsAndLearnerProgress : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            // --- MCQ categories -------------------------------------------------------
            migrationBuilder.AddColumn<string>(
                name: "category",
                table: "mcq_questions",
                type: "character varying(30)",
                maxLength: 30,
                nullable: false,
                defaultValue: "Assignment");

            // --- Python assignment fields on problems ----------------------------------
            migrationBuilder.AddColumn<string>(
                name: "language",
                table: "problems",
                type: "character varying(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "java");

            migrationBuilder.AddColumn<string>(
                name: "run_command",
                table: "problems",
                type: "character varying(200)",
                maxLength: 200,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "reference_solution",
                table: "problems",
                type: "text",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "source_type",
                table: "problems",
                type: "character varying(30)",
                maxLength: 30,
                nullable: false,
                defaultValue: "FROM_MATERIAL");

            // --- Owners on notes and activity ------------------------------------------
            migrationBuilder.AddColumn<int>(
                name: "user_id",
                table: "lesson_notes",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "user_id",
                table: "learning_activity",
                type: "integer",
                nullable: true);

            migrationBuilder.DropCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity");

            migrationBuilder.AddCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity",
                sql: "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported', 'LessonOpened', 'McqAnswered', 'ProblemAttempted', 'SolutionRevealed')");

            // --- New tables ------------------------------------------------------------
            migrationBuilder.CreateTable(
                name: "user_sessions",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    refresh_token_hash = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    previous_refresh_token_hash = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: true),
                    rotated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    remember_me = table.Column<bool>(type: "boolean", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    last_seen_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    expires_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    revoked_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    revoked_reason = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: true),
                    user_agent = table.Column<string>(type: "character varying(400)", maxLength: 400, nullable: true),
                    ip_address = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_sessions", x => x.id);
                    table.ForeignKey(
                        name: "FK_user_sessions_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_lesson_progress",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    lesson_id = table.Column<int>(type: "integer", nullable: false),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    first_opened_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    last_opened_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    completed_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    last_section_id = table.Column<string>(type: "character varying(160)", maxLength: 160, nullable: true),
                    scroll_percent = table.Column<int>(type: "integer", nullable: false),
                    visit_count = table.Column<int>(type: "integer", nullable: false),
                    time_spent_seconds = table.Column<int>(type: "integer", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_lesson_progress", x => x.id);
                    table.CheckConstraint("ck_user_lesson_progress_scroll", "scroll_percent >= 0 AND scroll_percent <= 100");
                    table.CheckConstraint("ck_user_lesson_progress_status", "status IN ('InProgress', 'Completed')");
                    table.ForeignKey(
                        name: "FK_user_lesson_progress_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_lesson_progress_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "user_problem_progress",
                columns: table => new
                {
                    id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    problem_id = table.Column<int>(type: "integer", nullable: false),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    solution_revealed_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    solved_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_user_problem_progress", x => x.id);
                    table.CheckConstraint("ck_user_problem_progress_status", "status IN ('NotStarted', 'Attempted', 'Solved')");
                    table.ForeignKey(
                        name: "FK_user_problem_progress_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_user_problem_progress_problems_problem_id",
                        column: x => x.problem_id,
                        principalTable: "problems",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            // --- Indexes & foreign keys ------------------------------------------------
            migrationBuilder.CreateIndex(name: "ux_user_sessions_refresh_token_hash", table: "user_sessions", column: "refresh_token_hash", unique: true);
            migrationBuilder.CreateIndex(name: "ix_user_sessions_previous_refresh_token_hash", table: "user_sessions", column: "previous_refresh_token_hash");
            migrationBuilder.CreateIndex(name: "ix_user_sessions_user_active", table: "user_sessions", columns: new[] { "user_id", "revoked_at" });

            migrationBuilder.CreateIndex(name: "ux_user_lesson_progress_user_lesson", table: "user_lesson_progress", columns: new[] { "user_id", "lesson_id" }, unique: true);
            migrationBuilder.CreateIndex(name: "ix_user_lesson_progress_user_recent", table: "user_lesson_progress", columns: new[] { "user_id", "last_opened_at" });
            migrationBuilder.CreateIndex(name: "IX_user_lesson_progress_lesson_id", table: "user_lesson_progress", column: "lesson_id");

            migrationBuilder.CreateIndex(name: "ux_user_problem_progress_user_problem", table: "user_problem_progress", columns: new[] { "user_id", "problem_id" }, unique: true);
            migrationBuilder.CreateIndex(name: "IX_user_problem_progress_problem_id", table: "user_problem_progress", column: "problem_id");

            migrationBuilder.CreateIndex(name: "ix_lesson_notes_user_lesson", table: "lesson_notes", columns: new[] { "user_id", "lesson_id" });
            migrationBuilder.CreateIndex(name: "ix_learning_activity_user", table: "learning_activity", columns: new[] { "user_id", "occurred_at" });

            migrationBuilder.AddForeignKey(
                name: "FK_lesson_notes_app_users_user_id",
                table: "lesson_notes",
                column: "user_id",
                principalTable: "app_users",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_learning_activity_app_users_user_id",
                table: "learning_activity",
                column: "user_id",
                principalTable: "app_users",
                principalColumn: "id",
                onDelete: ReferentialAction.Cascade);

            // --- Data: hand existing global progress to the site owner -------------------
            // Completion used to be a single global flag per lesson/problem. Those rows were
            // the owner's own study, so they move to the first Admin account. No admin, no-op.
            migrationBuilder.Sql(@"
INSERT INTO user_lesson_progress (user_id, lesson_id, status, first_opened_at, last_opened_at, completed_at, last_section_id, scroll_percent, visit_count, time_spent_seconds, updated_at)
SELECT a.id, l.id, 'Completed', l.updated_at, l.updated_at, l.updated_at, NULL, 100, 1, 0, now()
FROM lessons l
CROSS JOIN (SELECT id FROM app_users WHERE role = 'Admin' ORDER BY id LIMIT 1) a
WHERE l.is_completed = TRUE
ON CONFLICT (user_id, lesson_id) DO NOTHING;

INSERT INTO user_problem_progress (user_id, problem_id, status, solution_revealed_at, solved_at, created_at, updated_at)
SELECT a.id, p.id, 'Solved', NULL, p.updated_at, now(), now()
FROM problems p
CROSS JOIN (SELECT id FROM app_users WHERE role = 'Admin' ORDER BY id LIMIT 1) a
WHERE p.is_completed = TRUE
ON CONFLICT (user_id, problem_id) DO NOTHING;

UPDATE lesson_notes
SET user_id = (SELECT id FROM app_users WHERE role = 'Admin' ORDER BY id LIMIT 1)
WHERE note_type = 'PersonalNote' AND user_id IS NULL;
");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(name: "FK_learning_activity_app_users_user_id", table: "learning_activity");
            migrationBuilder.DropForeignKey(name: "FK_lesson_notes_app_users_user_id", table: "lesson_notes");

            migrationBuilder.DropTable(name: "user_problem_progress");
            migrationBuilder.DropTable(name: "user_lesson_progress");
            migrationBuilder.DropTable(name: "user_sessions");

            migrationBuilder.DropIndex(name: "ix_learning_activity_user", table: "learning_activity");
            migrationBuilder.DropIndex(name: "ix_lesson_notes_user_lesson", table: "lesson_notes");

            migrationBuilder.DropCheckConstraint(name: "ck_learning_activity_event_type", table: "learning_activity");
            migrationBuilder.Sql("DELETE FROM learning_activity WHERE event_type IN ('LessonOpened', 'McqAnswered', 'ProblemAttempted', 'SolutionRevealed');");
            migrationBuilder.AddCheckConstraint(
                name: "ck_learning_activity_event_type",
                table: "learning_activity",
                sql: "event_type IN ('LessonCompleted', 'LessonReopened', 'ProblemCompleted', 'ProblemReopened', 'TaskCompleted', 'TaskReopened', 'ReadingScheduled', 'ReadingDeferred', 'ReadingRevisited', 'NoteCreated', 'ChapterImported')");

            migrationBuilder.DropColumn(name: "user_id", table: "learning_activity");
            migrationBuilder.DropColumn(name: "user_id", table: "lesson_notes");
            migrationBuilder.DropColumn(name: "source_type", table: "problems");
            migrationBuilder.DropColumn(name: "reference_solution", table: "problems");
            migrationBuilder.DropColumn(name: "run_command", table: "problems");
            migrationBuilder.DropColumn(name: "language", table: "problems");
            migrationBuilder.DropColumn(name: "category", table: "mcq_questions");
        }
    }
}
