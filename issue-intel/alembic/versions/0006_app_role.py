"""Non-superuser app role so row-level security is enforced.

Revision ID: 0006_app_role
Revises: 0005_g4_routing
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_app_role"
down_revision: str | None = "0005_g4_routing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$\n"
        "BEGIN\n"
        "  IF NOT EXISTS (SELECT 1 FROM pg_roles"
        " WHERE rolname = 'issueintel_app') THEN\n"
        "    CREATE ROLE issueintel_app NOLOGIN NOSUPERUSER NOBYPASSRLS;\n"
        "  END IF;\n"
        "END\n"
        "$$;"
    )
    op.execute("GRANT issueintel_app TO CURRENT_USER")
    op.execute("GRANT USAGE ON SCHEMA public TO issueintel_app")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE"
        " ON ALL TABLES IN SCHEMA public TO issueintel_app"
    )
    op.execute(
        "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public"
        " TO issueintel_app"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public"
        " GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO issueintel_app"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public"
        " GRANT USAGE, SELECT ON SEQUENCES TO issueintel_app"
    )


def downgrade() -> None:
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public"
        " REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM issueintel_app"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public"
        " REVOKE USAGE, SELECT ON SEQUENCES FROM issueintel_app"
    )
    op.execute(
        "REVOKE SELECT, INSERT, UPDATE, DELETE"
        " ON ALL TABLES IN SCHEMA public FROM issueintel_app"
    )
    op.execute(
        "REVOKE USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public"
        " FROM issueintel_app"
    )
    op.execute("REVOKE USAGE ON SCHEMA public FROM issueintel_app")
