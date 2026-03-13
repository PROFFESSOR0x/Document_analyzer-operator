"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.settings import get_settings

settings = get_settings()


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
) -> None:
    """Configure application logging.

    Args:
        log_level: Override the default log level from settings.
        log_file: Override the default log file from settings.
        log_format: Override the default log format from settings.
    """
    level = getattr(logging, (log_level or settings.log_level).upper())
    fmt = log_format or settings.log_format
    log_path = log_file or settings.log_file

    # Create formatter
    formatter = logging.Formatter(fmt)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    # Create file handler if specified
    if log_path:
        log_dir = Path(log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: The logger name (typically __name__).

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
