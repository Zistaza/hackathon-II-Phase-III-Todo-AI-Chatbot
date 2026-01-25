"""
Comprehensive test suite covering all edge cases
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.src.agents.todo_chatbot.agent import Agent, AgentConfig
from backend.src.agents.todo_chatbot.intent_classifier import IntentClassifier, IntentType


@pytest.mark.asyncio
async def test_edge_case_empty_message():
    """Test handling of empty message"""
    config = AgentConfig()
    agent = Agent(config)

    result = await agent.process_message(
        user_id="user123",
        conversation_id="conv123",
        message=""
    )

    # Should handle gracefully
    assert result is not None
    assert "response" in result


@pytest.mark.asyncio
async def test_edge_case_very_long_message():
    """Test handling of very long message"""
    config = AgentConfig()
    agent = Agent(config)

    long_message = "This is a very long message. " * 1000

    result = await agent.process_message(
        user_id="user123",
        conversation_id="conv123",
        message=long_message
    )

    # Should handle without crashing
    assert result is not None


@pytest.mark.asyncio
async def test_edge_case_special_characters():
    """Test handling of special characters in message"""
    config = AgentConfig()
    agent = Agent(config)

    special_message = "Add task with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?~`"

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"task_id": "123", "title": "special chars task", "status": "pending"}

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message=special_message
        )

        # Should handle special characters properly
        assert result is not None


@pytest.mark.asyncio
async def test_edge_case_multiple_intents_in_one_message():
    """Test message that could be interpreted as multiple intents"""
    config = AgentConfig()
    agent = Agent(config)

    multi_intent_message = "Add a task to buy groceries and then show me all my tasks"

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"task_id": "123", "title": "buy groceries", "status": "pending"}

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message=multi_intent_message
        )

        # Should handle gracefully, likely focusing on the primary intent
        assert result is not None


@pytest.mark.asyncio
async def test_edge_case_ambiguous_pronouns():
    """Test handling of ambiguous pronouns like 'it', 'that', 'this'"""
    config = AgentConfig()
    agent = Agent(config)

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.side_effect = [
            {"tasks": [{"id": "1", "title": "meeting", "status": "pending"}]},  # list_tasks
            {"task_id": "1", "status": "completed"}  # complete_task
        ]

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Do that one"
        )

        # Should trigger ambiguity resolution
        assert result is not None


@pytest.mark.asyncio
async def test_edge_case_mcp_tool_failure():
    """Test graceful handling when MCP tool fails"""
    config = AgentConfig()
    agent = Agent(config)

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"error": "Connection failed", "degraded": True}

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Add a task to test"
        )

        # Should handle error gracefully
        assert "error" in result["response"].lower() or "failed" in result["response"].lower()


@pytest.mark.asyncio
async def test_edge_case_concurrent_users():
    """Test that the agent handles multiple users properly (stateless)"""
    config = AgentConfig()
    agent = Agent(config)

    # Simulate multiple concurrent users
    user_results = []
    for i in range(3):
        user_id = f"user{i}"
        conv_id = f"conv{i}"

        with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = {"task_id": f"task{i}", "title": f"task for user {i}", "status": "pending"}

            result = await agent.process_message(
                user_id=user_id,
                conversation_id=conv_id,
                message=f"Add a task for user {i}"
            )
            user_results.append(result)

    # All should succeed independently
    assert len(user_results) == 3
    for result in user_results:
        assert result is not None


@pytest.mark.asyncio
async def test_edge_case_invalid_json_in_tool_result():
    """Test handling of invalid JSON from MCP tools"""
    config = AgentConfig()
    agent = Agent(config)

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        # Return malformed result that should be handled gracefully
        mock_mcp.return_value = "invalid_json_result"

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Add a task"
        )

        # Should handle gracefully
        assert result is not None


def test_intent_classifier_edge_cases():
    """Test edge cases for intent classifier"""
    classifier = IntentClassifier()

    # Test empty input
    intent, confidence = classifier.classify_intent("")
    assert intent == IntentType.UNKNOWN

    # Test random input
    intent, confidence = classifier.classify_intent("asdlkfj asdfkj asdf")
    assert intent == IntentType.UNKNOWN

    # Test very short input
    intent, confidence = classifier.classify_intent("Hi")
    assert intent == IntentType.UNKNOWN


def test_tool_selection_edge_cases():
    """Test edge cases for tool selection"""
    from backend.src.agents.todo_chatbot.tool_selector import ToolSelector
    from backend.src.agents.todo_chatbot.intent_classifier import IntentType

    selector = ToolSelector()

    # Test with no parameters
    tool_call = selector.select_tool(IntentType.TASK_CREATION, {})
    # Should return None since title is required for add_task
    assert tool_call is None

    # Test with minimal valid parameters
    tool_call = selector.select_tool(IntentType.TASK_LISTING, {})
    # Should work since list_tasks has no required parameters
    assert tool_call is not None
    assert tool_call["name"] == "list_tasks"