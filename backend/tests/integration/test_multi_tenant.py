import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.utils.jwt import create_access_token, JWTData
from src.database import get_session
from src.models.task_model import Task

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_multi_tenant_data_isolation_tasks():
    """Test that users can only access their own tasks"""
    # Create tokens for two different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # User1 creates a task
    task_data = {"title": "User1's task", "description": "A task for user1", "completed": False}
    response = client.post(
        "/api/user1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    task1_id = response.json()["id"]

    # User2 creates a task
    task_data = {"title": "User2's task", "description": "A task for user2", "completed": False}
    response = client.post(
        "/api/user2/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 200
    task2_id = response.json()["id"]

    # User1 should be able to access their own task
    response = client.get(
        f"/api/user1/tasks/{task1_id}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task1_id

    # User1 should NOT be able to access User2's task (even if they try to access it via their own endpoint)
    response = client.get(
        f"/api/user1/tasks/{task2_id}",  # Trying to access user2's task through user1's endpoint
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 404  # Should return 404, not 403, to avoid revealing existence of other user's tasks

    # User2 should be able to access their own task
    response = client.get(
        f"/api/user2/tasks/{task2_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task2_id

    # User2 should NOT be able to access User1's task
    response = client.get(
        f"/api/user2/tasks/{task1_id}",  # Trying to access user1's task through user2's endpoint
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 404  # Should return 404, not 403


def test_cross_user_access_prevention():
    """Test that users cannot access other users' data even with valid tokens"""
    # Create tokens for two different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # User1 creates a task
    task_data = {"title": "Private task", "description": "This is user1's private task", "completed": False}
    response = client.post(
        "/api/user1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    task_id = response.json()["id"]

    # User2 should not be able to access User1's tasks list
    response = client.get(
        "/api/user1/tasks",  # User2 trying to access User1's tasks
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403  # Should return 403 for cross-user access attempt

    # User2 should not be able to access User1's specific task
    response = client.get(
        f"/api/user1/tasks/{task_id}",  # User2 trying to access User1's specific task
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403  # Should return 403 for cross-user access attempt


def test_same_user_access_succeeds():
    """Test that a user can access their own data"""
    # Create token for a user
    user_token = create_test_token("same_user", "same@example.com")

    # User creates a task
    task_data = {"title": "My task", "description": "This is my task", "completed": False}
    response = client.post(
        "/api/same_user/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    task_id = response.json()["id"]

    # User should be able to access their own task list
    response = client.get(
        "/api/same_user/tasks",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # User should be able to access their own specific task
    response = client.get(
        f"/api/same_user/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_task_modification_isolation():
    """Test that users can only modify their own tasks"""
    # Create tokens for two different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # User1 creates a task
    task_data = {"title": "Original task", "description": "Original description", "completed": False}
    response = client.post(
        "/api/user1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    task_id = response.json()["id"]

    # User2 should not be able to update User1's task
    update_data = {"title": "Hacked task", "completed": True}
    response = client.put(
        f"/api/user1/tasks/{task_id}",  # User2 trying to update User1's task
        json=update_data,
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

    # User2 should not be able to delete User1's task
    response = client.delete(
        f"/api/user1/tasks/{task_id}",  # User2 trying to delete User1's task
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

    # Verify the original task is unchanged
    response = client.get(
        f"/api/user1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Original task"
    assert response.json()["completed"] is False