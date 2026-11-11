"""Schema-parity check shared by the P1 proof test and the --migrate CLI mode.

Reflects the database and compares tables, columns, types, nullability, keys and
indexes against the SQLAlchemy metadata in both directions. Returns a list of
human-readable differences (empty means parity).
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncEngine

import app.models  # noqa: F401 - registers all models on Base.metadata
from app.models import Base

IGNORED_TABLES = {"__EFMigrationsHistory"}

# C# entities with no EF migration yet (verified: no CreateTable in
# api/Migrations/* and absent from StudyTrackerContextModelSnapshot.cs).
KNOWN_MISSING_TABLES = {
    "localization_glossary_terms",
    "localization_translation_cache_entries",
    "localization_eval_golden_cases",
    "localization_eval_runs",
    "localization_eval_case_results",
}

# C# properties with no EF migration yet (verified against the snapshot block
# for localization_translations).
KNOWN_MISSING_COLUMNS = {
    ("localization_translations", "raw_mt_text"),
    ("localization_translations", "raw_mt_qps_score"),
    ("localization_translations", "comet_kiwi_score"),
}


def _norm_type(type_: sa.types.TypeEngine) -> str:
    compiled = type_.compile(dialect=postgresql.dialect())
    return str(compiled).upper().replace(" ", "")


def _norm_sql(text: str) -> str:
    return " ".join(text.upper().replace("(", " ( ").replace(")", " ) ").split())


def _reflect(sync_conn: sa.engine.Connection) -> sa.MetaData:
    reflected = sa.MetaData()
    reflected.reflect(bind=sync_conn)
    return reflected


async def check_schema(engine: AsyncEngine) -> list[str]:
    async with engine.connect() as conn:
        reflected = await conn.run_sync(_reflect)

    errors: list[str] = []
    meta = Base.metadata

    meta_tables = set(meta.tables) - KNOWN_MISSING_TABLES
    db_tables = set(reflected.tables) - IGNORED_TABLES - KNOWN_MISSING_TABLES

    for table in sorted(meta_tables - db_tables):
        errors.append(f"table {table}: in SQLAlchemy metadata but missing from database")
    for table in sorted(db_tables - meta_tables):
        errors.append(f"table {table}: in database but missing from SQLAlchemy metadata")

    for name in sorted(meta_tables & db_tables):
        m_table = meta.tables[name]
        r_table = reflected.tables[name]

        m_cols = {
            c.name: c
            for c in m_table.columns
            if (name, c.name) not in KNOWN_MISSING_COLUMNS
        }
        r_cols = {c.name: c for c in r_table.columns}
        for col in sorted(set(m_cols) - set(r_cols)):
            errors.append(f"table {name}: column {col} in metadata but missing from database")
        for col in sorted(set(r_cols) - set(m_cols)):
            errors.append(f"table {name}: column {col} in database but missing from metadata")
        for col in sorted(set(m_cols) & set(r_cols)):
            mc, rc = m_cols[col], r_cols[col]
            if _norm_type(mc.type) != _norm_type(rc.type):
                errors.append(
                    f"table {name} column {col}: type metadata={mc.type} database={rc.type}"
                )
            if bool(mc.nullable) != bool(rc.nullable):
                errors.append(
                    f"table {name} column {col}: nullable metadata={mc.nullable} "
                    f"database={rc.nullable}"
                )
            if (mc.server_default is None) != (rc.server_default is None):
                errors.append(
                    f"table {name} column {col}: server-default presence differs "
                    f"(metadata={mc.server_default} database={rc.server_default})"
                )

        m_pk = tuple(c.name for c in (m_table.primary_key.columns.values()))
        r_pk = tuple(c.name for c in (r_table.primary_key.columns.values()))
        if m_pk != r_pk:
            errors.append(f"table {name}: PK metadata={m_pk} database={r_pk}")

        def _index_sig(table: sa.Table) -> set[tuple[str, tuple[str, ...], bool]]:
            return {
                (ix.name or "", tuple(c.name for c in ix.columns.values()), bool(ix.unique))
                for ix in table.indexes
            }

        m_ix, r_ix = _index_sig(m_table), _index_sig(r_table)
        for sig in sorted(m_ix - r_ix):
            errors.append(f"table {name}: index {sig} in metadata but missing from database")
        for sig in sorted(r_ix - m_ix):
            # Postgres auto-creates backing indexes for unique constraints; the
            # reflected unique constraints cover those, so only report indexes
            # that are not backing a unique constraint.
            backing = {
                tuple(sorted(c.name for c in uc.columns.values()))
                for uc in r_table.constraints
                if isinstance(uc, sa.UniqueConstraint)
            }
            if tuple(sorted(sig[1])) not in backing:
                errors.append(f"table {name}: index {sig} in database but missing from metadata")

        def _uq_sig(table: sa.Table) -> set[tuple[str, ...]]:
            sigs = set()
            for uc in table.constraints:
                if isinstance(uc, sa.UniqueConstraint):
                    sigs.add(tuple(sorted(c.name for c in uc.columns.values())))
            for ix in table.indexes:
                if ix.unique:
                    sigs.add(tuple(sorted(c.name for c in ix.columns.values())))
            return sigs

        if _uq_sig(m_table) != _uq_sig(r_table):
            errors.append(
                f"table {name}: unique sets metadata={sorted(_uq_sig(m_table))} "
                f"database={sorted(_uq_sig(r_table))}"
            )

        def _fk_sig(table: sa.Table) -> set[tuple[tuple[str, ...], str, tuple[str, ...], str]]:
            sigs = set()
            for fk in table.foreign_key_constraints:
                sigs.add(
                    (
                        tuple(sorted(c.parent.name for c in fk.elements)),
                        str(fk.referred_table.name),
                        tuple(sorted(c.column.name for c in fk.elements)),
                        str(fk.ondelete or "").upper(),
                    )
                )
            return sigs

        if _fk_sig(m_table) != _fk_sig(r_table):
            errors.append(
                f"table {name}: FK sets metadata={sorted(_fk_sig(m_table))} "
                f"database={sorted(_fk_sig(r_table))}"
            )

        m_checks = {c.name: str(c.sqltext) for c in m_table.constraints if isinstance(c, sa.CheckConstraint)}
        r_checks = {c.name: str(c.sqltext) for c in r_table.constraints if isinstance(c, sa.CheckConstraint)}
        if set(m_checks) != set(r_checks):
            errors.append(
                f"table {name}: check names metadata={sorted(n for n in m_checks if n is not None)} "
                f"database={sorted(n for n in r_checks if n is not None)}"
            )
        common_checks = sorted(
            name for name in set(m_checks) & set(r_checks) if name is not None
        )
        for check_name in common_checks:
            if _norm_sql(m_checks[check_name]) != _norm_sql(r_checks[check_name]):
                errors.append(
                    f"table {name}: check {check_name} SQL differs:\n"
                    f"  metadata: {m_checks[check_name]}\n"
                    f"  database: {r_checks[check_name]}"
                )

    return errors
