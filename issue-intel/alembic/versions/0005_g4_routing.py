"""G4 routing tables: versions, scorecards, budgets; extend model_calls.

Revision ID: 0005_g4_routing
Revises: 0004_g3_fix
"""
from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "0005_g4_routing"
down_revision: str | None = "0004_g3_fix"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# v1 mirrors the G0 static task table. Small tasks fall back to the large
# model; large tasks degrade to the small one; ingest classification is BATCH.
_V1 = {
    "ticket_parse": {"primary": "tessera-small", "fallback": "tessera-large",
                     "token_limit": 4000, "mode": "SYNC"},
    "module_check": {"primary": "tessera-small", "fallback": "tessera-large",
                     "token_limit": 2000, "mode": "SYNC"},
    "relevance": {"primary": "tessera-small", "fallback": "tessera-large",
                  "token_limit": 2000, "mode": "SYNC"},
    "synthesis": {"primary": "tessera-large", "fallback": "tessera-small",
                  "token_limit": 8000, "mode": "SYNC"},
    "outcome_classify": {"primary": "tessera-small", "fallback": "tessera-large",
                         "token_limit": 2000, "mode": "BATCH"},
    "fix_plan": {"primary": "tessera-large", "fallback": "tessera-small",
                 "token_limit": 8000, "mode": "SYNC"},
    "fix_patch": {"primary": "tessera-large", "fallback": "tessera-small",
                  "token_limit": 8000, "mode": "SYNC"},
    "conflict_resolve": {"primary": "tessera-large", "fallback": "tessera-small",
                         "token_limit": 8000, "mode": "SYNC"},
    "quality_verify": {"primary": "tessera-small", "fallback": "tessera-large",
                       "token_limit": 2000, "mode": "SYNC"},
    "final_check": {"primary": "tessera-large", "fallback": "tessera-small",
                    "token_limit": 8000, "mode": "SYNC"},
    "embed": {"primary": "tessera-embed", "fallback": "tessera-embed",
              "token_limit": 8000, "mode": "SYNC"},
}


def upgrade() -> None:
    op.create_table(
        "routing_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("version", sa.Integer(), nullable=False, unique=True),
        sa.Column("routes", JSONB(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_note", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_routing_one_active ON routing_versions (active)"
        " WHERE active"
    )
    op.create_table(
        "model_scorecards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("model", sa.Text(), nullable=False),
        sa.Column("task_type", sa.Text(), nullable=False),
        sa.Column("quality", sa.Float(), nullable=False),
        sa.Column("cost_per_resolved", sa.Float(), nullable=False),
        sa.Column("p95_latency_ms", sa.Float(), nullable=False),
        sa.Column("n", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("limit_usd", sa.Float(), nullable=False),
        sa.Column("spent_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("scope", "key", name="uq_budgets_scope_key"),
    )
    op.add_column("model_calls", sa.Column("fallback_used", sa.Boolean(),
                                           server_default="false"))
    op.add_column("model_calls", sa.Column("routing_version", sa.Integer(),
                                           nullable=True))
    op.add_column("model_calls", sa.Column("cached", sa.Boolean(),
                                           server_default="false"))
    op.add_column("model_calls", sa.Column("is_shadow", sa.Boolean(),
                                           server_default="false"))
    op.execute(
        "INSERT INTO routing_versions (version, routes, active, note, activated_at,"
        " activated_note) VALUES (1, :routes, true, 'initial', now(), 'initial')"
        .replace(":routes", f"'{json.dumps(_V1)}'")
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_routing_one_active")
    op.drop_table("budgets")
    op.drop_table("model_scorecards")
    op.drop_table("routing_versions")
    for column in ("fallback_used", "routing_version", "cached", "is_shadow"):
        op.drop_column("model_calls", column)
