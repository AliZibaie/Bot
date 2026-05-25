from bale import Message

def register(client):
    @client.message_handler()
    async def youtube_handler(message: Message):
        await message.reply("🔍 YouTube handler — coming soon.")
