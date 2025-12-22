# Logging Documentation

## Overview

The Daily Digest API uses a container-optimized logging system built on Python's `logging` module. The implementation follows 12-factor app principles with stdout-first logging for production deployments.

## Architecture

### 12-Factor App Approach

**Development:**
- Logs to stdout (console) + rotating files
- DEBUG level for detailed information
- Files stored in `logs/app.log` with automatic rotation

**Production (Docker/Container):**
- Logs to stdout only
- INFO level and above
- No file creation inside container
- Docker/journald handles log persistence

### Request Logging Architecture

**RequestLoggingRoute (Route Class Approach):**
- Applied to API routers (`/api/digest`)
- Logs all business endpoints with full request tracking
- Unique request IDs, timing, error handling

**Health Check Exclusion:**
- `/health` endpoint uses minimal DEBUG logging
- Avoids log noise from monitoring tools and load balancers
- Health checks can be pinged hundreds of times per minute

This selective approach keeps logs focused on actual user/API traffic while avoiding spam from infrastructure monitoring.

### Why Stdout-First?

✅ **Container-native** - Docker automatically captures stdout  
✅ **No disk management** - No need to worry about log rotation in containers  
✅ **Easy integration** - Can forward to CloudWatch, Datadog, Grafana, etc.  
✅ **Standard practice** - Follows cloud-native best practices  
✅ **Simple debugging** - `docker logs` command for immediate access  

## Configuration

### Log Levels

| Level | When Used | Example |
|-------|-----------|---------|
| `DEBUG` | Development only | Detailed cache operations, SQL queries with data |
| `INFO` | Development & Production | Request tracking, database operations, cache hits/misses |
| `WARNING` | All environments | Deprecated features, potential issues |
| `ERROR` | All environments | Failed requests, database errors, exceptions |
| `CRITICAL` | All environments | System failures requiring immediate attention |

### Environment Variables

```bash
# Controls log level and output
ENVIRONMENT=development  # DEBUG level, stdout + files
ENVIRONMENT=production   # INFO level, stdout only
```

### Log Format

**Console (stdout):**
```
%(asctime)s | %(levelname)-8s | %(name)s | %(message)s
```

**Files (development only):**
```
%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s
```

**Example Output:**
```
2024-01-15 10:30:45 | INFO     | app.main | Daily Digest API Starting
2024-01-15 10:30:52 | INFO     | app.middleware | [a1b2c3d4] Incoming: GET /api/digest - Query: {'offset': 0, 'limit': 6}
2024-01-15 10:30:52 | DEBUG    | app.cache | Cache MISS for key: digest:0:6
2024-01-15 10:30:52 | INFO     | app.database | Fetching digest entries - offset: 0, limit: 6
2024-01-15 10:30:52 | INFO     | app.middleware | [a1b2c3d4] Completed: GET /api/digest - Status: 200 - Duration: 45.32ms
```

## What Gets Logged

### Request Logging Scope

**Logged with full tracking (RequestLoggingRoute):**
- `/api/digest` - All digest requests with request ID, timing, cache status

**Minimal logging (DEBUG only):**
- `/health` - Health check pings (avoids monitoring noise)

### Application Lifecycle (`app.main`)

**Startup:**
- Environment configuration
- Database connection status  
- Cache settings (TTL, max size)
- CORS middleware status (dev only)

**Shutdown:**
- Graceful shutdown notification

```
INFO | app.main | ============================================================
INFO | app.main | Daily Digest API Starting
INFO | app.main | Environment: production
INFO | app.main | Database configured: True
INFO | app.main | Cache TTL: 300s, Max Size: 10
INFO | app.main | ============================================================
```

### HTTP Requests (`app.middleware`)

Every request gets:
- **Unique 8-character request ID** for correlation
- Method, path, and query parameters
- Response status code
- Duration in milliseconds
- Full error stack traces on failures

```
INFO | app.middleware | [a1b2c3d4] Incoming: GET /api/digest - Query: {'offset': 0, 'limit': 6}
INFO | app.middleware | [a1b2c3d4] Completed: GET /api/digest - Status: 200 - Duration: 45.32ms
```

**Error example:**
```
ERROR | app.middleware | [e5f6g7h8] Failed: GET /api/digest - Error: DatabaseError: connection timeout - Duration: 5000.12ms
Traceback (most recent call last):
  File "app/middleware.py", line 45, in custom_route_handler
  ...
```

### Database Operations (`app.database`)

- Query results with row counts (INFO)
- Entry titles (DEBUG)
- All errors with stack traces (ERROR)

```
INFO  | app.database | Successfully fetched 6 digest entries
DEBUG | app.database | Query returned entries: ['Article 1', 'Article 2', ...]
```

### Cache Operations (`app.cache`)

- Initialization with settings (INFO)
- Cache hits and misses (DEBUG)
- Items cached (DEBUG)
- Cache clears (INFO)

