from bale import Bot
from platforms.base import BasePlatform
from db.queries import upsert_user
from platforms.bale.handlers import youtube, pinterest

class BaleBot(BasePlatform):
    def __init__(self, token: str):
        self.client = Bot(token=token)
        self._register_handlers()

    def _register_handlers(self):
        youtube.register(self.client)
        pinterest.register(self.client)

    async def _ensure_user(self, message):
        await upsert_user(
            platform="bale",
            platform_user_id=str(message.from_user.id),
            username=message.from_user.username,
            full_name=message.from_user.first_name,
        )

    async def start(self):
        await self.client.run()

    async def stop(self):
        await self.client.close()
