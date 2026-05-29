import bale
from platforms.base import BasePlatform
from db.queries import upsert_user, get_user_by_platform
from db.engine import get_pool
from platforms.bale.handlers import youtube, pinterest


class BaleBot(BasePlatform):
    def __init__(self, token: str):
        self.client = bale.Bot(token=token)
        self._register_handlers()

        @self.client.listen("on_ready")
        async def on_ready():
            await get_pool()
            print("دیتابیس آماده شد.")

    def _register_handlers(self):
        @self.client.listen("on_message")
        async def on_message(message: bale.Message):
            print(f"پیام دریافت شد: {message.text}")
            if not message.text:
                return

            # Get database pool
            pool = await get_pool()

            # Extract user info
            platform_user_id = int(message.from_user.id)
            username = message.from_user.username

            # Upsert user (without full_name parameter)
            await upsert_user(
                pool=pool,
                platform="bale",
                platform_user_id=platform_user_id,
                username=username,
            )

            text = message.text.strip()

            if youtube.is_youtube(text):
                await youtube.handle(message, pool)
            elif pinterest.is_pinterest(text):
                await pinterest.handle(message, pool)
            else:
                await message.reply("دستور نامعتبر است.")

    def start(self):
        # Run the blocking run() method in a thread
        self.client.run()

    async def stop(self):
        from db.engine import close_pool
        await self.client.close()
        await close_pool()
