import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.utils.jwt import create_access_token, JWTData

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_full_mcp_tool_workflow():
    """Test the complete MCP tool workflow: register, execute, validate, unregister"""
    # Create tokens for different users
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # Step 1: Register a tool for user1
    tool_data = {
        "tool_id": "integration_test_tool",
        "name": "Integration Test Tool",
        "description": "A tool for integration testing",
        "allowed_resources": ["file", "code"]
    }

    response = client.post(
        "/api/mcp/register",
        json=tool_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    registered_tool = response.json()
    assert registered_tool["name"] == "Integration Test Tool"
    assert registered_tool["user_id"] == "user1"

    # Step 2: Validate that the tool was registered for user1
    response = client.get(
        "/api/mcp/validate/integration_test_tool",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200

    # Step 3: User2 should not be able to validate user1's tool
    response = client.get(
        "/api/mcp/validate/integration_test_tool",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 404  # Should return 404, not 403, to avoid information disclosure

    # Step 4: Execute a tool request for user1's tool
    mcp_request = {
        "tool_id": "integration_test_tool",
        "user_id": "user1",
        "action": "test_action",
        "resources": [{
            "resource_id": "test_resource",
            "resource_type": "file",
            "owner_id": "user1",
            "permissions": ["read_only"]
        }],
        "parameters": {"param1": "value1"}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    # Should succeed or return a structured response
    assert response.status_code in [200, 400]  # 400 might be returned for invalid parameters

    # Step 5: User2 should not be able to execute user1's tool on user2's behalf
    response = client.post(
        "/api/mcp/execute",
        json={
            "tool_id": "integration_test_tool",
            "user_id": "user2",  # User2 trying to use user1's tool for user2
            "action": "test_action",
            "resources": [{
                "resource_id": "test_resource",
                "resource_type": "file",
                "owner_id": "user2",
                "permissions": ["read_only"]
            }],
            "parameters": {"param1": "value1"}
        },
        headers={"Authorization": f"Bearer {user1_token}"}  # Using user1's token
    )
    assert response.status_code == 403  # Should fail because tool_id doesn't match user_id context

    # Step 6: User2 should not be able to execute user1's tool at all
    response = client.post(
        "/api/mcp/execute",
        json={
            "tool_id": "integration_test_tool",
            "user_id": "user1",  # Trying to use user1's tool for user1
            "action": "test_action",
            "resources": [{
                "resource_id": "test_resource",
                "resource_type": "file",
                "owner_id": "user1",
                "permissions": ["read_only"]
            }],
            "parameters": {"param1": "value1"}
        },
        headers={"Authorization": f"Bearer {user2_token}"}  # Using user2's token
    )
    assert response.status_code == 403  # Should fail because user2 doesn't own the tool

    # Step 7: List user1's tools
    response = client.get(
        "/api/mcp/my-tools",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200
    user1_tools = response.json()
    assert len([t for t in user1_tools if t["tool_id"] == "integration_test_tool"]) == 1

    # Step 8: User2 should not see user1's tools
    response = client.get(
        "/api/mcp/my-tools",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == 200
    user2_tools = response.json()
    assert len([t for t in user2_tools if t["tool_id"] == "integration_test_tool"]) == 0

    # Step 9: Unregister the tool
    response = client.delete(
        "/api/mcp/unregister/integration_test_tool",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200


def test_mcp_tool_resource_access_isolation():
    """Test that MCP tools enforce proper resource access isolation"""
    user1_token = create_test_token("user1", "user1@example.com")
    user2_token = create_test_token("user2", "user2@example.com")

    # Register a tool for user1
    tool_data = {
        "tool_id": "isolation_test_tool",
        "name": "Isolation Test Tool",
        "description": "A tool for testing resource isolation"
    }

    response = client.post(
        "/api/mcp/register",
        json=tool_data,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 200

    # User1 should be able to access their own resources
    mcp_request = {
        "tool_id": "isolation_test_tool",
        "user_id": "user1",
        "action": "read",
        "resources": [{
            "resource_id": "user1_resource",
            "resource_type": "file",
            "owner_id": "user1",  # User1 accessing their own resource
            "permissions": ["read_only"]
        }],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    # Should succeed or return a structured response
    assert response.status_code in [200, 400]

    # User1 should NOT be able to access user2's resources
    mcp_request = {
        "tool_id": "isolation_test_tool",
        "user_id": "user1",
        "action": "read",
        "resources": [{
            "resource_id": "user2_resource",
            "resource_type": "file",
            "owner_id": "user2",  # User1 trying to access user2's resource
            "permissions": ["read_only"]
        }],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403


def test_mcp_tool_execution_with_invalid_tokens():
    """Test MCP tool execution with invalid or expired tokens"""
    # Test with malformed token
    mcp_request = {
        "tool_id": "any_tool",
        "user_id": "any_user",
        "action": "any_action",
        "resources": [],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": "Bearer invalid.token.format"}
    )
    assert response.status_code == 401

    # Test without token
    response = client.post("/api/mcp/execute", json=mcp_request)
    assert response.status_code == 401