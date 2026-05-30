# Bot Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User (Bale)                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      BaleBot (bot.py)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Middleware Manager                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  1. LoggingMiddleware (optional)                 │  │ │
│  │  │     → Logs all requests                          │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  2. PremiumUserMiddleware                        │  │ │
│  │  │     → Checks premium status                      │  │ │
│  │  │     → Attaches user_data to message              │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  3. RateLimitMiddleware (optional)               │  │ │
│  │  │     → Limits requests per user                   │  │ │
│  │  │     → Bypasses premium users                     │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  4. Custom Middlewares (your own)                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                             │                                │
│                             ▼                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Message Router (Final Handler)            │ │
│  │  • Checks message type (YouTube/Pinterest/Other)      │ │
│  │  • Routes to appropriate handler                      │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│   YouTube Handler         │  │   Pinterest Handler       │
│   (handlers/youtube.py)   │  │   (handlers/pinterest.py) │
│                           │  │                           │
│  • is_youtube()           │  │  • is_pinterest()         │
│  • handle()               │  │  • handle()               │
│  • search_youtube()       │  │  • search_pinterest()     │
│  • handle_youtube_url()   │  │  • handle_pinterest_url() │
└────────────┬──────────────┘  └────────────┬──────────────┘
             │                              │
             ▼                              ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│   YouTube Service         │  │   Pinterest Service       │
│   (services/youtube.py)   │  │   (services/pinterest.py) │
│                           │  │                           │
│  • search_videos()        │  │  • search_pins()          │
│  • get_video_info()       │  │  • get_pin_info()         │
│  • get_download_url()     │  │  • download_pin_image()   │
│  • extract_video_id()     │  │  • extract_pin_id()       │
└────────────┬──────────────┘  └────────────┬──────────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
                ┌───────────────────────┐
                │   Database (MySQL)    │
                │   (db/queries.py)     │
                │                       │
                │  • users              │
                │  • search_logs        │
                │  • download_logs      │
                └───────────────────────┘
```

## Request Flow

### Example: User searches YouTube

```
1. User sends: "/youtube python tutorial"
   │
   ▼
2. BaleBot receives message
   │
   ▼
3. Middleware Chain Execution:
   │
   ├─► LoggingMiddleware
   │   └─► Logs: "[timestamp] User 123: /youtube python tutorial"
   │
   ├─► PremiumUserMiddleware
   │   ├─► Queries database for user
   │   └─► Attaches: message.user_data = {id: 1, is_premium: False}
   │
   ├─► RateLimitMiddleware
   │   ├─► Checks request count for user
   │   ├─► User has 3/10 requests in window
   │   └─► Allows request to continue
   │
   ▼
4. Final Handler (Message Router)
   │
   ├─► Checks: is_youtube("/youtube python tutorial") → True
   │
   ▼
5. YouTube Handler
   │
   ├─► Extracts query: "python tutorial"
   │
   ├─► Calls: search_youtube(message, pool, "python tutorial")
   │
   ▼
6. YouTube Service
   │
   ├─► Calls: youtube_service.search_videos("python tutorial", limit=5)
   │
   ├─► Uses yt-dlp to search
   │
   └─► Returns: [video1, video2, video3, video4, video5]
   │
   ▼
7. YouTube Handler (continued)
   │
   ├─► Logs search to database
   │
   ├─► Formats results with buttons
   │
   └─► Sends reply to user
   │
   ▼
8. User receives search results with interactive buttons
```

## Middleware Chain Detail

```
Request enters middleware chain:

┌─────────────────────────────────────────────────────────┐
│ Middleware 1 (Logging)                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ BEFORE: Log request                                 │ │
│ │ ┌─────────────────────────────────────────────────┐ │ │
│ │ │ Middleware 2 (Premium Check)                    │ │ │
│ │ │ ┌─────────────────────────────────────────────┐ │ │ │
│ │ │ │ BEFORE: Check premium status                │ │ │ │
│ │ │ │ ┌─────────────────────────────────────────┐ │ │ │ │
│ │ │ │ │ Middleware 3 (Rate Limit)               │ │ │ │ │
│ │ │ │ │ ┌─────────────────────────────────────┐ │ │ │ │ │
│ │ │ │ │ │ BEFORE: Check rate limit            │ │ │ │ │ │
│ │ │ │ │ │ ┌─────────────────────────────────┐ │ │ │ │ │ │
│ │ │ │ │ │ │ Final Handler                   │ │ │ │ │ │ │
│ │ │ │ │ │ │ (YouTube/Pinterest Handler)     │ │ │ │ │ │ │
│ │ │ │ │ │ └─────────────────────────────────┘ │ │ │ │ │ │
│ │ │ │ │ │ AFTER: Update rate limit counter    │ │ │ │ │ │
│ │ │ │ │ └─────────────────────────────────────┘ │ │ │ │ │
│ │ │ │ │ AFTER: (nothing)                        │ │ │ │ │
│ │ │ │ └─────────────────────────────────────────┘ │ │ │ │
│ │ │ │ AFTER: (nothing)                            │ │ │ │
│ │ │ └─────────────────────────────────────────────┘ │ │ │
│ │ │ AFTER: (nothing)                                │ │ │
│ │ └─────────────────────────────────────────────────┘ │ │
│ │ AFTER: Log completion                               │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

