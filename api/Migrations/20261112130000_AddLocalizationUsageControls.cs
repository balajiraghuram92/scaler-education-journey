using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLocalizationUsageControls : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "ai_enabled",
                table: "localization_projects",
                type: "boolean",
                nullable: false,
                defaultValue: true);

            migrationBuilder.CreateTable(
                name: "localization_usage_caps",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    kind = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    monthly_limit = table.Column<long>(type: "bigint", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_usage_caps", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_usage_caps_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ux_localization_usage_caps_project_kind",
                table: "localization_usage_caps",
                columns: new[] { "project_id", "kind" },
                unique: true);

            migrationBuilder.Sql(
                "UPDATE localization_workflow_steps SET action = 'Auto-Translate via Azure Translator' WHERE action = 'Auto-Translate via Google MT'");

            migrationBuilder.Sql(
                "UPDATE localization_provider_health SET provider = 'AzureTranslator' WHERE provider = 'GoogleMT'");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(
                "UPDATE localization_provider_health SET provider = 'GoogleMT' WHERE provider = 'AzureTranslator'");

            migrationBuilder.Sql(
                "UPDATE localization_workflow_steps SET action = 'Auto-Translate via Google MT' WHERE action = 'Auto-Translate via Azure Translator'");

            migrationBuilder.DropTable(
                name: "localization_usage_caps");

            migrationBuilder.DropColumn(
                name: "ai_enabled",
                table: "localization_projects");
        }
    }
}
