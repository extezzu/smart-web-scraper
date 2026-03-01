"""Async HTTP client with rate limiting, retries, and header rotation."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from scraper.config import RequestConfig

logger = logging.getLogger(__name__)

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ),
]


class ScraperClient:
    """Async HTTP client with rate limiting and retry logic.

    Attributes:
        config: Request configuration settings.
    """

    def __init__(self, config: RequestConfig) -> None:
        self._config = config
        self._client: httpx.AsyncClient | None = None
        self._last_request_time: float = 0

    async def __aenter__(self) -> ScraperClient:
        self._client = httpx.AsyncClient(
            timeout=self._config.timeout,
            proxy=self._config.proxy,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with a random User-Agent."""
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            **self._config.headers,
        }
        return headers

    async def _apply_rate_limit(self) -> None:
        """Wait if needed to respect the configured delay."""
        if self._config.delay <= 0:
            return
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._config.delay:
            wait_time = self._config.delay - elapsed
            logger.debug("Rate limiting: waiting %.2fs", wait_time)
            await asyncio.sleep(wait_time)

    async def fetch(self, url: str) -> str:
        """Fetch a URL and return its HTML content.

        Args:
            url: The URL to fetch.

        Returns:
            HTML content as a string.

        Raises:
            httpx.HTTPStatusError: If the response status is 4xx/5xx.
            httpx.ConnectError: If the connection fails after retries.
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        await self._apply_rate_limit()
        response = await self._fetch_with_retry(url)
        self._last_request_time = asyncio.get_event_loop().time()
        return response

    async def _fetch_with_retry(self, url: str) -> str:
        """Fetch with tenacity retry logic.

        Args:
            url: The URL to fetch.

        Returns:
            HTML content as a string.
        """
        max_attempts = max(1, self._config.max_retries + 1)
        base_delay = self._config.retry_base_delay

        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=base_delay, min=base_delay, max=60),
            retry=retry_if_exception_type(
                (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError),
            ),
            reraise=True,
        )
        async def _do_fetch() -> str:
            headers = self._build_headers()
            logger.debug("Fetching %s", url)
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            logger.info("Fetched %s [%d]", url, response.status_code)
            return response.text

        return await _do_fetch()
