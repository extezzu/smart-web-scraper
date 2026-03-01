"""Shared utilities for the web scraper."""

from __future__ import annotations

import logging
import sys
from urllib.parse import urljoin


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging for the scraper.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path to a log file.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def resolve_url(base_url: str, relative: str) -> str:
    """Resolve a relative URL against a base URL.

    Args:
        base_url: The base URL to resolve against.
        relative: The relative URL to resolve.

    Returns:
        Absolute URL string.
    """
    return urljoin(base_url, relative)


def build_start_url(base_url: str, start_path: str) -> str:
    """Build the initial scraping URL from base and path.

    Args:
        base_url: Base URL of the target site.
        start_path: Starting path to append.

    Returns:
        Complete starting URL.
    """
    if start_path:
        return urljoin(base_url + "/", start_path)
    return base_url
