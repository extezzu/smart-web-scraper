"""Pagination handling for multi-page scraping."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from scraper.config import PaginationConfig

logger = logging.getLogger(__name__)


def get_next_url(
    html: str,
    current_url: str,
    pagination: PaginationConfig,
) -> str | None:
    """Extract the next page URL from HTML content.

    Args:
        html: Raw HTML content of the current page.
        current_url: URL of the current page (for resolving relative links).
        pagination: Pagination configuration with selectors.

    Returns:
        Absolute URL of the next page, or None if no next page.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_tag = soup.select_one(pagination.next_selector)
    if not next_tag:
        logger.info("No next page link found")
        return None

    href = next_tag.get(pagination.next_attribute, "")
    if not href:
        return None

    next_url = urljoin(current_url, href)
    logger.debug("Next page URL: %s", next_url)
    return next_url


def get_page_info(html: str, pagination: PaginationConfig) -> tuple[int, int] | None:
    """Extract current page number and total pages.

    Args:
        html: Raw HTML content.
        pagination: Pagination configuration with selectors.

    Returns:
        Tuple of (current_page, total_pages) or None if not found.
    """
    if not pagination.page_info_selector:
        return None

    soup = BeautifulSoup(html, "html.parser")
    info_tag = soup.select_one(pagination.page_info_selector)
    if not info_tag:
        return None

    text = info_tag.get_text(strip=True)
    match = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None
