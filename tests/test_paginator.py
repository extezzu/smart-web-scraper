"""Tests for scraper.paginator — next-URL extraction and page-info parsing."""

from __future__ import annotations

from scraper.config import PaginationConfig
from scraper.paginator import get_next_url, get_page_info

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pagination(**overrides: object) -> PaginationConfig:
    """Return a PaginationConfig, applying any keyword overrides."""
    defaults: dict = {
        "next_selector": "li.next a",
        "next_attribute": "href",
        "page_info_selector": "li.current",
    }
    defaults.update(overrides)
    return PaginationConfig(**defaults)


# ---------------------------------------------------------------------------
# get_next_url tests
# ---------------------------------------------------------------------------


def test_get_next_url_found(sample_listing_html: str) -> None:
    """get_next_url returns an absolute URL when the next-page link is present."""
    pagination = _make_pagination()
    current_url = "https://books.toscrape.com/catalogue/page-1.html"

    next_url = get_next_url(sample_listing_html, current_url, pagination)

    assert next_url is not None
    assert next_url.startswith("https://")
    assert "page-2.html" in next_url


def test_get_next_url_last_page() -> None:
    """get_next_url returns None when the page has no next-page link."""
    html_no_next = """<html><body>
        <ul class="pager">
          <li class="current">Page 3 of 3</li>
        </ul>
    </body></html>"""
    pagination = _make_pagination()
    current_url = "https://books.toscrape.com/catalogue/page-3.html"

    next_url = get_next_url(html_no_next, current_url, pagination)

    assert next_url is None


# ---------------------------------------------------------------------------
# get_page_info tests
# ---------------------------------------------------------------------------


def test_get_page_info(sample_listing_html: str) -> None:
    """get_page_info extracts (current, total) from 'Page 1 of 3' text."""
    pagination = _make_pagination(page_info_selector="li.current")

    info = get_page_info(sample_listing_html, pagination)

    assert info == (1, 3)


def test_get_page_info_no_selector() -> None:
    """get_page_info returns None when page_info_selector is not configured."""
    pagination = _make_pagination(page_info_selector=None)
    html = "<html><body><li class='current'>Page 1 of 5</li></body></html>"

    assert get_page_info(html, pagination) is None


def test_get_page_info_selector_missing_from_html() -> None:
    """get_page_info returns None when the selector matches nothing in the HTML."""
    pagination = _make_pagination(page_info_selector="li.current")
    html = "<html><body><p>No pager here</p></body></html>"

    assert get_page_info(html, pagination) is None


# ---------------------------------------------------------------------------
# URL resolution tests
# ---------------------------------------------------------------------------


def test_relative_url_resolution() -> None:
    """Relative hrefs are correctly resolved against the current page URL."""
    html = """<html><body>
        <ul class="pager">
          <li class="next"><a href="../page-4.html">next</a></li>
        </ul>
    </body></html>"""
    pagination = _make_pagination()
    current_url = "https://example.com/catalogue/category/books/page-3.html"

    next_url = get_next_url(html, current_url, pagination)

    assert next_url == "https://example.com/catalogue/category/page-4.html"
