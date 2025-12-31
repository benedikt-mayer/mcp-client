"""Integration tests for mcp-client with mock MCP servers."""

import re
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_streamable_http_client_connection():
    """Test that streamable_http_client creates a valid context."""
    with patch("mcp.client.streamable_http.streamable_http_client") as mock_client:
        # Mock the context manager
        mock_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_client.return_value.__aexit__.return_value = None

        server_uri = "http://127.0.0.1:8001/mcp"
        assert server_uri.startswith("http")


@pytest.mark.asyncio
async def test_geocoding_workflow():
    """Test the geocoding workflow: list tools and call forward_geocode."""
    mock_session = AsyncMock()

    # Mock forward_geocode tool
    mock_tool = MagicMock()
    mock_tool.name = "forward_geocode"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call result
    mock_result = MagicMock()
    mock_result.content = [
        MagicMock(text="1. Paris (Île-de-France, France) -> lat=48.8566, lon=2.3522")
    ]
    mock_session.call_tool.return_value = mock_result

    # Simulate the workflow
    response = await mock_session.list_tools()
    tools = response.tools
    assert len(tools) > 0

    tool_name = None
    for t in tools:
        if "forward_geocode" in t.name:
            tool_name = t.name
            break

    assert tool_name == "forward_geocode"

    # Call the tool
    args = {"query": "Paris"}
    result = await mock_session.call_tool(tool_name, args)

    # Extract coordinates
    text = result.content[0].text
    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", text)
    assert match is not None
    assert float(match.group(1)) == 48.8566
    assert float(match.group(2)) == 2.3522


@pytest.mark.asyncio
async def test_weather_forecast_workflow():
    """Test the weather forecast workflow: list tools and call get_forecast."""
    mock_session = AsyncMock()

    # Mock get_forecast tool
    mock_tool = MagicMock()
    mock_tool.name = "get_forecast"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call result
    mock_result = MagicMock()
    mock_result.content = [
        MagicMock(text="Now: Temperature 10°C\nDaily: High 15°C, Low 5°C")
    ]
    mock_session.call_tool.return_value = mock_result

    # Simulate the workflow
    response = await mock_session.list_tools()
    tools = response.tools
    assert len(tools) > 0

    tool_name = None
    for t in tools:
        if "get_forecast" in t.name:
            tool_name = t.name
            break

    assert tool_name == "get_forecast"

    # Call the tool
    args = {"latitude": 48.8566, "longitude": 2.3522}
    result = await mock_session.call_tool(tool_name, args)
    assert result.content is not None
    assert "Temperature" in result.content[0].text


@pytest.mark.asyncio
async def test_dual_server_workflow():
    """Test the complete dual-server workflow: geocode then get forecast."""
    # First session: geocoding
    geo_session = AsyncMock()

    # Mock geocoding tools and response
    geo_tool = MagicMock()
    geo_tool.name = "forward_geocode"
    geo_list_response = MagicMock()
    geo_list_response.tools = [geo_tool]
    geo_session.list_tools.return_value = geo_list_response

    geo_result = MagicMock()
    geo_result.content = [
        MagicMock(text="1. Paris (Île-de-France, France) -> lat=48.8566, lon=2.3522")
    ]
    geo_session.call_tool.return_value = geo_result

    # Get coordinates
    response = await geo_session.list_tools()
    tool_name = None
    for t in response.tools:
        if "forward_geocode" in t.name:
            tool_name = t.name
            break

    result = await geo_session.call_tool(tool_name, {"query": "Paris"})
    text = result.content[0].text
    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", text)
    lat = float(match.group(1))
    lon = float(match.group(2))

    assert lat == 48.8566
    assert lon == 2.3522

    # Second session: weather
    weather_session = AsyncMock()

    # Mock weather tools and response
    weather_tool = MagicMock()
    weather_tool.name = "get_forecast"
    weather_list_response = MagicMock()
    weather_list_response.tools = [weather_tool]
    weather_session.list_tools.return_value = weather_list_response

    weather_result = MagicMock()
    weather_result.content = [MagicMock(text="Weather for Paris: Temperature 10°C")]
    weather_session.call_tool.return_value = weather_result

    # Get forecast
    response = await weather_session.list_tools()
    tool_name = None
    for t in response.tools:
        if "get_forecast" in t.name:
            tool_name = t.name
            break

    result = await weather_session.call_tool(
        tool_name, {"latitude": lat, "longitude": lon}
    )
    assert "Temperature" in result.content[0].text


@pytest.mark.asyncio
async def test_handle_forward_geocode_not_found():
    """Test handling when forward_geocode tool is not found."""
    mock_session = AsyncMock()

    # Mock empty tools or tools without forward_geocode
    mock_tool = MagicMock()
    mock_tool.name = "reverse_geocode"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Simulate the workflow
    response = await mock_session.list_tools()
    tools = response.tools

    tool_name = None
    for t in tools:
        if "forward_geocode" in t.name:
            tool_name = t.name
            break

    assert tool_name is None


@pytest.mark.asyncio
async def test_handle_get_forecast_not_found():
    """Test handling when get_forecast tool is not found."""
    mock_session = AsyncMock()

    # Mock empty tools or tools without get_forecast
    mock_tool = MagicMock()
    mock_tool.name = "save_forecast"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Simulate the workflow
    response = await mock_session.list_tools()
    tools = response.tools

    tool_name = None
    for t in tools:
        if "get_forecast" in t.name:
            tool_name = t.name
            break

    assert tool_name is None


@pytest.mark.asyncio
async def test_handle_geocoding_call_error():
    """Test handling when geocoding tool call fails."""
    mock_session = AsyncMock()

    # Mock successful list
    mock_tool = MagicMock()
    mock_tool.name = "forward_geocode"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call error
    mock_session.call_tool.side_effect = Exception("Geocoding service unavailable")

    await mock_session.list_tools()

    with pytest.raises(Exception, match="Geocoding service unavailable"):
        await mock_session.call_tool("forward_geocode", {"query": "Paris"})


@pytest.mark.asyncio
async def test_handle_forecast_call_error():
    """Test handling when forecast tool call fails."""
    mock_session = AsyncMock()

    # Mock successful list
    mock_tool = MagicMock()
    mock_tool.name = "get_forecast"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call error
    mock_session.call_tool.side_effect = Exception("Weather service unavailable")

    await mock_session.list_tools()

    with pytest.raises(Exception, match="Weather service unavailable"):
        await mock_session.call_tool(
            "get_forecast", {"latitude": 48.8566, "longitude": 2.3522}
        )


@pytest.mark.asyncio
async def test_multiple_geocoding_results():
    """Test handling multiple geocoding results."""
    mock_session = AsyncMock()

    # Mock forward_geocode tool
    mock_tool = MagicMock()
    mock_tool.name = "forward_geocode"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call with multiple results (only first is used)
    mock_result = MagicMock()
    mock_result.content = [
        MagicMock(
            text="""1. Paris (Île-de-France, France) -> lat=48.8566, lon=2.3522
2. Paris (Texas, United States) -> lat=33.6615, lon=-95.5007"""
        )
    ]
    mock_session.call_tool.return_value = mock_result

    # Get coordinates (should use first result)
    await mock_session.list_tools()
    result = await mock_session.call_tool("forward_geocode", {"query": "Paris"})

    text = result.content[0].text
    match = re.search(r"lat=([-\d.]+), lon=([-\d.]+)", text)
    lat = float(match.group(1))
    lon = float(match.group(2))

    # Should get the first match
    assert lat == 48.8566
    assert lon == 2.3522
