"""
Unit tests for the delete_task MCP tool.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.mcp_tools.delete_task import delete_task


@pytest.mark.asyncio
async def test_delete_task_success():
    """Test successful deletion of a task."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.delete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.delete_task.TaskService') as mock_service:

        # Mock JWT validation
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # Mock tenant checker
        mock_tenant.verify_user_access.return_value = True

        # Mock service to return True for successful deletion
        mock_service.return_value.delete_task.return_value = True

        # Call the function
        result = await delete_task(
            task_id="task-123",
            token="valid-token"
        )

        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["deleted"] is True
        assert result["data"]["task_id"] == "task-123"


@pytest.mark.asyncio
async def test_delete_task_invalid_token():
    """Test delete_task with invalid token."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = None

        result = await delete_task(
            task_id="task-123",
            token="invalid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthenticationError"


@pytest.mark.asyncio
async def test_delete_task_missing_task_id():
    """Test delete_task with missing task_id."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await delete_task(
            task_id="",  # Empty task_id
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "task_id is required" in result["error"]["message"]


@pytest.mark.asyncio
async def test_delete_task_invalid_task_id_format():
    """Test delete_task with invalid task_id format."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await delete_task(
            task_id="invalid-uuid-format",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "Invalid task_id format" in result["error"]["message"]


@pytest.mark.asyncio
async def test_delete_task_unauthorized_user():
    """Test delete_task with unauthorized user."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.delete_task.MultiTenantChecker') as mock_tenant:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = False

        result = await delete_task(
            task_id="task-123",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthorizationError"


@pytest.mark.asyncio
async def test_delete_task_not_found():
    """Test delete_task when task doesn't exist."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.delete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.delete_task.TaskService') as mock_service:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = True
        mock_service.return_value.delete_task.return_value = False  # Task not found/deletion failed

        result = await delete_task(
            task_id="non-existent-task",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "NotFoundError"
        assert "not found" in result["error"]["message"].lower()


@pytest.mark.asyncio
async def test_delete_task_internal_error():
    """Test delete_task with internal error."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.delete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.delete_task.TaskService') as mock_service:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = True
        mock_service.return_value.delete_task.side_effect = Exception("Database error")

        result = await delete_task(
            task_id="task-123",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "InternalError"


@pytest.mark.asyncio
async def test_delete_task_valid_uuid_format():
    """Test delete_task with valid UUID format."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.delete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.delete_task.TaskService') as mock_service:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = True
        mock_service.return_value.delete_task.return_value = True

        # Test with a properly formatted UUID
        result = await delete_task(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            token="valid-token"
        )

        assert result["success"] is True
        assert result["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_task_empty_string_task_id():
    """Test delete_task with empty string as task_id."""
    with patch('src.api.mcp_tools.delete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await delete_task(
            task_id="",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "task_id is required" in result["error"]["message"]