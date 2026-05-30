"""
Example: Creating and using custom middlewares

This file demonstrates how to create custom middlewares for various use cases.
"""

from typing import Callable, Any
import bale
from platforms.middleware import Middleware
from db.queries import get_user_by_platform
import time


# Example 1: Admin-only commands middleware
class AdminOnlyMiddleware(Middleware):
    """Restrict certain commands to admin users only."""
    
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        # Check if message contains admin command
        if message.text and message.text.startswith('/admin'):
            user_id = int(message.from_user.id)
            
            if user_id not in self.admin_ids:
                await message.reply("⛔️ شما دسترسی به این دستور را ندارید.")
                return None
        
        return await next_handler(message, pool)


# Example 2: Usage tracking middleware
class UsageTrackingMiddleware(Middleware):
    """Track user activity and command usage."""
    
    def __init__(self):
        self.command_stats = {}
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        if message.text:
            # Extract command
            command = message.text.split()[0] if message.text else "unknown"
            
            # Track usage
            self.command_stats[command] = self.command_stats.get(command, 0) + 1
            
            # Log every 100 requests
            total = sum(self.command_stats.values())
            if total % 100 == 0:
                print(f"📊 Usage Stats: {self.command_stats}")
        
        return await next_handler(message, pool)


# Example 3: Maintenance mode middleware
class MaintenanceModeMiddleware(Middleware):
    """Block all requests during maintenance except for admins."""
    
    def __init__(self, enabled: bool = False, admin_ids: list[int] = None):
        self.enabled = enabled
        self.admin_ids = admin_ids or []
    
    def enable(self):
        """Enable maintenance mode."""
        self.enabled = True
    
    def disable(self):
        """Disable maintenance mode."""
        self.enabled = False
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        if self.enabled:
            user_id = int(message.from_user.id)
            
            if user_id not in self.admin_ids:
                await message.reply(
                    "🔧 ربات در حال تعمیر و نگهداری است.\n"
                    "لطفاً بعداً دوباره تلاش کنید."
                )
                return None
        
        return await next_handler(message, pool)


# Example 4: Daily limit middleware (non-premium users)
class DailyLimitMiddleware(Middleware):
    """Limit daily requests for non-premium users."""
    
    def __init__(self, daily_limit: int = 50):
        self.daily_limit = daily_limit
        self.user_daily_count = {}
        self.last_reset = time.time()
    
    def _reset_if_needed(self):
        """Reset counters if 24 hours have passed."""
        current_time = time.time()
        if current_time - self.last_reset > 86400:  # 24 hours
            self.user_daily_count.clear()
            self.last_reset = current_time
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        self._reset_if_needed()
        
        # Check if user is premium
        is_premium = getattr(message, 'user_data', {}).get('is_premium', False)
        
        if not is_premium:
            user_id = int(message.from_user.id)
            count = self.user_daily_count.get(user_id, 0)
            
            if count >= self.daily_limit:
                await message.reply(
                    f"⚠️ شما به حد مجاز روزانه ({self.daily_limit} درخواست) رسیده‌اید.\n\n"
                    f"💎 با ارتقا به نسخه ویژه، محدودیت نداشته باشید!"
                )
                return None
            
            self.user_daily_count[user_id] = count + 1
        
        return await next_handler(message, pool)


# Example 5: Command alias middleware
class CommandAliasMiddleware(Middleware):
    """Allow command aliases (shortcuts)."""
    
    def __init__(self):
        self.aliases = {
            '/yt': '/youtube',
            '/pin': '/pinterest',
            '/search': '/youtube',
            'یوتیوب': '/youtube',
            'پینترست': '/pinterest',
        }
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        if message.text:
            # Check for aliases
            for alias, command in self.aliases.items():
                if message.text.startswith(alias):
                    # Replace alias with actual command
                    message.text = message.text.replace(alias, command, 1)
                    break
        
        return await next_handler(message, pool)


# Example 6: Response time middleware
class ResponseTimeMiddleware(Middleware):
    """Measure and log response time for each request."""
    
    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        start_time = time.time()
        
        result = await next_handler(message, pool)
        
        duration = time.time() - start_time
        user_id = message.from_user.id
        command = message.text.split()[0] if message.text else "unknown"
        
        print(f"⏱ User {user_id} | Command: {command} | Duration: {duration:.2f}s")
        
        # Alert if slow
        if duration > 5.0:
            print(f"⚠️ SLOW REQUEST: {duration:.2f}s for {command}")
        
        return result


# How to use these middlewares in bot.py:
"""
from platforms.bale.middlewares import PremiumUserMiddleware
from examples.custom_middleware_example import (
    AdminOnlyMiddleware,
    UsageTrackingMiddleware,
    MaintenanceModeMiddleware,
    DailyLimitMiddleware,
    CommandAliasMiddleware,
    ResponseTimeMiddleware
)

def _setup_middlewares(self):
    # Order matters! These run in sequence
    
    # 1. Logging and monitoring
    self.middleware_manager.add(ResponseTimeMiddleware())
    self.middleware_manager.add(UsageTrackingMiddleware())
    
    # 2. Command preprocessing
    self.middleware_manager.add(CommandAliasMiddleware())
    
    # 3. Maintenance mode (blocks everything if enabled)
    self.maintenance = MaintenanceModeMiddleware(
        enabled=False,
        admin_ids=[123456789]  # Your admin user IDs
    )
    self.middleware_manager.add(self.maintenance)
    
    # 4. User authentication and premium check
    self.middleware_manager.add(PremiumUserMiddleware())
    
    # 5. Access control
    self.middleware_manager.add(AdminOnlyMiddleware(admin_ids=[123456789]))
    
    # 6. Rate limiting
    self.middleware_manager.add(DailyLimitMiddleware(daily_limit=50))
    
    # 7. Request-specific rate limiting
    from platforms.bale.middlewares import RateLimitMiddleware
    self.middleware_manager.add(RateLimitMiddleware(
        max_requests=10,
        window_seconds=60
    ))

# To enable/disable maintenance mode:
# bot.maintenance.enable()
# bot.maintenance.disable()
"""
