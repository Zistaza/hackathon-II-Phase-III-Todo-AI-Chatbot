"""
MCP Tool for marking a task as completed.
"""
from typing import Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from src.models.task_model import Task
from src.services.task_service import TaskService
from src.utils.jwt_validator import JWTValidator
from src.utils.multi_tenant_checker import MultiTenantChecker


async def complete_task(
    task_id: str,
    completed: Optional[bool] = True,
    token: str = None
) -> Dict[str, Any]:
    """
    Mark a specific task as completed.

    Args:
        task_id: ID of the task to complete (required)
        completed: Whether the task is completed (default: true)
        token: JWT token for authentication

    Returns:
        Dictionary with success status and task update data
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

        if completed is not None and not isinstance(completed, bool):
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "completed must be a boolean value",
                    "code": "VALIDATION_003"
                }
            }

        # Set default completed value if not provided
        if completed is None:
            completed = True

        # Update the task using the service
        task_service = TaskService()
        task = await task_service.update_task_completion(
            task_id=task_id,
            user_id=user_id,
            completed=completed
        )

        if not task:
            return {
                "success": False,
                "error": {
                    "type": "NotFoundError",
                    "message": "Task not found or user not authorized to access this task",
                    "code": "NOT_FOUND_001"
                }
            }

        return {
            "success": True,
            "data": {
                "task_id": str(task.id),
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
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