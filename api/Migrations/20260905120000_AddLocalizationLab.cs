using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLocalizationLab : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "localization_projects",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    slug = table.Column<string>(type: "character varying(150)", maxLength: 150, nullable: false),
                    name = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    source_locale = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_projects", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "localization_vendors",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    name = table.Column<string>(type: "character varying(150)", maxLength: 150, nullable: false),
                    languages = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    rating = table.Column<decimal>(type: "numeric(3,1)", precision: 3, scale: 1, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_vendors", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "localization_provider_health",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    provider = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    p50_latency_ms = table.Column<int>(type: "integer", nullable: false),
                    p99_latency_ms = table.Column<int>(type: "integer", nullable: false),
                    error_rate_percent = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: false),
                    circuit_state = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_provider_health", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "localization_locales",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    display_name = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_locales", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_locales_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_strings",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    key = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    source_text = table.Column<string>(type: "text", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_strings", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_strings_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_workflow_steps",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    order = table.Column<int>(type: "integer", nullable: false),
                    trigger = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    action = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    condition_expression = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    last_run_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    last_run_outcome = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_workflow_steps", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_workflow_steps_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_build_snapshots",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    snapshot_identifier = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    source_revision = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    localization_revision = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    config = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_build_snapshots", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_build_snapshots_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_marketplace_jobs",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    string_count = table.Column<int>(type: "integer", nullable: false),
                    word_count = table.Column<int>(type: "integer", nullable: false),
                    suggested_price_low = table.Column<decimal>(type: "numeric(10,2)", precision: 10, scale: 2, nullable: false),
                    suggested_price_high = table.Column<decimal>(type: "numeric(10,2)", precision: 10, scale: 2, nullable: false),
                    awarded_vendor_id = table.Column<int>(type: "integer", nullable: true),
                    posted_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    awarded_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    submitted_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    approved_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_marketplace_jobs", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_marketplace_jobs_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_localization_marketplace_jobs_localization_vendors_awarded_vendor_id",
                        column: x => x.awarded_vendor_id,
                        principalTable: "localization_vendors",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "localization_translations",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    string_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    target_text = table.Column<string>(type: "text", nullable: true),
                    stage = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    translation_source = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    qps_score = table.Column<int>(type: "integer", nullable: true),
                    needs_review = table.Column<bool>(type: "boolean", nullable: false, defaultValue: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_translations", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_translations_localization_strings_string_id",
                        column: x => x.string_id,
                        principalTable: "localization_strings",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_build_snapshot_locale_counts",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    build_snapshot_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    approved_count = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_build_snapshot_locale_counts", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_build_snapshot_locale_counts_localization_build_snapshots_build_snapshot_id",
                        column: x => x.build_snapshot_id,
                        principalTable: "localization_build_snapshots",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

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

            migrationBuilder.CreateTable(
                name: "localization_ledger_entries",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    source = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    amount = table.Column<decimal>(type: "numeric(10,2)", precision: 10, scale: 2, nullable: false),
                    related_marketplace_job_id = table.Column<int>(type: "integer", nullable: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_ledger_entries", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_ledger_entries_localization_marketplace_jobs_related_marketplace_job_id",
                        column: x => x.related_marketplace_job_id,
                        principalTable: "localization_marketplace_jobs",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                    table.ForeignKey(
                        name: "FK_localization_ledger_entries_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_localization_projects_slug",
                table: "localization_projects",
                column: "slug",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_localization_locales_project_id",
                table: "localization_locales",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_strings_project_id",
                table: "localization_strings",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_translations_string_id_locale_code",
                table: "localization_translations",
                columns: new[] { "string_id", "locale_code" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "ix_localization_workflow_steps_project_id",
                table: "localization_workflow_steps",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_build_snapshots_project_id",
                table: "localization_build_snapshots",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_build_snapshot_locale_counts_snapshot_id",
                table: "localization_build_snapshot_locale_counts",
                column: "build_snapshot_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_jobs_project_id",
                table: "localization_marketplace_jobs",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_jobs_vendor_id",
                table: "localization_marketplace_jobs",
                column: "awarded_vendor_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_bids_job_id",
                table: "localization_marketplace_bids",
                column: "marketplace_job_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_marketplace_bids_vendor_id",
                table: "localization_marketplace_bids",
                column: "vendor_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_ledger_entries_project_id",
                table: "localization_ledger_entries",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_ledger_entries_job_id",
                table: "localization_ledger_entries",
                column: "related_marketplace_job_id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(name: "localization_ledger_entries");
            migrationBuilder.DropTable(name: "localization_marketplace_bids");
            migrationBuilder.DropTable(name: "localization_build_snapshot_locale_counts");
            migrationBuilder.DropTable(name: "localization_translations");
            migrationBuilder.DropTable(name: "localization_marketplace_jobs");
            migrationBuilder.DropTable(name: "localization_build_snapshots");
            migrationBuilder.DropTable(name: "localization_workflow_steps");
            migrationBuilder.DropTable(name: "localization_strings");
            migrationBuilder.DropTable(name: "localization_locales");
            migrationBuilder.DropTable(name: "localization_provider_health");
            migrationBuilder.DropTable(name: "localization_vendors");
            migrationBuilder.DropTable(name: "localization_projects");
        }
    }
}
