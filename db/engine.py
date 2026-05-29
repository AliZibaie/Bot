import aiomysql
import asyncio
from config import settings

_pools = {}  # key: loop id, value: pool

async def get_pool() -> aiomysql.Pool:
    loop = asyncio.get_running_loop()
    loop_id = id(loop)
    if loop_id not in _pools:
        _pools[loop_id] = await aiomysql.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            minsize=1,
            maxsize=settings.db_pool_size,
            autocommit=True,
            charset="utf8mb4",
            loop=loop,  # explicitly attach to this loop
        )
    return _pools[loop_id]

async def close_pool() -> None:
    for pool in _pools.values():
        pool.close()
        await pool.wait_closed()
    _pools.clear()