```
INFO  | app.cache | Cache initialized - Max size: 10, TTL: 300s
DEBUG | app.cache | Cache MISS for key: digest:0:6
DEBUG | app.cache | Caching value for key: digest:0:6 (items in value: 6)
DEBUG | app.cache | Cache HIT for key: digest:0:6
```

### Endpoint Handlers (`app.routers.digest`)

- Cache hit status (INFO)
- Model conversion (DEBUG)

**Cache hit:**
```
INFO  | app.routers.digest | Serving from cache
```

**Cache miss:**
```
DEBUG | app.routers.digest | Converted 6 rows to DigestEntry models
```

### Health Check (`app.main`)

**Why minimal logging?**
Health checks are pinged constantly by:
- Docker health checks
- Load balancers (AWS ELB, ALB)
- Monitoring tools (Datadog, New Relic, etc.)
- Kubernetes liveness/readiness probes

This can generate thousands of logs per day with no useful information. We log at DEBUG level only to confirm the endpoint was called during development, but production logs stay clean.

**Health endpoint access (DEBUG level):**
## Usage in Code

### Getting a Logger

```python
import logging

# Option 1: Direct logger (recommended)
logger = logging.getLogger(__name__)

# Option 2: Using helper function
from app.logging_config import get_logger
logger = get_logger(__name__)
```

### Logging Examples

```python
# Info messages
logger.info("Processing user request")
logger.info(f"Fetching {count} entries from database")

# Debug messages (dev only)
logger.debug(f"Cache key: {key}, value: {value}")
logger.debug(f"Query parameters: offset={offset}, limit={limit}")

# Warnings
logger.warning("Cache size approaching limit")

# Errors with automatic stack traces
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise

# Critical errors
logger.critical("Database connection pool exhausted!")
```

### Request ID Correlation

Access the request ID in your route handlers:

```python
from fastapi import Request

@router.get("/my-endpoint")
async def my_endpoint(request: Request):
    request_id = request.state.request_id
    logger.info(f"[{request_id}] Processing custom logic")
    return {"status": "ok"}
```

## Docker Deployment

### Dockerfile Example

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application
COPY app ./app

# Expose port
EXPOSE 8000

# Set production environment
ENV ENVIRONMENT=production

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Example

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - CACHE_TTL=300
      - CACHE_MAX_SIZE=10
    # Optional: If you want to persist logs on host
    # volumes:
    #   - ./logs:/app/logs
    restart: unless-stopped
```

### Viewing Logs in Production

**Basic Docker commands:**
```bash
# View last 100 lines
docker logs --tail 100 daily-digest-backend

# Follow logs in real-time
docker logs -f daily-digest-backend

# View logs with timestamps
docker logs -t daily-digest-backend

# View logs from last hour
docker logs --since 1h daily-digest-backend

# Search for errors
docker logs daily-digest-backend 2>&1 | grep ERROR

# Track a specific request
docker logs daily-digest-backend 2>&1 | grep "a1b2c3d4"
```

**Docker Compose commands:**
```bash
# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Last 50 lines
docker-compose logs --tail 50 backend

# Logs since timestamp
docker-compose logs --since 2024-01-15T10:00:00 backend
```

**On EC2 with journald:**
```bash
# View Docker logs via journald
journalctl -u docker -f

# Filter by container name
journalctl CONTAINER_NAME=daily-digest-backend -f

# Show last hour
journalctl -u docker --since "1 hour ago"

# Export logs to file
journalctl -u docker --since today > /tmp/app-logs.txt
```

### Log Forwarding (Optional)

**To CloudWatch:**
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: awslogs
      options:
        awslogs-region: us-east-1
        awslogs-group: /aws/ec2/daily-digest
        awslogs-stream: backend
```

**To JSON files:**
```yaml
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

**To syslog:**
```yaml
services:
  backend:
    logging:
      driver: syslog
      options:
        syslog-address: "tcp://logs.example.com:514"
        tag: "daily-digest-api"
```

## Development Workflow

### Running Locally

```bash
cd backend

# Development mode (DEBUG level, stdout + files)
export ENVIRONMENT=development
uv run uvicorn app.main:app --reload

# Watch logs in terminal
tail -f logs/app.log
```

### File Logs (Development Only)

**Location:**
```
backend/logs/
├── app.log          # Current log file
├── app.log.1        # Most recent backup
├── app.log.2
├── app.log.3
├── app.log.4
└── app.log.5        # Oldest backup
```

**Rotation:**
- Automatic rotation at 10MB per file
- Keeps 5 backup files
- Total storage: ~50MB maximum
- Old backups automatically deleted

**Commands:**
```bash
# View recent logs
tail -n 100 logs/app.log

# Follow in real-time
tail -f logs/app.log

# Search for patterns
grep "ERROR" logs/app.log
grep "Cache MISS" logs/app.log

# View all logs including backups
cat logs/app.log* | grep "database"

