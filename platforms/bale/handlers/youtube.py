import bale
from typing import Optional
from services.youtube import youtube_service
from db.queries import log_search, log_download
from utils.helpers import extract_url, truncate


def is_youtube(text: str) -> bool:
    """Check if text is related to YouTube."""
    return youtube_service.is_youtube_url(text) or text.startswith('/youtube') or 'یوتیوب' in text.lower()


async def handle(message: bale.Message, pool) -> None:
    """Handle YouTube-related messages."""
    text = message.text.strip()

    # Extract URL if present
    url = extract_url(text)

    if url and youtube_service.is_youtube_url(url):
        await handle_youtube_url(message, pool, url)
    elif text.startswith('/youtube'):
        query = text.replace('/youtube', '').strip()
        if query:
            await search_youtube(message, pool, query)
        else:
            await message.reply("لطفاً بعد از /youtube عبارت جستجو را وارد کنید.")
    else:
        await message.reply("لینک یوتیوب معتبر نیست. لطفاً یک لینک یوتیوب ارسال کنید.")


async def handle_youtube_url(message: bale.Message, pool, url: str) -> None:
    """Handle YouTube URL for download."""
    # Get user ID for logging
    user = await get_user_by_platform(pool, "bale", int(message.from_user.id))
    user_id = user['id'] if user else None

    # Log download attempt
    if user_id:
        await log_download(pool, user_id, "bale", "youtube", url)

    # Get video info
    video_info = await youtube_service.get_video_info(url)

    if not video_info:
        await message.reply("❌ دریافت اطلاعات ویدیو با مشکل مواجه شد.")
        return

    # Create response with video info
    title = truncate(video_info['title'], 100)
    duration = format_duration(video_info['duration'])
    uploader = video_info['uploader']

    response = f"""
🎬 **{title}**

👤 آپلود کننده: {uploader}
⏱ مدت زمان: {duration}
👁 تعداد بازدید: {format_number(video_info['view_count'])}

📥 برای دانلود، کیفیت مورد نظر را انتخاب کنید:
"""

    # Add format options
    keyboard = bale.InlineKeyboardMarkup()

    # Group formats by quality
    video_formats = [f for f in video_info['formats'] if f['vcodec'] != 'none']
    audio_formats = [f for f in video_info['formats'] if f['vcodec'] == 'none']

    # Add video quality buttons
    row_num = 1
    row = []
    for fmt in video_formats[:3]:
        quality = fmt['resolution'] or fmt['quality']
        button = bale.InlineKeyboardButton(
            text=f"🎥 {quality}",
            callback_data=f"youtube_dl:{video_info['id']}:{fmt['format_id']}"
        )
        row.append(button)
        if len(row) == 2:
            for btn in row:
                keyboard.add(btn, row_num)
            row_num += 1
            row = []

    if row:
        for btn in row:
            keyboard.add(btn, row_num)
        row_num += 1

    if audio_formats:
        audio_fmt = audio_formats[0]
        keyboard.add(
            bale.InlineKeyboardButton(
                text="🎵 فقط صدا (MP3)",
                callback_data=f"youtube_dl:{video_info['id']}:{audio_fmt['format_id']}"
            ),
            row_num
        )

    await message.reply(response, components=keyboard)


async def search_youtube(message: bale.Message, pool, query: str) -> None:
    """Search YouTube videos."""
    # Get user ID for logging
    user = await get_user_by_platform(pool, "bale", int(message.from_user.id))
    user_id = user['id'] if user else None

    # Log search
    if user_id:
        await log_search(pool, user_id, "bale", "youtube", query)

    await message.reply("🔍 در حال جستجو در یوتیوب...")

    # Search videos
    videos = await youtube_service.search_videos(query, limit=5)

    if not videos:
        await message.reply("❌ نتیجه‌ای یافت نشد.")
        return

    # Create response
    response = "🔍 **نتایج جستجو:**\n\n"

    keyboard = bale.InlineKeyboardMarkup()

    for i, video in enumerate(videos, 1):
        title = truncate(video['title'], 60)
        duration = format_duration(video['duration'])

        response += f"{i}. {title}\n"
        response += f"   ⏱ {duration} | 👤 {video['uploader']}\n"
        response += f"   👁 {format_number(video['view_count'])}\n\n"

        # Add button for each video
        keyboard.add(
            bale.InlineKeyboardButton(
                text=f"🎬 {i}. {truncate(title, 20)}",
                callback_data=f"youtube_select:{video['id']}"
            )
        )

    await message.reply(response, components=keyboard)


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to HH:MM:SS."""
    if not seconds:
        return "نامشخص"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_number(num: Optional[int]) -> str:
    """Format large numbers with Persian separators."""
    if not num:
        return "۰"

    return f"{num:,}".replace(",", "٬")


async def get_user_by_platform(pool, platform: str, platform_user_id: int):
    """Get user by platform (temporary until proper import)."""
    from db.queries import  log_search, log_download, get_user_by_platform
    return await get_user_by_platform(pool, platform, platform_user_id)
