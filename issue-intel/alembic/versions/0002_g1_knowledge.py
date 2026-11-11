"""G1 knowledge tables: cases, threads, changes, chunks, links, ACLs, RLS.

Revision ID: 0002_g1_knowledge
Revises: 0001_g0_base
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_g1_knowledge"
down_revision: str | None = "0001_g0_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tables carrying acl_id. FORCE ROW LEVEL SECURITY so the table owner (the app
# role) is filtered too; an unset context fails closed (current_setting -> NULL).
RLS_TABLES = ("cases", "threads", "messages", "changes", "chunks")

POLICY_SQL = """
CREATE POLICY {table}_entitlement ON {table} FOR ALL USING (
  EXISTS (
    SELECT 1 FROM acls a
    WHERE a.id = {table}.acl_id
      AND a.restriction <= current_setting('app.max_restriction', true)::int
      AND string_to_array(a.modules, ',') && string_to_array(current_setting('app.modules', true), ',')
      AND string_to_array(a.departments, ',') && string_to_array(current_setting('app.departments', true), ',')
  )
);
"""


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "acls",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("modules", sa.Text(), nullable=False),
        sa.Column("departments", sa.Text(), nullable=False),
        sa.Column("restriction", sa.Integer(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
    )
    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("handle", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("team", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.Text(), nullable=False, unique=True),
        sa.Column("display_name", sa.Text(), nullable=False),
    )
    op.create_table(
        "entitlements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("modules", sa.Text(), nullable=False),
        sa.Column("departments", sa.Text(), nullable=False),
        sa.Column("max_restriction", sa.Integer(), nullable=False),
    )
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_key", sa.Text(), nullable=False),
        sa.Column("module", sa.Text(), nullable=False),
        sa.Column("filed_module", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("raw_resolution", sa.Text(), nullable=False, server_default=""),
        sa.Column("outcome", sa.Text(), nullable=False, server_default="UNKNOWN"),
        sa.Column("fixed_change", sa.Text(), nullable=False, server_default=""),
        sa.Column("customer_ref", sa.Text(), nullable=False, server_default=""),
        sa.Column("acl_id", sa.Integer(), sa.ForeignKey("acls.id"), nullable=False),
        sa.UniqueConstraint("source", "source_key", name="uq_cases_source_key"),
    )
    op.create_table(
        "threads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.Text(), nullable=False, unique=True),
        sa.Column("case_source", sa.Text(), nullable=False),
        sa.Column("case_key", sa.Text(), nullable=False),
        sa.Column("acl_id", sa.Integer(), sa.ForeignKey("acls.id"), nullable=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("thread_id", sa.Integer(), sa.ForeignKey("threads.id"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("author", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("acl_id", sa.Integer(), sa.ForeignKey("acls.id"), nullable=False),
        sa.UniqueConstraint("thread_id", "seq", name="uq_messages_thread_seq"),
    )
    op.create_table(
        "changes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ref", sa.Text(), nullable=False, unique=True),
        sa.Column("repo", sa.Text(), nullable=False),
        sa.Column("author", sa.Text(), nullable=False),
        sa.Column("reviewers", sa.Text(), nullable=False, server_default=""),
        sa.Column("files", sa.Text(), nullable=False, server_default=""),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("legacy_id", sa.Text(), nullable=False, server_default=""),
        sa.Column("planned_seq", sa.Integer(), nullable=True),
        sa.Column("acl_id", sa.Integer(), sa.ForeignKey("acls.id"), nullable=False),
    )
    # VECTOR(64) must match Settings.embedding_dim default.
    op.execute(
        "CREATE TABLE chunks (id SERIAL PRIMARY KEY, owner_type TEXT NOT NULL,"
        " owner_key TEXT NOT NULL, seq INTEGER NOT NULL, text TEXT NOT NULL,"
        " embedding vector(64) NOT NULL, tsv TSVECTOR NOT NULL,"
        " acl_id INTEGER NOT NULL REFERENCES acls(id),"
        " UNIQUE (owner_type, owner_key, seq))"
    )
    op.execute(
        "CREATE INDEX ix_chunks_embedding_hnsw ON chunks"
        " USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute("CREATE INDEX ix_chunks_tsv ON chunks USING gin (tsv)")
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("from_type", sa.Text(), nullable=False),
        sa.Column("from_key", sa.Text(), nullable=False),
        sa.Column("to_type", sa.Text(), nullable=False),
        sa.Column("to_key", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False, server_default=""),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "from_type", "from_key", "to_type", "to_key", "kind",
            name="uq_links_endpoints_kind",
        ),
    )
    op.create_table(
        "ownership",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("target", sa.Text(), nullable=False),
        sa.Column("owner_handle", sa.Text(), nullable=False),
        sa.UniqueConstraint("scope", "target", name="uq_ownership_scope_target"),
    )
    op.create_table(
        "eval_cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("expected", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    for table in RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(POLICY_SQL.format(table=table))


def downgrade() -> None:
    for table in RLS_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_entitlement ON {table}")
    for table in (
        "eval_cases", "ownership", "links", "chunks", "changes", "messages",
        "threads", "cases", "entitlements", "users", "people", "acls",
    ):
        op.drop_table(table)
