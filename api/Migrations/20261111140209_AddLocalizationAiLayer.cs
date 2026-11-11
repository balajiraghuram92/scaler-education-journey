using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddLocalizationAiLayer : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "comet_kiwi_score",
                table: "localization_translations",
                type: "numeric(5,4)",
                precision: 5,
                scale: 4,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "raw_mt_qps_score",
                table: "localization_translations",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "raw_mt_text",
                table: "localization_translations",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "qps_threshold",
                table: "localization_projects",
                type: "integer",
                nullable: false,
                defaultValue: 70);

            migrationBuilder.AddColumn<decimal>(
                name: "real_cost_usd",
                table: "localization_ledger_entries",
                type: "numeric(12,6)",
                precision: 12,
                scale: 6,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "unit_type",
                table: "localization_ledger_entries",
                type: "character varying(20)",
                maxLength: 20,
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "units_consumed",
                table: "localization_ledger_entries",
                type: "integer",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "localization_eval_golden_cases",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    source_text = table.Column<string>(type: "text", nullable: false),
                    gold_translation = table.Column<string>(type: "text", nullable: false),
                    category = table.Column<string>(type: "character varying(30)", maxLength: 30, nullable: false),
                    notes = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_eval_golden_cases", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_eval_golden_cases_localization_projects_projec~",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_eval_runs",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    pipeline_config = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    run_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    avg_comet_kiwi = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    avg_qps_score = table.Column<decimal>(type: "numeric(5,2)", precision: 5, scale: 2, nullable: true),
                    glossary_adherence_rate = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    placeholder_preservation_rate = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    cache_hit_rate = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    avg_latency_ms = table.Column<int>(type: "integer", nullable: true),
                    total_cost_usd = table.Column<decimal>(type: "numeric(12,6)", precision: 12, scale: 6, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_eval_runs", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_eval_runs_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_glossary_terms",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    source_term = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    target_term = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    notes = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_glossary_terms", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_glossary_terms_localization_projects_project_id",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_translation_cache_entries",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    project_id = table.Column<int>(type: "integer", nullable: false),
                    locale_code = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    source_text = table.Column<string>(type: "text", nullable: false),
                    cached_translation = table.Column<string>(type: "text", nullable: false),
                    hit_count = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    last_hit_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_translation_cache_entries", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_translation_cache_entries_localization_project~",
                        column: x => x.project_id,
                        principalTable: "localization_projects",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "localization_eval_case_results",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    eval_run_id = table.Column<int>(type: "integer", nullable: false),
                    eval_golden_case_id = table.Column<int>(type: "integer", nullable: false),
                    produced_translation = table.Column<string>(type: "text", nullable: false),
                    comet_kiwi_score = table.Column<decimal>(type: "numeric(5,4)", precision: 5, scale: 4, nullable: true),
                    qps_score = table.Column<int>(type: "integer", nullable: true),
                    glossary_adherence_ok = table.Column<bool>(type: "boolean", nullable: true),
                    placeholder_preserved_ok = table.Column<bool>(type: "boolean", nullable: true),
                    latency_ms = table.Column<int>(type: "integer", nullable: true),
                    cache_hit = table.Column<bool>(type: "boolean", nullable: true),
                    cost_usd = table.Column<decimal>(type: "numeric(12,6)", precision: 12, scale: 6, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_localization_eval_case_results", x => x.id);
                    table.ForeignKey(
                        name: "FK_localization_eval_case_results_localization_eval_golden_cas~",
                        column: x => x.eval_golden_case_id,
                        principalTable: "localization_eval_golden_cases",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_localization_eval_case_results_localization_eval_runs_eval_~",
                        column: x => x.eval_run_id,
                        principalTable: "localization_eval_runs",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "ix_localization_eval_case_results_case_id",
                table: "localization_eval_case_results",
                column: "eval_golden_case_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_eval_case_results_run_id",
                table: "localization_eval_case_results",
                column: "eval_run_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_eval_golden_cases_project_id",
                table: "localization_eval_golden_cases",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_eval_golden_cases_project_locale",
                table: "localization_eval_golden_cases",
                columns: new[] { "project_id", "locale_code" });

            migrationBuilder.CreateIndex(
                name: "ix_localization_eval_runs_project_id",
                table: "localization_eval_runs",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_glossary_terms_project_id",
                table: "localization_glossary_terms",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_glossary_terms_project_locale",
                table: "localization_glossary_terms",
                columns: new[] { "project_id", "locale_code" });

            migrationBuilder.CreateIndex(
                name: "ix_localization_translation_cache_project_id",
                table: "localization_translation_cache_entries",
                column: "project_id");

            migrationBuilder.CreateIndex(
                name: "ix_localization_translation_cache_project_locale",
                table: "localization_translation_cache_entries",
                columns: new[] { "project_id", "locale_code" });

            // The embedding column is not mapped in EF (no pgvector package is
            // referenced); only the Python localization-ai service reads and
            // writes it. 384 dimensions matches its embedding model.
            migrationBuilder.Sql("CREATE EXTENSION IF NOT EXISTS vector;");
            migrationBuilder.Sql(
                "ALTER TABLE localization_translation_cache_entries " +
                "ADD COLUMN source_embedding vector(384) NULL;");
            migrationBuilder.Sql(
                "CREATE INDEX ix_localization_translation_cache_embedding_hnsw " +
                "ON localization_translation_cache_entries " +
                "USING hnsw (source_embedding vector_cosine_ops);");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "localization_eval_case_results");

            migrationBuilder.DropTable(
                name: "localization_glossary_terms");

            migrationBuilder.DropTable(
                name: "localization_translation_cache_entries");

            migrationBuilder.DropTable(
                name: "localization_eval_golden_cases");

            migrationBuilder.DropTable(
                name: "localization_eval_runs");

            migrationBuilder.DropColumn(
                name: "comet_kiwi_score",
                table: "localization_translations");

            migrationBuilder.DropColumn(
                name: "raw_mt_qps_score",
                table: "localization_translations");

            migrationBuilder.DropColumn(
                name: "raw_mt_text",
                table: "localization_translations");

            migrationBuilder.DropColumn(
                name: "qps_threshold",
                table: "localization_projects");

            migrationBuilder.DropColumn(
                name: "real_cost_usd",
                table: "localization_ledger_entries");

            migrationBuilder.DropColumn(
                name: "unit_type",
                table: "localization_ledger_entries");

            migrationBuilder.DropColumn(
                name: "units_consumed",
                table: "localization_ledger_entries");
        }
    }
}
