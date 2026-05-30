# Changelog

## [2025-01-15] - Major Update

### Added

#### 1. Middleware System (Laravel-style)
- **Base middleware infrastructure** (`platforms/middleware.py`)
  - Abstract `Middleware` class for creating custom middlewares
  - `MiddlewareManager` for chaining and executing middlewares
  - Support for request preprocessing and postprocessing

- **Built-in Middlewares:**
  - `PremiumUserMiddleware` - Checks premium status and attaches user data
  - `RateLimitMiddleware` - Rate limiting with premium user bypass
  - `LoggingMiddleware` - Request/response logging

#### 2. Search Functionality
- **YouTube Search** - Already implemented, now properly integrated
  - `/youtube [query]` - Search YouTube videos
  - Returns top 5 results with video info
  - Interactive buttons for each result

- **Pinterest Search** - NEW
  - `/pinterest [query]` - Search Pinterest pins
  - Returns top 5 results with pin info
  - Interactive buttons for each result
  - Proper service layer implementation

#### 3. Premium User System
- **Database Schema:**
  - Added `is_premium` field to users table
  - Added `premium_expires_at` field for subscription management
  - Index for efficient premium user queries

- **Database Functions:**
  - `set_user_premium()` - Set/remove premium status
  - `check_premium_expired()` - Get list of expired premiums
  - `expire_premium_users()` - Automatically expire subscriptions

#### 4. Documentation
- `MIDDLEWARE.md` - Complete middleware system documentation
- `CHANGELOG.md` - This file

### Fixed

#### Pinterest Handler
- Fixed missing `pool` parameter in handler
- Removed dependency on old service layer structure
- Now properly integrated with new service architecture
- Added proper error handling

#### Service Layer
- Refactored `services/pinterest.py` to use class-based service
- Created `PinterestService` singleton similar to `YouTubeService`
- Removed platform-specific logic from service layer
- Proper separation of concerns

### Changed

#### Bot Architecture
- Integrated middleware system into message handling
- All requests now go through middleware chain
- Better error messages with command hints
- Improved user experience

#### Handler Structure
- Both YouTube and Pinterest handlers now follow same pattern
- Consistent parameter passing (message, pool)
- Better separation between search and download functionality

### Migration Required

Run the following SQL migration:
```sql
ALTER TABLE users 
ADD COLUMN is_premium BOOLEAN NOT NULL DEFAULT FALSE AFTER username,
ADD COLUMN premium_expires_at DATETIME NULL AFTER is_premium;

CREATE INDEX idx_users_premium ON users(is_premium, premium_expires_at);
```

Or use: `db/migrations/002_add_premium_field.sql`

## Usage Examples

### Search YouTube
```
/youtube python tutorial
```

### Search Pinterest
```
/pinterest home decoration ideas
```

### Download from URL
Just send a YouTube or Pinterest URL directly.

### Check Premium Status (in handler)
```python
if message.user_data['is_premium']:
    # Premium feature
else:
    await message.reply("⭐️ این ویژگی فقط برای کاربران ویژه است.")
```

### Add Custom Middleware
```python
# In platforms/bale/bot.py
def _setup_middlewares(self):
    self.middleware_manager.add(PremiumUserMiddleware())
    self.middleware_manager.add(RateLimitMiddleware(max_requests=10, window_seconds=60))
    self.middleware_manager.add(YourCustomMiddleware())
```

## Breaking Changes

None - All changes are backward compatible.

## Notes

- Pinterest search/download uses placeholder implementation
- In production, implement proper Pinterest API integration
- Rate limiting is in-memory (resets on bot restart)
- Consider Redis for persistent rate limiting in production
