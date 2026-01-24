import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.jwt import create_access_token, JWTData

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_complete_authentication_flow():
    """Test the complete authentication flow across different endpoints"""
    # Create tokens for different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # Test 1: User1 can access their own resources
    response = client.get(
        "/api/user1/tasks",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200

    # Test 2: User1 cannot access User2's resources
    response = client.get(
        "/api/user2/tasks",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403

    # Test 3: User2 can access their own resources
    response = client.get(
        "/api/user2/tasks",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 200

    # Test 4: User2 cannot access User1's resources
    response = client.get(
        "/api/user1/tasks",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

    # Test 5: Chat endpoints follow the same pattern
    response = client.post(
        "/api/user1/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200

    # Test 6: User2 cannot access User1's chat
    response = client.post(
        "/api/user1/chat",
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 403

    # Test 7: Unauthenticated requests fail
    response = client.get("/api/user1/tasks")
    assert response.status_code == 401

    # Test 8: Health check endpoint works without authentication
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Test 9: Auth health check endpoint works without authentication
    response = client.get("/auth-health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["features"]["jwt"] == "enabled"


def test_token_validation_across_endpoints():
    """Test that token validation works consistently across all endpoints"""
    # Create a valid token
    valid_token = create_test_token("test_user", "test@example.com")

    # Test various endpoints with valid token
    endpoints_to_test = [
        ("/api/test_user/tasks", "GET"),
        ("/api/test_user/tasks", "POST", {"title": "Test", "description": "Desc", "completed": False}),
        ("/api/test_user/chat", "POST", {"content": "Hi", "role": "user"}),
        ("/api/test_user/chat/history", "GET"),
    ]

    for endpoint_data in endpoints_to_test:
        if len(endpoint_data) == 2:
            url, method = endpoint_data
            response = client.request(method, url, headers={"Authorization": f"Bearer {valid_token}"})
        else:
            url, method, payload = endpoint_data
            response = client.request(method, url, json=payload, headers={"Authorization": f"Bearer {valid_token}"})

        # All should succeed (200) or have other valid responses (not 401/403 due to auth)
        assert response.status_code != 401, f"Unexpected 401 for {method} {url}"

    # Test all endpoints with no token (should return 401)
    for endpoint_data in endpoints_to_test:
        if len(endpoint_data) == 2:
            url, method = endpoint_data
            response = client.request(method, url)
        else:
            url, method, payload = endpoint_data
            response = client.request(method, url, json=payload)

        assert response.status_code == 401, f"Expected 401 for {method} {url} without token"


def test_cross_component_authentication_consistency():
    """Test that authentication works consistently across different components"""
    user_token = create_test_token("consistent_user", "consistent@example.com")

    # Test tasks API
    response = client.get("/api/consistent_user/tasks", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

    # Test chat API
    response = client.post(
        "/api/consistent_user/chat",
        json={"content": "Test message", "role": "user"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200

    # Test MCP tools API
    response = client.get("/api/mcp/my-tools", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

    # Test with wrong user ID (should fail across all)
    wrong_endpoints = [
        ("/api/wrong_user/tasks", "GET"),
        ("/api/wrong_user/chat", "POST", {"content": "Test", "role": "user"}),
        ("/api/wrong_user/chat/history", "GET"),
    ]

    for endpoint_data in wrong_endpoints:
        if len(endpoint_data) == 2:
            url, method = endpoint_data
            response = client.request(method, url, headers={"Authorization": f"Bearer {user_token}"})
        else:
            url, method, payload = endpoint_data
            response = client.request(method, url, json=payload, headers={"Authorization": f"Bearer {user_token}"})

        assert response.status_code == 403, f"Expected 403 for {method} {url} with mismatched user ID"