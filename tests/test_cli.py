"""Tests for scraper.cli — Click command-line interface via CliRunner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from click.testing import CliRunner

from scraper.cli import cli

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def runner() -> CliRunner:
    """Return a Click CliRunner for invoking CLI commands in tests."""
    return CliRunner()


def _write_valid_config(path: Path) -> None:
    """Write a minimal valid YAML configuration file to *path*."""
    data: dict[str, Any] = {
        "target": {
            "base_url": "https://example.com",
            "selectors": {
                "item": "article",
                "title": "h2",
            },
        }
    }
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh)


# ---------------------------------------------------------------------------
# Help text tests
# ---------------------------------------------------------------------------


def test_cli_help(runner: CliRunner) -> None:
    """The top-level --help flag exits cleanly and prints the group description."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Smart Web Scraper" in result.output


def test_scrape_help(runner: CliRunner) -> None:
    """scrape --help exits cleanly and documents the --config option."""
    result = runner.invoke(cli, ["scrape", "--help"])
    assert result.exit_code == 0
    assert "--config" in result.output


def test_convert_help(runner: CliRunner) -> None:
    """convert --help exits cleanly and documents the --input and --format options."""
    result = runner.invoke(cli, ["convert", "--help"])
    assert result.exit_code == 0
    assert "--input" in result.output
    assert "--format" in result.output


def test_clean_help(runner: CliRunner) -> None:
    """clean --help exits cleanly and documents the --state-file option."""
    result = runner.invoke(cli, ["clean", "--help"])
    assert result.exit_code == 0
    assert "--state-file" in result.output


# ---------------------------------------------------------------------------
# Error condition tests
# ---------------------------------------------------------------------------


def test_scrape_missing_config(runner: CliRunner) -> None:
    """scrape with no --config option exits with a non-zero code and an error message."""
    result = runner.invoke(cli, ["scrape"])
    assert result.exit_code != 0
    # Click should mention the missing required option
    assert "config" in result.output.lower() or "missing" in result.output.lower()


def test_scrape_invalid_config_file(runner: CliRunner, tmp_path: Path) -> None:
    """scrape with a --config path that does not exist exits with a non-zero code."""
    nonexistent = str(tmp_path / "no_such_config.yaml")
    result = runner.invoke(cli, ["scrape", "--config", nonexistent])
    assert result.exit_code != 0
