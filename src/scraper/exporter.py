"""Data export to CSV, JSON, and Excel formats."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def export_data(
    data: list[dict[str, Any]],
    fmt: str,
    directory: str,
    filename: str,
    include_timestamp: bool = True,
) -> Path:
    """Export scraped data to the specified format.

    Args:
        data: List of dictionaries to export.
        fmt: Export format ('csv', 'json', or 'excel').
        directory: Output directory path.
        filename: Base filename (without extension).
        include_timestamp: Whether to append a timestamp to filename.

    Returns:
        Path to the created output file.

    Raises:
        ValueError: If format is not supported or data is empty.
    """
    if not data:
        raise ValueError("No data to export")

    exporters = {
        "csv": _export_csv,
        "json": _export_json,
        "excel": _export_excel,
    }

    exporter_fn = exporters.get(fmt)
    if not exporter_fn:
        raise ValueError(f"Unsupported format: {fmt}. Use: csv, json, excel")

    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    full_name = _build_filename(filename, fmt, include_timestamp)
    output_path = output_dir / full_name

    exporter_fn(data, output_path)
    logger.info("Exported %d records to %s", len(data), output_path)
    return output_path


def _build_filename(base: str, fmt: str, include_timestamp: bool) -> str:
    """Build the output filename with optional timestamp.

    Args:
        base: Base filename.
        fmt: Export format.
        include_timestamp: Whether to include timestamp.

    Returns:
        Complete filename with extension.
    """
    ext_map = {"csv": "csv", "json": "json", "excel": "xlsx"}
    ext = ext_map[fmt]
    if include_timestamp:
        ts = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        return f"{base}_{ts}.{ext}"
    return f"{base}.{ext}"


def _export_csv(data: list[dict[str, Any]], path: Path) -> None:
    """Export data as CSV."""
    df = pd.DataFrame(data)
    df.to_csv(path, index=False, encoding="utf-8")


def _export_json(data: list[dict[str, Any]], path: Path) -> None:
    """Export data as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _export_excel(data: list[dict[str, Any]], path: Path) -> None:
    """Export data as Excel."""
    df = pd.DataFrame(data)
    df.to_excel(path, index=False, engine="openpyxl")
