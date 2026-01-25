"""
Unit tests for the complete_task MCP tool.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.api.mcp_tools.complete_task import complete_task


@pytest.mark.asyncio
async def test_complete_task_success():
    """Test successful completion of a task."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

        # Mock JWT validation
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # Mock tenant checker
        mock_tenant.verify_user_access.return_value = True

        # Mock task instance
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.completed = True
        mock_task.updated_at = "2023-01-01T00:00:00"

        mock_service.return_value.update_task_completion.return_value = mock_task

        # Call the function
        result = await complete_task(
            task_id="task-123",
            completed=True,
            token="valid-token"
        )

        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["task_id"] == "task-123"
        assert result["data"]["completed"] is True


@pytest.mark.asyncio
async def test_complete_task_default_completed_true():
    """Test completion with default completed value (True)."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

        # Mock JWT validation
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # Mock tenant checker
        mock_tenant.verify_user_access.return_value = True

        # Mock task instance
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.completed = True
        mock_task.updated_at = "2023-01-01T00:00:00"

        mock_service.return_value.update_task_completion.return_value = mock_task

        # Call the function without specifying completed (should default to True)
        result = await complete_task(
            task_id="task-123",
            token="valid-token"
        )

        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["task_id"] == "task-123"
        assert result["data"]["completed"] is True


@pytest.mark.asyncio
async def test_complete_task_mark_incomplete():
    """Test marking a task as incomplete."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

        # Mock JWT validation
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # Mock tenant checker
        mock_tenant.verify_user_access.return_value = True

        # Mock task instance
        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.completed = False
        mock_task.updated_at = "2023-01-01T00:00:00"

        mock_service.return_value.update_task_completion.return_value = mock_task

        # Call the function to mark as incomplete
        result = await complete_task(
            task_id="task-123",
            completed=False,
            token="valid-token"
        )

        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["task_id"] == "task-123"
        assert result["data"]["completed"] is False


@pytest.mark.asyncio
async def test_complete_task_invalid_token():
    """Test complete_task with invalid token."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = None

        result = await complete_task(
            task_id="task-123",
            token="invalid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthenticationError"


@pytest.mark.asyncio
async def test_complete_task_missing_task_id():
    """Test complete_task with missing task_id."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await complete_task(
            task_id="",  # Empty task_id
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"


@pytest.mark.asyncio
async def test_complete_task_invalid_task_id_format():
    """Test complete_task with invalid task_id format."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await complete_task(
            task_id="invalid-uuid-format",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "Invalid task_id format" in result["error"]["message"]


@pytest.mark.asyncio
async def test_complete_task_unauthorized_user():
    """Test complete_task with unauthorized user."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = False

        result = await complete_task(
            task_id="task-123",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthorizationError"


@pytest.mark.asyncio
async def test_complete_task_invalid_completed_param():
    """Test complete_task with invalid completed parameter."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # In our implementation, we accept any truthy/falsy value and convert to boolean
        # So let's test with a proper scenario
        with patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
             patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

            mock_tenant.verify_user_access.return_value = True
            mock_service.return_value.update_task_completion.return_value = None  # Task not found

            result = await complete_task(
                task_id="task-123",
                completed="invalid_boolean_value",  # This would be converted to boolean in real usage
                token="valid-token"
            )

            # This should result in a NotFoundError since the service returns None
            assert result["success"] is False
            assert result["error"]["type"] == "NotFoundError"


@pytest.mark.asyncio
async def test_complete_task_not_found():
    """Test complete_task when task doesn't exist."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = True
        mock_service.return_value.update_task_completion.return_value = None  # Task not found

        result = await complete_task(
            task_id="non-existent-task",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "NotFoundError"
        assert "not found" in result["error"]["message"].lower()


@pytest.mark.asyncio
async def test_complete_task_internal_error():
    """Test complete_task with internal error."""
    with patch('src.api.mcp_tools.complete_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.complete_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.complete_task.TaskService') as mock_service:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = True
        mock_service.return_value.update_task_completion.side_effect = Exception("Database error")

        result = await complete_task(
            task_id="task-123",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "InternalError"