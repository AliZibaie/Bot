# Middleware System

This project implements a Laravel-style middleware system for handling requests in the bot.

## Architecture

The middleware system is based on a chain of responsibility pattern where each middleware can:
1. Process the request before passing it to the next handler
2. Modify the request/message
3. Stop the chain by not calling the next handler
4. Execute code after the handler completes

## Available Middlewares

### 1. PremiumUserMiddleware
Located: `platforms/bale/middlewares/premium.py`

**Purpose:** Checks if a user is premium and attaches user data to the message.

**Usage:**
```python
# Automatically adds message.user_data with:
# - id: User database ID
# - is_premium: Boolean premium status
# - username: User's username
```

**Example - Blocking non-premium features:**
```python
# In your handler
if not message.user_data['is_premium']:
    await message.reply("⭐️ این ویژگی فقط برای کاربران ویژه است.")
    return
```

### 2. RateLimitMiddleware
Located: `platforms/bale/middlewares/rate_limit.py`

**Purpose:** Limits the number of requests per user in a time window.

**Configuration:**
```python
# In bot.py _setup_middlewares()
self.middleware_manager.add(RateLimitMiddleware(
    max_requests=10,      # Max requests per window
    window_seconds=60     # Time window in seconds
))
```

**Features:**
- Premium users bypass rate limits
- Automatic cleanup of old request history
- Customizable limits per instance

### 3. LoggingMiddleware
Located: `platforms/bale/middlewares/logging.py`

**Purpose:** Logs all incoming messages and request processing.

**Output:**
```
[2025-01-15 10:30:45] User 123456 (@username): /youtube search query
[2025-01-15 10:30:46] Request processed for user 123456
```

## Creating Custom Middlewares

### Step 1: Create Middleware Class

Create a new file in `platforms/bale/middlewares/`:

```python
from typing import Callable, Any
import bale
from platforms.middleware import Middleware


class MyCustomMiddleware(Middleware):
    """Description of what this middleware does."""

    def __init__(self, config_param: str = "default"):
        """Initialize with any configuration."""
        self.config_param = config_param

    async def process(self, message: bale.Message, pool, next_handler: Callable) -> Any:
        """
        Process the message.
        
        Args:
            message: The incoming Bale message
            pool: Database connection pool
            next_handler: Next handler in the chain
            
        Returns:
            Result from the handler chain or None to stop
        """
        # Do something before the handler
        print(f"Before: {message.text}")
        
        # Check conditions
        if some_condition:
            await message.reply("Blocked by middleware")
            return None  # Stop the chain
        
        # Call next handler
        result = await next_handler(message, pool)
        
        # Do something after the handler
        print(f"After: completed")
        
        return result
```

### Step 2: Register Middleware

Add to `platforms/bale/middlewares/__init__.py`:
```python
from .my_custom import MyCustomMiddleware

__all__ = [..., 'MyCustomMiddleware']
```

### Step 3: Add to Bot

In `platforms/bale/bot.py`, add to `_setup_middlewares()`:
```python
from platforms.bale.middlewares import MyCustomMiddleware

def _setup_middlewares(self):
    self.middleware_manager.add(PremiumUserMiddleware())
    self.middleware_manager.add(MyCustomMiddleware(config_param="value"))
    # ... other middlewares
```

## Middleware Execution Order

Middlewares execute in the order they are added:

```
Request → Middleware 1 → Middleware 2 → Middleware 3 → Handler
                ↓              ↓              ↓           ↓
Response ← Middleware 1 ← Middleware 2 ← Middleware 3 ← Handler
```

**Example:**
```python
self.middleware_manager.add(LoggingMiddleware())      # Runs first
self.middleware_manager.add(PremiumUserMiddleware())  # Runs second
self.middleware_manager.add(RateLimitMiddleware())    # Runs third
# Then the actual handler (youtube/pinterest)
```

## Common Use Cases

### 1. Authentication/Authorization
```python
class AuthMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        user = await get_user_by_platform(pool, "bale", int(message.from_user.id))
        if not user:
            await message.reply("لطفاً ابتدا ثبت‌نام کنید.")
            return None
        return await next_handler(message, pool)
```

### 2. Feature Flags
```python
class FeatureFlagMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        if '/beta_feature' in message.text and not is_beta_user(message.from_user.id):
            await message.reply("این ویژگی هنوز در دسترس نیست.")
            return None
        return await next_handler(message, pool)
```

### 3. Analytics
```python
class AnalyticsMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        start_time = time.time()
        result = await next_handler(message, pool)
        duration = time.time() - start_time
        
        await log_analytics(pool, message.from_user.id, duration)
        return result
```

### 4. Content Filtering
```python
class ContentFilterMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        if contains_spam(message.text):
            await message.reply("پیام شما حاوی محتوای نامناسب است.")
            return None
        return await next_handler(message, pool)
```

## Database Functions for Premium Users

### Set Premium Status
```python
from db.queries import set_user_premium
from datetime import datetime, timedelta

# Set user as premium for 30 days
expires_at = datetime.now() + timedelta(days=30)
await set_user_premium(pool, user_id, True, expires_at)

# Set user as premium forever
await set_user_premium(pool, user_id, True, None)

# Remove premium status
await set_user_premium(pool, user_id, False, None)
```

### Check Expired Premiums
```python
from db.queries import check_premium_expired, expire_premium_users

# Get list of expired user IDs
expired_users = await check_premium_expired(pool)

# Automatically expire all expired premiums
count = await expire_premium_users(pool)
print(f"Expired {count} premium subscriptions")
```

## Testing Middlewares

To test a middleware:

1. Add it to the bot temporarily
2. Send test messages
3. Check logs and behavior
4. Remove or keep based on results

Example test:
```python
# In bot.py for testing
def _setup_middlewares(self):
    self.middleware_manager.add(LoggingMiddleware())  # See what's happening
    self.middleware_manager.add(YourTestMiddleware())
```

## Best Practices

1. **Keep middlewares focused** - Each middleware should do one thing well
2. **Order matters** - Put authentication/logging first, rate limiting after
3. **Handle errors** - Wrap middleware logic in try/except
4. **Document behavior** - Add docstrings explaining what the middleware does
5. **Make configurable** - Use __init__ parameters for flexibility
6. **Test thoroughly** - Ensure middlewares don't break the chain unexpectedly

## Migration

To apply the premium user database changes:

```bash
# Run the migration
python db/migrations/migrate.py
```

Or manually execute:
```sql
ALTER TABLE users 
ADD COLUMN is_premium BOOLEAN NOT NULL DEFAULT FALSE AFTER username,
ADD COLUMN premium_expires_at DATETIME NULL AFTER is_premium;

CREATE INDEX idx_users_premium ON users(is_premium, premium_expires_at);
```
