"""Caching layer for digest entries."""

import logging

from cachetools import TTLCache

from app.config import settings

logger = logging.getLogger("app.cache")

# Cache for digest entries
# Key format: "digest:{offset}:{limit}"
digest_cache: TTLCache = TTLCache(
    maxsize=settings.cache_max_size,
    ttl=settings.cache_ttl,
)

logger.info(
    f"Cache initialized - Max size: {settings.cache_max_size}, TTL: {settings.cache_ttl}s"
)


def get_cache_key(offset: int, limit: int) -> str:
    """Generate cache key for digest queries."""
    return f"digest:{offset}:{limit}"


def get_cached(key: str):
    """Get value from cache, returns None if not found."""
    value = digest_cache.get(key)
    if value is not None:
        logger.debug(f"Cache HIT for key: {key}")
    else:
        logger.debug(f"Cache MISS for key: {key}")
    return value


def set_cached(key: str, value):
    """Set value in cache."""
    logger.debug(
        f"Caching value for key: {key} "
        f"(items in value: {len(value) if isinstance(value, list) else 'N/A'})"
    )
    digest_cache[key] = value


def clear_cache():
    """Clear all cached entries."""
    logger.info("Clearing all cache entries")
    digest_cache.clear()
