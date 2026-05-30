# Quick Reference Card

## 🚀 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/youtube [query]` | Search YouTube | `/youtube python tutorial` |
| `/pinterest [query]` | Search Pinterest | `/pinterest home ideas` |
| Send YouTube URL | Download video | `https://youtube.com/watch?v=...` |
| Send Pinterest URL | Download pin | `https://pinterest.com/pin/...` |

## 🔧 Database Functions

```python
from db.queries import set_user_premium, expire_premium_users
from datetime import datetime, timedelta

# Set premium for 30 days
expires = datetime.now() + timedelta(days=30)
await set_user_premium(pool, user_id=1, is_premium=True, expires_at=expires)

# Set premium forever
await set_user_premium(pool, user_id=1, is_premium=True, expires_at=None)

# Remove premium
await set_user_premium(pool, user_id=1, is_premium=False, expires_at=None)

# Auto-expire subscriptions
count = await expire_premium_users(pool)
```

## 🛡️ Built-in Middlewares

```python
# In platforms/bale/bot.py

def _setup_middlewares(self):
    # Premium user checking
    self.middleware_manager.add(PremiumUserMiddleware())
    
    # Rate limiting (10 requests per 60 seconds)
    self.middleware_manager.add(RateLimitMiddleware(
        max_requests=10,
        window_seconds=60
    ))
    
    # Request logging
    self.middleware_manager.add(LoggingMiddleware())
```

## 📝 Create Custom Middleware

```python
from platforms.middleware import Middleware

class MyMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        # Before handler
        print("Before")
        
        # Block if needed
        if should_block:
            await message.reply("Blocked!")
            return None
        
        # Call next handler
        result = await next_handler(message, pool)
        
        # After handler
        print("After")
        
        return result
```

## 🔍 Check Premium Status in Handler

```python
async def handle(message, pool):
    # Access premium status
    is_premium = message.user_data['is_premium']
    user_id = message.user_data['id']
    
    if not is_premium:
        await message.reply("⭐️ Premium only!")
        return
    
    # Premium feature here
```

## 📊 Database Schema

```sql
-- Users table
users (
    id INT PRIMARY KEY,
    platform VARCHAR(20),
    platform_user_id BIGINT,
    username VARCHAR(255),
    is_premium BOOLEAN DEFAULT FALSE,      -- NEW
    premium_expires_at DATETIME NULL,      -- NEW
    created_at DATETIME,
    updated_at DATETIME
)

-- Search logs
search_logs (
    id INT PRIMARY KEY,
    user_id INT,
    platform VARCHAR(20),
    service VARCHAR(20),  -- 'youtube' or 'pinterest'
    query TEXT,
    created_at DATETIME
)

-- Download logs
download_logs (
    id INT PRIMARY KEY,
    user_id INT,
    platform VARCHAR(20),
    service VARCHAR(20),  -- 'youtube' or 'pinterest'
    url TEXT,
    quality VARCHAR(20),
    created_at DATETIME
)
```

## 🎯 Middleware Order

```python
# Order matters! Execution flows top to bottom

self.middleware_manager.add(LoggingMiddleware())      # 1. Log first
self.middleware_manager.add(PremiumUserMiddleware())  # 2. Check premium
self.middleware_manager.add(RateLimitMiddleware())    # 3. Rate limit
self.middleware_manager.add(CustomMiddleware())       # 4. Your logic
# Then final handler (YouTube/Pinterest)
```

## 📁 File Locations

```
platforms/
├── middleware.py                    # Base classes
└── bale/
    ├── bot.py                       # Add middlewares here
    ├── middlewares/
    │   ├── premium.py              # Premium checking
    │   ├── rate_limit.py           # Rate limiting
    │   └── logging.py              # Logging
    └── handlers/
        ├── youtube.py              # YouTube handler
        └── pinterest.py            # Pinterest handler

services/
├── youtube.py                       # YouTube service
└── pinterest.py                     # Pinterest service

db/
├── queries.py                       # Database functions
└── migrations/
    └── 002_add_premium_field.sql   # Premium migration
```

## 🧪 Quick Tests

```bash
# 1. Test YouTube search
# Send: /youtube test

# 2. Test Pinterest search
# Send: /pinterest test

# 3. Test rate limiting
# Send 15 requests quickly

# 4. Set premium
mysql> UPDATE users SET is_premium = TRUE WHERE id = 1;

# 5. Test premium bypass
# Send 15 requests again (should work)
```

## 🔗 Documentation Links

| Document | Purpose |
|----------|---------|
| `MIDDLEWARE.md` | Full middleware guide |
| `TESTING_GUIDE.md` | Testing instructions |
| `ARCHITECTURE.md` | System architecture |
| `examples/custom_middleware_example.py` | 6 examples |

## 💡 Common Patterns

### Block Non-Premium Feature
```python
if not message.user_data['is_premium']:
    await message.reply("⭐️ Premium only!")
    return None
```

### Admin Only
```python
ADMIN_IDS = [123456, 789012]
if user_id not in ADMIN_IDS:
    await message.reply("⛔️ Admin only!")
    return None
```

### Daily Limit
```python
if daily_count >= 50 and not is_premium:
    await message.reply("⚠️ Daily limit reached!")
    return None
```

### Maintenance Mode
```python
if self.maintenance_mode and user_id not in ADMIN_IDS:
    await message.reply("🔧 Under maintenance!")
    return None
```

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Check file paths and imports |
| Database error | Run migration SQL |
| Rate limit not working | Restart bot (in-memory cache) |
| Premium not working | Check database: `SELECT is_premium FROM users` |
| Middleware not executing | Check `_setup_middlewares()` in bot.py |

## 📞 Quick Help

```bash
# Check if migration applied
mysql> DESCRIBE users;
# Should see: is_premium, premium_expires_at

# Check premium users
mysql> SELECT * FROM users WHERE is_premium = TRUE;

# Check recent searches
mysql> SELECT * FROM search_logs ORDER BY created_at DESC LIMIT 10;

# Check recent downloads
mysql> SELECT * FROM download_logs ORDER BY created_at DESC LIMIT 10;
```

## ✅ Checklist

- [ ] Database migration applied
- [ ] Bot starts without errors
- [ ] YouTube search works
- [ ] Pinterest search works
- [ ] Rate limiting works
- [ ] Premium bypass works
- [ ] Custom middleware added (optional)
- [ ] Documentation reviewed

## 🎉 You're Ready!

All features implemented and documented. Start building! 🚀
