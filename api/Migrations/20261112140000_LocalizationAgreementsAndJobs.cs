using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class LocalizationAgreementsAndJobs : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "alias",
                table: "localization_vendors",
                type: "character varying(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "client_alias",
                table: "localization_projects",
                type: "character varying(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.Sql("UPDATE localization_vendors SET alias = 'Vendor Team ' || id");
            migrationBuilder.Sql("UPDATE localization_projects SET client_alias = 'Client Team ' || id");

            migrationBuilder.AlterColumn<string>(
                name: "alias",
                table: "localization_vendors",
                type: "character varying(100)",
                maxLength: 100,
                nullable: false,
                oldClrType: typeof(string),
                oldType: "character varying(100)",
                oldMaxLength: 100,
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "client_alias",
                table: "localization_projects",
                type: "character varying(100)",
                maxLength: 100,
                nullable: false,
                oldClrType: typeof(string),
                oldType: "character varying(100)",
                oldMaxLength: 100,
                oldNullable: true);

            migrationBuilder.CreateIndex(
                name: "ux_localization_vendors_alias",
                table: "localization_vendors",
                column: "alias",
                unique: true);

            migrationBuilder.CreateTable(
                name: "localization_service_agreements",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    tier = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    valid_from = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    valid_to = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    notes = table.Column<string>(type: "text", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_service_agreements", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_service_agreements_localization_projects_proje~",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_team_assignments",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    agreement_id = table.Column<int>(type: "integer", nullable: false),
                    vendor_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    member_count = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_team_assignments", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_team_assignments_localization_service_agreeme~",
                        column: x => x.agreement_id,
                        principalTable: "localization_service_agreements",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_localization_team_assignments_vendors_vendor_id",
                        column: x => x.vendor_id,
                        principalTable: "localization_vendors",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "ux_localization_service_agreements_project_id",
                table: "localization_service_agreements",
                column: "project_id",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ux_localization_team_assignments_agreement_locale",
                table: "localization_team_assignments",
                columns: new[] { "agreement_id", "locale_code" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_localization_team_assignments_vendor_id",
                table: "localization_team_assignments",
                column: "vendor_id");

            migrationBuilder.Sql("UPDATE localization_translations SET qps_score = NULL");
            migrationBuilder.Sql("UPDATE localization_translations SET raw_mt_qps_score = NULL");
            migrationBuilder.Sql("UPDATE localization_translations SET needs_review = false");

            migrationBuilder.Sql("UPDATE localization_projects SET qps_threshold = 4");
            migrationBuilder.AlterColumn<int>(
                name: "qps_threshold",
                table: "localization_projects",
                type: "integer",
                nullable: false,
                defaultValue: 4,
                oldClrType: typeof(int),
                oldType: "integer",
                oldDefaultValue: 70);

            migrationBuilder.Sql("UPDATE localization_workflow_steps SET action = 'Create Translation Jobs' WHERE action = 'Post to Marketplace'");
            migrationBuilder.Sql("UPDATE localization_workflow_steps SET action = 'Score Quality' WHERE action = 'Score QPS'");

            migrationBuilder.Sql("UPDATE localization_marketplace_jobs SET status = 'Assigned' WHERE status = 'Open'");
            migrationBuilder.Sql("UPDATE localization_marketplace_jobs SET status = 'Assigned' WHERE status = 'Awarded'");
            migrationBuilder.Sql("DELETE FROM localization_marketplace_jobs WHERE awarded_vendor_id IS NULL");

            migrationBuilder.AddCheckConstraint(
                name: "ck_localization_translations_qps_score_range",
                table: "localization_translations",
                sql: "qps_score IS NULL OR (qps_score BETWEEN 1 AND 5)");

            migrationBuilder.AddCheckConstraint(
                name: "ck_localization_translations_raw_mt_qps_score_range",
                table: "localization_translations",
                sql: "raw_mt_qps_score IS NULL OR (raw_mt_qps_score BETWEEN 1 AND 5)");

            migrationBuilder.DropTable(
                name: "localization_marketplace_bids");

            migrationBuilder.DropColumn(
                name: "suggested_price_low",
                table: "localization_marketplace_jobs");

            migrationBuilder.DropColumn(
                name: "suggested_price_high",
                table: "localization_marketplace_jobs");

            migrationBuilder.DropColumn(
                name: "awarded_at",
                table: "localization_marketplace_jobs");

            migrationBuilder.DropColumn(
                name: "rating",
                table: "localization_vendors");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            // Down restores the schema only. Deleted data (bids, vendorless jobs),
            // nulled scores, cleared review flags, overwritten thresholds and the
            // original Open/Awarded statuses cannot be restored.
            migrationBuilder.AddColumn<decimal>(
                name: "suggested_price_low",
                table: "localization_marketplace_jobs",
                type: "numeric(10,2)",
                precision: 10,
                scale: 2,
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.AddColumn<decimal>(
                name: "suggested_price_high",
                table: "localization_marketplace_jobs",
                type: "numeric(10,2)",
                precision: 10,
                scale: 2,
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.AddColumn<DateTime>(
                name: "awarded_at",
                table: "localization_marketplace_jobs",
                type: "timestamp with time zone",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "rating",
                table: "localization_vendors",
                type: "numeric(3,1)",
                precision: 3,
                scale: 1,
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.CreateTable(
                name: "localization_marketplace_bids",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    marketplace_job_id = table.Column<int>(type: "integer", nullable: false),
                    vendor_id = table.Column<int>(type: "integer", nullable: false),
                    proposed_price = table.Column<decimal>(type: "numeric(10,2)", precision: 10, scale: 2, nullable: false),
                    note = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: false),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    submitted_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_marketplace_bids", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_marketplace_bids_localization_marketplace_jobs_marketplace_job_id",
                        column: x => x.marketplace_job_id,
                        principalTable: "localization_marketplace_jobs",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_localization_marketplace_bids_localization_vendors_vendor_id",
                        column: x => x.vendor_id,
                        principalTable: "localization_vendors",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_bids_job_id",
                table: "localization_marketplace_bids",
                column: "marketplace_job_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_bids_vendor_id",
                table: "localization_marketplace_bids",
                column: "vendor_id");

            migrationBuilder.DropCheckConstraint(
                name: "ck_localization_translations_qps_score_range",
                table: "localization_translations");

            migrationBuilder.DropCheckConstraint(
                name: "ck_localization_translations_raw_mt_qps_score_range",
                table: "localization_translations");

            migrationBuilder.Sql("UPDATE localization_workflow_steps SET action = 'Post to Marketplace' WHERE action = 'Create Translation Jobs'");
            migrationBuilder.Sql("UPDATE localization_workflow_steps SET action = 'Score QPS' WHERE action = 'Score Quality'");

            migrationBuilder.AlterColumn<int>(
                name: "qps_threshold",
                table: "localization_projects",
                type: "integer",
                nullable: false,
                defaultValue: 70,
                oldClrType: typeof(int),
                oldType: "integer",
                oldDefaultValue: 4);

            migrationBuilder.DropTable(
                name: "localization_team_assignments");

            migrationBuilder.DropTable(
                name: "localization_service_agreements");

            migrationBuilder.DropIndex(
                name: "ux_localization_vendors_alias",
                table: "localization_vendors");

            migrationBuilder.DropColumn(
                name: "alias",
                table: "localization_vendors");

            migrationBuilder.DropColumn(
                name: "client_alias",
                table: "localization_projects");
        }
    }
}
