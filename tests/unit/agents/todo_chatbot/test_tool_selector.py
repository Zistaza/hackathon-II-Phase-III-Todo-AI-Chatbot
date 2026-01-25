"""
Unit tests for Tool Selector
"""

import pytest
from backend.src.agents.todo_chatbot.tool_selector import ToolSelector
from backend.src.agents.todo_chatbot.intent_classifier import IntentType


@pytest.fixture
def tool_selector():
    """Create an instance of ToolSelector for testing"""
    return ToolSelector()


def test_select_add_task(tool_selector):
    """Test selection of add_task tool"""
    intent = IntentType.TASK_CREATION
    params = {"title": "Buy groceries", "description": "Get milk and bread"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "add_task"
    assert tool_call["arguments"]["title"] == "Buy groceries"
    assert tool_call["arguments"]["description"] == "Get milk and bread"


def test_select_list_tasks(tool_selector):
    """Test selection of list_tasks tool"""
    intent = IntentType.TASK_LISTING
    params = {"status_filter": "pending", "limit": 5}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "list_tasks"
    assert tool_call["arguments"]["status_filter"] == "pending"
    assert tool_call["arguments"]["limit"] == 5


def test_select_complete_task(tool_selector):
    """Test selection of complete_task tool"""
    intent = IntentType.TASK_COMPLETION
    params = {"task_id": "12345"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "complete_task"
    assert tool_call["arguments"]["task_id"] == "12345"


def test_select_delete_task(tool_selector):
    """Test selection of delete_task tool"""
    intent = IntentType.TASK_DELETION
    params = {"task_reference": "grocery list"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "delete_task"
    assert tool_call["arguments"]["task_reference"] == "grocery list"


def test_select_update_task(tool_selector):
    """Test selection of update_task tool"""
    intent = IntentType.TASK_UPDATE
    params = {"task_id": "12345", "title": "Updated title", "description": "Updated description"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is not None
    assert tool_call["name"] == "update_task"
    assert tool_call["arguments"]["task_id"] == "12345"
    assert tool_call["arguments"]["title"] == "Updated title"
    assert tool_call["arguments"]["description"] == "Updated description"


def test_invalid_add_task_without_title(tool_selector):
    """Test that add_task tool is not selected without required title"""
    intent = IntentType.TASK_CREATION
    params = {"description": "Just a description without title"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is None


def test_invalid_complete_task_without_id(tool_selector):
    """Test that complete_task tool is not selected without required id"""
    intent = IntentType.TASK_COMPLETION
    params = {"description": "Trying to complete without ID"}

    tool_call = tool_selector.select_tool(intent, params)

    assert tool_call is None


def test_handle_ambiguous_request(tool_selector):
    """Test handling of ambiguous requests"""
    intent = IntentType.TASK_COMPLETION
    params = {"task_reference": "it"}

    tool_calls = tool_selector.handle_ambiguous_request(intent, params)

    # Should return list_tasks first, then the original intent
    assert len(tool_calls) == 2
    assert tool_calls[0]["name"] == "list_tasks"
    assert tool_calls[1]["name"] == "complete_task"


def test_prioritize_tools(tool_selector):
    """Test prioritization of tools"""
    possible_tools = [
        {"name": "complete_task", "arguments": {"task_id": "123"}},
        {"name": "list_tasks", "arguments": {"status_filter": "all"}},
        {"name": "add_task", "arguments": {"title": "new task"}}
    ]

    prioritized = tool_selector.prioritize_tools(possible_tools)

    # list_tasks should come first
    assert prioritized[0]["name"] == "list_tasks"
    assert prioritized[1]["name"] == "complete_task"
    assert prioritized[2]["name"] == "add_task"