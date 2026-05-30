import bale
from platforms.base import BasePlatform
from platforms.middleware import MiddlewareManager
from platforms.bale.middlewares import PremiumUserMiddleware
from db.queries import upsert_user, get_user_by_platform
from db.engine import get_pool
from platforms.bale.handlers import youtube, pinterest


class BaleBot(BasePlatform):
    def __init__(self, token: str):
        self.client = bale.Bot(token=token)
        self.middleware_manager = MiddlewareManager()
        self._setup_middlewares()
        self._register_handlers()

        @self.client.listen("on_ready")
        async def on_ready():
            await get_pool()
            print("دیتابیس آماده شد.")

    def _setup_middlewares(self):
        """Setup middleware chain."""
        # Add premium user middleware
        self.middleware_manager.add(PremiumUserMiddleware())
        
        # You can add more middlewares here
        # self.middleware_manager.add(RateLimitMiddleware())
        # self.middleware_manager.add(LoggingMiddleware())

    def _register_handlers(self):
        @self.client.listen("on_message")
        async def on_message(message: bale.Message):
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

            # Execute middleware chain
            async def final_handler(msg: bale.Message, p):
                """Final handler after all middlewares."""
                text = msg.text.strip()

                if youtube.is_youtube(text):
                    await youtube.handle(msg, p)
                elif pinterest.is_pinterest(text):
                    await pinterest.handle(msg, p)
                else:
                    await msg.reply("دستور نامعتبر است.\n\nدستورات موجود:\n/youtube [جستجو] - جستجو در یوتیوب\n/pinterest [جستجو] - جستجو در پینترست\n\nیا لینک یوتیوب/پینترست ارسال کنید.")

            await self.middleware_manager.execute(message, pool, final_handler)

    def start(self):
        # Run the blocking run() method in a thread
        self.client.run()

    async def stop(self):
        from db.engine import close_pool
        await self.client.close()
        await close_pool()
