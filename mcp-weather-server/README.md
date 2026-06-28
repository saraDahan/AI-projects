# MCP Weather Server

A Model Context Protocol (MCP) server that provides weather information for both Israel and the USA, powered by Claude (Anthropic).

## Overview

This project implements an MCP-based weather assistant with two separate servers:

- **weather_Israel.py** — Scrapes live weather forecasts from [weather2day.co.il](https://www.weather2day.co.il/forecast) using Playwright (browser automation).
- **weather_USA.py** — Fetches weather alerts and forecasts from the [National Weather Service API](https://api.weather.gov) (no API key required).

The `host.py` connects both servers, collects their tools, and exposes them to Claude (`claude-haiku-4-5`) via a chat loop. The `client.py` handles the MCP client session for each server.

## Project Structure

```
mcp-weather-server/
├── weather_Israel.py   # MCP server - Israeli weather via Playwright
├── weather_USA.py      # MCP server - USA weather via NWS API
├── client.py           # MCP client session wrapper
├── host.py             # Chat host - connects clients, calls Claude
├── pyproject.toml      # Project dependencies
└── .env                # Environment variables (not committed)
```

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

## Configuration

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

> Without this key, the host will not be able to communicate with Claude.

## Usage

Run the interactive chat loop:

```bash
uv run python host.py
```

Then type your weather queries, for example:

- `What is the weather in Tel Aviv?`
- `Are there any weather alerts in California?`
- `What is the forecast for New York? (latitude: 40.71, longitude: -74.00)`

Type `quit` to exit.

## Available Tools

### Israel
| Tool | Description |
|------|-------------|
| `open_weather_forecast_israel` | Opens the Israeli weather forecast website |
| `enter_weather_forecast_city_israel` | Enters a city name (in Hebrew) in the search field |
| `select_weather_forecast_city_israel` | Selects the first city from the autocomplete list |
| `get_weather_forecast_page_content_israel` | Reads and returns the forecast page content |

### USA
| Tool | Description |
|------|-------------|
| `get_alerts_in_USA` | Gets active weather alerts for a US state (e.g. `CA`, `NY`) |
| `get_forecast_in_USA` | Gets a weather forecast by latitude and longitude |

## Notes

- The Israel server launches a **visible Chromium browser** (`headless=False`) to scrape the forecast site.
- SSL verification is disabled for Netfree network compatibility.
