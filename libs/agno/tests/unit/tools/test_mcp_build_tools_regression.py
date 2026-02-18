"""
BUG #4573 regression guard: MCPTools.build_tools() must populate functions.

The original bug was that AgentOS didn't see MCP tools because the MCP
connection lifecycle wasn't integrated with the agent lifecycle. Fixed in
commit ba81b82da (Oct 2025) — MCPTools now self-connect inside agents.

This test verifies the core build_tools() path works and populates the
functions dict, which is what the agent (and AgentOS) reads to list tools.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agno.tools.mcp import MCPTools


@pytest.mark.asyncio
async def test_build_tools_populates_functions_from_session():
    """
    BUG #4573: MCPTools must populate self.functions from session.list_tools()
    so that the agent (and AgentOS) can see and use the tools.
    """
    tools = MCPTools(url="http://localhost:8000/mcp")

    mock_tool_a = MagicMock()
    mock_tool_a.name = "get_weather"
    mock_tool_a.description = "Get weather for a city"
    mock_tool_a.inputSchema = {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    }

    mock_tool_b = MagicMock()
    mock_tool_b.name = "search_docs"
    mock_tool_b.description = "Search documents"
    mock_tool_b.inputSchema = {
        "type": "object",
        "properties": {"query": {"type": "string"}},
    }

    mock_tools_result = MagicMock()
    mock_tools_result.tools = [mock_tool_a, mock_tool_b]

    mock_session = AsyncMock()
    mock_session.list_tools = AsyncMock(return_value=mock_tools_result)

    tools.session = mock_session

    with patch("agno.tools.mcp.mcp.get_entrypoint_for_tool", return_value=lambda: "result"):
        await tools.build_tools()

    assert len(tools.functions) == 2
    assert "get_weather" in tools.functions
    assert "search_docs" in tools.functions
    assert tools.functions["get_weather"].description == "Get weather for a city"
    assert tools.functions["search_docs"].description == "Search documents"
