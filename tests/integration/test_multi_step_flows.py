"""
Integration tests for multi-step reasoning flows
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.src.agents.todo_chatbot.agent import Agent, AgentConfig


@pytest.mark.asyncio
async def test_multi_step_discovery_flow():
    """Test the discovery-first pattern (list_tasks → action)"""
    config = AgentConfig()
    agent = Agent(config)

    # Mock MCP integration to simulate listing tasks first, then performing an action
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        # First call: list_tasks
        mock_mcp.side_effect = [
            {"tasks": [{"id": "1", "title": "grocery shopping", "status": "pending"}]},  # list_tasks result
            {"task_id": "1", "status": "completed"}  # complete_task result
        ]

        # Test a message that would trigger ambiguity resolution
        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Complete the shopping task"
        )

        # Verify that list_tasks was called first (discovery step)
        assert mock_mcp.call_count >= 1
        first_call = mock_mcp.call_args_list[0]
        assert first_call[0][0] == "list_tasks"  # First call should be to list tasks


@pytest.mark.asyncio
async def test_ambiguous_request_triggers_clarification():
    """Test that ambiguous requests trigger clarification"""
    config = AgentConfig()
    agent = Agent(config)

    # Mock MCP integration
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"tasks": [
            {"id": "1", "title": "meeting with John", "status": "pending"},
            {"id": "2", "title": "grocery shopping", "status": "pending"}
        ]}

        # Test an ambiguous request
        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Complete it"  # Very ambiguous
        )

        # Should have triggered the ambiguous request handling
        assert "found" in result["response"].lower() or "specify" in result["response"].lower()
        assert result["next_action"] == "await_confirmation"


@pytest.mark.asyncio
async def test_partial_match_detection():
    """Test detection and handling of partial matches"""
    config = AgentConfig()
    agent = Agent(config)

    # Mock MCP integration
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"tasks": [
            {"id": "1", "title": "meeting with John Smith", "status": "pending"},
            {"id": "2", "title": "meeting with Jane Doe", "status": "pending"},
            {"id": "3", "title": "grocery shopping", "status": "pending"}
        ]}

        # Test a partial match request
        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Update the meeting task"  # Matches multiple tasks
        )

        # Should have asked for clarification due to multiple matches
        assert "multiple" in result["response"].lower() or "specify" in result["response"].lower()