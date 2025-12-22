# Daily Digest Architecture

## Overview

A daily digest page for a personal website displaying RSS feed entries as Vue cards with infinite scroll. Data is sourced from a self-hosted Miniflux instance via a FastAPI backend.

## Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend | Vue 3 (Composition API) | 3.5.25 |
| Styling | Tailwind CSS | 4.1.17 |
| Build | Vite (rolldown) | latest |
| Routing | vue-router | 4.6.3 |
| Icons | lucide-vue-next | 0.555.0 |
| API | FastAPI + uvicorn | 0.124.4 / 0.38.0 |
| Database | PostgreSQL (shared with Miniflux) | 17+ |
| DB Driver | psycopg | 3.3.2 |
| RSS Engine | Miniflux (Docker) | latest |
| Caching | cachetools (in-memory TTL) | 6.2.4 |
| Runtime | Python | 3.13+ |

## Architecture Diagram

```
User Request Path:

┌──────────┐     ┌─────────────────┐     ┌─────────────┐     ┌───────────┐     ┌──────────────────┐
│  User    │────▶│  Vue Frontend   │────▶│   FastAPI   │────▶│ TTLCache  │────▶│    PostgreSQL    │
│ (Browser)│     │  (Vite build)   │     │   Backend   │     │ (300s)    │     │  (Miniflux DB)   │
└──────────┘     └─────────────────┘     └─────────────┘     └───────────┘     └──────────────────┘
                   Infinite Scroll         /api/digest           │                      ▲
                   Max 42 cards            /health               │ cache miss           │
                                                                 └──────────────────────┤
                                                                                        │ writes
                                                                               ┌────────┴────────┐
                                                                               │    Miniflux     │
                                                                               │    Server       │
                                                                               └────────┬────────┘
                                                                                        │ fetches
                                                                               ┌────────┴────────┐
                                                                               │  RSS Feeds      │
                                                                               └─────────────────┘
```

## API Endpoints

### `GET /api/digest`

Fetch digest entries with pagination.

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `offset` | int | 0 | 0-36 | Starting position |
| `limit` | int | 6 | 1-6 | Entries per request |

**Response:** `DigestEntry[]`

```json
[
  {
    "title": "Article Title",
    "source": "Feed Name",
    "link": "https://example.com/article",
    "published_at": "2025-01-15T10:30:00Z"
  }
]
```

**Query Logic:**
- Fetches entries from last 24 hours
- Ordered by `published_at DESC`
- Joins `entries` and `feeds` tables from Miniflux DB

### `GET /health`

Health check endpoint.

**Response:** `{"status": "ok"}`

## Frontend Behavior

- **Infinite scroll**: Loads 6 entries at a time when user scrolls within 200px of bottom
- **Max cards**: Stops loading after 42 cards
- **Same-origin**: Uses relative API paths in production (`/api/digest`)
- **Development**: Supports `VITE_API_BASE` env var for separate backend

## Caching

| Setting | Default | Environment Variable |
|---------|---------|---------------------|
| TTL | 300 seconds | `CACHE_TTL` |
| Max Size | 10 entries | `CACHE_MAX_SIZE` |

Cache key format: `digest:{offset}:{limit}`

## Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Production | - | PostgreSQL connection string |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `CACHE_TTL` | No | `300` | Cache TTL in seconds |
| `CACHE_MAX_SIZE` | No | `10` | Max cached entries |
| `CORS_ORIGINS` | No | localhost:5173 | Dev only, comma-separated |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE` | No | `""` (relative) | API base URL for development |

## Security Features

- **Same-origin deployment**: No CORS needed in production
- **CORS dev-only**: Middleware only loaded when `ENVIRONMENT=development`
- **Docs disabled in production**: `/docs` and `/redoc` return 404
- **Config validation**: App exits on startup if production config is invalid
- **Parameterized queries**: SQL injection protection via psycopg
- **Input validation**: FastAPI Query constraints on offset/limit
- **No hardcoded secrets**: All credentials via environment variables

## Logging & Monitoring

### Overview

Comprehensive logging system using Python's built-in `logging` module with structured output, request tracking, and automatic file rotation.

### Logging Configuration

**Container-optimized following 12-factor app principles:**

| Setting | Development | Production (Docker) |
|---------|------------|---------------------|
| Log Level | `DEBUG` | `INFO` |
| Console Output | ✅ stdout | ✅ stdout |
| File Output | ✅ `logs/app.log` | ❌ None |
| File Rotation | 10MB max, 5 backups | N/A |
| Log Persistence | Local files | Docker/journald |

**Why stdout-only in production:**
- Docker automatically captures stdout logs
- No disk space concerns inside containers
- Easy to view with `docker logs` command
- Can forward to CloudWatch, Datadog, etc.
- Follows cloud-native best practices

### Log Format

**Console:**
```
%(asctime)s | %(levelname)-8s | %(name)s | %(message)s
```

**File:**
```
%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s
```

**Example:**
```
2024-01-15 10:30:45 | INFO     | app.main | Daily Digest API Starting
2024-01-15 10:30:52 | INFO     | app.middleware | [a1b2c3d4] Incoming: GET /api/digest - Query: {'offset': 0, 'limit': 6}
```

### What Gets Logged

#### Application Lifecycle (`app.main`)
- **Startup events:**
  - Environment configuration
  - Database connection status
  - Cache settings (TTL, max size)
  - CORS middleware status (dev only)
- **Shutdown events:**
  - Graceful shutdown notification

**Example:**
```
INFO | app.main | ============================================================
INFO | app.main | Daily Digest API Starting
INFO | app.main | Environment: development
INFO | app.main | Database configured: True
INFO | app.main | Cache TTL: 300s, Max Size: 10
INFO | app.main | ============================================================
```

#### HTTP Requests (`app.middleware`)
- **Unique request ID** (8-character UUID) for correlation
- **Incoming request:**
  - HTTP method (GET, POST, etc.)
  - Full URL path
  - Query parameters
- **Completed request:**
  - Response status code
  - Request duration in milliseconds
- **Failed request:**
  - Exception type and message
  - Full stack trace
  - Duration until failure

**Example:**
```
INFO | app.middleware | [a1b2c3d4] Incoming: GET /api/digest - Query: {'offset': 0, 'limit': 6}
INFO | app.middleware | [a1b2c3d4] Completed: GET /api/digest - Status: 200 - Duration: 45.32ms
```

**Error Example:**
```
ERROR | app.middleware | [e5f6g7h8] Failed: GET /api/digest - Error: DatabaseError: connection timeout - Duration: 5000.12ms
Traceback (most recent call last):
  File "app/middleware.py", line 45, in custom_route_handler
  ...
```

#### Database Operations (`app.database`)
- **Query results:**
  - Number of rows returned
  - Entry titles (DEBUG level only)
- **Errors:**
  - Connection failures with stack traces
  - Query execution errors

**Example:**
```
INFO  | app.database | Successfully fetched 6 digest entries
DEBUG | app.database | Query returned entries: ['Article 1', 'Article 2', 'Article 3', ...]
```

#### Cache Operations (`app.cache`)
- **Initialization:**
  - Cache max size and TTL settings
- **Cache lookups:**
  - Cache HIT with key
  - Cache MISS with key
- **Cache writes:**
  - Cache key and number of items stored
- **Cache clears:**
  - Manual cache clearing events

**Example:**
```
INFO  | app.cache | Cache initialized - Max size: 10, TTL: 300s
DEBUG | app.cache | Cache MISS for key: digest:0:6
DEBUG | app.cache | Caching value for key: digest:0:6 (items in value: 6)
DEBUG | app.cache | Cache HIT for key: digest:0:6
```

#### Endpoint Handlers (`app.routers.digest`)
- **Cache status:**
  - Whether serving from cache
- **Data processing:**
  - Number of rows converted to models (DEBUG level)

**Example (cache hit):**
```
INFO  | app.routers.digest | Serving from cache
```

**Example (cache miss):**
```
DEBUG | app.routers.digest | Converted 6 rows to DigestEntry models
```

#### Health Check (`app.main`)
- Health endpoint access (DEBUG level)

**Example:**
```
DEBUG | app.main | Health check requested
```

### Request Tracking Flow

Complete example of a single request lifecycle:

```
# Request arrives
INFO  | app.middleware | [a1b2c3d4] Incoming: GET /api/digest - Query: {'offset': 0, 'limit': 6}

