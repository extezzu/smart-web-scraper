"""Tests for scraper.state — pause/resume state persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scraper.state import StateManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manager(path: Path, enabled: bool = True) -> StateManager:
    """Return a StateManager pointing at *path* with the given *enabled* flag."""
    return StateManager(path=str(path), enabled=enabled)


_SAMPLE_DATA: list[dict[str, Any]] = [
    {"title": "A Light in the Attic", "price": "£51.77"},
    {"title": "Tipping the Velvet", "price": "£53.74"},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_save_and_load(tmp_state_file: Path) -> None:
    """State saved to disk is fully round-tripped on load."""
    mgr = _make_manager(tmp_state_file)
    mgr.save(
        current_page=2,
        current_url="https://example.com/catalogue/page-2.html",
        collected_data=_SAMPLE_DATA,
    )

    loaded = mgr.load()

    assert loaded is not None
    assert loaded["current_page"] == 2
    assert loaded["current_url"] == "https://example.com/catalogue/page-2.html"
    assert loaded["collected_count"] == 2
    assert len(loaded["collected_data"]) == 2
    assert loaded["collected_data"][0]["title"] == "A Light in the Attic"
    assert "saved_at" in loaded


def test_load_no_file(tmp_state_file: Path) -> None:
    """load returns None when no state file exists on disk."""
    mgr = _make_manager(tmp_state_file)
    assert not tmp_state_file.exists()

    result = mgr.load()

    assert result is None


def test_load_disabled(tmp_state_file: Path) -> None:
    """load returns None immediately when state tracking is disabled."""
    # Write a valid state file so we confirm it is intentionally ignored
    mgr_write = _make_manager(tmp_state_file, enabled=True)
    mgr_write.save(1, "https://example.com/", _SAMPLE_DATA)
    assert tmp_state_file.exists()

    mgr_disabled = _make_manager(tmp_state_file, enabled=False)
    result = mgr_disabled.load()

    assert result is None


def test_clear_state(tmp_state_file: Path) -> None:
    """clear removes the state file from disk."""
    mgr = _make_manager(tmp_state_file)
    mgr.save(1, "https://example.com/", _SAMPLE_DATA)
    assert tmp_state_file.exists()

    mgr.clear()

    assert not tmp_state_file.exists()


def test_clear_nonexistent(tmp_state_file: Path) -> None:
    """clear does not raise an error when the state file does not exist."""
    mgr = _make_manager(tmp_state_file)
    assert not tmp_state_file.exists()

    # Should complete without raising any exception
    mgr.clear()


def test_corrupt_state_file(tmp_state_file: Path) -> None:
    """load returns None gracefully when the state file contains invalid JSON."""
    tmp_state_file.write_text("NOT VALID JSON {{{{", encoding="utf-8")
    mgr = _make_manager(tmp_state_file)

    result = mgr.load()

    assert result is None


def test_save_disabled(tmp_state_file: Path) -> None:
    """save does not write any file to disk when state tracking is disabled."""
    mgr = _make_manager(tmp_state_file, enabled=False)
    mgr.save(1, "https://example.com/", _SAMPLE_DATA)

    assert not tmp_state_file.exists()
