"""
MCP Tool for deleting a task from a user's todo list.
"""
from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session
from src.models.task_model import Task
from src.services.task_service import TaskService
from src.utils.jwt_validator import JWTValidator
from src.utils.multi_tenant_checker import MultiTenantChecker


async def delete_task(
    task_id: str,
    token: str = None
) -> Dict[str, Any]:
    """
    Remove a task from the user's todo list.

    Args:
        task_id: ID of the task to delete (required)
        token: JWT token for authentication

    Returns:
        Dictionary with success status and deletion confirmation
    """
    try:
        # Validate JWT token and extract user_id
        user_data = JWTValidator.validate_token(token)
        if not user_data:
            return {
                "success": False,
                "error": {
                    "type": "AuthenticationError",
                    "message": "Invalid or expired JWT token",
                    "code": "AUTH_001"
                }
            }

        user_id = user_data.get("user_id")

        # Verify user has access to this operation
        if not MultiTenantChecker.verify_user_access(user_id):
            return {
                "success": False,
                "error": {
                    "type": "AuthorizationError",
                    "message": "User not authorized to perform this operation",
                    "code": "AUTH_002"
                }
            }

        # Validate input parameters
        if not task_id:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "task_id is required",
                    "code": "VALIDATION_001"
                }
            }

        try:
            # Validate UUID format
            UUID(task_id)
        except ValueError:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Invalid task_id format",
                    "code": "VALIDATION_002"
                }
            }

        # Delete the task using the service
        task_service = TaskService()
        deleted = await task_service.delete_task(
            task_id=task_id,
            user_id=user_id
        )

        if not deleted:
            return {
                "success": False,
                "error": {
                    "type": "NotFoundError",
                    "message": "Task not found or user not authorized to delete this task",
                    "code": "NOT_FOUND_001"
                }
            }

        return {
            "success": True,
            "data": {
                "deleted": True,
                "task_id": task_id
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "InternalError",
                "message": f"An internal error occurred: {str(e)}",
                "code": "INTERNAL_001"
            }
        }