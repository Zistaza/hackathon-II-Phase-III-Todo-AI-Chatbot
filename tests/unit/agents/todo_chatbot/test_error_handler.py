"""
Unit tests for Error Handler
"""

import pytest
from backend.src.agents.todo_chatbot.error_handler import ErrorHandler


@pytest.fixture
def error_handler():
    """Create an instance of ErrorHandler for testing"""
    return ErrorHandler()


def test_handle_mcp_tool_error(error_handler):
    """Test handling of MCP tool errors"""
    tool_name = "add_task"
    error_message = "Task title is required"
    arguments = {"description": "test description"}

    result = error_handler.handle_mcp_tool_error(tool_name, error_message, arguments)

    assert "explanation" in result
    assert "recovery_suggestion" in result
    assert "add a task" in result["explanation"]


def test_handle_invalid_input(error_handler):
    """Test handling of invalid input"""
    user_input = "asdgf"
    error_details = "Input too short"

    result = error_handler.handle_invalid_input(user_input, error_details)

    assert "explanation" in result
    assert "guidance" in result


def test_handle_task_not_found(error_handler):
    """Test handling of task not found errors"""
    search_criteria = {"title": "nonexistent task"}

    result = error_handler.handle_task_not_found(search_criteria)

    assert "explanation" in result
    assert "alternatives" in result
    assert "nonexistent task" in result["explanation"]