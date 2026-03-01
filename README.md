# Smart Web Scraper

A production-ready web scraper with YAML-based configuration, advanced retry logic, and flexible export formats.

## Features

- **YAML Configuration**: Declarative scraping rules via simple YAML files
- **Async HTTP Requests**: High-performance scraping with httpx
- **Pagination Support**: Automatic multi-page traversal with configurable limits
- **Multiple Export Formats**: CSV, JSON, and Excel output
- **Rate Limiting & Retry Logic**: Exponential backoff and intelligent retry strategies
- **User-Agent Rotation**: Avoid detection with automatic header management
- **Proxy Support**: Optional proxy configuration for anonymity
- **Resume Capability**: Save and restore scraping state between sessions
- **Rich CLI Interface**: User-friendly command-line with progress indicators
- **Comprehensive Tests**: Full test coverage with pytest and respx mocking

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/smart-web-scraper.git
cd smart-web-scraper
pip install -e ".[dev]"
```

### Usage

Scrape a website using a configuration file:

```bash
# Basic usage with default settings
smart-scraper scrape -c configs/books_toscrape.yaml

# Override format and limit pages
smart-scraper scrape -c configs/books_toscrape.yaml -f json --max-pages 5

# Verbose output for debugging
smart-scraper scrape -c configs/books_toscrape.yaml -v

# Convert existing data to another format
smart-scraper convert -i output/books.json -f excel

# Clear state and start fresh
smart-scraper clean --yes
```

## Configuration

Configuration files are simple YAML files defining the target website, CSS selectors, and request parameters.

See [`configs/config_schema.md`](configs/config_schema.md) for complete documentation.

### Example Configuration

```yaml
target:
  base_url: "https://books.toscrape.com/"
  start_path: "catalogue/page-1.html"
  selectors:
    item: "article.product_pod"
    title: "h3 a"
    title_attribute: "title"
    price: ".price_color"
    link: "h3 a"
    link_attribute: "href"
  pagination:
    next_selector: "li.next a"
    next_attribute: "href"
  max_pages: 0  # 0 = all pages

request:
  delay: 1.0
  timeout: 30
  max_retries: 3
  retry_base_delay: 1.0

output:
  format: "csv"
  directory: "output"
  filename: "books"
  include_timestamp: true

state:
  enabled: true
  file: ".scraper_state.json"
```

## Project Structure

```
smart-web-scraper/
├── configs/                    # Example configurations
│   ├── books_toscrape.yaml
│   └── config_schema.md
├── src/scraper/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── client.py              # HTTP client with retry logic
│   ├── config.py              # Configuration parsing and validation
│   ├── exporter.py            # CSV, JSON, Excel export
│   ├── paginator.py           # Pagination handling
│   ├── parser.py              # HTML parsing with BeautifulSoup
│   ├── state.py               # Resume capability
│   └── utils.py               # Utility functions
├── tests/                     # Comprehensive test suite
├── pyproject.toml             # Project metadata and dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## Development

Install dependencies and run tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ -v --cov=src

# Lint and format check
ruff check src/ tests/

# Fix style issues automatically
ruff check --fix src/ tests/
```

## Tech Stack

- **Python 3.11+**: Modern Python with type hints
- **httpx**: Modern async HTTP client with connection pooling
- **BeautifulSoup4**: Reliable HTML parsing
- **Click**: Intuitive CLI framework
- **Pydantic**: Data validation and settings management
- **Pandas**: Data manipulation and Excel export
- **Tenacity**: Advanced retry logic with exponential backoff
- **Rich**: Beautiful terminal output
- **PyYAML**: YAML configuration parsing

## License

MIT License - See [`LICENSE`](LICENSE) file for details.
