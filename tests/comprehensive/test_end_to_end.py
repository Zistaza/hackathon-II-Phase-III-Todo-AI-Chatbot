"""
End-to-end tests for all user stories
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.src.agents.todo_chatbot.agent import Agent, AgentConfig


@pytest.mark.asyncio
async def test_end_to_end_user_story_1_correct_tool_selection():
    """Test complete User Story 1: Correct Tool Selection"""
    config = AgentConfig()
    agent = Agent(config)

    # Test task creation
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"task_id": "123", "title": "buy groceries", "status": "pending"}

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Add a task to buy groceries"
        )

        # Verify correct tool was called
        assert mock_mcp.called
        args, kwargs = mock_mcp.call_args
        assert args[0] == "add_task"  # Correct tool selected
        assert result["response"] != ""  # Got a response


@pytest.mark.asyncio
async def test_end_to_end_user_story_2_multi_step_reasoning():
    """Test complete User Story 2: Multi-Step Reasoning"""
    config = AgentConfig()
    agent = Agent(config)

    # Test ambiguous request that triggers multi-step flow
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        # First call: list_tasks (discovery step)
        # Second call: complete_task (action step)
        mock_mcp.side_effect = [
            {"tasks": [{"id": "1", "title": "meeting with John", "status": "pending"}]},  # list_tasks result
            {"task_id": "1", "status": "completed"}  # complete_task result
        ]

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Complete the meeting task"
        )

        # Should have made multiple tool calls
        assert mock_mcp.call_count >= 2
        first_call = mock_mcp.call_args_list[0]
        assert first_call[0][0] == "list_tasks"  # Discovery step
        second_call = mock_mcp.call_args_list[1]
        assert second_call[0][0] in ["complete_task", "add_task", "delete_task", "update_task", "list_tasks"]


@pytest.mark.asyncio
async def test_end_to_end_user_story_3_error_handling():
    """Test complete User Story 3: Error & Confirmation Handling"""
    config = AgentConfig()
    agent = Agent(config)

    # Test error handling
    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        mock_mcp.return_value = {"error": "Task not found", "degraded": True}

        result = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Complete task 999"
        )

        # Verify error was handled gracefully
        assert "error" in result["response"].lower() or "couldn't" in result["response"].lower()


@pytest.mark.asyncio
async def test_end_to_end_complete_workflow():
    """Test a complete workflow spanning multiple user stories"""
    config = AgentConfig()
    agent = Agent(config)

    with patch.object(agent.mcp_integration, 'execute_tool_call', new_callable=AsyncMock) as mock_mcp:
        # Simulate a sequence of operations
        mock_mcp.side_effect = [
            {"task_id": "1", "title": "grocery shopping", "status": "pending"},  # add_task
            {"tasks": [{"id": "1", "title": "grocery shopping", "status": "pending"}]},  # list_tasks
            {"task_id": "1", "status": "completed"}  # complete_task
        ]

        # Step 1: Add a task
        result1 = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Add a task to go grocery shopping"
        )

        # Step 2: List tasks
        result2 = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Show me my tasks"
        )

        # Step 3: Complete the task
        result3 = await agent.process_message(
            user_id="user123",
            conversation_id="conv123",
            message="Complete the grocery shopping task"
        )

        # Verify all steps worked
        assert "grocery" in result1["response"].lower() or "add" in result1["response"].lower()
        assert "tasks" in result2["response"].lower() or "show" in result2["response"].lower()
        assert "complete" in result3["response"].lower() or "done" in result3["response"].lower()


def test_agent_configuration_options():
    """Test that agent configuration options work properly"""
    config = AgentConfig()
    config.intent_confidence_threshold = 0.5
    config.enable_logging = True

    agent = Agent(config)

    # Verify configuration was applied
    assert agent.config.intent_confidence_threshold == 0.5
    assert agent.config.enable_logging is True