# Cache lookup (miss)
DEBUG | app.cache | Cache MISS for key: digest:0:6

# Database query
INFO  | app.database | Successfully fetched 6 digest entries
DEBUG | app.database | Query returned entries: ['Article 1', 'Article 2', ...]

# Model conversion and caching
DEBUG | app.routers.digest | Converted 6 rows to DigestEntry models
DEBUG | app.cache | Caching value for key: digest:0:6 (items in value: 6)

# Response sent
INFO  | app.middleware | [a1b2c3d4] Completed: GET /api/digest - Status: 200 - Duration: 45.32ms
```

### Log Files

**Development only:**
```
backend/logs/
├── app.log          # Current log file
├── app.log.1        # Most recent backup
├── app.log.2
├── app.log.3
├── app.log.4
└── app.log.5        # Oldest backup
```

**Rotation (development):**
- Automatic rotation at 10MB
- Keeps 5 backup files
- Total maximum: ~50MB of logs

**Production (Docker):**
- No log files created inside container
- All logs go to stdout
- Docker captures and manages logs
- Access via `docker logs` or `journalctl`

### Viewing Logs

**Development (local):**
```bash
# View recent logs
tail -n 50 logs/app.log

# Follow logs in real-time
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# Find all logs for a specific request
grep "a1b2c3d4" logs/app.log
```

**Production (Docker on EC2):**
```bash
# View recent logs from container
docker logs --tail 100 daily-digest-backend

# Follow logs in real-time
docker logs -f daily-digest-backend

# Search for errors
docker logs daily-digest-backend 2>&1 | grep ERROR

# Find all logs for a specific request
docker logs daily-digest-backend 2>&1 | grep "a1b2c3d4"

# Search for cache misses
docker logs daily-digest-backend 2>&1 | grep "Cache MISS"

# Find slow requests (>1 second)
docker logs daily-digest-backend 2>&1 | grep -E "Duration: [0-9]{4,}\."

# View logs via journald (if using systemd)
journalctl -u docker CONTAINER_NAME=daily-digest-backend -f
```

**Docker Compose:**
```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail 100 backend
```

### Performance Metrics Available

From logs, you can extract:
- **Average request duration** by endpoint
- **Cache hit rate** (MISS vs HIT counts)
- **Error rate** (ERROR vs INFO counts)
- **Database query frequency** (cache effectiveness)
- **Peak usage times** (timestamp analysis)

### Third-Party Library Logging

Noise reduction for common libraries:

| Library | Level | Purpose |
|---------|-------|---------|
| `uvicorn.access` | `WARNING` | Reduce access log duplication |
| `uvicorn.error` | `INFO` | Keep error visibility |

## Development

### Run Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### Run Frontend

```bash
cd frontend
bun install
bun run dev
```

### Run Miniflux + Postgres

```bash
cd backend
# Create .env with required variables first
docker-compose up -d
```

## Production Deployment

1. Frontend and backend served from same origin (no CORS)
2. Reverse proxy routes `/api/*` to FastAPI, `/*` to static files
3. Set `ENVIRONMENT=production` and `DATABASE_URL`
4. Database credentials via environment variables only