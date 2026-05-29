import bale
from typing import Optional
from services.pinterest import handle_pinterest_message, is_pinterest
from db.engine import get_pool


async def handle(message: bale.Message) -> None:
    """
    Handle incoming messages for Pinterest.
    This function acts as a dispatcher to the service layer logic.
    """
    # Prepare message data in a dictionary format expected by the service layer
    message_data = {
        "text": message.text,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "full_name": message.from_user.first_name,
    }

    response = await handle_pinterest_message(message_data, "bale")
    await message.reply(response)
