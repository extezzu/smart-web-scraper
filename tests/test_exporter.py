"""Tests for scraper.exporter — data export to CSV, JSON, and Excel formats."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from scraper.exporter import export_data

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_data() -> list[dict[str, Any]]:
    """Return a small list of records suitable for export tests."""
    return [
        {"title": "A Light in the Attic", "price": "£51.77", "rating": 3},
        {"title": "Tipping the Velvet", "price": "£53.74", "rating": 1},
        {"title": "Soumission", "price": "£50.10", "rating": 1},
    ]


# ---------------------------------------------------------------------------
# CSV tests
# ---------------------------------------------------------------------------


def test_export_csv(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """CSV export creates a file with a header row and one row per record."""
    out = export_data(
        data=sample_data,
        fmt="csv",
        directory=str(tmp_output_dir),
        filename="test_books",
        include_timestamp=False,
    )

    assert out.exists()
    assert out.suffix == ".csv"
    df = pd.read_csv(out)
    assert list(df.columns) == ["title", "price", "rating"]
    assert len(df) == 3
    assert df["title"].iloc[0] == "A Light in the Attic"


# ---------------------------------------------------------------------------
# JSON tests
# ---------------------------------------------------------------------------


def test_export_json(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """JSON export creates a valid JSON file containing all records."""
    out = export_data(
        data=sample_data,
        fmt="json",
        directory=str(tmp_output_dir),
        filename="test_books",
        include_timestamp=False,
    )

    assert out.exists()
    assert out.suffix == ".json"
    with open(out, encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert isinstance(loaded, list)
    assert len(loaded) == 3
    assert loaded[0]["title"] == "A Light in the Attic"


# ---------------------------------------------------------------------------
# Excel tests
# ---------------------------------------------------------------------------


def test_export_excel(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """Excel export creates a .xlsx file readable by pandas."""
    out = export_data(
        data=sample_data,
        fmt="excel",
        directory=str(tmp_output_dir),
        filename="test_books",
        include_timestamp=False,
    )

    assert out.exists()
    assert out.suffix == ".xlsx"
    df = pd.read_excel(out, engine="openpyxl")
    assert len(df) == 3
    assert "title" in df.columns


# ---------------------------------------------------------------------------
# Timestamp tests
# ---------------------------------------------------------------------------


_TIMESTAMP_PATTERN = re.compile(r"\d{8}_\d{6}")


def test_export_with_timestamp(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """When include_timestamp=True, the output filename contains a timestamp."""
    out = export_data(
        data=sample_data,
        fmt="csv",
        directory=str(tmp_output_dir),
        filename="books",
        include_timestamp=True,
    )

    assert _TIMESTAMP_PATTERN.search(out.name) is not None


def test_export_without_timestamp(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """When include_timestamp=False, the filename is exactly <base>.<ext>."""
    out = export_data(
        data=sample_data,
        fmt="json",
        directory=str(tmp_output_dir),
        filename="books",
        include_timestamp=False,
    )

    assert out.name == "books.json"
    assert _TIMESTAMP_PATTERN.search(out.name) is None


# ---------------------------------------------------------------------------
# Error condition tests
# ---------------------------------------------------------------------------


def test_export_empty_data_raises(tmp_output_dir: Path) -> None:
    """ValueError is raised when the data list is empty."""
    with pytest.raises(ValueError, match="No data to export"):
        export_data(
            data=[],
            fmt="csv",
            directory=str(tmp_output_dir),
            filename="empty",
            include_timestamp=False,
        )


def test_export_unsupported_format_raises(
    sample_data: list[dict[str, Any]],
    tmp_output_dir: Path,
) -> None:
    """ValueError is raised for an unsupported format string."""
    with pytest.raises(ValueError, match="Unsupported format"):
        export_data(
            data=sample_data,
            fmt="xml",
            directory=str(tmp_output_dir),
            filename="books",
            include_timestamp=False,
        )


def test_export_creates_directory(
    sample_data: list[dict[str, Any]],
    tmp_path: Path,
) -> None:
    """export_data creates the output directory when it does not already exist."""
    new_dir = tmp_path / "deeply" / "nested" / "output"
    assert not new_dir.exists()

    out = export_data(
        data=sample_data,
        fmt="json",
        directory=str(new_dir),
        filename="books",
        include_timestamp=False,
    )

    assert new_dir.exists()
    assert out.exists()
