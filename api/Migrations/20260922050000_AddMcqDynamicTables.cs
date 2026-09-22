using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddMcqDynamicTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "mcq_questions",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    lesson_id = table.Column<int>(type: "integer", nullable: false),
                    legacy_key = table.Column<string>(type: "character varying(120)", maxLength: 120, nullable: true),
                    question_text = table.Column<string>(type: "text", nullable: false),
                    source_type = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    explanation = table.Column<string>(type: "text", nullable: false),
                    is_active = table.Column<bool>(type: "boolean", nullable: false, defaultValue: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mcq_questions", x => x.id);
                    table.ForeignKey(
                        name: "FK_mcq_questions_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "mcq_options",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    question_id = table.Column<int>(type: "integer", nullable: false),
                    option_key = table.Column<string>(type: "character varying(10)", maxLength: 10, nullable: false),
                    option_text = table.Column<string>(type: "text", nullable: false),
                    is_correct = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mcq_options", x => x.id);
                    table.ForeignKey(
                        name: "FK_mcq_options_mcq_questions_question_id",
                        column: x => x.question_id,
                        principalTable: "mcq_questions",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "mcq_presentations",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    question_id = table.Column<int>(type: "integer", nullable: false),
                    user_id = table.Column<int>(type: "integer", nullable: true),
                    displayed_option_order = table.Column<string>(type: "jsonb", nullable: false),
                    question_text_shown = table.Column<string>(type: "text", nullable: true),
                    presented_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mcq_presentations", x => x.id);
                    table.ForeignKey(
                        name: "FK_mcq_presentations_mcq_questions_question_id",
                        column: x => x.question_id,
                        principalTable: "mcq_questions",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_mcq_presentations_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "mcq_attempts",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    presentation_id = table.Column<Guid>(type: "uuid", nullable: false),
                    selected_option_key = table.Column<string>(type: "character varying(10)", maxLength: 10, nullable: false),
                    is_correct = table.Column<bool>(type: "boolean", nullable: false),
                    answered_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mcq_attempts", x => x.id);
                    table.ForeignKey(
                        name: "FK_mcq_attempts_mcq_presentations_presentation_id",
                        column: x => x.presentation_id,
                        principalTable: "mcq_presentations",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_mcq_questions_lesson_id",
                table: "mcq_questions",
                column: "lesson_id");

            migrationBuilder.CreateIndex(
                name: "ux_mcq_questions_legacy_key",
                table: "mcq_questions",
                column: "legacy_key",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_mcq_options_question_id",
                table: "mcq_options",
                column: "question_id");

            migrationBuilder.CreateIndex(
                name: "ix_mcq_presentations_question_id",
                table: "mcq_presentations",
                column: "question_id");

            migrationBuilder.CreateIndex(
                name: "ix_mcq_presentations_user_id",
                table: "mcq_presentations",
                column: "user_id");

            migrationBuilder.CreateIndex(
                name: "ux_mcq_attempts_presentation_id",
                table: "mcq_attempts",
                column: "presentation_id",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "mcq_attempts");

            migrationBuilder.DropTable(
                name: "mcq_presentations");

            migrationBuilder.DropTable(
                name: "mcq_options");

            migrationBuilder.DropTable(
                name: "mcq_questions");
        }
    }
}
