import asyncio
import os
import aiomysql
from config import settings

MIGRATIONS_DIR = os.path.dirname(__file__)


async def run_migrations() -> None:
    conn = await aiomysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        db=settings.db_name,
        charset="utf8mb4",
        autocommit=True,
    )

    # Track applied migrations
    async with conn.cursor() as cur:
        await cur.execute(
            """
            CREATE TABLE IF NOT EXISTS _migrations (
                name VARCHAR(255) PRIMARY KEY,
                applied_at DATETIME NOT NULL DEFAULT NOW()
            )
            """
        )

    sql_files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )

    for filename in sql_files:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1 FROM _migrations WHERE name = %s", (filename,))
            if await cur.fetchone():
                print(f"[skip] {filename}")
                continue

        filepath = os.path.join(MIGRATIONS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            sql = f.read()

        # Execute each statement separately
        async with conn.cursor() as cur:
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    await cur.execute(stmt)
            await cur.execute("INSERT INTO _migrations (name) VALUES (%s)", (filename,))

        print(f"[applied] {filename}")

    conn.close()
    print("Migrations complete.")


if __name__ == "__main__":
    asyncio.run(run_migrations())
