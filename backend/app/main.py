"""FastAPI app entry point."""

import logging

from fastapi import FastAPI

from app.config import settings
from app.logging_config import setup_logging
from app.middleware import RequestLoggingRoute
from app.routers import digest

# Setup logging first thing
setup_logging()
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Daily Digest API",
    description="API for fetching RSS feed entries from Miniflux",
    version="0.1.0",
    # Disable docs in production
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# CORS middleware - only needed in development when frontend/backend are on different ports
# In production, frontend and backend are served from the same origin (no CORS needed)
if settings.environment == "development":
    from fastapi.middleware.cors import CORSMiddleware

    logger.info("Development mode: Enabling CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Accept", "Accept-Language", "Content-Type"],
    )

# Include routers with custom logging route class
# RequestLoggingRoute is applied per-router (not globally) to avoid logging noise
# from health checks, which get pinged constantly by monitoring tools
app.include_router(digest.router, route_class=RequestLoggingRoute)


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("=" * 60)
    logger.info("Daily Digest API Starting")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database configured: {bool(settings.database_url)}")
    logger.info(
        f"Cache TTL: {settings.cache_ttl}s, Max Size: {settings.cache_max_size}"
    )
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Daily Digest API shutting down...")


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Note: This endpoint does NOT use RequestLoggingRoute to avoid log spam
    from load balancers, Docker health checks, and monitoring tools.
    Uses DEBUG-level logging only for development troubleshooting.
    """
    logger.debug("Health check requested")
    return {"status": "ok"}
