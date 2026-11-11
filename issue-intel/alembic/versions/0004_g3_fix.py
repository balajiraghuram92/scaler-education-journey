"""G3 fix tables: candidates, attempts, PRs, final checks, tokens, profiles.

Revision ID: 0004_g3_fix
Revises: 0003_g2_runs
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0004_g3_fix"
down_revision: str | None = "0003_g2_runs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fix_candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(64), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("ticket_key", sa.Text(), nullable=False),
        sa.Column("module", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("owner_opt_in", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.Text(), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "fix_attempts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("fix_candidates.id"),
                  nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="RUNNING"),
        sa.Column("branch", sa.Text(), nullable=False, server_default=""),
        sa.Column("trace", JSONB(), nullable=False, server_default="[]"),
        sa.Column("tokens_in", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tokens_out", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("build_output", sa.Text(), nullable=False, server_default=""),
        sa.Column("test_output", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("candidate_id", "attempt_no",
                            name="uq_fix_attempts_candidate_no"),
    )
    op.create_table(
        "fix_prs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("fix_attempts.id"),
                  nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("branch", sa.Text(), nullable=False),
        sa.Column("base", sa.Text(), nullable=False, server_default="main"),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("root_cause", sa.Text(), nullable=False, server_default=""),
        sa.Column("citations", JSONB(), nullable=False, server_default="[]"),
        sa.Column("risk_note", sa.Text(), nullable=False, server_default=""),
        sa.Column("test_results", JSONB(), nullable=False, server_default="{}"),
        sa.Column("diff", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.Text(), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "final_checks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(64), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("fix_attempts.id"),
                  nullable=True),
        sa.Column("verdict", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "approval_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("run_id", sa.String(64), sa.ForeignKey("runs.id"), nullable=False),
        sa.Column("ticket_key", sa.Text(), nullable=False),
        sa.Column("payload_hash", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "audience_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("departments", sa.Text(), nullable=False),
        sa.Column("max_restriction", sa.Integer(), nullable=False),
        sa.Column("hide_fields", JSONB(), nullable=False, server_default="[]"),
    )
    op.create_table(
        "developer_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("handle", sa.Text(), nullable=False, unique=True),
        sa.Column("modules", sa.Text(), nullable=False),
        sa.Column("opt_in_fix", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    for table in ("developer_profiles", "audience_profiles", "approval_tokens",
                  "final_checks", "fix_prs", "fix_attempts", "fix_candidates"):
        op.drop_table(table)
