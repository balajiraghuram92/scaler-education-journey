using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLocalizationUsageMetering : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "localization_usage_events",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    workflow_step_id = table.Column<int>(type: "integer", nullable: true),
                    meter = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    operation = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: true),
                    units = table.Column<int>(type: "integer", nullable: false),
                    units_out = table.Column<int>(type: "integer", nullable: true),
                    cache_hit = table.Column<bool>(type: "boolean", nullable: false),
                    succeeded = table.Column<bool>(type: "boolean", nullable: false),
                    cost_usd = table.Column<decimal>(type: "numeric(12,6)", precision: 12, scale: 6, nullable: false),
                    occurred_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_usage_events", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_usage_events_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_localization_usage_events_localization_workflow_steps_workf~",
                        column: x => x.workflow_step_id,
                        principalTable: "localization_workflow_steps",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "localization_provider_rates",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    meter = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    unit_kind = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    usd_per_million = table.Column<decimal>(type: "numeric(12,6)", precision: 12, scale: 6, nullable: false),
                    valid_from = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_provider_rates", x => x.id);
                });

            migrationBuilder.CreateIndex(
                name: "ix_localization_usage_events_project_occurred",
                table: "localization_usage_events",
                columns: new[] { "project_id", "occurred_at" });

            migrationBuilder.CreateIndex(
                name: "ix_localization_usage_events_meter_occurred",
                table: "localization_usage_events",
                columns: new[] { "meter", "occurred_at" });

            migrationBuilder.CreateIndex(
                name: "ix_localization_usage_events_workflow_step_id",
                table: "localization_usage_events",
                column: "workflow_step_id");

            migrationBuilder.CreateIndex(
                name: "ux_localization_provider_rates_meter_kind_from",
                table: "localization_provider_rates",
                columns: new[] { "meter", "unit_kind", "valid_from" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "localization_provider_rates");

            migrationBuilder.DropTable(
                name: "localization_usage_events");
        }
    }
}
