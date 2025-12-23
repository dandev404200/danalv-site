"""
Digest router - /api/digest endpoint
"""

import logging

from fastapi import APIRouter, Query

from app.cache import get_cache_key, get_cached, set_cached
from app.database import get_digest_entries
from app.middleware import RequestLoggingRoute
from app.models import DigestEntry

logger = logging.getLogger("app.routers.digest")

router = APIRouter(route_class=RequestLoggingRoute)


@router.get("/api/digest", response_model=list[DigestEntry])
async def get_digest(
    offset: int = Query(default=0, ge=0, le=36),
    limit: int = Query(default=6, ge=1, le=6),
) -> list[DigestEntry]:
    """
    Get digest entries with pagination.

    Args:
        offset: Starting position (0-36, default 0)
        limit: Number of entries to return (1-6, default 6)

    Returns:
        List of digest entries
    """
    # Check cache first
    cache_key = get_cache_key(offset, limit)
    cached_result = get_cached(cache_key)

    if cached_result is not None:
        logger.info("Serving from cache")
        return cached_result

    # Cache miss - query database
    rows = get_digest_entries(offset, limit)

    # Convert to Pydantic models
    entries = [DigestEntry(**row) for row in rows]
    logger.debug(f"Converted {len(entries)} rows to DigestEntry models")

    # Only cache non-empty results to avoid stale empty responses
    if entries:
        set_cached(cache_key, entries)
    else:
        logger.debug("Skipping cache for empty result")

    return entries