# Find slow requests
grep -E "Duration: [0-9]{3,}\." logs/app.log

# Count requests per endpoint
grep "Incoming:" logs/app.log | cut -d' ' -f8 | sort | uniq -c
```

## Troubleshooting

### No Logs Appearing

**Check environment variable:**
```bash
echo $ENVIRONMENT
# Should be "development" or "production"
```

**Check log level:**
```python
import logging
print(logging.root.level)  # Should be 10 (DEBUG) or 20 (INFO)
```

**Check handlers:**
```python
import logging
print(logging.root.handlers)  # Should show StreamHandler (and FileHandler in dev)
```

### Logs Not Captured by Docker

Ensure logs go to stdout (not stderr exclusively):
```python
# In logging_config.py
console_handler = logging.StreamHandler(sys.stdout)  # ✅ Correct
# NOT sys.stderr for normal logs
```

### File Logs Growing Too Large (Development)

Adjust rotation settings in `app/logging_config.py`:
```python
file_handler = RotatingFileHandler(
    logs_dir / "app.log",
    maxBytes=5 * 1024 * 1024,  # 5MB instead of 10MB
    backupCount=3,              # 3 backups instead of 5
    encoding="utf-8"
)
```

### Too Much Noise from Third-Party Libraries

Add to `setup_logging()` in `app/logging_config.py`:
```python
# Reduce noise from specific libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("psycopg").setLevel(logging.INFO)
```

## Performance Metrics from Logs

You can extract valuable metrics from logs:

### Request Duration Analysis

```bash
# Average request duration
grep "Duration:" logs/app.log | \
  awk '{print $(NF-1)}' | \
  sed 's/ms$//' | \
  awk '{sum+=$1; count++} END {print sum/count " ms average"}'

# Slowest requests
grep "Duration:" logs/app.log | sort -t: -k5 -n | tail -20
```

### Cache Hit Rate

```bash
# Count hits vs misses
echo "Hits: $(grep -c 'Cache HIT' logs/app.log)"
echo "Misses: $(grep -c 'Cache MISS' logs/app.log)"

# Calculate hit rate
hits=$(grep -c 'Cache HIT' logs/app.log)
misses=$(grep -c 'Cache MISS' logs/app.log)
total=$((hits + misses))
rate=$(echo "scale=2; $hits * 100 / $total" | bc)
echo "Cache hit rate: ${rate}%"
```

### Error Rate

```bash
# Error count by type
grep "ERROR" logs/app.log | \
  awk -F'Error: ' '{print $2}' | \
  cut -d: -f1 | \
  sort | uniq -c | sort -rn

# Errors over time (hourly)
grep "ERROR" logs/app.log | \
  cut -d' ' -f1-2 | \
  cut -d: -f1 | \
  uniq -c
```

### Request Volume

```bash
# Requests per hour
grep "Incoming:" logs/app.log | \
  cut -d' ' -f1-2 | \
  cut -d: -f1 | \
  uniq -c

# Most requested endpoints
grep "Incoming:" logs/app.log | \
  awk '{print $8}' | \
  sort | uniq -c | sort -rn
```

## Future Enhancements

### Adding OpenTelemetry

If you decide to add distributed tracing later:

```bash
uv add opentelemetry-api opentelemetry-sdk \
  opentelemetry-instrumentation-fastapi \
  opentelemetry-exporter-otlp
```

See [OpenTelemetry documentation](https://opentelemetry.io/docs/instrumentation/python/) for setup.

### Adding Sentry

For error tracking and monitoring:

```bash
uv add sentry-sdk[fastapi]
```

```python
# app/main.py
import sentry_sdk

if settings.environment == "production":
    sentry_sdk.init(
        dsn="your-sentry-dsn",
        environment=settings.environment,
        traces_sample_rate=0.1,  # 10% of traces
    )
```

### Structured JSON Logging

For better machine parsing:

```bash
uv add python-json-logger
```

```python
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
```

## Best Practices

✅ **Use appropriate log levels** - DEBUG for dev, INFO for important events, ERROR for failures  
✅ **Include context** - Request IDs, user IDs, resource IDs in log messages  
✅ **Log exceptions properly** - Always use `exc_info=True` for stack traces  
✅ **Avoid logging sensitive data** - No passwords, tokens, PII in logs  
✅ **Use structured messages** - Consistent format makes parsing easier  
✅ **Don't log in loops** - Aggregate first, log summary  
✅ **Monitor log volume** - High volume = high costs with cloud logging services  

## Summary

- **Development**: DEBUG logs to console + files for easy debugging
- **Production**: INFO logs to stdout for Docker to capture
- **Container-friendly**: No disk management needed in production
- **Request tracking**: Unique IDs correlate all logs for a single request
- **Easy access**: `docker logs` command or forward to logging service
- **Future-proof**: Can add Sentry, OpenTelemetry, or other tools later

Your logging system is production-ready and follows industry best practices! 🚀