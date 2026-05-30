from typing import Callable, Any
import bale
from platforms.middleware import Middleware, set_message_context
from db.queries import get_user_by_platform


class PremiumUserMiddleware(Middleware):
    """Middleware to check and handle premium user features."""

    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        """
        Check if user is premium and add premium status to message context.
        You can extend this to limit features for non-premium users.
        """
        # Get user from database
        platform_user_id = int(message.from_user.id)
        user = await get_user_by_platform(pool, "bale", platform_user_id)
        
        # Store user data in message context
        if user:
            user_data = {
                'id': user['id'],
                'is_premium': user.get('is_premium', False),
                'username': user.get('username'),
            }
        else:
            user_data = {
                'id': None,
                'is_premium': False,
                'username': None,
            }
        
        # Set context for this message
        set_message_context(message, user_data)
        
        # Example: Block non-premium users from certain features
        # if not user_data['is_premium'] and '/premium_feature' in message.text:
        #     await message.reply("⭐️ این ویژگی فقط برای کاربران ویژه است.")
        #     return None
        
        # Continue to next middleware/handler
        return await next_handler(message, pool)
