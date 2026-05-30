# Testing Guide

This guide helps you test all the new features implemented in the bot.

## Prerequisites

1. Database migration applied:
```bash
mysql -u your_user -p your_database < db/migrations/002_add_premium_field.sql
```

2. Bot is running:
```bash
python main.py
```

## Test 1: YouTube Search

### Steps:
1. Open your Bale bot chat
2. Send: `/youtube python tutorial`

### Expected Result:
- Bot replies with "🔍 در حال جستجو در یوتیوب..."
- Returns 5 search results with:
  - Video title
  - Duration
  - Uploader name
  - View count
  - Interactive buttons for each video

### Success Criteria:
✅ Search results displayed
✅ Buttons are clickable
✅ No errors in console

## Test 2: Pinterest Search

### Steps:
1. Send: `/pinterest home decoration`

### Expected Result:
- Bot replies with "🔍 در حال جستجو در پینترست..."
- Returns 5 search results with:
  - Pin title
  - Description
  - URL
  - Interactive buttons for each pin

### Success Criteria:
✅ Search results displayed
✅ Buttons are clickable
✅ No errors in console

## Test 3: YouTube URL Download

### Steps:
1. Send a YouTube URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

### Expected Result:
- Bot displays video information
- Shows quality options
- Provides download buttons

### Success Criteria:
✅ Video info displayed
✅ Quality options shown
✅ Download logged in database

## Test 4: Pinterest URL Download

### Steps:
1. Send a Pinterest URL: `https://www.pinterest.com/pin/123456789/`

### Expected Result:
- Bot displays pin information
- Shows download confirmation

### Success Criteria:
✅ Pin info displayed
✅ Download logged in database

## Test 5: Middleware - Premium User Check

### Steps:
1. Check database for your user:
```sql
SELECT * FROM users WHERE platform = 'bale' AND platform_user_id = YOUR_ID;
```

2. Note the `is_premium` field (should be FALSE by default)

3. Send any command to the bot

4. Check console logs - should show user data attached

### Expected Result:
- Middleware attaches `user_data` to message
- `is_premium` is FALSE for new users

### Success Criteria:
✅ No errors
✅ User data attached to message
✅ Premium status correctly identified

## Test 6: Middleware - Rate Limiting

### Steps:
1. Send 15 requests quickly (within 60 seconds):
```
/youtube test 1
/youtube test 2
/youtube test 3
... (repeat 15 times)
```

### Expected Result:
- First 10 requests: Normal processing
- After 10 requests: Rate limit message
  - "⚠️ شما به حد مجاز درخواست رسیده‌اید."
  - "لطفاً 60 ثانیه صبر کنید."

### Success Criteria:
✅ Rate limit triggered after 10 requests
✅ Error message displayed
✅ Requests blocked until window expires

## Test 7: Premium User Bypass

### Steps:
1. Set yourself as premium:
```sql
UPDATE users 
SET is_premium = TRUE 
WHERE platform = 'bale' AND platform_user_id = YOUR_ID;
```

2. Restart the bot (to clear rate limit cache)

3. Send 15 requests quickly again

### Expected Result:
- All 15 requests processed successfully
- No rate limit message
- Premium users bypass rate limiting

### Success Criteria:
✅ All requests processed
✅ No rate limit triggered
✅ Premium bypass working

## Test 8: Logging Middleware

### Steps:
1. Enable logging middleware in `platforms/bale/bot.py`:
```python
from platforms.bale.middlewares import LoggingMiddleware

def _setup_middlewares(self):
    self.middleware_manager.add(LoggingMiddleware())
    self.middleware_manager.add(PremiumUserMiddleware())
```

2. Restart bot

3. Send any command

### Expected Result:
Console shows:
```
[2025-01-15 10:30:45] User 123456 (@username): /youtube test
[2025-01-15 10:30:46] Request processed for user 123456
```

### Success Criteria:
✅ Request logged with timestamp
✅ User info displayed
✅ Processing completion logged

## Test 9: Invalid Commands

### Steps:
1. Send: `hello`
2. Send: `random text`
3. Send: `/unknown`

### Expected Result:
Bot replies with:
```
دستور نامعتبر است.

دستورات موجود:
/youtube [جستجو] - جستجو در یوتیوب
/pinterest [جستجو] - جستجو در پینترست

یا لینک یوتیوب/پینترست ارسال کنید.
```

### Success Criteria:
✅ Helpful error message
✅ Available commands listed
✅ No crashes

## Test 10: Database Logging

### Steps:
1. Send: `/youtube test query`
2. Send a YouTube URL

3. Check database:
```sql
-- Check search log
SELECT * FROM search_logs 
WHERE service = 'youtube' 
ORDER BY created_at DESC 
LIMIT 1;

-- Check download log
SELECT * FROM download_logs 
WHERE service = 'youtube' 
ORDER BY created_at DESC 
LIMIT 1;
```

