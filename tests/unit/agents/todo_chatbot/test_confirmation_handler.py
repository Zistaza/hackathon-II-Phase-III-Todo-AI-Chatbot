"""
Unit tests for Confirmation Handler
"""

import pytest
from backend.src.agents.todo_chatbot.confirmation_handler import ConfirmationHandler


@pytest.fixture
def confirmation_handler():
    """Create an instance of ConfirmationHandler for testing"""
    return ConfirmationHandler()


def test_generate_success_confirmation(confirmation_handler):
    """Test generation of success confirmations"""
    tool_name = "add_task"
    result = {"title": "Buy groceries", "task_id": "12345"}
    original_args = {"title": "Buy groceries"}

    confirmation = confirmation_handler.generate_success_confirmation(tool_name, result, original_args)

    assert "Buy groceries" in confirmation
    assert "add" in confirmation or "created" in confirmation


def test_generate_error_explanation(confirmation_handler):
    """Test generation of error explanations"""
    error_type = "tool_failure"
    error_details = {
        "tool_name": "delete_task",
        "error_message": "Task not found"
    }

    explanation = confirmation_handler.generate_error_explanation(error_type, error_details)

    assert "delete" in explanation or "task" in explanation
    assert "not found" in explanation


def test_generate_confirmation_request(confirmation_handler):
    """Test generation of confirmation requests"""
    action = "delete"
    target = "grocery list"

    confirmation_request = confirmation_handler.generate_confirmation_request(action, target)

    assert "delete" in confirmation_request
    assert "grocery list" in confirmation_request
    assert "confirm" in confirmation_request.lower() or "sure" in confirmation_request.lower()


def test_generate_operation_summary(confirmation_handler):
    """Test generation of operation summaries"""
    tool_calls = [
        {"name": "add_task", "arguments": {"title": "task1"}},
        {"name": "list_tasks", "arguments": {}}
    ]
    results = [
        {"task_id": "1", "title": "task1"},
        {"tasks": []}
    ]

    summary = confirmation_handler.generate_operation_summary(tool_calls, results)

    assert "operations" in summary.lower()