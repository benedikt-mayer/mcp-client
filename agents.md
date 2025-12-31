# Agents & Tools — mcp-client

A focused reference for using the `mcp-client` to fetch weather forecasts by place name, combining two MCP servers.

## Overview ✅
- The client takes a **place name** as input and returns a weather forecast.
- It orchestrates two MCP servers over HTTP(S):
  - **lat-long-mcp-server** (e.g. `http://127.0.0.1:8001/mcp`): resolves place names to latitude/longitude
  - **weather-mcp-server** (e.g. `http://127.0.0.1:8000/mcp`): fetches weather forecasts for coordinates

## Prerequisites 🔧
- Both MCP servers must be running and reachable.
- Use a virtual environment: `python -m venv .venv && source .venv/bin/activate`
- Always install packages using `uv` (preferred) or your chosen project tooling. Do NOT mix system pip with project-managed installs.

## Running the client 💡
**Basic usage (with defaults):**
```bash
python -m call_forecast "Paris"
```

**With custom server URIs:**
```bash
python -m call_forecast "London" \
  --geo-server http://127.0.0.1:8001/mcp \
  --weather-server http://127.0.0.1:8000/mcp
```

**Using environment variables:**
```bash
export GEO_SERVER=http://127.0.0.1:8001/mcp
export WEATHER_SERVER=http://127.0.0.1:8000/mcp
python -m call_forecast "Berlin"
```

## Workflow 🔄
1. User calls: `python -m call_forecast "Place Name"`
2. Client calls `forward_geocode("Place Name")` on lat-long-mcp-server
3. Client parses the response to extract lat/lon
4. Client calls `get_forecast(lat, lon)` on weather-mcp-server
5. Client displays the formatted forecast

## Starting the MCP servers (when needed) — use `uv` ⚠️
**Weather Server:**
```bash
cd ../weather-mcp-server
uv run --with mcp python -m weather
# Runs on http://127.0.0.1:8000/mcp by default
```

**Lat-Long Server (requires OPENWEATHERMAP_API_KEY):**
```bash
cd ../lat-long-mcp-server
export OPENWEATHERMAP_API_KEY=your_key
uv run --with mcp python -m lat_long_mcp_server
# Runs on http://127.0.0.1:8001/mcp by default
```

## Testing & linting 🧪
- Tests (if present) can be run with `pytest` inside the activated virtual environment.
- Use `ruff` (or configured project tools) for linting/formatting.
- **After every code change, run:** `ruff check --fix .` and `ruff format .` to ensure code quality and consistency.
- **Commit and push separately:** run `git commit` first, then `git push` as separate steps (avoid chaining commit+push).
- Always ask before pushing to any remote.

## Troubleshooting ⚠️
- If you see "forward_geocode tool not found", check that lat-long-mcp-server is running on the correct URI.
- If you see "get_forecast tool not found", check that weather-mcp-server is running on the correct URI.
- If geocoding fails: verify the place name is valid and the OPENWEATHERMAP_API_KEY is set on the lat-long server.
- If coordinates are extracted incorrectly, check the regex pattern in `call_forecast.py`.

## Contributing
- Keep changes small and focused; add tests for behavioral changes.
- When adding new servers or tools, update the client to discover and call them appropriately.
- Follow the repository's existing patterns for dependency and CI configuration.

---
Concise and targeted for developers who need to run or test the unified weather client. Always prefer `uv` for running and installing project dependencies.