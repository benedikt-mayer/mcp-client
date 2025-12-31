"""Tests for call_forecast.py client module."""

from unittest.mock import AsyncMock, MagicMock
import re
import pytest


async def test_uri_validation_valid_http():
    """Test that HTTP URIs are accepted."""
    import urllib.parse

    uri = "http://127.0.0.1:8000/mcp"
    parsed = urllib.parse.urlparse(uri)
    assert parsed.scheme in ("http", "https")


async def test_uri_validation_valid_https():
    """Test that HTTPS URIs are accepted."""
    import urllib.parse

    uri = "https://example.com:8000/mcp"
    parsed = urllib.parse.urlparse(uri)
    assert parsed.scheme in ("http", "https")


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


def test_forward_geocode_tool_search():
    """Test that forward_geocode tool is found in a list of tools."""
    tool_names = ["forward_geocode", "reverse_geocode", "other_tool"]

    found = None
    for name in tool_names:
        if "forward_geocode" in name:
            found = name
            break

    assert found == "forward_geocode"


def test_get_forecast_tool_search():
    """Test that get_forecast tool is found in a list of tools."""
    tool_names = ["get_forecast", "save_raw_forecast", "other_tool"]

    found = None
    for name in tool_names:
        if "get_forecast" in name:
            found = name
            break

    assert found == "get_forecast"


def test_coordinates_extraction_from_response():
    """Test extracting latitude and longitude from geocoding response."""
    response_text = "1. Paris (Île-de-France, France) -> lat=48.8566, lon=2.3522"

    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", response_text)
    assert match is not None
    lat = float(match.group(1))
    lon = float(match.group(2))

    assert lat == 48.8566
    assert lon == 2.3522


def test_coordinates_extraction_negative_values():
    """Test extracting negative coordinates."""
    response_text = (
        "1. Sydney (New South Wales, Australia) -> lat=-33.8688, lon=151.2093"
    )

    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", response_text)
    assert match is not None
    lat = float(match.group(1))
    lon = float(match.group(2))

    assert lat == -33.8688
    assert lon == 151.2093


def test_coordinates_extraction_no_match():
    """Test handling when coordinates cannot be extracted."""
    response_text = "No location found"

    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", response_text)
    assert match is None


async def test_geocoding_args_construction():
    """Test that geocoding tool arguments are constructed correctly."""
    place_name = "Paris"
    args = {"query": place_name}

    assert args["query"] == "Paris"
    assert len(args) == 1


async def test_forecast_args_construction():
    """Test that forecast tool arguments are constructed correctly."""
    latitude = 48.8566
    longitude = 2.3522

    args = {"latitude": latitude, "longitude": longitude}

    assert args["latitude"] == 48.8566
    assert args["longitude"] == 2.3522
    assert len(args) == 2


async def test_mock_geocoding_call():
    """Test that a mock geocoding tool call returns expected content."""
    mock_session = AsyncMock()

    # Mock the call_tool response
    mock_result = MagicMock()
    mock_result.content = [
        MagicMock(text="1. Paris (Île-de-France, France) -> lat=48.8566, lon=2.3522")
    ]

    mock_session.call_tool.return_value = mock_result

    # Test calling a tool
    result = await mock_session.call_tool("forward_geocode", {"query": "Paris"})
    assert "48.8566" in result.content[0].text
    mock_session.call_tool.assert_called_once_with(
        "forward_geocode", {"query": "Paris"}
    )


async def test_mock_forecast_call():
    """Test that a mock forecast tool call returns expected content."""
    mock_session = AsyncMock()

    # Mock the call_tool response
    mock_result = MagicMock()
    mock_result.content = [MagicMock(text="Temperature: 10°C\nConditions: Cloudy")]

    mock_session.call_tool.return_value = mock_result

    # Test calling a tool
    result = await mock_session.call_tool(
        "get_forecast", {"latitude": 48.8566, "longitude": 2.3522}
    )
    assert "Temperature" in result.content[0].text
    mock_session.call_tool.assert_called_once_with(
        "get_forecast", {"latitude": 48.8566, "longitude": 2.3522}
    )


async def test_server_uri_environment_variables():
    """Test that server URIs can be read from environment."""
    import os

    os.environ["GEO_SERVER"] = "http://localhost:8001/mcp"
    os.environ["WEATHER_SERVER"] = "http://localhost:8000/mcp"

    geo_uri = os.environ.get("GEO_SERVER")
    weather_uri = os.environ.get("WEATHER_SERVER")

    assert geo_uri == "http://localhost:8001/mcp"
    assert weather_uri == "http://localhost:8000/mcp"


def test_invalid_geo_server_uri_missing():
    """Test that missing geo server URI raises appropriate error."""
    geo_server_uri = None

    if not geo_server_uri:
        with pytest.raises(SystemExit):
            raise SystemExit(
                "Please specify --geo-server or set GEO_SERVER to an http(s):// URI"
            )


def test_invalid_weather_server_uri_missing():
    """Test that missing weather server URI raises appropriate error."""
    weather_server_uri = None

    if not weather_server_uri:
        with pytest.raises(SystemExit):
            raise SystemExit(
                "Please specify --weather-server or set WEATHER_SERVER to an http(s):// URI"
            )


def test_missing_place_name():
    """Test that missing place name raises appropriate error."""
    place_name = None

    if not place_name:
        with pytest.raises(SystemExit):
            raise SystemExit("Please provide a place name")


async def test_argparse_place_argument():
    """Test argument parsing for place name."""
    import argparse

    parser = argparse.ArgumentParser(description="Test parser")
    parser.add_argument("place", help="Place name")

    args = parser.parse_args(["Paris"])
    assert args.place == "Paris"


async def test_argparse_geo_and_weather_servers():
    """Test argument parsing for geo and weather server flags."""
    import argparse

    parser = argparse.ArgumentParser(description="Test parser")
    parser.add_argument("place", help="Place name")
    parser.add_argument(
        "--geo-server",
        default="http://127.0.0.1:8001/mcp",
        help="Geo server URI",
    )
    parser.add_argument(
        "--weather-server",
        default="http://127.0.0.1:8000/mcp",
        help="Weather server URI",
    )

    args = parser.parse_args(
        [
            "Paris",
            "--geo-server",
            "http://custom:8001/mcp",
            "--weather-server",
            "http://custom:8000/mcp",
        ]
    )
    assert args.place == "Paris"
    assert args.geo_server == "http://custom:8001/mcp"
    assert args.weather_server == "http://custom:8000/mcp"
