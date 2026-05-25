from bale import Message

def register(client):
    @client.message_handler()
    async def pinterest_handler(message: Message):
        await message.reply("🔍 Pinterest handler — coming soon.")
