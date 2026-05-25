import asyncio
from config import settings
from db.engine import get_pool, close_pool
from platforms.bale.bot import BaleBot

async def main():
    await get_pool()
    bot = BaleBot(token=settings.bale_token)
    try:
        await bot.start()
    finally:
        await bot.stop()
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())
