# Configuration Schema

Configuration files use YAML format. Below is the complete reference.

## `target`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `base_url` | string | yes | Base URL of the target website |
| `start_path` | string | no | Path to start scraping from (default: empty) |
| `selectors` | object | yes | CSS selectors for listing page elements |
| `detail_selectors` | object | no | CSS selectors for detail page elements |
| `pagination` | object | no | Pagination configuration |
| `max_pages` | integer | no | Max pages to scrape (0 = unlimited, default: 0) |

### `target.selectors`

| Field | Type | Description |
|-------|------|-------------|
| `item` | string | Selector for each item container |
| `title` | string | Selector for title element within item |
| `title_attribute` | string | Attribute to extract (default: text content) |
| `price` | string | Selector for price element |
| `rating` | string | Selector for rating element |
| `link` | string | Selector for detail page link |
| `link_attribute` | string | Attribute containing the URL (default: "href") |

### `target.pagination`

| Field | Type | Description |
|-------|------|-------------|
| `next_selector` | string | CSS selector for the "next page" link |
| `next_attribute` | string | Attribute with the URL (default: "href") |
| `page_info_selector` | string | Selector showing current page info |

## `request`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `delay` | float | 1.0 | Seconds between requests |
| `timeout` | integer | 30 | Request timeout in seconds |
| `max_retries` | integer | 3 | Maximum retry attempts |
| `retry_base_delay` | float | 1.0 | Base delay for exponential backoff |
| `follow_detail_links` | boolean | false | Whether to follow links to detail pages |
| `headers` | object | {} | Custom HTTP headers |
| `proxy` | string | null | Proxy URL (e.g., `http://proxy:8080`) |

## `output`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `format` | string | "csv" | Export format: `csv`, `json`, or `excel` |
| `directory` | string | "output" | Output directory path |
| `filename` | string | "data" | Base filename (without extension) |
| `include_timestamp` | boolean | true | Append timestamp to filename |

## `logging`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | string | "INFO" | Log level: DEBUG, INFO, WARNING, ERROR |
| `file` | string | null | Log file path (null = console only) |

## `state`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | true | Enable resume capability |
| `file` | string | ".scraper_state.json" | State file path |
