"""Tests for scraper.config — loading and validation of YAML configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from scraper.config import ScraperConfig, load_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data: Any) -> None:
    """Write *data* as YAML to *path*."""
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_load_valid_config(tmp_path: Path, sample_config_dict: dict[str, Any]) -> None:
    """Loading a well-formed YAML file returns a ScraperConfig with all fields set."""
    cfg_file = tmp_path / "config.yaml"
    _write_yaml(cfg_file, sample_config_dict)

    cfg = load_config(cfg_file)

    assert isinstance(cfg, ScraperConfig)
    assert cfg.target.base_url == "https://books.toscrape.com"
    assert cfg.target.selectors.item == "article.product_pod"
    assert cfg.target.selectors.title == "h3 a"
    assert cfg.target.selectors.title_attribute == "title"
    assert cfg.target.selectors.price == ".price_color"
    assert cfg.target.pagination.next_selector == "li.next a"
    assert cfg.target.pagination.page_info_selector == "li.current"
    assert cfg.request.delay == 1.0
    assert cfg.request.timeout == 30
    assert cfg.request.max_retries == 3
    assert cfg.output.format == "csv"
    assert cfg.output.filename == "books"
    assert cfg.logging.level == "INFO"
    assert cfg.state.enabled is True


def test_load_missing_file(tmp_path: Path) -> None:
    """load_config raises FileNotFoundError when the YAML path does not exist."""
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config(tmp_path / "nonexistent.yaml")


def test_invalid_url(tmp_path: Path, sample_config_dict: dict[str, Any]) -> None:
    """ValidationError is raised when base_url does not start with http(s)."""
    sample_config_dict["target"]["base_url"] = "ftp://not-valid.com"
    cfg_file = tmp_path / "bad_url.yaml"
    _write_yaml(cfg_file, sample_config_dict)

    with pytest.raises(ValidationError, match="base_url must start with"):
        load_config(cfg_file)


def test_invalid_format(tmp_path: Path, sample_config_dict: dict[str, Any]) -> None:
    """ValidationError is raised when output.format is not csv/json/excel."""
    sample_config_dict["output"]["format"] = "xml"
    cfg_file = tmp_path / "bad_format.yaml"
    _write_yaml(cfg_file, sample_config_dict)

    with pytest.raises(ValidationError, match="format must be one of"):
        load_config(cfg_file)


def test_invalid_log_level(tmp_path: Path, sample_config_dict: dict[str, Any]) -> None:
    """ValidationError is raised when logging.level is not a valid level string."""
    sample_config_dict["logging"]["level"] = "VERBOSE"
    cfg_file = tmp_path / "bad_log.yaml"
    _write_yaml(cfg_file, sample_config_dict)

    with pytest.raises(ValidationError, match="level must be one of"):
        load_config(cfg_file)


def test_defaults_applied(tmp_path: Path) -> None:
    """Optional config sections fall back to their defaults when omitted."""
    minimal: dict[str, Any] = {
        "target": {
            "base_url": "https://example.com",
            "selectors": {
                "item": "div.item",
                "title": "h2",
            },
        }
    }
    cfg_file = tmp_path / "minimal.yaml"
    _write_yaml(cfg_file, minimal)

    cfg = load_config(cfg_file)

    # request defaults
    assert cfg.request.delay == 1.0
    assert cfg.request.timeout == 30
    assert cfg.request.max_retries == 3
    assert cfg.request.follow_detail_links is False
    assert cfg.request.proxy is None
    # output defaults
    assert cfg.output.format == "csv"
    assert cfg.output.directory == "output"
    assert cfg.output.filename == "data"
    assert cfg.output.include_timestamp is True
    # logging defaults
    assert cfg.logging.level == "INFO"
    assert cfg.logging.file is None
    # state defaults
    assert cfg.state.enabled is True
    assert cfg.state.file == ".scraper_state.json"
    # pagination defaults
    assert cfg.target.pagination.next_selector == "li.next a"
    assert cfg.target.max_pages == 0


def test_config_with_proxy(tmp_path: Path, sample_config_dict: dict[str, Any]) -> None:
    """Proxy field is stored correctly when set in configuration."""
    sample_config_dict["request"]["proxy"] = "http://proxy.example.com:8080"
    cfg_file = tmp_path / "proxy.yaml"
    _write_yaml(cfg_file, sample_config_dict)

    cfg = load_config(cfg_file)

    assert cfg.request.proxy == "http://proxy.example.com:8080"


def test_empty_config_file(tmp_path: Path) -> None:
    """ValueError is raised when the YAML file contains only a null/empty document."""
    cfg_file = tmp_path / "empty.yaml"
    cfg_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Config file must contain a YAML mapping"):
        load_config(cfg_file)
