"""Tests for scraper.client — async HTTP client with rate limiting and retries."""

from __future__ import annotations

import time
from unittest.mock import patch

import httpx
import pytest
import respx

from scraper.client import USER_AGENTS, ScraperClient
from scraper.config import RequestConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides: object) -> RequestConfig:
    """Return a RequestConfig, applying any keyword overrides."""
    defaults: dict = {
        "delay": 0.0,
        "timeout": 10,
        "max_retries": 0,
        "retry_base_delay": 0.1,
        "follow_detail_links": False,
        "headers": {},
        "proxy": None,
    }
    defaults.update(overrides)
    return RequestConfig(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_fetch_success() -> None:
    """A successful GET request returns the response HTML body as a string."""
    url = "https://example.com/page"
    respx.get(url).mock(return_value=httpx.Response(200, text="<html>hello</html>"))

    cfg = _make_config()
    async with ScraperClient(cfg) as client:
        html = await client.fetch(url)

    assert html == "<html>hello</html>"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_404_raises() -> None:
    """A 404 response causes httpx.HTTPStatusError to be raised."""
    url = "https://example.com/missing"
    respx.get(url).mock(return_value=httpx.Response(404))

    cfg = _make_config()
    async with ScraperClient(cfg) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.fetch(url)


@pytest.mark.asyncio
async def test_rate_limiting() -> None:
    """A delay > 0 causes asyncio.sleep to be called between requests."""
    cfg = _make_config(delay=0.5)

    sleep_calls: list[float] = []

    async def fake_sleep(t: float) -> None:
        sleep_calls.append(t)

    # Two successful HTML responses for two consecutive fetches
    with respx.mock:
        respx.get("https://example.com/a").mock(return_value=httpx.Response(200, text="a"))
        respx.get("https://example.com/b").mock(return_value=httpx.Response(200, text="b"))

        with patch("scraper.client.asyncio.sleep", side_effect=fake_sleep):
            async with ScraperClient(cfg) as client:
                # Set _last_request_time far in the past so rate limit triggers
                # on the *second* call.
                await client.fetch("https://example.com/a")
                # Force elapsed to be near zero so the wait fires.
                client._last_request_time = time.monotonic() + 1_000_000
                await client.fetch("https://example.com/b")

    assert len(sleep_calls) >= 1, "Expected at least one rate-limit sleep call"


@respx.mock
@pytest.mark.asyncio
async def test_user_agent_rotation() -> None:
    """The User-Agent header sent is always one of the known user-agent strings."""
    url = "https://example.com/ua-test"
    captured_headers: list[str] = []

    def capture(request: httpx.Request) -> httpx.Response:
        captured_headers.append(request.headers.get("user-agent", ""))
        return httpx.Response(200, text="ok")

    respx.get(url).mock(side_effect=capture)

    cfg = _make_config()
    async with ScraperClient(cfg) as client:
        await client.fetch(url)

    assert len(captured_headers) == 1
    assert captured_headers[0] in USER_AGENTS


@respx.mock
@pytest.mark.asyncio
async def test_custom_headers_applied() -> None:
    """Custom headers defined in RequestConfig are forwarded with every request."""
    url = "https://example.com/custom-headers"
    captured_headers: dict[str, str] = {}

    def capture(request: httpx.Request) -> httpx.Response:
        captured_headers.update(dict(request.headers))
        return httpx.Response(200, text="ok")

    respx.get(url).mock(side_effect=capture)

    cfg = _make_config(headers={"X-Custom-Token": "abc123", "X-Source": "test"})
    async with ScraperClient(cfg) as client:
        await client.fetch(url)

    assert captured_headers.get("x-custom-token") == "abc123"
    assert captured_headers.get("x-source") == "test"


@pytest.mark.asyncio
async def test_client_context_manager() -> None:
    """ScraperClient supports the async-with protocol and cleans up on exit."""
    cfg = _make_config()

    async with ScraperClient(cfg) as client:
        assert client._client is not None, "Client should be initialised inside context"

    # After exiting the context the internal httpx client is cleaned up
    assert client._client is None


@pytest.mark.asyncio
async def test_client_not_initialized_error() -> None:
    """Calling fetch outside an async-with block raises RuntimeError."""
    cfg = _make_config()
    client = ScraperClient(cfg)

    with pytest.raises(RuntimeError, match="Client not initialized"):
        await client.fetch("https://example.com/")
