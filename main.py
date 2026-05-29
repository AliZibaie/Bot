import asyncio
import sys
from config import settings
from platforms.bale.bot import BaleBot
from db.engine import get_pool, close_pool


async def main():
    # Initialize database pool
    await get_pool()

    # Create bot
    bot = BaleBot(token=settings.bale_token)

    print("ربات در حال راه‌اندازی...")

    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nدریافت سیگنال خاموش شدن...")
    except asyncio.CancelledError:
        pass
    finally:
        print("در حال خاموش کردن ربات...")
        await bot.stop()
        print("ربات خاموش شد.")


if __name__ == "__main__":
    # Windows: use ProactorEventLoop (default on 3.8+)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
