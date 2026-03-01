"""Resume state management for interrupted scraping sessions."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StateManager:
    """Manages scraper state for pause/resume capability.

    Attributes:
        path: Path to the state file.
        enabled: Whether state tracking is active.
    """

    def __init__(self, path: str, enabled: bool = True) -> None:
        self.path = Path(path)
        self.enabled = enabled

    def save(
        self,
        current_page: int,
        current_url: str,
        collected_data: list[dict[str, Any]],
    ) -> None:
        """Save current scraping state to disk.

        Args:
            current_page: The page number being processed.
            current_url: URL of the current page.
            collected_data: All data collected so far.
        """
        if not self.enabled:
            return

        state = {
            "current_page": current_page,
            "current_url": current_url,
            "collected_count": len(collected_data),
            "collected_data": collected_data,
            "saved_at": datetime.now(tz=UTC).isoformat(),
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        logger.debug("State saved: page %d, %d items", current_page, len(collected_data))

    def load(self) -> dict[str, Any] | None:
        """Load previously saved state.

        Returns:
            State dictionary or None if no state exists.
        """
        if not self.enabled or not self.path.exists():
            return None

        try:
            with open(self.path, encoding="utf-8") as f:
                state = json.load(f)
            logger.info(
                "Resumed from page %d (%d items)",
                state["current_page"],
                state["collected_count"],
            )
            return state
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Corrupt state file, starting fresh: %s", exc)
            return None

    def clear(self) -> None:
        """Remove the state file."""
        if self.path.exists():
            self.path.unlink()
            logger.debug("State file removed")
