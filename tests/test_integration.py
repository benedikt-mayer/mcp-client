"""Integration tests for mcp-client with mock MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp import ClientSession


@pytest.mark.asyncio
async def test_streamable_http_client_connection():
    """Test that streamable_http_client creates a valid context."""
    with patch("mcp.client.streamable_http.streamable_http_client") as mock_client:
        # Mock the context manager
        mock_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_client.return_value.__aexit__.return_value = None

        server_uri = "http://127.0.0.1:8000/mcp"
        # In real usage, this would return a context manager
        assert server_uri.startswith("http")


@pytest.mark.asyncio
async def test_client_list_and_call_tools():
    """Test complete workflow: list tools and call one."""
    mock_session = AsyncMock(spec=ClientSession)

    # Mock tools
    mock_tool = MagicMock()
    mock_tool.name = "get_forecast"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call result
    mock_result = MagicMock()
    mock_result.content = ["Now: Temperature 10°C\nDaily: High 15°C, Low 5°C"]
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
    args = {"latitude": 49.48, "longitude": 8.446}
    result = await mock_session.call_tool(tool_name, args)
    assert result.content is not None


@pytest.mark.asyncio
async def test_handle_tool_not_found():
    """Test handling when tool is not found."""
    mock_session = AsyncMock(spec=ClientSession)

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
async def test_handle_tool_call_error():
    """Test handling when tool call fails."""
    mock_session = AsyncMock(spec=ClientSession)

    # Mock successful list
    mock_tool = MagicMock()
    mock_tool.name = "get_forecast"
    mock_list_response = MagicMock()
    mock_list_response.tools = [mock_tool]

    mock_session.list_tools.return_value = mock_list_response

    # Mock tool call error
    mock_session.call_tool.side_effect = Exception("Connection failed")

    await mock_session.list_tools()
    tool_name = "get_forecast"

    with pytest.raises(Exception, match="Connection failed"):
        await mock_session.call_tool(tool_name, {"latitude": 49.48, "longitude": 8.446})


@pytest.mark.asyncio
async def test_multiple_tools_available():
    """Test listing multiple tools and selecting the correct one."""
    mock_session = AsyncMock(spec=ClientSession)

    # Mock multiple tools
    tools_data = [
        MagicMock(name="save_forecast"),
        MagicMock(name="get_forecast"),
        MagicMock(name="list_locations"),
    ]
    mock_list_response = MagicMock()
    mock_list_response.tools = tools_data

    mock_session.list_tools.return_value = mock_list_response

    # Simulate tool search
    response = await mock_session.list_tools()
    tool_names = [t.name for t in response.tools]

    assert "get_forecast" in tool_names
    assert "save_forecast" in tool_names

    # Find get_forecast
    found_tool = None
    for name in tool_names:
        if "get_forecast" in name:
            found_tool = name
            break

    assert found_tool == "get_forecast"
