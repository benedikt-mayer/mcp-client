# /// script
# dependencies = [
#   "asyncio",
#   "mcp",
# ]
# ///

import argparse
import asyncio
import os
import re
import urllib.parse
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def create_session(server_uri: str) -> ClientSession:
    """Create and initialize a ClientSession for the given server URI."""
    parsed = urllib.parse.urlparse(server_uri)
    scheme = parsed.scheme
    if scheme not in ("http", "https"):
        raise ValueError(
            f"Unsupported server URI scheme: {scheme}. Use http:// or https://"
        )

    client_ctx = streamable_http_client(server_uri)
    ctx = await client_ctx.__aenter__()

    # ctx may be (read, write) or (read, write, get_session_id)
    if len(ctx) == 2:
        stdio, write = ctx
    else:
        stdio, write = ctx[0], ctx[1]

    session = ClientSession(stdio, write)
    await session.__aenter__()
    await session.initialize()
    return session, client_ctx


async def get_coordinates(place_name: str, geo_server_uri: str) -> tuple[float, float]:
    """Get latitude and longitude for a place name using the lat-long-mcp-server."""
    session, ctx = await create_session(geo_server_uri)

    try:
        # List available tools
        response = await session.list_tools()
        tools = response.tools
        print(f"Available geo tools: {[t.name for t in tools]}")

        # Find the forward_geocode tool
        tool_name = None
        for t in tools:
            if "forward_geocode" in t.name:
                tool_name = t.name
                break

        if tool_name is None:
            raise RuntimeError("forward_geocode tool not found on lat-long-mcp-server")

        # Call the geocoding tool
        args = {"query": place_name}
        print(f"Calling {tool_name} with query '{place_name}'...")
        result = await session.call_tool(tool_name, args)

        # Parse the result to extract latitude and longitude
        # Expected format: "1. {name} ({state}, {country}) -> lat={lat}, lon={lon}"
        text = result.content[0].text
        print(f"Geocoding response: {text}")

        match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", text)
        if not match:
            raise RuntimeError(f"Could not parse coordinates from response: {text}")

        lat = float(match.group(1))
        lon = float(match.group(2))
        print(f"Extracted coordinates: lat={lat}, lon={lon}")

        return lat, lon
    finally:
        await session.__aexit__(None, None, None)
        await ctx.__aexit__(None, None, None)


async def get_forecast(
    latitude: float, longitude: float, weather_server_uri: str
) -> str:
    """Get weather forecast for coordinates using the weather-mcp-server."""
    session, ctx = await create_session(weather_server_uri)

    try:
        # List available tools
        response = await session.list_tools()
        tools = response.tools
        print(f"Available weather tools: {[t.name for t in tools]}")

        # Find the get_forecast tool
        tool_name = None
        for t in tools:
            if "get_forecast" in t.name:
                tool_name = t.name
                break

        if tool_name is None:
            raise RuntimeError("get_forecast tool not found on weather-mcp-server")

        # Call the weather tool
        args = {"latitude": latitude, "longitude": longitude}
        print(f"Calling {tool_name} with args {args}...")
        result = await session.call_tool(tool_name, args)

        # Extract and return the forecast text
        return result.content[0].text
    finally:
        await session.__aexit__(None, None, None)
        await ctx.__aexit__(None, None, None)


async def main():
    parser = argparse.ArgumentParser(
        description="Get weather forecast for a place by name using dual MCP servers."
    )
    parser.add_argument(
        "place",
        help="Place name to look up (e.g., 'Paris' or 'Ludwigshafen am Rhein')",
    )
    parser.add_argument(
        "--geo-server",
        default=os.environ.get("GEO_SERVER", "http://127.0.0.1:8001/mcp"),
        help="Lat-long MCP server URI (default: http://127.0.0.1:8001/mcp or GEO_SERVER env var)",
    )
    parser.add_argument(
        "--weather-server",
        default=os.environ.get("WEATHER_SERVER", "http://127.0.0.1:8000/mcp"),
        help="Weather MCP server URI (default: http://127.0.0.1:8000/mcp or WEATHER_SERVER env var)",
    )
    ns = parser.parse_args()

    place_name = ns.place
    geo_server_uri = ns.geo_server
    weather_server_uri = ns.weather_server

    if not place_name:
        raise SystemExit("Please provide a place name")

    if not geo_server_uri:
        raise SystemExit(
            "Please specify --geo-server or set GEO_SERVER to an http(s):// URI"
        )

    if not weather_server_uri:
        raise SystemExit(
            "Please specify --weather-server or set WEATHER_SERVER to an http(s):// URI"
        )

    try:
        # Step 1: Get coordinates for the place
        print(f"\n=== Step 1: Looking up coordinates for '{place_name}' ===")
        latitude, longitude = await get_coordinates(place_name, geo_server_uri)

        # Step 2: Get weather forecast for the coordinates
        print(f"\n=== Step 2: Getting forecast for {place_name} ===")
        forecast = await get_forecast(latitude, longitude, weather_server_uri)

        # Print the result
        print("\n--- Forecast Result ---\n")
        print(forecast)
        print("\n--- End ---\n")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
