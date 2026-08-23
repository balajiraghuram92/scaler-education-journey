using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class NormalizeKnowledgeThreads : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "knowledge_thread_steps",
                columns: table => new
                {
                    thread_id = table.Column<int>(type: "integer", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    concept_id = table.Column<int>(type: "integer", nullable: true),
                    lesson_id = table.Column<int>(type: "integer", nullable: true),
                    label = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false, defaultValueSql: "now()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_knowledge_thread_steps", x => new { x.thread_id, x.order_index });
                    table.CheckConstraint("ck_knowledge_thread_step_label", "length(trim(label)) > 0");
                    table.ForeignKey(
                        name: "FK_knowledge_thread_steps_knowledge_threads_thread_id",
                        column: x => x.thread_id,
                        principalTable: "knowledge_threads",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_knowledge_thread_steps_knowledge_concepts_concept_id",
                        column: x => x.concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_knowledge_thread_steps_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateIndex(
                name: "ix_knowledge_thread_steps_concept",
                table: "knowledge_thread_steps",
                column: "concept_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "knowledge_thread_steps");
        }
    }
}
