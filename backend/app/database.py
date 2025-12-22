"""Database connection and queries for Miniflux Postgres."""

import logging

import psycopg
from psycopg.rows import dict_row

from app.config import settings

logger = logging.getLogger("app.database")


def get_connection():
    """Create a new database connection."""
    try:
        conn = psycopg.connect(settings.database_url, row_factory=dict_row)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        raise


def get_digest_entries(offset: int = 0, limit: int = 6) -> list[dict]:
    """
    Fetch digest entries from Miniflux database.

    Args:
        offset: Starting position for pagination
        limit: Number of entries to return

    Returns:
        List of digest entries with title, summary, source, link, published_at
    """
    query = """
        SELECT
            e.title,
            f.title AS source,
            e.url AS link,
            e.published_at
        FROM entries e
        JOIN feeds f ON e.feed_id = f.id
        WHERE e.published_at >= NOW() - INTERVAL '24 hours'
          AND e.published_at <= NOW()
        ORDER BY e.published_at DESC
        LIMIT %s OFFSET %s;
    """

    try:
        with get_connection() as conn:
            rows = conn.execute(query, (limit, offset)).fetchall()
            logger.info(f"Successfully fetched {len(rows)} digest entries")
            logger.debug(
                f"Query returned entries: {[row.get('title') for row in rows]}"
            )
            return list(rows)
    except Exception as e:
        logger.error(f"Failed to fetch digest entries: {e}", exc_info=True)
        raise
