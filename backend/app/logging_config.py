"""Logging configuration for the application.

Container-optimized logging following 12-factor app principles:
- Production: stdout only (Docker captures logs)
- Development: stdout + rotating file logs
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


def setup_logging() -> None:
    """Configure application logging.

    Production (containers):
    - Logs to stdout only
    - Docker/journald handles log persistence
    - INFO level and above

    Development:
    - Logs to stdout + rotating files
    - DEBUG level for detailed output
    - Files stored in logs/ directory
    """
    # Determine log level based on environment
    log_level = logging.DEBUG if settings.environment == "development" else logging.INFO

    # Console formatter - clean and structured
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout) - ALWAYS enabled for Docker
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File logging ONLY in development
    # In production, Docker handles log persistence
    if settings.environment == "development":
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # File formatter - more detailed with function names and line numbers
        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            logs_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # Log configuration confirmation
    logger = logging.getLogger("app")
    logger.info(
        f"Logging configured - Environment: {settings.environment}, "
        f"Level: {logging.getLevelName(log_level)}, "
        f"Handlers: stdout{' + file' if settings.environment == 'development' else ''}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Usually __name__ from the calling module

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing request")
    """
    # Ensure all app loggers are under 'app' namespace
    if not name.startswith("app"):
        name = f"app.{name}"
    return logging.getLogger(name)
