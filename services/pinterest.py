import re
import asyncio
import aiohttp
from urllib.parse import urlparse, parse_qs
from typing import Optional

from utils.helpers import extract_url, truncate
from db.queries import log_download, log_search, get_user_by_platform, upsert_user
from db.engine import get_pool
from config import settings

PINTEREST_BASE_URL = "https://www.pinterest.com"


async def search_pinterest(query: str, user_id: int, platform: str) -> list[dict]:
    """
    Search Pinterest for images and return a list of results.
    Note: Pinterest doesn't have a public API, so we'll use web scraping.
    This is a simplified implementation that may need adjustments.
    """
    pool = await get_pool()
    await log_search(
        pool=pool, user_id=user_id, platform=platform, service="pinterest", query=query
    )

    # Pinterest search URL format
    search_url = f"https://www.pinterest.com/resource/BaseSearchResource/get/"

    # Note: Pinterest requires authentication and has anti-scraping measures
    # This is a placeholder implementation
    results = []

    try:
        # In a real implementation, you would need to:
        # 1. Handle Pinterest authentication
        # 2. Make requests with proper headers
        # 3. Parse the JSON response
        # 4. Extract pin information

        # For now, return simulated results
        for i in range(5):
            results.append({
                "title": f"Pin result {i + 1} for '{query}'",
                "url": f"https://www.pinterest.com/pin/{hash(query + str(i))}/",
                "thumbnail": f"https://picsum.photos/300/200?random={i}",
                "description": f"Description for pin about {query}",
                "pin_id": f"pin_{i}_{hash(query)}"
            })

        await asyncio.sleep(0.5)  # Simulate network delay
        return results

    except Exception as e:
        print(f"Error searching Pinterest: {e}")
        return []


async def download_pinterest_image(url: str, user_id: int, platform: str) -> str | None:
    """
    Download a Pinterest image and return its file path.
    Pinterest images require extracting the actual image URL from the pin page.
    """
    pool = await get_pool()
    await log_download(
        pool=pool, user_id=user_id, platform=platform, service="pinterest", url=url
    )

    try:
        # Extract pin ID from URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        if 'pin' in path_parts:
            pin_index = path_parts.index('pin')
            if pin_index + 1 < len(path_parts):
                pin_id = path_parts[pin_index + 1]
            else:
                return None
        else:
            return None

        # In a real implementation, you would:
        # 1. Fetch the pin page HTML
        # 2. Extract the image URL (usually in meta tags or JSON-LD)
        # 3. Download the actual image

        # For now, simulate download with a placeholder
        file_path = f"downloads/pinterest_{pin_id}_{user_id}.jpg"

        # Create downloads directory if it doesn't exist
        import os
        os.makedirs("downloads", exist_ok=True)

        # Simulate download (in real implementation, use aiohttp to download)
        print(f"Simulating download of Pinterest image: {url}")
        print(f"Saved to: {file_path}")

        # Return the simulated file path
        return file_path

    except Exception as e:
        print(f"Error downloading Pinterest image: {e}")
        return None


def is_pinterest(text: str) -> bool:
    """Check if the text is a Pinterest URL or search query."""
    if text.startswith("/pinterest"):
        return True

    parsed_url = urlparse(text)
    # Check for common Pinterest domains
    return parsed_url.netloc in ("www.pinterest.com", "pinterest.com", "pin.it")


async def handle_pinterest_message(message: dict, platform: str) -> str:
    """Handle incoming Pinterest related messages."""
    user_id = await get_user_id(message, platform)
    text = message["text"].strip()

    if text.startswith("/pinterest"):
        query = text[len("/pinterest"):].strip()
        if not query:
            return "لطفا برای جستجو عبارت خود را وارد کنید.\nمثال: /pinterest طرح های خانه"

        results = await search_pinterest(query, user_id, platform)
        if not results:
            return "متاسفانه چیزی پیدا نشد."

        response = "🔍 **نتایج جستجو در پینترست:**\n\n"
        for i, result in enumerate(results[:5]):  # Show first 5 results
            response += f"{i + 1}. **{truncate(result['title'], 60)}**\n"
            response += f"   🔗 {result['url']}\n"
            if result.get('description'):
                response += f"   📝 {truncate(result['description'], 100)}\n"
            response += "\n"

        response += "برای دانلود، لینک پین را ارسال کنید."
        return response

    else:
        url = extract_url(text)
        if not url or not is_pinterest(url):
            return "لطفا یک URL معتبر پینترست وارد کنید یا از دستور /pinterest برای جستجو استفاده کنید."

        file_path = await download_pinterest_image(url, user_id, platform)
        if not file_path:
            return "❌ متاسفانه دانلود تصویر با خطا مواجه شد."

        return f"✅ تصویر دانلود شد: `{file_path}`"


async def get_user_id(message: dict, platform: str) -> int:
    """Get user ID from the database, creating the user if they don't exist."""
    pool = await get_pool()

    platform_user_id = int(message["user_id"])
    username = message.get("username")

    user_data = await get_user_by_platform(
        pool=pool,
        platform=platform,
        platform_user_id=str(platform_user_id)
    )

    if user_data:
        return user_data["id"]
    else:
        # Create new user (without full_name parameter)
        await upsert_user(
            pool=pool,
            platform=platform,
            platform_user_id=platform_user_id,
            username=username
        )

        # Re-fetch to get the newly created user's ID
        user_data = await get_user_by_platform(
            pool=pool,
            platform=platform,
            platform_user_id=str(platform_user_id)
        )

        if user_data:
            return user_data["id"]
        else:
            raise Exception(f"Failed to create or retrieve user for platform {platform} ID {platform_user_id}")
