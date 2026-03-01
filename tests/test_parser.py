"""Tests for scraper.parser — HTML extraction of listing and detail pages."""

from __future__ import annotations

import pytest

from scraper.config import DetailSelectorsConfig, SelectorsConfig
from scraper.parser import parse_detail, parse_listing

# ---------------------------------------------------------------------------
# Shared selector configs
# ---------------------------------------------------------------------------


@pytest.fixture
def listing_selectors() -> SelectorsConfig:
    """Return SelectorsConfig matching the books.toscrape.com listing page."""
    return SelectorsConfig(
        item="article.product_pod",
        title="h3 a",
        title_attribute="title",
        price=".price_color",
        rating=".star-rating",
        availability=".instock",
        link="h3 a",
        link_attribute="href",
        image=".image_container img",
        image_attribute="src",
    )


@pytest.fixture
def detail_selectors() -> DetailSelectorsConfig:
    """Return DetailSelectorsConfig matching the books.toscrape.com detail page."""
    return DetailSelectorsConfig(
        title=".product_main h1",
        price=".product_main .price_color",
        description="#product_description + p",
        upc=".table-striped td:nth-of-type(1)",
        availability=".availability",
        rating=".product_main .star-rating",
    )


# ---------------------------------------------------------------------------
# Listing tests
# ---------------------------------------------------------------------------


def test_parse_listing_extracts_items(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """parse_listing returns one dict per article.product_pod in the HTML."""
    items = parse_listing(sample_listing_html, listing_selectors)
    assert len(items) == 3


def test_parse_listing_title(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """Title is read from the title attribute of the anchor tag."""
    items = parse_listing(sample_listing_html, listing_selectors)
    titles = [item["title"] for item in items]
    assert "A Light in the Attic" in titles
    assert "Tipping the Velvet" in titles
    assert "Soumission" in titles


def test_parse_listing_price(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """Price is cleaned to the £XX.XX format, stripping surrounding whitespace."""
    items = parse_listing(sample_listing_html, listing_selectors)
    # Prices present in the fixture
    prices = {item["price"] for item in items}
    assert "£51.77" in prices
    assert "£53.74" in prices
    assert "£50.10" in prices


def test_parse_listing_rating(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """Rating is extracted as an integer from the CSS class name (e.g. 'Three' -> 3)."""
    items = parse_listing(sample_listing_html, listing_selectors)
    first = next(i for i in items if i["title"] == "A Light in the Attic")
    assert first["rating"] == 3


def test_parse_listing_link(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """Link attribute (href) is extracted from the h3 anchor element."""
    items = parse_listing(sample_listing_html, listing_selectors)
    first = next(i for i in items if i["title"] == "A Light in the Attic")
    assert "a-light-in-the-attic" in first["link"]


def test_parse_listing_availability(
    sample_listing_html: str,
    listing_selectors: SelectorsConfig,
) -> None:
    """Availability is True when the .instock selector matches an element."""
    items = parse_listing(sample_listing_html, listing_selectors)
    # All three fixture books are in stock
    assert all(item["availability"] is True for item in items)


def test_parse_listing_empty_html(listing_selectors: SelectorsConfig) -> None:
    """An HTML page with no matching items returns an empty list."""
    empty_html = "<html><body><p>No books here.</p></body></html>"
    items = parse_listing(empty_html, listing_selectors)
    assert items == []


# ---------------------------------------------------------------------------
# Detail tests
# ---------------------------------------------------------------------------


def test_parse_detail_all_fields(
    sample_detail_html: str,
    detail_selectors: DetailSelectorsConfig,
) -> None:
    """parse_detail extracts title, price, description, upc, and availability."""
    record = parse_detail(sample_detail_html, detail_selectors)

    assert record["title"] == "A Light in the Attic"
    assert record["price"] == "£51.77"
    assert record["upc"] == "a897fe39b1053632"
    assert "In stock" in record["availability"]
    assert record["description"] is not None
    assert len(record["description"]) > 10


def test_parse_detail_rating(
    sample_detail_html: str,
    detail_selectors: DetailSelectorsConfig,
) -> None:
    """Rating is correctly extracted as an integer from the detail page (Four -> 4)."""
    record = parse_detail(sample_detail_html, detail_selectors)
    assert record["rating"] == 4