### Expected Result:
- Search logged with query "test query"
- Download logged with URL

### Success Criteria:
✅ Search logged correctly
✅ Download logged correctly
✅ User ID matches
✅ Timestamps correct

## Test 11: Premium Expiration

### Steps:
1. Set premium with expiration:
```sql
UPDATE users 
SET is_premium = TRUE, 
    premium_expires_at = DATE_ADD(NOW(), INTERVAL 1 MINUTE)
WHERE platform = 'bale' AND platform_user_id = YOUR_ID;
```

2. Wait 2 minutes

3. Run expiration check:
```python
from db.engine import get_pool
from db.queries import expire_premium_users

pool = await get_pool()
count = await expire_premium_users(pool)
print(f"Expired {count} users")
```

### Expected Result:
- Your premium status set to FALSE
- `premium_expires_at` remains set

### Success Criteria:
✅ Premium expired automatically
✅ Count returned correctly
✅ Database updated

## Test 12: Custom Middleware

### Steps:
1. Add a simple test middleware in `bot.py`:
```python
class TestMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        print("🧪 Test middleware executed!")
        return await next_handler(message, pool)

def _setup_middlewares(self):
    self.middleware_manager.add(TestMiddleware())
    self.middleware_manager.add(PremiumUserMiddleware())
```

2. Restart bot

3. Send any command

### Expected Result:
Console shows: `🧪 Test middleware executed!`

### Success Criteria:
✅ Custom middleware executed
✅ Message passed to next handler
✅ No errors

## Test 13: Middleware Order

### Steps:
1. Add multiple middlewares with logging:
```python
class FirstMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        print("1️⃣ First middleware - BEFORE")
        result = await next_handler(message, pool)
        print("1️⃣ First middleware - AFTER")
        return result

class SecondMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        print("2️⃣ Second middleware - BEFORE")
        result = await next_handler(message, pool)
        print("2️⃣ Second middleware - AFTER")
        return result

def _setup_middlewares(self):
    self.middleware_manager.add(FirstMiddleware())
    self.middleware_manager.add(SecondMiddleware())
```

2. Send any command

### Expected Result:
Console shows:
```
1️⃣ First middleware - BEFORE
2️⃣ Second middleware - BEFORE
2️⃣ Second middleware - AFTER
1️⃣ First middleware - AFTER
```

### Success Criteria:
✅ Middlewares execute in order
✅ Nested execution (onion pattern)
✅ All middlewares complete

## Test 14: Middleware Blocking

### Steps:
1. Add blocking middleware:
```python
class BlockingMiddleware(Middleware):
    async def process(self, message, pool, next_handler):
        if "block" in message.text.lower():
            await message.reply("🚫 Blocked by middleware!")
            return None  # Don't call next handler
        return await next_handler(message, pool)
```

2. Send: `block this message`

### Expected Result:
- Bot replies: "🚫 Blocked by middleware!"
- Handler never executes
- No further processing

### Success Criteria:
✅ Message blocked
✅ Handler not executed
✅ Custom reply sent

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Make sure all files are created and Python can import them

### Issue: Database errors
**Solution:** Run migration: `mysql -u user -p db < db/migrations/002_add_premium_field.sql`

### Issue: Rate limit not working
**Solution:** Restart bot to clear in-memory cache

### Issue: Middleware not executing
**Solution:** Check `_setup_middlewares()` in `bot.py` and ensure middleware is added

### Issue: Premium status not working
**Solution:** Check database: `SELECT is_premium FROM users WHERE ...`

## Performance Testing

### Load Test:
1. Send 100 requests rapidly
2. Monitor response times
3. Check for memory leaks
4. Verify all requests processed

### Expected:
- All requests handled
- No crashes
- Reasonable response times
- Memory stable

## Success Checklist

- [ ] YouTube search working
- [ ] Pinterest search working
- [ ] YouTube download working
- [ ] Pinterest download working
- [ ] Premium user middleware working
- [ ] Rate limiting working
- [ ] Premium bypass working
- [ ] Logging middleware working
- [ ] Database logging working
- [ ] Premium expiration working
- [ ] Custom middleware working
- [ ] Middleware order correct
- [ ] Middleware blocking working
- [ ] Invalid commands handled
- [ ] No console errors

## Next Steps After Testing

1. ✅ All tests pass → Deploy to production
2. ❌ Some tests fail → Check logs and fix issues
3. 🔧 Need modifications → Adjust middleware/handlers as needed

## Getting Help

If tests fail:
1. Check console logs for errors
2. Verify database schema is correct
3. Ensure all files are created
4. Check `MIDDLEWARE.md` for documentation
5. Review `examples/custom_middleware_example.py` for examples
