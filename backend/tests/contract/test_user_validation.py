import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.jwt import create_access_token, JWTData

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_api_contract_user_id_matching():
    """
    Contract test to ensure API endpoints properly validate user_id matching
    between JWT claims and URL path parameters.
    """
    # Create tokens for different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # Test 1: Verify that endpoints reject requests where JWT user_id doesn't match URL user_id
    response = client.get(
        "/api/user2/tasks",  # Requesting user2's tasks
        headers={"Authorization": f"Bearer {user1_token}"}  # But using user1's token
    )
    assert response.status_code == 403, "Expected 403 when JWT user_id doesn't match URL user_id"

    # Test 2: Verify that endpoints accept requests where JWT user_id matches URL user_id
    response = client.get(
        "/api/user1/tasks",  # Requesting user1's tasks
        headers={"Authorization": f"Bearer {user1_token}"}  # Using user1's token
    )
    assert response.status_code == 200, "Expected 200 when JWT user_id matches URL user_id"

    # Test 3: Verify chat endpoint follows the same pattern
    response = client.post(
        "/api/user2/chat",  # Requesting user2's chat
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {user1_token}"}  # But using user1's token
    )
    assert response.status_code == 403, "Expected 403 when JWT user_id doesn't match URL user_id for chat"

    # Test 4: Verify chat endpoint accepts matching user_id
    response = client.post(
        "/api/user1/chat",  # Requesting user1's chat
        json={"content": "Hello", "role": "user"},
        headers={"Authorization": f"Bearer {user1_token}"}  # Using user1's token
    )
    # This might fail due to other validation, but shouldn't fail due to user_id mismatch
    assert response.status_code != 403, "Unexpected 403 when JWT user_id matches URL user_id for chat"

    # Test 5: Verify that unauthorized requests return 401
    response = client.get("/api/user1/tasks")  # No token provided
    assert response.status_code == 401, "Expected 401 when no token is provided"


def test_api_contract_error_responses():
    """
    Contract test to ensure API endpoints return consistent error responses
    for authentication and authorization failures.
    """
    # Test 401 Unauthorized responses
    response = client.get("/api/user1/tasks")  # No authorization header
    assert response.status_code == 401
    assert "detail" in response.json() or response.status_code == 401

    # Test 403 Forbidden responses (when token is valid but user lacks permission)
    user1_token = create_test_token("user1", "user1@example.com")
    response = client.get(
        "/api/user2/tasks",  # Trying to access user2's tasks
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403
    response_data = response.json()
    assert "detail" in response_data  # Should have a detail message


def test_api_contract_jwt_claim_validation():
    """
    Contract test to ensure API endpoints validate required JWT claims.
    """
    # Test with a malformed token (this would normally be tested with an invalid signature)
    response = client.get(
        "/api/user1/tasks",
        headers={"Authorization": "Bearer invalid.token.format"}
    )
    assert response.status_code in [401, 422], "Expected 401 for invalid token format"


def test_api_contract_user_id_format_validation():
    """
    Contract test to ensure API endpoints handle various user_id formats appropriately.
    """
    user_token = create_test_token("user-with_special.chars123", "user@example.com")

    # Test with special characters in user_id (should work if properly encoded)
    response = client.get(
        "/api/user-with_special.chars123/tasks",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # Should either succeed or fail for reasons other than user_id mismatch
    assert response.status_code != 403, "User ID format should not cause user_id mismatch errors"