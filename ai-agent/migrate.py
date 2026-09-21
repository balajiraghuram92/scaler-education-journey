import asyncio
from pathlib import Path
import db

async def main():
    await db.pool.open()
    try:
         async with db.pool.connection() as conn:
            await conn.execute("""
              CREATE TABLE IF NOT EXISTS schema_migrations (
                filename    TEXT PRIMARY KEY,
                applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
                )
             """)
            await conn.commit()
            migration_files = sorted(Path("migrations").glob("*.sql"))
            for path in migration_files:
                cur = await conn.execute(
                    "SELECT 1 FROM schema_migrations WHERE filename = %s",
                    (path.name,)
                )
                already_applied = await cur.fetchone()
                if already_applied :
                    print(f"{path.name}: already applied, skipping")
                    continue

                sql = path.read_text()
                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute(
                        "INSERT INTO schema_migrations (filename) VALUES (%s)",
                        (path.name,)
                    )
                print(f"{path.name}: applied")    
        
    finally:
        await db.pool.close()

if __name__ == "__main__":
    asyncio.run(main())