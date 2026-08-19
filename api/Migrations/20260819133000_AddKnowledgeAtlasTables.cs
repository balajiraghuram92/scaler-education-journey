using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace StudyTracker.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddKnowledgeAtlasTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "knowledge_domains",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    slug = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    code = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    description = table.Column<string>(type: "text", nullable: false),
                    icon = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    color_hex = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_knowledge_domains", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "knowledge_concepts",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    slug = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    title = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    sub_label = table.Column<string>(type: "text", nullable: false),
                    summary = table.Column<string>(type: "text", nullable: false),
                    description = table.Column<string>(type: "text", nullable: false),
                    difficulty = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    icon = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    estimated_hours = table.Column<int>(type: "integer", nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_knowledge_concepts", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "concept_next_lessons",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    concept_id = table.Column<int>(type: "integer", nullable: false),
                    lesson_title = table.Column<string>(type: "character varying(300)", maxLength: 300, nullable: false),
                    module_name = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    lesson_slug = table.Column<string>(type: "character varying(150)", maxLength: 150, nullable: false),
                    lesson_id = table.Column<int>(type: "integer", nullable: true),
                    order_index = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_concept_next_lessons", x => x.id);
                    table.ForeignKey(
                        name: "FK_concept_next_lessons_knowledge_concepts_concept_id",
                        column: x => x.concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_concept_next_lessons_lessons_lesson_id",
                        column: x => x.lesson_id,
                        principalTable: "lessons",
                        principalColumn: "id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "concept_prerequisites",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    concept_id = table.Column<int>(type: "integer", nullable: false),
                    prerequisite_concept_id = table.Column<int>(type: "integer", nullable: false),
                    status = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_concept_prerequisites", x => x.id);
                    table.ForeignKey(
                        name: "FK_concept_prerequisites_knowledge_concepts_concept_id",
                        column: x => x.concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_concept_prerequisites_knowledge_concepts_prerequisite_conce~",
                        column: x => x.prerequisite_concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "concept_relations",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    source_concept_id = table.Column<int>(type: "integer", nullable: false),
                    target_concept_id = table.Column<int>(type: "integer", nullable: false),
                    relationship_type = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_concept_relations", x => x.id);
                    table.ForeignKey(
                        name: "FK_concept_relations_knowledge_concepts_source_concept_id",
                        column: x => x.source_concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_concept_relations_knowledge_concepts_target_concept_id",
                        column: x => x.target_concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "domain_concept_connections",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    domain_id = table.Column<int>(type: "integer", nullable: false),
                    concept_id = table.Column<int>(type: "integer", nullable: false),
                    is_primary = table.Column<bool>(type: "boolean", nullable: false),
                    relevance_weight = table.Column<int>(type: "integer", nullable: false),
                    role_description = table.Column<string>(type: "character varying(250)", maxLength: 250, nullable: false),
                    order_index = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_domain_concept_connections", x => x.id);
                    table.ForeignKey(
                        name: "FK_domain_concept_connections_knowledge_concepts_concept_id",
                        column: x => x.concept_id,
                        principalTable: "knowledge_concepts",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_domain_concept_connections_knowledge_domains_domain_id",
                        column: x => x.domain_id,
                        principalTable: "knowledge_domains",
                        principalColumn: "id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_concept_next_lessons_concept_id",
                table: "concept_next_lessons",
                column: "concept_id");

            migrationBuilder.CreateIndex(
                name: "IX_concept_next_lessons_lesson_id",
                table: "concept_next_lessons",
                column: "lesson_id");

            migrationBuilder.CreateIndex(
                name: "IX_concept_prerequisites_concept_id_prerequisite_concept_id",
                table: "concept_prerequisites",
                columns: new[] { "concept_id", "prerequisite_concept_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_concept_prerequisites_prerequisite_concept_id",
                table: "concept_prerequisites",
                column: "prerequisite_concept_id");

            migrationBuilder.CreateIndex(
                name: "IX_concept_relations_source_concept_id_target_concept_id",
                table: "concept_relations",
                columns: new[] { "source_concept_id", "target_concept_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_concept_relations_target_concept_id",
                table: "concept_relations",
                column: "target_concept_id");

            migrationBuilder.CreateIndex(
                name: "IX_domain_concept_connections_concept_id",
                table: "domain_concept_connections",
                column: "concept_id");

            migrationBuilder.CreateIndex(
                name: "IX_domain_concept_connections_domain_id_concept_id",
                table: "domain_concept_connections",
                columns: new[] { "domain_id", "concept_id" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_knowledge_concepts_slug",
                table: "knowledge_concepts",
                column: "slug",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_knowledge_domains_code",
                table: "knowledge_domains",
                column: "code",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_knowledge_domains_slug",
                table: "knowledge_domains",
                column: "slug",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "concept_next_lessons");

            migrationBuilder.DropTable(
                name: "concept_prerequisites");

            migrationBuilder.DropTable(
                name: "concept_relations");

            migrationBuilder.DropTable(
                name: "domain_concept_connections");

            migrationBuilder.DropTable(
                name: "knowledge_concepts");

            migrationBuilder.DropTable(
                name: "knowledge_domains");
        }
    }
}
