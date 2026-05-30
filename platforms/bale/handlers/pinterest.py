import bale
from typing import Optional
from services.pinterest import pinterest_service
from db.queries import log_search, log_download, get_user_by_platform
from utils.helpers import truncate
from db.engine import get_pool


def is_pinterest(text: str) -> bool:
    """Check if text is related to Pinterest."""
    return pinterest_service.is_pinterest_url(text) or text.startswith('/pinterest')


async def handle(message: bale.Message, pool) -> None:
    """Handle Pinterest-related messages."""
    text = message.text.strip()

    # Get user ID for logging
    user = await get_user_by_platform(pool, "bale", int(message.from_user.id))
    user_id = user['id'] if user else None

    if text.startswith('/pinterest'):
        query = text.replace('/pinterest', '').strip()
        if query:
            await search_pinterest(message, pool, user_id, query)
        else:
            await message.reply("لطفاً بعد از /pinterest عبارت جستجو را وارد کنید.\nمثال: /pinterest طرح های خانه")
    elif pinterest_service.is_pinterest_url(text):
        await handle_pinterest_url(message, pool, user_id, text)
    else:
        await message.reply("لینک پینترست معتبر نیست. لطفاً یک لینک پینترست ارسال کنید یا از /pinterest برای جستجو استفاده کنید.")


async def search_pinterest(message: bale.Message, pool, user_id: Optional[int], query: str) -> None:
    """Search Pinterest pins."""
    if user_id:
        await log_search(pool, user_id, "bale", "pinterest", query)

    await message.reply("🔍 در حال جستجو در پینترست...")

    # Search pins
    pins = await pinterest_service.search_pins(query, limit=5)

    if not pins:
        await message.reply("❌ نتیجه‌ای یافت نشد.")
        return

    # Create response
    response = "🔍 **نتایج جستجو در پینترست:**\n\n"

    keyboard = bale.InlineKeyboardMarkup()

    for i, pin in enumerate(pins, 1):
        title = truncate(pin['title'], 60)
        
        response += f"{i}. {title}\n"
        if pin.get('description'):
            response += f"   📝 {truncate(pin['description'], 80)}\n"
        response += f"   🔗 {pin['url']}\n\n"

        # Add button for each pin
        keyboard.add(
            bale.InlineKeyboardButton(
                text=f"📌 {i}. {truncate(title, 20)}",
                callback_data=f"pinterest_select:{pin['id']}"
            )
        )

    await message.reply(response, components=keyboard)


async def handle_pinterest_url(message: bale.Message, pool, user_id: Optional[int], url: str) -> None:
    """Handle Pinterest URL for download."""
    if user_id:
        await log_download(pool, user_id, "bale", "pinterest", url)

    await message.reply("📥 در حال دریافت اطلاعات پین...")

    # Get pin info
    pin_info = await pinterest_service.get_pin_info(url)

    if not pin_info:
        await message.reply("❌ دریافت اطلاعات پین با مشکل مواجه شد.")
        return

    # Create response with pin info
    title = truncate(pin_info['title'], 100)
    description = truncate(pin_info.get('description', ''), 150)

    response = f"""
📌 **{title}**

📝 {description}

✅ پین آماده دانلود است.
"""

    await message.reply(response)
