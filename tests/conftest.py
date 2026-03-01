"""Shared pytest fixtures for the smart-web-scraper test suite."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from scraper.config import ScraperConfig

# ---------------------------------------------------------------------------
# Raw config dictionary
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_config_dict() -> dict[str, Any]:
    """Return a valid configuration dictionary matching the YAML schema."""
    return {
        "target": {
            "base_url": "https://books.toscrape.com",
            "start_path": "catalogue/page-1.html",
            "selectors": {
                "item": "article.product_pod",
                "title": "h3 a",
                "title_attribute": "title",
                "price": ".price_color",
                "rating": ".star-rating",
                "availability": ".instock",
                "link": "h3 a",
                "link_attribute": "href",
                "image": ".image_container img",
                "image_attribute": "src",
            },
            "detail_selectors": {
                "title": ".product_main h1",
                "price": ".product_main .price_color",
                "description": "#product_description + p",
                "upc": ".table-striped td:nth-of-type(1)",
                "availability": ".availability",
                "rating": ".product_main .star-rating",
            },
            "pagination": {
                "next_selector": "li.next a",
                "next_attribute": "href",
                "page_info_selector": "li.current",
            },
            "max_pages": 0,
        },
        "request": {
            "delay": 1.0,
            "timeout": 30,
            "max_retries": 3,
            "retry_base_delay": 1.0,
            "follow_detail_links": False,
            "headers": {
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            },
            "proxy": None,
        },
        "output": {
            "format": "csv",
            "directory": "output",
            "filename": "books",
            "include_timestamp": True,
        },
        "logging": {
            "level": "INFO",
            "file": None,
        },
        "state": {
            "enabled": True,
            "file": ".scraper_state.json",
        },
    }


# ---------------------------------------------------------------------------
# ScraperConfig instance
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_config(sample_config_dict: dict[str, Any]) -> ScraperConfig:
    """Return a validated ScraperConfig built from sample_config_dict."""
    return ScraperConfig(**sample_config_dict)


# ---------------------------------------------------------------------------
# Sample HTML fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_listing_html() -> str:
    """Return HTML that mimics a books.toscrape.com listing page.

    Contains three book items, a "next" pagination link, and a current-page
    indicator reading "Page 1 of 3".
    """
    return """<!DOCTYPE html>
<html>
<head><title>Books to Scrape</title></head>
<body>
<div class="container-fluid page">
  <ul class="breadcrumb">
    <li><a href="/">Home</a></li>
  </ul>
  <div class="row">
    <section>
      <div class="pager">
        <ul class="pager">
          <li class="current">Page 1 of 3</li>
          <li class="next"><a href="page-2.html">next</a></li>
        </ul>
      </div>
      <ol class="row">
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
          <article class="product_pod">
            <div class="image_container">
              <a href="a-light-in-the-attic_1000/index.html">
                <img src="img1.jpg" alt="A Light in the Attic" class="thumbnail"/>
              </a>
            </div>
            <p class="star-rating Three">
              <i class="icon-star"></i>
            </p>
            <h3>
              <a href="a-light-in-the-attic_1000/index.html"
                 title="A Light in the Attic">
                A Light in the Atti...
              </a>
            </h3>
            <div class="product_price">
              <p class="price_color">£51.77</p>
              <p class="instock availability">
                <i class="icon-ok"></i>In stock
              </p>
            </div>
          </article>
        </li>
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
          <article class="product_pod">
            <div class="image_container">
              <a href="tipping-the-velvet_999/index.html">
                <img src="../../media/cache/img2.jpg" alt="Tipping the Velvet" class="thumbnail"/>
              </a>
            </div>
            <p class="star-rating One">
              <i class="icon-star"></i>
            </p>
            <h3>
              <a href="tipping-the-velvet_999/index.html"
                 title="Tipping the Velvet">
                Tipping the Velvet
              </a>
            </h3>
            <div class="product_price">
              <p class="price_color">£53.74</p>
              <p class="instock availability">
                <i class="icon-ok"></i>In stock
              </p>
            </div>
          </article>
        </li>
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
          <article class="product_pod">
            <div class="image_container">
              <a href="soumission_998/index.html">
                <img src="../../media/cache/img3.jpg" alt="Soumission" class="thumbnail"/>
              </a>
            </div>
            <p class="star-rating One">
              <i class="icon-star"></i>
            </p>
            <h3>
              <a href="soumission_998/index.html"
                 title="Soumission">
                Soumission
              </a>
            </h3>
            <div class="product_price">
              <p class="price_color">£50.10</p>
              <p class="instock availability">
                <i class="icon-ok"></i>In stock
              </p>
            </div>
          </article>
        </li>
      </ol>
    </section>
  </div>
</div>
</body>
</html>
"""


@pytest.fixture
def sample_detail_html() -> str:
    """Return HTML that mimics a books.toscrape.com detail page.

    Contains all fields: title, price, description, UPC, availability, and
    a Four-star rating.
    """
    return """<!DOCTYPE html>
<html>
<head><title>A Light in the Attic | Books to Scrape</title></head>
<body>
<div class="container-fluid page">
  <div class="row">
    <div class="col-sm-6">
      <div class="product_main">
        <h1>A Light in the Attic</h1>
        <p class="price_color">£51.77</p>
        <p class="star-rating Four">
          <i class="icon-star"></i>
        </p>
        <p class="availability instock">
          <i class="icon-ok"></i>In stock
        </p>
      </div>
    </div>
  </div>
  <div class="row">
    <div id="product_description">
      <h2>Product Description</h2>
    </div>
    <p>
      It's hard to imagine a world without A Light in the Attic.
      This now-classic collection of poetry and drawings from Shel Silverstein
      celebrates its 20th anniversary with this special edition.
    </p>
    <table class="table table-striped">
      <tbody>
        <tr>
          <th>UPC</th>
          <td>a897fe39b1053632</td>
        </tr>
        <tr>
          <th>Product Type</th>
          <td>Books</td>
        </tr>
        <tr>
          <th>Price (incl. tax)</th>
          <td>£51.77</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Filesystem fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory to use for export tests."""
    out = tmp_path / "export_output"
    out.mkdir(parents=True, exist_ok=True)
    return out


@pytest.fixture
def tmp_state_file(tmp_path: Path) -> Path:
    """Return a temporary file path for state persistence tests."""
    return tmp_path / "test_state.json"
