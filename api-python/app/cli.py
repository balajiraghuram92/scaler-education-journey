"""Ported from the CLI section of api/Program.cs (lines 278-416).

Modes: --migrate (schema check only; migrations stay EF-owned), --seed-reference-data
(alias --seed), --seed-admin, --reconcile-content. Exit codes mirror the C# CLI.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .db import dotnet_connstr_to_asyncpg_url
from .services.reconciliation.reconciliation_engine import ReconciliationEngine
from .services.reconciliation.reconciliation_models import (
    ReconciliationExecutionMode,
    ReconciliationOptions,
)
from .settings import get_dotnet_connection_string, get_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StudyTracker Python API CLI")
    parser.add_argument("--migrate", action="store_true")
    parser.add_argument("--seed-reference-data", "--seed", action="store_true", dest="seed_reference_data")
    parser.add_argument("--seed-admin", action="store_true")
    parser.add_argument("--reconcile-content", action="store_true")
    parser.add_argument("--scope", default="all")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    return parser


def _engine():  # type: ignore[no-untyped-def]
    url = dotnet_connstr_to_asyncpg_url(
        get_dotnet_connection_string(get_environment())
    )
    return create_async_engine(url, pool_pre_ping=True)


async def _run_migrate() -> int:
    from .seed.schema_check import check_schema

    engine = _engine()
    try:
        async with engine.connect() as conn:
            try:
                applied = await conn.execute(
                    text('SELECT COUNT(*) FROM "__EFMigrationsHistory"')
                )
                applied_count = applied.scalar() or 0
            except Exception:
                applied_count = 0
        print("Database connection verified (migrations are managed externally).")
        errors = await check_schema(engine)
        if errors:
            print("Schema differences detected between the database and the Python models:")
            for error in errors:
                print(f"  - {error}")
            return 1
        print(
            f"Database schema matches the Python models ({applied_count} migrations applied)."
        )
        return 0
    except Exception as exc:
        print(f"An error occurred while checking the database schema: {exc}")
        return 1
    finally:
        await engine.dispose()


async def _run_seed_reference_data() -> int:
    from .seed.db_seeder import initialize

    engine = _engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            await initialize(session)
        return 0
    except Exception as exc:
        print(f"An error occurred while seeding the database: {exc}")
        return 1
    finally:
        await engine.dispose()


async def _run_seed_admin() -> int:
    from .models.app_user import AppUser
    from .services.auth.pbkdf2_password_hasher import hash_password

    email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD") or ""
    display_name = os.environ.get("ADMIN_DISPLAY_NAME") or "Administrator"
    reset_totp = (os.environ.get("RESET_ADMIN_TOTP") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if not email or not password:
        print("ADMIN_EMAIL and ADMIN_PASSWORD environment variables are required for --seed-admin.")
        return 1
    if len(password) < 16:
        print("ADMIN_PASSWORD must be at least 16 characters for --seed-admin.")
        return 1

    engine = _engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            existing = (
                await session.execute(select(AppUser).where(AppUser.email == email))
            ).scalar_one_or_none()
            now = datetime.now(UTC)
            if existing is None:
                password_hash, salt, iterations = hash_password(password)
                session.add(
                    AppUser(
                        email=email,
                        password_hash=password_hash,
                        password_salt=salt,
                        password_iterations=iterations,
                        role="Admin",
                        status="Approved",
                        display_name=display_name,
                        created_at=now,
                        decided_at=now,
                        totp_enabled=False,
                    )
                )
                await session.commit()
                print(f"Admin user '{email}' created and approved.")
                return 0

            # Refresh credentials and approval state without disturbing TOTP enrollment,
            # unless RESET_ADMIN_TOTP=1 explicitly clears the device binding.
            password_hash, salt, iterations = hash_password(password)
            existing.password_hash = password_hash
            existing.password_salt = salt
            existing.password_iterations = iterations
            existing.role = "Admin"
            existing.status = "Approved"
            existing.display_name = display_name
            existing.decided_at = now
            if reset_totp:
                existing.totp_enabled = False
                existing.totp_secret_encrypted = None
                existing.last_accepted_totp_counter = None
            await session.commit()
            print(
                f"Admin user '{email}' refreshed (TOTP {'reset' if reset_totp else 'preserved'})."
            )
            return 0
    except Exception as exc:
        print(f"An error occurred while seeding the admin user: {exc}")
        return 1
    finally:
        await engine.dispose()


async def _run_reconcile(args: argparse.Namespace) -> int:
    engine = _engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            options = ReconciliationOptions(
                scope=args.scope or "all",
                mode=(
                    ReconciliationExecutionMode.APPLY
                    if args.apply
                    else (
                        ReconciliationExecutionMode.VERIFY
                        if args.verify
                        else ReconciliationExecutionMode.DRY_RUN
                    )
                ),
            )
            print(
                f"[CLI] Executing Reconciliation Engine (Scope: {options.scope}, "
                f"Mode: {options.mode.value})..."
            )
            reports = await ReconciliationEngine(session).execute_async(options)
            for report in reports:
                print(
                    f"Scope={report.scope} Mode={report.mode.value} "
                    f"Discovered={report.discovered_count} "
                    f"ExactMapped={report.exact_mapped_count} "
                    f"Proposed={report.proposed_count} "
                    f"Verified={report.verified_count} "
                    f"Conflicts={report.conflict_count} "
                    f"Skipped={report.skipped_count}"
                )
                for line in report.audit_log:
                    print(f"  {line}")
            print(f"[CLI] Reconciliation completed with {len(reports)} reports.")
            return 0
    except Exception as exc:
        print(f"An error occurred during content reconciliation: {exc}")
        return 1
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.migrate:
        return asyncio.run(_run_migrate())
    if args.seed_reference_data:
        return asyncio.run(_run_seed_reference_data())
    if args.seed_admin:
        return asyncio.run(_run_seed_admin())
    if args.reconcile_content:
        return asyncio.run(_run_reconcile(args))
    build_parser().print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
