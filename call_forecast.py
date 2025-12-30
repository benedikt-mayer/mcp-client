# /// script
# dependencies = [
#   "asyncio",
#   "mcp",
# ]
# ///

import argparse
import asyncio
import urllib.parse
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    parser = argparse.ArgumentParser(
        description="Call a running MCP server or start one locally."
    )
    parser.add_argument(
        "--server",
        help="Server URI to connect to. Examples: http://127.0.0.1:8000/mcp or https://server.example/mcp.",
    )
    ns = parser.parse_args()

    server_uri = ns.server

    # Only support HTTP(S) MCP servers. Require --server.
    if not server_uri:
        raise SystemExit(
            "Please specify --server or set MCP_SERVER to an http(s):// URI"
        )

    # Validate scheme and create an HTTP client context
    parsed = urllib.parse.urlparse(server_uri)
    scheme = parsed.scheme
    if scheme not in ("http", "https"):
        raise ValueError(
            f"Unsupported server URI scheme: {scheme}. Use http:// or https://"
        )

    client_ctx = streamable_http_client(server_uri)

    async with client_ctx as ctx:
        # ctx may be (read, write) or (read, write, get_session_id)
        if len(ctx) == 2:
            stdio, write = ctx
        else:
            stdio, write = ctx[0], ctx[1]

        async with ClientSession(stdio, write) as session:
            await session.initialize()

            # List available tools
            response = await session.list_tools()
            tools = response.tools
            print("Available tools:", [t.name for t in tools])

            # Find a tool that contains 'get_forecast' in its name
            tool_name = None
            for t in tools:
                if "get_forecast" in t.name:
                    tool_name = t.name
                    break

            if tool_name is None:
                print("get_forecast tool not found")
                return

            # Call the tool for Ludwigshafen am Rhein (49.48, 8.446)
            args = {"latitude": 49.48, "longitude": 8.446}
            print(f"Calling {tool_name} with args {args}...")
            result = await session.call_tool(tool_name, args)

            # Print the result
            try:
                print("\n--- Forecast Result ---\n")
                print(result.content)
                print("\n--- End ---\n")
            except Exception as e:
                print("Tool returned non-text result:", e)


if __name__ == "__main__":
    asyncio.run(main())
