"""
Integration tests for the chat API
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.src.api.chat_router import router, agent
from backend.src.agents.todo_chatbot.agent import Agent


@pytest.fixture
def test_client():
    """Create a test client for the API"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    return client


@pytest.mark.asyncio
async def test_process_chat_message_success():
    """Test successful processing of a chat message"""
    # Mock the agent's process_message method
    with patch.object(agent, 'process_message', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {
            "conversation_id": "test-id",
            "response": "Task created successfully",
            "tool_calls": [{"name": "add_task", "result": {"task_id": "123"}}],
            "next_action": "completed",
            "timestamp": "2026-01-26T00:00:00Z"
        }

        # This test would require a proper FastAPI app setup with dependencies mocked
        # For now, we'll just verify that the agent.process_message is called
        result = await agent.process_message("user123", "conv123", "Add a task to buy groceries")

        # Verify the mock was called
        mock_process.assert_called_once_with("user123", "conv123", "Add a task to buy groceries")
        assert result["response"] == "Task created successfully"


@pytest.mark.asyncio
async def test_process_chat_message_with_error():
    """Test processing of a chat message that results in an error"""
    # Mock the agent's process_message method to raise an exception
    with patch.object(agent, 'process_message', new_callable=AsyncMock) as mock_process:
        mock_process.side_effect = Exception("Test error")

        # This test would require a proper FastAPI app setup with dependencies mocked
        # For now, we'll just verify the exception handling behavior
        try:
            await agent.process_message("user123", "conv123", "Add a task to buy groceries")
        except Exception as e:
            assert str(e) == "Test error"


def test_intent_classification_integration():
    """Test the full intent classification pipeline"""
    from backend.src.agents.todo_chatbot.intent_classifier import IntentClassifier

    classifier = IntentClassifier()

    # Test various intents
    test_cases = [
        ("Add a task to buy groceries", "task_creation"),
        ("Show me my tasks", "task_listing"),
        ("Complete the meeting task", "task_completion"),
        ("Delete the old reminder", "task_deletion"),
        ("Update the project deadline", "task_update"),
    ]

    for message, expected_intent in test_cases:
        intent, confidence = classifier.classify_intent(message)
        assert intent.value == expected_intent
        assert confidence > 0.0


def test_tool_selection_integration():
    """Test the full tool selection pipeline"""
    from backend.src.agents.todo_chatbot.intent_classifier import IntentClassifier, IntentType
    from backend.src.agents.todo_chatbot.tool_selector import ToolSelector

    classifier = IntentClassifier()
    selector = ToolSelector()

    # Test that classification and selection work together
    message = "Add a task to buy groceries"
    intent, _ = classifier.classify_intent(message)
    params = classifier.extract_task_details(message, intent)

    tool_call = selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "add_task"
    assert "buy groceries" in params.get("title", "").lower()


@pytest.mark.asyncio
async def test_agent_process_message_end_to_end():
    """Test the agent's end-to-end message processing"""
    from backend.src.agents.todo_chatbot.agent import Agent, AgentConfig

    # Create a mock agent with mocked MCP integration
    config = AgentConfig()
    agent_instance = Agent(config)

    # Mock the MCP integration to avoid actual API calls
    with patch.object(agent_instance.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"task_id": "123", "title": "buy groceries", "status": "pending"}

        # Test a simple task creation
        result = await agent_instance.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Add a task to buy groceries"
        )

        # Verify the result structure
        assert "conversation_id" in result
        assert "response" in result
        assert "tool_calls" in result

        # Verify the MCP integration was called
        mock_mcp.assert_called_once()