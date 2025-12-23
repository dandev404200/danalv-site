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

### Production Architecture

```
User Request Flow:

┌──────────┐
│  User    │
│ (Browser)│
└─────┬────┘
      │
      ├─────────────────────────────────────┐
      │                                     │
      ↓                                     ↓
┌─────────────────┐              ┌──────────────────────┐
│   S3 Bucket     │              │   EC2 Instance       │
│  (Vue Static)   │              │  (Public IP/DNS)     │
│   - index.html  │              │                      │
│   - assets/     │              │  ┌────────────────┐  │
│   - *.js, *.css │              │  │ Nginx (80/443) │  │
└─────────────────┘              │  │ Rate Limiting  │  │
                                 │  └────────┬───────┘  │
      Vue app loaded                        │           │
      from S3 makes API                     ↓           │
      requests to EC2 ───────────────▶ ┌─────────────┐  │
      (CORS enabled)                   │  FastAPI    │  │
                                       │  (port 8000)│  │
                                       └──────┬──────┘  │
                                              │         │
                                              ↓         │
                                       ┌─────────────┐  │
                                       │  TTLCache   │  │
                                       │  (1800s)    │  │
                                       └──────┬──────┘  │
                                              │         │
                                    cache miss│         │
                                              ↓         │
                                       ┌─────────────┐  │
                                       │  Miniflux   │  │
                                       │ (port 8080) │  │
                                       └──────┬──────┘  │
                                              │         │
                                              ↓         │
                                       ┌─────────────┐  │
                                       │ PostgreSQL  │  │
                                       │ (port 5432) │  │
                                       └─────────────┘  │
                                                        │
                                 Docker Network         │
                                 (internal only)        │
└──────────────────────────────────────────────────────┘

External RSS Feeds ─────▶ Miniflux (fetches & stores)
```

### Container Layout on EC2

```
EC2 Security Group:
- Inbound: 80/443 from 0.0.0.0/0
- Outbound: All

Docker Containers (same network):
┌─────────────────────────────────────┐
│  nginx:latest                       │
│  Ports: 80:80, 443:443 (exposed)   │
│  - Reverse proxy to FastAPI         │
│  - Rate limiting: 10 req/s          │
│  - TLS termination                  │
│  - Pass-through (no header mods)    │
└─────────────────────────────────────┘
            │
            ↓ (internal network)
┌─────────────────────────────────────┐
│  fastapi-backend                    │
│  Port: 8000 (internal only)         │
│  - API endpoints                    │
│  - CORS middleware (production)     │
│  - Caching layer                    │
└─────────────────────────────────────┘
            │
            ↓ (internal network)
┌─────────────────────────────────────┐
│  miniflux:latest                    │
│  Port: 8080 (internal only)         │
│  - RSS aggregation                  │
│  - Feed management                  │
└─────────────────────────────────────┘
            │
            ↓ (internal network)
┌─────────────────────────────────────┐
│  postgres:17                        │
│  Port: 5432 (internal only)         │
│  - Persistent volume                │
│  - Shared by Miniflux + FastAPI     │
└─────────────────────────────────────┘
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
- **Cross-origin**: Vue app from S3 calls EC2 public IP/DNS for API
- **Development**: Supports `VITE_API_BASE` env var for separate backend
- **Production**: `VITE_API_BASE` set to EC2 public endpoint (e.g., `https://ec2-xx-xxx-xxx-xxx.compute.amazonaws.com`)

## Caching

| Setting | Default | Recommended Production | Environment Variable |
|---------|---------|------------------------|---------------------|
| TTL | 300 seconds | 1800 seconds (30 min) | `CACHE_TTL` |
| Max Size | 10 entries | 10 entries | `CACHE_MAX_SIZE` |

Cache key format: `digest:{offset}:{limit}`

## Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Production | - | PostgreSQL connection string |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `CACHE_TTL` | No | `300` | Cache TTL in seconds |
| `CACHE_MAX_SIZE` | No | `10` | Max cached entries |
| `CORS_ORIGINS` | Production | - | S3 bucket URL in production, localhost in dev |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE` | No | `""` (relative) | API base URL for development |

## Security Features

### Separation of Concerns

**Nginx Layer (Traffic Management):**
- Rate limiting: 10 requests/second per IP, burst 20
- TLS termination (HTTPS enforcement)
- Reverse proxy to FastAPI (pass-through only)
- No header modification or CORS handling

**FastAPI Layer (Application Logic):**
- CORS protection: Middleware allows S3 bucket origin only in production
- Docs disabled in production: `/docs` and `/redoc` return 404
- Config validation: App exits on startup if production config is invalid
- Parameterized queries: SQL injection protection via psycopg
- Input validation: Query constraints on offset/limit
- No hardcoded secrets: All credentials via environment variables

### Infrastructure Security
- **S3 bucket**: Public read-only for static files (no write access)
- **EC2 security group**: Only ports 80/443 open to internet
- **Container isolation**: FastAPI, Miniflux, PostgreSQL not exposed to internet
- **Docker network**: Internal-only communication between containers
- **Nginx TLS termination**: HTTPS enforced (with Let's Encrypt or self-signed cert)

### CORS Configuration Notes

Unlike same-origin deployments, this architecture requires CORS because:
- Frontend served from: `https://your-bucket.s3.amazonaws.com`
- Backend served from: `https://ec2-xx-xxx-xxx-xxx.compute.amazonaws.com`

**Important:** FastAPI CORS middleware MUST be enabled in production with `CORS_ORIGINS` set to S3 bucket URL(s). Nginx does NOT add or modify CORS headers - it passes responses through unchanged. This keeps CORS policy enforcement at the application layer where it belongs.

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

### Overview

This architecture separates static assets (S3) from dynamic backend (EC2) for cost optimization while gaining AWS practice with EC2, Docker, and Nginx.

### Deployment Components

1. **S3 Bucket**: Hosts Vue static files with public read access
2. **EC2 Instance**: Runs Docker containers (Nginx, FastAPI, Miniflux, PostgreSQL)
3. **Docker Compose**: Orchestrates all containers on single EC2 instance
4. **Nginx**: Reverse proxy with rate limiting and TLS termination (pass-through only, no header modification)
5. **FastAPI**: Handles CORS policy - configured to accept requests from S3 bucket origin only

### Configuration Requirements

**Backend (.env on EC2):**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://miniflux:PASSWORD@postgres:5432/miniflux
CACHE_TTL=1800  # 30 minutes recommended
CACHE_MAX_SIZE=10

# CORS - S3 bucket URL (REQUIRED in production for this architecture)
CORS_ORIGINS=https://your-bucket-name.s3.amazonaws.com,https://your-bucket-name.s3.us-east-1.amazonaws.com

# Miniflux
MINIFLUX_ADMIN_USERNAME=admin
MINIFLUX_ADMIN_PASSWORD=SECURE_PASSWORD
MINIFLUX_DATABASE_URL=postgresql://miniflux:PASSWORD@postgres:5432/miniflux?sslmode=disable

# PostgreSQL
POSTGRES_USER=miniflux
POSTGRES_PASSWORD=PASSWORD
POSTGRES_DB=miniflux
```

**Frontend (.env.production):**
```bash
# EC2 public endpoint
VITE_API_BASE=https://ec2-xx-xxx-xxx-xxx.compute.amazonaws.com
# OR use Elastic IP / custom domain
VITE_API_BASE=https://api.yourdomain.com
```

### Deployment Steps

1. **S3**: Upload Vue build (`dist/`) to S3 bucket, enable static website hosting
2. **EC2**: Launch instance, install Docker & Docker Compose
3. **Nginx**: Configure reverse proxy to FastAPI container with rate limiting
4. **Docker Compose**: Start all containers with proper environment variables
5. **DNS** (optional): Point custom domain to EC2 Elastic IP

### Trade-offs of This Architecture

**Advantages:**
- Lower cost than ALB (~$18/month savings)
- S3 for static assets (cheap, fast)
- Docker practice on EC2
- Nginx configuration experience
- Clean separation of concerns (Nginx for traffic, FastAPI for logic)
- Simple to understand and debug

**Disadvantages:**
- CORS required (S3 and EC2 are different origins)
- No built-in auto-scaling (single EC2 instance)
- Manual SSL certificate management (or use Let's Encrypt)
- Single point of failure (no high availability)

### Cost Estimate

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| S3 | ~5GB storage + requests | $0.50 |
| EC2 | t3.small (2vCPU, 2GB RAM) | $15.00 |
| EBS | 30GB gp3 | $2.40 |
| Elastic IP | 1 IP | $0.00 (free if attached) |
| **TOTAL** | | **~$18/month** |

Compare to ALB architecture: ~$35-40/month (saves ~$20/month)