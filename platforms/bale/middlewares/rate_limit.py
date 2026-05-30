from typing import Callable, Any
import bale
import time
from collections import defaultdict
from platforms.middleware import Middleware, get_message_context


class RateLimitMiddleware(Middleware):
    """Middleware to rate limit requests per user."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests = defaultdict(list)

    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        """Check rate limit before processing request."""
        user_id = int(message.from_user.id)
        current_time = time.time()
        
        # Clean old requests outside the window
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check if user has exceeded rate limit
        if len(self.user_requests[user_id]) >= self.max_requests:
            # Check if user is premium (premium users have higher limits or no limits)
            user_data = get_message_context(message)
            is_premium = user_data.get('is_premium', False)
            
            if not is_premium:
                await message.reply(
                    f"⚠️ شما به حد مجاز درخواست رسیده‌اید.\n"
                    f"لطفاً {self.window_seconds} ثانیه صبر کنید.\n\n"
                    f"💎 کاربران ویژه محدودیت ندارند!"
                )
                return None
        
        # Add current request to history
        self.user_requests[user_id].append(current_time)
        
        # Continue to next middleware/handler
        return await next_handler(message, pool)