Response exits middleware chain
```

## Database Schema

```
┌─────────────────────────────────────────────────────────┐
│ users                                                    │
├─────────────────────────────────────────────────────────┤
│ id                INT (PK, AUTO_INCREMENT)              │
│ platform          VARCHAR(20)                           │
│ platform_user_id  BIGINT                                │
│ username          VARCHAR(255)                          │
│ is_premium        BOOLEAN (DEFAULT FALSE)        ← NEW  │
│ premium_expires_at DATETIME (NULL)               ← NEW  │
│ created_at        DATETIME                              │
│ updated_at        DATETIME                              │
├─────────────────────────────────────────────────────────┤
│ UNIQUE KEY: (platform, platform_user_id)                │
│ INDEX: (is_premium, premium_expires_at)          ← NEW  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ search_logs                                              │
├─────────────────────────────────────────────────────────┤
│ id         INT (PK, AUTO_INCREMENT)                     │
│ user_id    INT (FK → users.id)                          │
│ platform   VARCHAR(20)                                  │
│ service    VARCHAR(20) (youtube/pinterest)              │
│ query      TEXT                                         │
│ created_at DATETIME                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ download_logs                                            │
├─────────────────────────────────────────────────────────┤
│ id         INT (PK, AUTO_INCREMENT)                     │
│ user_id    INT (FK → users.id)                          │
│ platform   VARCHAR(20)                                  │
│ service    VARCHAR(20) (youtube/pinterest)              │
│ url        TEXT                                         │
│ quality    VARCHAR(20)                                  │
│ created_at DATETIME                                     │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
project/
│
├── platforms/                    # Platform-specific code
│   ├── middleware.py            # Base middleware system
│   ├── base.py                  # Abstract platform interface
│   │
│   └── bale/                    # Bale platform implementation
│       ├── bot.py               # Main bot class with middleware integration
│       │
│       ├── middlewares/         # Bale-specific middlewares
│       │   ├── __init__.py
│       │   ├── premium.py       # Premium user checking
│       │   ├── rate_limit.py    # Rate limiting
│       │   └── logging.py       # Request logging
│       │
│       └── handlers/            # Message handlers
│           ├── __init__.py
│           ├── youtube.py       # YouTube search/download
│           └── pinterest.py     # Pinterest search/download
│
├── services/                    # Business logic (platform-agnostic)
│   ├── youtube.py              # YouTube service (yt-dlp wrapper)
│   └── pinterest.py            # Pinterest service
│
├── db/                         # Database layer
│   ├── engine.py               # Connection pool management
│   ├── queries.py              # SQL query functions
│   │
│   └── migrations/             # Database migrations
│       ├── migrate.py
│       ├── 001_init.sql
│       └── 002_add_premium_field.sql
│
├── utils/                      # Utility functions
│   └── helpers.py
│
├── examples/                   # Example code
│   └── custom_middleware_example.py
│
├── config.py                   # Configuration (pydantic-settings)
├── main.py                     # Entry point
│
└── Documentation
    ├── MIDDLEWARE.md           # Middleware system guide
    ├── CHANGELOG.md            # What changed
    ├── IMPLEMENTATION_SUMMARY.md # Summary of implementation
    ├── TESTING_GUIDE.md        # How to test
    └── ARCHITECTURE.md         # This file
```

## Key Design Principles

### 1. Separation of Concerns
- **Handlers**: Platform-specific message handling
- **Services**: Business logic (platform-agnostic)
- **Middleware**: Cross-cutting concerns (auth, logging, rate limiting)
- **Database**: Data persistence

### 2. Middleware Pattern (Laravel-style)
- Chain of responsibility
- Each middleware can:
  - Process before handler
  - Modify request
  - Block request
  - Process after handler

### 3. Service Layer
- Platform-agnostic business logic
- Reusable across different platforms (Bale, Telegram, etc.)
- No direct dependency on bot libraries

### 4. Database Layer
- Raw SQL with aiomysql (no ORM)
- Connection pooling for performance
- Async/await throughout

## Adding New Features

### Add New Platform (e.g., Telegram)
```
1. Create platforms/telegram/
2. Implement TelegramBot(BasePlatform)
3. Create handlers in platforms/telegram/handlers/
4. Reuse existing services/ (no changes needed)
5. Add platform-specific middlewares if needed
```

### Add New Service (e.g., Instagram)
```
1. Create services/instagram.py
2. Implement InstagramService class
3. Create platforms/bale/handlers/instagram.py
4. Add routing in bot.py
5. No middleware changes needed
```

### Add New Middleware
```
1. Create platforms/bale/middlewares/your_middleware.py
2. Extend Middleware base class
3. Implement process() method
4. Add to bot.py _setup_middlewares()
```

## Performance Considerations

- **Connection Pooling**: Database connections reused
- **Async/Await**: Non-blocking I/O throughout
- **Rate Limiting**: In-memory (fast, but resets on restart)
- **Middleware Chain**: Minimal overhead, executes in order

## Security Considerations

- **SQL Injection**: Prevented by parameterized queries
- **Rate Limiting**: Protects against abuse
- **Premium Bypass**: Premium users have higher limits
- **Input Validation**: URLs validated before processing

## Scalability

### Current Architecture
- Single bot instance
- In-memory rate limiting
- MySQL database

### For Production Scale
- Multiple bot instances behind load balancer
- Redis for shared rate limiting
- Database read replicas
- Message queue for downloads
- CDN for media delivery
