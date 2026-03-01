"""CLI entry point for the smart web scraper."""

from __future__ import annotations

import asyncio
import logging
import sys

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from scraper.client import ScraperClient
from scraper.config import ScraperConfig, load_config
from scraper.exporter import export_data
from scraper.paginator import get_next_url, get_page_info
from scraper.parser import parse_listing
from scraper.state import StateManager
from scraper.utils import build_start_url, setup_logging

logger = logging.getLogger(__name__)
console = Console()


@click.group()
@click.version_option(package_name="smart-web-scraper")
def cli() -> None:
    """Smart Web Scraper — configurable, production-ready web scraper."""


@cli.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to YAML configuration file.",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    type=click.Choice(["csv", "json", "excel"]),
    default=None,
    help="Override output format from config.",
)
@click.option(
    "--max-pages",
    type=int,
    default=None,
    help="Override max pages from config (0 = unlimited).",
)
@click.option(
    "--no-resume",
    is_flag=True,
    default=False,
    help="Ignore saved state and start fresh.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose (DEBUG) logging.",
)
def scrape(
    config_path: str,
    output_format: str | None,
    max_pages: int | None,
    no_resume: bool,
    verbose: bool,
) -> None:
    """Run the scraper with the given configuration."""
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        sys.exit(1)

    if verbose:
        config.logging.level = "DEBUG"
    if output_format:
        config.output.format = output_format
    if max_pages is not None:
        config.target.max_pages = max_pages

    setup_logging(config.logging.level, config.logging.file)
    asyncio.run(_run_scraper(config, no_resume))


async def _run_scraper(config: ScraperConfig, no_resume: bool) -> None:
    """Execute the scraping pipeline.

    Args:
        config: Validated scraper configuration.
        no_resume: If True, ignore any saved state.
    """
    state_mgr = StateManager(
        path=config.state.file,
        enabled=config.state.enabled,
    )

    all_data, current_url, page_num = _restore_state(config, state_mgr, no_resume)

    async with ScraperClient(config.request) as client:
        all_data, page_num = await _scrape_pages(
            client,
            config,
            state_mgr,
            all_data,
            current_url,
            page_num,
        )

    _export_results(all_data, config)
    state_mgr.clear()


def _restore_state(
    config: ScraperConfig,
    state_mgr: StateManager,
    no_resume: bool,
) -> tuple[list[dict], str, int]:
    """Load saved state or initialize fresh scraping session.

    Args:
        config: Scraper configuration.
        state_mgr: State persistence manager.
        no_resume: If True, skip loading saved state.

    Returns:
        Tuple of (collected_data, current_url, page_number).
    """
    start_url = build_start_url(config.target.base_url, config.target.start_path)

    if not no_resume:
        saved = state_mgr.load()
        if saved:
            data = saved.get("collected_data", [])
            console.print(
                f"[yellow]Resuming from page {saved['current_page']} "
                f"({len(data)} items collected)[/yellow]",
            )
            return data, saved["current_url"], saved["current_page"]

    return [], start_url, 1


async def _scrape_pages(
    client: ScraperClient,
    config: ScraperConfig,
    state_mgr: StateManager,
    all_data: list[dict],
    current_url: str,
    page_num: int,
) -> tuple[list[dict], int]:
    """Fetch and parse pages in a loop until done.

    Args:
        client: Initialized HTTP client.
        config: Scraper configuration.
        state_mgr: State persistence manager.
        all_data: Previously collected records.
        current_url: URL to start fetching from.
        page_num: Current page number.

    Returns:
        Tuple of (all_collected_data, last_page_number).
    """
    max_pages = config.target.max_pages
    selectors = config.target.selectors
    pagination = config.target.pagination

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scraping...", total=None)

        while not (max_pages and page_num > max_pages):
            progress.update(task, description=f"Scraping page {page_num}...")

            try:
                html = await client.fetch(current_url)
            except Exception as exc:
                console.print(f"[red]Fetch error on page {page_num}:[/red] {exc}")
                break

            all_data.extend(parse_listing(html, selectors))

            info = get_page_info(html, pagination)
            if info:
                cur, total = info
                progress.update(
                    task,
                    description=f"Page {cur}/{total} — {len(all_data)} items",
                )

            state_mgr.save(page_num, current_url, all_data)

            next_url = get_next_url(html, current_url, pagination)
            if not next_url:
                break
            current_url = next_url
            page_num += 1

    return all_data, page_num


def _export_results(all_data: list[dict], config: ScraperConfig) -> None:
    """Export collected data or print a warning if empty.

    Args:
        all_data: All scraped records.
        config: Scraper configuration for output settings.
    """
    if not all_data:
        console.print("[yellow]No data collected.[/yellow]")
        return

    try:
        output_path = export_data(
            data=all_data,
            fmt=config.output.format,
            directory=config.output.directory,
            filename=config.output.filename,
            include_timestamp=config.output.include_timestamp,
        )
        console.print(f"[green]Exported {len(all_data)} items to {output_path}[/green]")
    except ValueError as exc:
        console.print(f"[red]Export error:[/red] {exc}")
        sys.exit(1)


@cli.command()
@click.option(
    "-i",
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to a JSON data file to convert.",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    required=True,
    type=click.Choice(["csv", "json", "excel"]),
    help="Target export format.",
)
@click.option(
    "-o",
    "--output-dir",
    default="output",
    help="Output directory.",
)
def convert(input_path: str, output_format: str, output_dir: str) -> None:
    """Convert an existing JSON data file to another format."""
    import json
    from pathlib import Path

    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        console.print(f"[red]Error reading file:[/red] {exc}")
        sys.exit(1)

    if not isinstance(data, list):
        console.print("[red]Input file must contain a JSON array.[/red]")
        sys.exit(1)

    name = Path(input_path).stem
    output_path = export_data(
        data=data,
        fmt=output_format,
        directory=output_dir,
        filename=name,
        include_timestamp=False,
    )
    console.print(f"[green]Converted to {output_path}[/green]")


@cli.command()
@click.option(
    "--state-file",
    default=".scraper_state.json",
    help="Path to state file to remove.",
)
@click.confirmation_option(prompt="Remove saved state?")
def clean(state_file: str) -> None:
    """Remove saved scraper state."""
    mgr = StateManager(path=state_file, enabled=True)
    mgr.clear()
    console.print("[green]State cleaned.[/green]")


if __name__ == "__main__":
    cli()
