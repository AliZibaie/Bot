from typing import Callable, Any
import bale
from platforms.middleware import Middleware
from datetime import datetime


class LoggingMiddleware(Middleware):
    """Middleware to log all incoming messages."""

    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        """Log message details before processing."""
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        text = message.text[:50] if message.text else "No text"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[{timestamp}] User {user_id} (@{username}): {text}")
        
        # Continue to next middleware/handler
        result = await next_handler(message, pool)
        
        print(f"[{timestamp}] Request processed for user {user_id}")
        
        return result
