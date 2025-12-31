# MCP Client - Unified Weather Forecast

A client that combines two MCP servers to provide weather forecasts for a given place name.

## Overview

This client:
1. Takes a place name as input
2. Calls **lat-long-mcp-server** to resolve the place name to latitude/longitude
3. Calls **weather-mcp-server** to get the weather forecast for those coordinates
4. Returns the formatted forecast

## Prerequisites

- Both MCP servers must be running:
  - `weather-mcp-server` on `http://127.0.0.1:8000/mcp` (default)
  - `lat-long-mcp-server` on `http://127.0.0.1:8001/mcp` (default)
- Python 3.12+
- Install dependencies: `uv pip install -e .` or `uv sync`

## Running the Client

### Basic usage (using defaults):
```bash
python -m call_forecast "Paris"
```

### With custom server URIs:
```bash
python -m call_forecast "London" \
  --geo-server http://127.0.0.1:8001/mcp \
  --weather-server http://127.0.0.1:8000/mcp
```

### Using environment variables:
```bash
export GEO_SERVER=http://127.0.0.1:8001/mcp
export WEATHER_SERVER=http://127.0.0.1:8000/mcp
python -m call_forecast "Berlin"
```

## Examples

Get weather for Ludwigshafen am Rhein:
```bash
python -m call_forecast "Ludwigshafen am Rhein"
```

Get weather for New York:
```bash
python -m call_forecast "New York"
```

## Starting the MCP Servers (if needed)

In separate terminal windows:

```bash
# Terminal 1: Start weather server
cd ../weather-mcp-server
uv run --with mcp python -m weather

# Terminal 2: Start lat-long server (requires OPENWEATHERMAP_API_KEY)
cd ../lat-long-mcp-server
export OPENWEATHERMAP_API_KEY=your_api_key_here
uv run --with mcp python -m lat_long_mcp_server
```

## Testing

Run the test suite:
```bash
uv run pytest
```

Or with a specific test file:
```bash
uv run pytest tests/test_call_forecast.py -v
```
