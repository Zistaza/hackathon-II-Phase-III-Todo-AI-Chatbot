import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.utils.jwt import create_access_token, JWTData
from src.models.mcp_tool import MCPToolRequest, MCPToolResource, MCPToolAccessType

client = TestClient(app)


def create_test_token(user_id: str = "test_user", email: str = "test@example.com"):
    """Helper function to create a valid test JWT token"""
    jwt_data = JWTData(user_id=user_id, email=email)
    return create_access_token(data=jwt_data)


def test_mcp_tool_execution_requires_authentication():
    """Test that MCP tool execution requires valid authentication"""
    # Test without token
    mcp_request = {
        "tool_id": "test_tool",
        "user_id": "test_user",
        "action": "execute",
        "resources": [],
        "parameters": {}
    }

    response = client.post("/api/mcp/execute", json=mcp_request)
    assert response.status_code == 401

    # Test with valid token
    token = create_test_token("test_user")
    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should succeed or fail for other reasons, but not for auth
    assert response.status_code != 401


def test_mcp_tool_user_id_matching():
    """Test that MCP tools validate user_id matching between request and JWT"""
    # Create token for user1
    token_for_user1 = create_test_token("user1", "user1@example.com")

    # Try to execute tool for user2 with token for user1 (should fail)
    mcp_request = {
        "tool_id": "test_tool",
        "user_id": "user2",  # Different user than token
        "action": "execute",
        "resources": [],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {token_for_user1}"}
    )
    assert response.status_code == 403


def test_mcp_tool_resource_access_control():
    """Test that MCP tools validate resource access permissions"""
    # Create token for user1
    token_for_user1 = create_test_token("user1", "user1@example.com")

    # Create MCP request with resource owned by user2
    mcp_request = {
        "tool_id": "test_tool",
        "user_id": "user1",
        "action": "read",
        "resources": [{
            "resource_id": "resource1",
            "resource_type": "file",
            "owner_id": "user2",  # Owned by different user
            "permissions": ["read_only"]
        }],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {token_for_user1}"}
    )
    assert response.status_code == 403


def test_mcp_tool_valid_resource_access():
    """Test that MCP tools allow access to user's own resources"""
    # Create token for user1
    token_for_user1 = create_test_token("user1", "user1@example.com")

    # Create MCP request with resource owned by user1
    mcp_request = {
        "tool_id": "test_tool",
        "user_id": "user1",
        "action": "read",
        "resources": [{
            "resource_id": "resource1",
            "resource_type": "file",
            "owner_id": "user1",  # Owned by same user
            "permissions": ["read_only"]
        }],
        "parameters": {}
    }

    response = client.post(
        "/api/mcp/execute",
        json=mcp_request,
        headers={"Authorization": f"Bearer {token_for_user1}"}
    )
    # Should succeed or fail for other reasons, but not for access control
    assert response.status_code != 403


def test_mcp_tool_registration():
    """Test MCP tool registration endpoint"""
    # Test without token
    tool_data = {
        "tool_id": "new_tool",
        "name": "New Tool",
        "description": "A new MCP tool"
    }

    response = client.post("/api/mcp/register", json=tool_data)
    assert response.status_code == 401

    # Test with valid token
    token = create_test_token("test_user")
    response = client.post(
        "/api/mcp/register",
        json=tool_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should succeed or fail for other reasons, but not for auth
    assert response.status_code != 401


def test_mcp_tool_list_my_tools():
    """Test listing user's MCP tools"""
    # Test without token
    response = client.get("/api/mcp/my-tools")
    assert response.status_code == 401

    # Test with valid token
    token = create_test_token("test_user")
    response = client.get(
        "/api/mcp/my-tools",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_mcp_tool_validation():
    """Test MCP tool validation endpoint"""
    # Test without token
    response = client.get("/api/mcp/validate/nonexistent_tool")
    assert response.status_code == 401

    # Test with valid token
    token = create_test_token("test_user")
    response = client.get(
        "/api/mcp/validate/nonexistent_tool",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should return 404 if tool doesn't exist, but not 401 for auth
    assert response.status_code != 401


def test_mcp_tool_unregistration():
    """Test MCP tool unregistration endpoint"""
    # Test without token
    response = client.delete("/api/mcp/unregister/test_tool")
    assert response.status_code == 401

    # Test with valid token
    token = create_test_token("test_user")
    response = client.delete(
        "/api/mcp/unregister/test_tool",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should return 404 if tool doesn't exist, but not 401 for auth
    assert response.status_code != 401