"""
MCP Tool for adding tasks to a user's todo list.
"""
import uuid
from typing import Dict, Any, Optional
from sqlmodel import Session
from src.models.task_model import Task
from src.services.task_service import TaskService
from src.utils.jwt_validator import JWTValidator
from src.utils.multi_tenant_checker import MultiTenantChecker


async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    token: str = None
) -> Dict[str, Any]:
    """
    Add a new task to the user's todo list.

    Args:
        title: Title of the task (required)
        description: Detailed description of the task (optional)
        priority: Priority level (1-5, optional)
        token: JWT token for authentication

    Returns:
        Dictionary with success status and task data
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
        if not title or len(title.strip()) == 0:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Title is required and cannot be empty",
                    "code": "VALIDATION_001"
                }
            }

        if len(title) > 200:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Title must be 200 characters or less",
                    "code": "VALIDATION_002"
                }
            }

        if description and len(description) > 1000:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Description must be 1000 characters or less",
                    "code": "VALIDATION_003"
                }
            }

        if priority is not None and (priority < 1 or priority > 5):
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Priority must be between 1 and 5",
                    "code": "VALIDATION_004"
                }
            }

        # Create the task using the service
        task_service = TaskService()
        task = await task_service.create_task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority
        )

        return {
            "success": True,
            "data": {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None
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