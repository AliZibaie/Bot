from aiomysql import Pool
import aiomysql
from datetime import datetime

async def upsert_user(pool: Pool, platform: str, platform_user_id: int, username: str | None) -> None:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users (platform, platform_user_id, username)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE username = VALUES(username), updated_at = NOW()
                """,
                (platform, platform_user_id, username),
            )


async def log_search(pool: Pool, user_id: int, platform: str, service: str, query: str) -> int:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO search_logs (user_id, platform, service, query)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, platform, service, query),
            )
            return cur.lastrowid


async def log_download(pool: Pool, user_id: int, platform: str, service: str, url: str, quality: str | None = None) -> int:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO download_logs (user_id, platform, service, url, quality)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, platform, service, url, quality),
            )
            return cur.lastrowid


async def get_user_by_platform(pool: Pool, platform: str, platform_user_id: int) -> dict | None:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM users WHERE platform = %s AND platform_user_id = %s",
                (platform, platform_user_id),
            )
            return await cur.fetchone()


async def set_user_premium(pool: Pool, user_id: int, is_premium: bool, expires_at: datetime | None = None) -> None:
    """Set premium status for a user."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE users 
                SET is_premium = %s, premium_expires_at = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (is_premium, expires_at, user_id),
            )


async def check_premium_expired(pool: Pool) -> list[int]:
    """Check and return list of users whose premium has expired."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id FROM users 
                WHERE is_premium = TRUE 
                AND premium_expires_at IS NOT NULL 
                AND premium_expires_at < NOW()
                """
            )
            result = await cur.fetchall()
            return [row[0] for row in result]


async def expire_premium_users(pool: Pool) -> int:
    """Expire premium status for users whose subscription has ended."""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE users 
                SET is_premium = FALSE, updated_at = NOW()
                WHERE is_premium = TRUE 
                AND premium_expires_at IS NOT NULL 
                AND premium_expires_at < NOW()
                """
            )
            return cur.rowcount
