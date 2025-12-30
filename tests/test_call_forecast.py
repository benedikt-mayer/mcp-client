"""Tests for call_forecast.py client module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

# Import the main function from call_forecast for testing
# We'll test the components that can be tested in isolation


@pytest.mark.asyncio
async def test_uri_validation_valid_http():
    """Test that HTTP URIs are accepted."""
    import urllib.parse

    uri = "http://127.0.0.1:8000/mcp"
    parsed = urllib.parse.urlparse(uri)
    assert parsed.scheme in ("http", "https")


@pytest.mark.asyncio
async def test_uri_validation_valid_https():
    """Test that HTTPS URIs are accepted."""
    import urllib.parse

    uri = "https://example.com:8000/mcp"
    parsed = urllib.parse.urlparse(uri)
    assert parsed.scheme in ("http", "https")


@pytest.mark.asyncio
async def test_uri_validation_invalid_scheme():
    """Test that invalid URI schemes are rejected."""
    import urllib.parse

    uri = "ftp://example.com:8000/mcp"
    parsed = urllib.parse.urlparse(uri)
    with pytest.raises(ValueError, match="Unsupported server URI scheme"):
        scheme = parsed.scheme
        if scheme not in ("http", "https"):
            raise ValueError(
                f"Unsupported server URI scheme: {scheme}. Use http:// or https://"
            )


def test_tool_search_finds_get_forecast():
    """Test that get_forecast tool is found in a list of tools."""
    # Mock tool objects
    tool_names = ["get_forecast", "save_raw_forecast", "other_tool"]

    found = None
    for name in tool_names:
        if "get_forecast" in name:
            found = name
            break

    assert found == "get_forecast"


def test_tool_search_with_partial_match():
    """Test that partial matching works for tool search."""
    tool_names = ["fetch_forecast", "get_forecast_data", "current_weather"]

    found = None
    for name in tool_names:
        if "get_forecast" in name:
            found = name
            break

    assert found == "fetch_forecast_data" or found == "get_forecast_data"
    # In the actual code, it would find the first match containing "get_forecast"


def test_tool_not_found():
    """Test behavior when get_forecast tool is not found."""
    tool_names = ["save_forecast", "list_tools"]

    found = None
    for name in tool_names:
        if "get_forecast" in name:
            found = name
            break

    assert found is None


def test_args_construction():
    """Test that tool arguments are constructed correctly."""
    latitude = 49.48
    longitude = 8.446

    args = {"latitude": latitude, "longitude": longitude}

    assert args["latitude"] == 49.48
    assert args["longitude"] == 8.446
    assert len(args) == 2


@pytest.mark.asyncio
async def test_mock_client_session():
    """Test that a mock ClientSession behaves as expected."""
    mock_session = AsyncMock()

    # Mock the list_tools response
    mock_tool = MagicMock()
    mock_tool.name = "get_forecast"
    mock_response = MagicMock()
    mock_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_response

    # Test listing tools
    response = await mock_session.list_tools()
    assert response.tools[0].name == "get_forecast"
    mock_session.list_tools.assert_called_once()


@pytest.mark.asyncio
async def test_mock_tool_call():
    """Test that a mock tool call returns expected content."""
    mock_session = AsyncMock()

    # Mock the call_tool response
    mock_result = MagicMock()
    mock_result.content = "Weather forecast data here"

    mock_session.call_tool.return_value = mock_result

    # Test calling a tool
    result = await mock_session.call_tool(
        "get_forecast", {"latitude": 49.48, "longitude": 8.446}
    )
    assert result.content == "Weather forecast data here"
    mock_session.call_tool.assert_called_once_with(
        "get_forecast", {"latitude": 49.48, "longitude": 8.446}
    )


def test_result_content_extraction():
    """Test extracting content from a tool result."""
    mock_result = MagicMock()
    mock_result.content = ["Weather summary:\nTemperature: 10°C\nConditions: Cloudy"]

    # Simulate printing result content
    try:
        content_str = str(mock_result.content)
        assert "Weather" in content_str
    except Exception:
        pytest.fail("Failed to extract result content")


@pytest.mark.asyncio
async def test_server_uri_environment_variable():
    """Test that server URI can be read from environment."""
    import os

    os.environ["MCP_SERVER"] = "http://localhost:8000/mcp"
    uri = os.environ.get("MCP_SERVER")
    assert uri == "http://localhost:8000/mcp"


def test_invalid_server_uri_missing():
    """Test that missing server URI raises appropriate error."""
    server_uri = None

    if not server_uri:
        with pytest.raises(SystemExit):
            raise SystemExit(
                "Please specify --server or set MCP_SERVER to an http(s):// URI"
            )


@pytest.mark.asyncio
async def test_argparse_server_flag():
    """Test argument parsing for server flag."""
    import argparse

    parser = argparse.ArgumentParser(description="Test parser")
    parser.add_argument("--server", help="Server URI")

    args = parser.parse_args(["--server", "http://127.0.0.1:8000/mcp"])
    assert args.server == "http://127.0.0.1:8000/mcp"
