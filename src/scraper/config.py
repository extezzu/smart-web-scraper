"""Configuration models for the web scraper."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class SelectorsConfig(BaseModel):
    """CSS selectors for listing page elements."""

    item: str
    title: str
    title_attribute: str | None = None
    price: str | None = None
    rating: str | None = None
    availability: str | None = None
    link: str | None = None
    link_attribute: str = "href"
    image: str | None = None
    image_attribute: str = "src"


class DetailSelectorsConfig(BaseModel):
    """CSS selectors for detail page elements."""

    title: str | None = None
    price: str | None = None
    description: str | None = None
    upc: str | None = None
    availability: str | None = None
    rating: str | None = None


class PaginationConfig(BaseModel):
    """Pagination settings."""

    next_selector: str = "li.next a"
    next_attribute: str = "href"
    page_info_selector: str | None = None


class TargetConfig(BaseModel):
    """Target website configuration."""

    base_url: str
    start_path: str = ""
    selectors: SelectorsConfig
    detail_selectors: DetailSelectorsConfig | None = None
    pagination: PaginationConfig = PaginationConfig()
    max_pages: int = Field(default=0, ge=0)

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure base_url starts with http(s)."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")


class RequestConfig(BaseModel):
    """HTTP request settings."""

    delay: float = Field(default=1.0, ge=0)
    timeout: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=0)
    retry_base_delay: float = Field(default=1.0, ge=0)
    follow_detail_links: bool = False
    headers: dict[str, str] = Field(default_factory=dict)
    proxy: str | None = None


class OutputConfig(BaseModel):
    """Export output settings."""

    format: str = "csv"
    directory: str = "output"
    filename: str = "data"
    include_timestamp: bool = True

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Ensure format is supported."""
        allowed = {"csv", "json", "excel"}
        if v.lower() not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v.lower()


class LoggingConfig(BaseModel):
    """Logging settings."""

    level: str = "INFO"
    file: str | None = None

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return v.upper()


class StateConfig(BaseModel):
    """Resume state settings."""

    enabled: bool = True
    file: str = ".scraper_state.json"


class ScraperConfig(BaseModel):
    """Root configuration model."""

    target: TargetConfig
    request: RequestConfig = RequestConfig()
    output: OutputConfig = OutputConfig()
    logging: LoggingConfig = LoggingConfig()
    state: StateConfig = StateConfig()


def load_config(path: str | Path) -> ScraperConfig:
    """Load and validate scraper configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Validated ScraperConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the config file is invalid.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a YAML mapping")

    return ScraperConfig(**raw)
