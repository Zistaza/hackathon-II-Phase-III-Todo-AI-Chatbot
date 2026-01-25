"""
Integration tests for the chat endpoint to validate User Story 1 acceptance scenarios.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlmodel import Session

from src.main import app
from src.database import engine
from src.models.user import CurrentUser
from src.dependencies.auth import get_current_user


@pytest.fixture
def client():
    """Create a test client with mocked authentication."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    return CurrentUser(
        user_id="test_user_123",
        email="test@example.com",
        is_authenticated=True
    )


@pytest.fixture
def setup_mock_auth(mock_user):
    """Setup mock authentication dependency."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_story_1_scenario_1_create_todo(setup_mock_auth, client):
    """
    Test User Story 1 acceptance scenario 1: "Create a todo: Buy groceries"

    Given I am an authenticated user with a valid JWT,
    When I send a message "Create a todo: Buy groceries" to the chat endpoint,
    Then the AI assistant should respond acknowledging the task creation and the todo should be created in my list.
    """
    # Mock the agent's response for creating a task
    mock_agent_response = {
        "conversation_id": 1,
        "response": "I've created the task: 'Buy groceries'",
        "tool_calls": [{
            "id": "call_1",
            "name": "add_task",
            "arguments": {"title": "Buy groceries"},
            "status": "success",
            "result": {"task_id": "task_123", "title": "Buy groceries", "completed": False}
        }]
    }

    # Mock the agent's process_message method
    with patch('src.services.stateless_chat_service.StatelessChatService.process_chat_request') as mock_process:
        mock_process.return_value = mock_agent_response

        # Send the request to the chat endpoint
        response = client.post(
            "/api/test_user_123/chat",
            json={"message": "Create a todo: Buy groceries", "conversation_id": 1},
            headers={"Authorization": "Bearer fake-jwt-token"}
        )

        # Assert the response
        assert response.status_code == 200
        response_data = response.json()
        assert "Buy groceries" in response_data["response"]
        assert response_data["conversation_id"] == 1
        assert len(response_data["tool_calls"]) == 1
        assert response_data["tool_calls"][0]["tool_name"] == "add_task"


@pytest.mark.asyncio
async def test_user_story_1_scenario_2_query_pending_tasks(setup_mock_auth, client):
    """
    Test User Story 1 acceptance scenario 2: "What are my pending tasks?"

    Given I have existing todos in my list,
    When I ask "What are my pending tasks?",
    Then the AI assistant should return a list of my uncompleted todos.
    """
    # Mock the agent's response for listing tasks
    mock_agent_response = {
        "conversation_id": 1,
        "response": "You have 2 pending tasks: 'Buy groceries', 'Walk the dog'",
        "tool_calls": [{
            "id": "call_1",
            "name": "list_tasks",
            "arguments": {"status_filter": "pending"},
            "status": "success",
            "result": {
                "tasks": [
                    {"id": "task_123", "title": "Buy groceries", "completed": False},
                    {"id": "task_124", "title": "Walk the dog", "completed": False}
                ]
            }
        }]
    }

    # Mock the agent's process_message method
    with patch('src.services.stateless_chat_service.StatelessChatService.process_chat_request') as mock_process:
        mock_process.return_value = mock_agent_response

        # Send the request to the chat endpoint
        response = client.post(
            "/api/test_user_123/chat",
            json={"message": "What are my pending tasks?", "conversation_id": 1},
            headers={"Authorization": "Bearer fake-jwt-token"}
        )

        # Assert the response
        assert response.status_code == 200
        response_data = response.json()
        assert "pending tasks" in response_data["response"]
        assert "Buy groceries" in response_data["response"]
        assert "Walk the dog" in response_data["response"]
        assert response_data["conversation_id"] == 1
        assert len(response_data["tool_calls"]) == 1
        assert response_data["tool_calls"][0]["tool_name"] == "list_tasks"


@pytest.mark.asyncio
async def test_user_story_1_scenario_3_complete_task(setup_mock_auth, client):
    """
    Test User Story 1 acceptance scenario 3: "Complete the grocery shopping task"

    Given I have a todo with ID 123,
    When I say "Complete the grocery shopping task",
    Then the AI assistant should mark the task as completed and confirm the action.
    """
    # Mock the agent's response for completing a task
    mock_agent_response = {
        "conversation_id": 1,
        "response": "I've marked the task 'Buy groceries' as completed.",
        "tool_calls": [{
            "id": "call_1",
            "name": "complete_task",
            "arguments": {"task_id": "task_123"},
            "status": "success",
            "result": {"task_id": "task_123", "title": "Buy groceries", "completed": True}
        }]
    }

    # Mock the agent's process_message method
    with patch('src.services.stateless_chat_service.StatelessChatService.process_chat_request') as mock_process:
        mock_process.return_value = mock_agent_response

        # Send the request to the chat endpoint
        response = client.post(
            "/api/test_user_123/chat",
            json={"message": "Complete the grocery shopping task", "conversation_id": 1},
            headers={"Authorization": "Bearer fake-jwt-token"}
        )

        # Assert the response
        assert response.status_code == 200
        response_data = response.json()
        assert "completed" in response_data["response"]
        assert "Buy groceries" in response_data["response"]
        assert response_data["conversation_id"] == 1
        assert len(response_data["tool_calls"]) == 1
        assert response_data["tool_calls"][0]["tool_name"] == "complete_task"


def test_jwt_validation_user_id_mismatch(client):
    """
    Test that JWT validation properly enforces user_id matching.
    """
    # Create a mock user with different ID than what's in the URL
    different_user = CurrentUser(
        user_id="different_user_456",
        email="different@example.com",
        is_authenticated=True
    )

    # Override the auth dependency
    app.dependency_overrides[get_current_user] = lambda: different_user

    try:
        # Send a request with mismatched user_id
        response = client.post(
            "/api/test_user_123/chat",  # URL has test_user_123
            json={"message": "Hello", "conversation_id": 1},
            headers={"Authorization": "Bearer fake-jwt-token"}
        )

        # Should return 403 Forbidden due to user_id mismatch
        assert response.status_code == 403
    finally:
        # Clean up the dependency override
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__])