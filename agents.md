# Agents & Tools — mcp-client

A small, focused reference for using the `mcp-client` example scripts and interacting with HTTP(S) MCP servers.

## Overview ✅
- This repository contains simple example clients (e.g. `call_forecast.py`) that call MCP servers over HTTP(S).
- The client expects a reachable MCP HTTP endpoint (e.g. `http://127.0.0.1:8000/mcp`).

## Prerequisites 🔧
- Use a virtual environment: python -m venv .venv && source .venv/bin/activate
- Always install packages using `uv` (preferred) or your chosen project tooling. Do NOT mix system pip with project-managed installs.

## Running the client 💡
- Set a server URI via the `--server` flag or `MCP_SERVER` env var:
  - Example:
    - `python -m call_forecast --server http://127.0.0.1:8000/mcp`
    - `MCP_SERVER=http://127.0.0.1:8000/mcp python -m call_forecast`
- The client will connect with `mcp.client.streamable_http.streamable_http_client` and list/call tools on the server.

## Starting a local MCP server (when needed) — use `uv` ⚠️
- If you need a local server for testing, run the server project with `uv` as recommended:
  - `cd ../weather-mcp-server`
  - `uv run --with mcp python -m weather`
- Using `uv` ensures dependencies are consistent with the project lock file and avoids environment drift.

## Testing & linting 🧪
- Tests (if present) can be run with `pytest` inside the activated virtual environment.
- Use `ruff` (or configured project tools) for linting/formatting.

## Troubleshooting ⚠️
- If you see transport errors, confirm:
  - `--server` or `MCP_SERVER` is set and uses `http://` or `https://`.
  - The server is reachable (use curl or a browser to verify).
  - The `mcp` package with `streamable_http` client is installed in the active environment.

## Contributing
- Keep changes small and focused; add tests for behavioral changes.
- Follow the repository's existing patterns for dependency and CI configuration.

---
Concise and targeted for developers who need to run or test the example client code. Always prefer `uv` for running and installing project dependencies.