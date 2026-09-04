using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddTotpMfaChallenges : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<long>(
                name: "last_accepted_totp_counter",
                table: "app_users",
                type: "bigint",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "totp_enabled",
                table: "app_users",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<string>(
                name: "totp_secret_encrypted",
                table: "app_users",
                type: "text",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "mfa_challenges",
                columns: table => new
                {
                    id = table.Column<Guid>(type: "uuid", nullable: false),
                    user_id = table.Column<int>(type: "integer", nullable: false),
                    purpose = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    expires_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    consumed_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    failed_attempts = table.Column<int>(type: "integer", nullable: false, defaultValue: 0)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_mfa_challenges", x => x.id);
                    table.CheckConstraint("ck_mfa_challenges_purpose", "purpose IN ('Enrollment', 'Login')");
                    table.ForeignKey(
                        name: "FK_mfa_challenges_app_users_user_id",
                        column: x => x.user_id,
                        principalTable: "app_users",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_mfa_challenges_expires_at",
                table: "mfa_challenges",
                column: "expires_at");

            migrationBuilder.CreateIndex(
                name: "ix_mfa_challenges_user_id",
                table: "mfa_challenges",
                column: "user_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "mfa_challenges");

            migrationBuilder.DropColumn(
                name: "last_accepted_totp_counter",
                table: "app_users");

            migrationBuilder.DropColumn(
                name: "totp_enabled",
                table: "app_users");

            migrationBuilder.DropColumn(
                name: "totp_secret_encrypted",
                table: "app_users");
        }
    }
}
