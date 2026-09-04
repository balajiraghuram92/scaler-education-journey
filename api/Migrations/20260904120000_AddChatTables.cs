using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddChatTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "chat_conversations",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    lesson_id = table.Column<int>(type: "integer", nullable: true),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_chat_conversations", x => x.id);
                    table.ForeignKey(
                        name: "FK_chat_conversations_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_chat_conversations_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "chat_messages",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    conversation_id = table.Column<Guid>(type: "uuid", nullable: false),
                    role = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    content = table.Column<string>(type: "text", nullable: false),
                    client_request_id = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: true),
                    prompt_tokens = table.Column<int>(type: "integer", nullable: true),
                    completion_tokens = table.Column<int>(type: "integer", nullable: true),
                    usage_estimated = table.Column<bool>(type: "boolean", nullable: false, defaultValue: false),
                    estimated_cost_usd = table.Column<decimal>(type: "numeric(10,6)", nullable: true),
                    latency_ms = table.Column<int>(type: "integer", nullable: true),
                    error_message = table.Column<string>(type: "text", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_chat_messages", x => x.id);
                    table.CheckConstraint("ck_chat_messages_role", "role IN ('system', 'user', 'assistant')");
                    table.ForeignKey(
                        name: "FK_chat_messages_chat_conversations_conversation_id",
                        column: x => x.conversation_id,
                        principalTable: "chat_conversations",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_chat_conversations_lesson_id",
                table: "chat_conversations",
                column: "lesson_id");

            migrationBuilder.CreateIndex(
                name: "ix_chat_conversations_updated_at",
                table: "chat_conversations",
                column: "updated_at");

            migrationBuilder.CreateIndex(
                name: "ix_chat_conversations_user_id",
                table: "chat_conversations",
                column: "user_id");

            migrationBuilder.CreateIndex(
                name: "ix_chat_messages_client_request_id",
                table: "chat_messages",
                column: "client_request_id");

            migrationBuilder.CreateIndex(
                name: "ix_chat_messages_conversation_id",
                table: "chat_messages",
                column: "conversation_id");

            migrationBuilder.CreateIndex(
                name: "ix_chat_messages_created_at",
                table: "chat_messages",
                column: "created_at");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "chat_messages");
            migrationBuilder.DropTable(name: "chat_conversations");
        }
    }
}
