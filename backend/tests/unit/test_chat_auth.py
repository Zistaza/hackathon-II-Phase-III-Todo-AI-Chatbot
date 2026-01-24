import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.utils.jwt import create_access_token, JWTData
from src.models.chat import ChatMessage, ChatRole

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_chat_endpoint_requires_authentication():
    """Test that chat endpoint requires valid authentication token"""
    # Test without token
    response = client.post("/api/test_user/chat", json={"content": "Hello", "role": "user"})
    assert response.status_code == 401

    # Test with valid token but wrong user_id
    token = create_test_token("actual_user")
    response = client.post(
        "/api/wrong_user/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

    # Test with valid token and matching user_id
    token = create_test_token("test_user")
    response = client.post(
        "/api/test_user/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_chat_message_structure():
    """Test that chat messages are properly structured"""
    token = create_test_token("test_user")

    # Test valid message
    valid_message = {
        "content": "Hello, this is a test message",
        "role": "user"
    }

    response = client.post(
        "/api/test_user/chat",
        json=valid_message,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Check response structure
    data = response.json()
    assert "response" in data
    assert "message_id" in data
    assert "timestamp" in data
    assert "conversation_id" in data


def test_chat_endpoint_user_id_matching():
    """Test that user_id in path matches user_id in JWT token"""
    # Create token for user1
    token_for_user1 = create_test_token("user1", "user1@example.com")

    # Try to access user2's chat with token for user1 (should fail)
    response = client.post(
        "/api/user2/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {token_for_user1}"}
    )
    assert response.status_code == 403

    # Try to access user1's chat with token for user1 (should succeed)
    response = client.post(
        "/api/user1/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {token_for_user1}"}
    )
    assert response.status_code == 200


def test_get_chat_history_requires_authentication():
    """Test that getting chat history requires authentication"""
    # Test without token
    response = client.get("/api/test_user/chat/history")
    assert response.status_code == 401

    # Test with valid token but wrong user_id
    token = create_test_token("actual_user")
    response = client.get(
        "/api/wrong_user/chat/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

    # Test with valid token and matching user_id
    token = create_test_token("test_user")
    response = client.get(
        "/api/test_user/chat/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_delete_conversation_requires_authentication():
    """Test that deleting conversation requires authentication"""
    # Test without token
    response = client.delete("/api/test_user/chat/conversation/test_conv")
    assert response.status_code == 401

    # Test with valid token but wrong user_id
    token = create_test_token("actual_user")
    response = client.delete(
        "/api/wrong_user/chat/conversation/test_conv",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

    # Test with valid token and matching user_id
    token = create_test_token("test_user")
    response = client.delete(
        "/api/test_user/chat/conversation/test_conv",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200