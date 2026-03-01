"""HTML parsing logic for extracting structured data."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

from bs4 import BeautifulSoup, Tag

if TYPE_CHECKING:
    from scraper.config import DetailSelectorsConfig, SelectorsConfig

logger = logging.getLogger(__name__)

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def parse_listing(html: str, selectors: SelectorsConfig) -> list[dict[str, Any]]:
    """Parse a listing page and extract items.

    Args:
        html: Raw HTML content of the listing page.
        selectors: CSS selectors for extracting fields.

    Returns:
        List of dictionaries, each representing a scraped item.
    """
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(selectors.item)
    logger.info("Found %d items on page", len(items))
    results = []
    for item in items:
        record = _extract_item(item, selectors)
        if record:
            results.append(record)
    return results


def _extract_item(
    element: Tag,
    selectors: SelectorsConfig,
) -> dict[str, Any] | None:
    """Extract data from a single item element.

    Args:
        element: BeautifulSoup Tag for one item.
        selectors: CSS selectors configuration.

    Returns:
        Dictionary of extracted fields, or None if title missing.
    """
    record: dict[str, Any] = {}
    record["title"] = _extract_field(
        element,
        selectors.title,
        selectors.title_attribute,
    )
    if not record["title"]:
        return None

    if selectors.price:
        raw_price = _extract_field(element, selectors.price)
        record["price"] = _clean_price(raw_price) if raw_price else None

    if selectors.rating:
        record["rating"] = _extract_rating(element, selectors.rating)

    if selectors.availability:
        tag = element.select_one(selectors.availability)
        record["availability"] = bool(tag)

    if selectors.link:
        record["link"] = _extract_field(
            element,
            selectors.link,
            selectors.link_attribute,
        )

    if selectors.image:
        record["image"] = _extract_field(
            element,
            selectors.image,
            selectors.image_attribute,
        )

    return record


def _extract_field(
    element: Tag,
    selector: str,
    attribute: str | None = None,
) -> str | None:
    """Extract a text or attribute value from an element.

    Args:
        element: Parent BeautifulSoup Tag.
        selector: CSS selector to find the child element.
        attribute: HTML attribute to extract. None for text content.

    Returns:
        Extracted string value, or None if not found.
    """
    tag = element.select_one(selector)
    if not tag:
        return None
    if attribute:
        return tag.get(attribute, "").strip()
    return tag.get_text(strip=True)


def _clean_price(raw: str) -> str:
    """Clean a price string, keeping currency symbol and number.

    Args:
        raw: Raw price text (e.g., '£51.77').

    Returns:
        Cleaned price string.
    """
    match = re.search(r"[£$€]?\d+\.?\d*", raw)
    return match.group(0) if match else raw.strip()


def _extract_rating(element: Tag, selector: str) -> int | None:
    """Extract a star rating from CSS class names.

    Args:
        element: Parent BeautifulSoup Tag.
        selector: CSS selector for the rating element.

    Returns:
        Integer rating (1-5) or None.
    """
    tag = element.select_one(selector)
    if not tag:
        return None
    classes = tag.get("class", [])
    for cls in classes:
        lower = cls.lower()
        if lower in RATING_MAP:
            return RATING_MAP[lower]
    return None


def parse_detail(
    html: str,
    detail_selectors: DetailSelectorsConfig,
) -> dict[str, Any]:
    """Parse a detail page and extract fields.

    Args:
        html: Raw HTML content of the detail page.
        detail_selectors: CSS selectors for detail page fields.

    Returns:
        Dictionary of extracted detail fields.
    """
    soup = BeautifulSoup(html, "html.parser")
    record: dict[str, Any] = {}

    for field_name in ("title", "price", "description", "upc", "availability"):
        selector = getattr(detail_selectors, field_name, None)
        if selector:
            tag = soup.select_one(selector)
            record[field_name] = tag.get_text(strip=True) if tag else None

    if detail_selectors.rating:
        record["rating"] = _extract_rating_from_soup(
            soup,
            detail_selectors.rating,
        )

    return record


def _extract_rating_from_soup(soup: BeautifulSoup, selector: str) -> int | None:
    """Extract rating from a full soup (not a sub-element).

    Args:
        soup: BeautifulSoup parsed page.
        selector: CSS selector for the rating element.

    Returns:
        Integer rating (1-5) or None.
    """
    tag = soup.select_one(selector)
    if not tag:
        return None
    classes = tag.get("class", [])
    for cls in classes:
        lower = cls.lower()
        if lower in RATING_MAP:
            return RATING_MAP[lower]
    return None
