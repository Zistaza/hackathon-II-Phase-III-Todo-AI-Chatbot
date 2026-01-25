"""
Unit tests for the add_task MCP tool.
"""
import pytest
from unittest.mock import AsyncMock, patch
from src.api.mcp_tools.add_task import add_task


@pytest.mark.asyncio
async def test_add_task_success():
    """Test successful task creation."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.add_task.MultiTenantChecker') as mock_tenant, \
         patch('src.api.mcp_tools.add_task.TaskService') as mock_service:

        # Mock JWT validation
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        # Mock tenant checker
        mock_tenant.verify_user_access.return_value = True

        # Mock task service
        mock_task_instance = AsyncMock()
        mock_task_instance.id = "test-task-id"
        mock_task_instance.title = "Test Task"
        mock_task_instance.description = "Test Description"
        mock_task_instance.completed = False
        mock_task_instance.priority = 3
        mock_task_instance.created_at = "2023-01-01T00:00:00"

        mock_service.return_value.create_task.return_value = mock_task_instance

        # Call the function
        result = await add_task(
            title="Test Task",
            description="Test Description",
            priority=3,
            token="valid-token"
        )

        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["title"] == "Test Task"
        assert result["data"]["description"] == "Test Description"
        assert result["data"]["priority"] == 3


@pytest.mark.asyncio
async def test_add_task_invalid_token():
    """Test add_task with invalid token."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = None

        result = await add_task(
            title="Test Task",
            token="invalid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthenticationError"


@pytest.mark.asyncio
async def test_add_task_missing_title():
    """Test add_task with missing title."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await add_task(
            title="",  # Empty title
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"


@pytest.mark.asyncio
async def test_add_task_unauthorized_user():
    """Test add_task with unauthorized user."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt, \
         patch('src.api.mcp_tools.add_task.MultiTenantChecker') as mock_tenant:

        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}
        mock_tenant.verify_user_access.return_value = False

        result = await add_task(
            title="Test Task",
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "AuthorizationError"


@pytest.mark.asyncio
async def test_add_task_title_too_long():
    """Test add_task with title exceeding character limit."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        long_title = "x" * 201  # More than 200 characters

        result = await add_task(
            title=long_title,
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "200 characters" in result["error"]["message"]


@pytest.mark.asyncio
async def test_add_task_description_too_long():
    """Test add_task with description exceeding character limit."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        long_description = "x" * 1001  # More than 1000 characters

        result = await add_task(
            title="Test Task",
            description=long_description,
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "1000 characters" in result["error"]["message"]


@pytest.mark.asyncio
async def test_add_task_invalid_priority():
    """Test add_task with invalid priority."""
    with patch('src.api.mcp_tools.add_task.JWTValidator') as mock_jwt:
        mock_jwt.validate_token.return_value = {"user_id": "test-user-id"}

        result = await add_task(
            title="Test Task",
            priority=6,  # Higher than max of 5
            token="valid-token"
        )

        assert result["success"] is False
        assert result["error"]["type"] == "ValidationError"
        assert "between 1 and 5" in result["error"]["message"]