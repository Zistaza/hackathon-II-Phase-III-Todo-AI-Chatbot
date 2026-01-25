"""
MCP Tool for updating a task's properties.
"""
from typing import Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session
from src.models.task_model import Task
from src.services.task_service import TaskService
from src.utils.jwt_validator import JWTValidator
from src.utils.multi_tenant_checker import MultiTenantChecker


async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    completed: Optional[bool] = None,
    token: str = None
) -> Dict[str, Any]:
    """
    Modify an existing task's properties.

    Args:
        task_id: ID of the task to update (required)
        title: New title for the task (optional)
        description: New description for the task (optional)
        priority: New priority level (1-5, optional)
        completed: Whether the task is completed (optional)
        token: JWT token for authentication

    Returns:
        Dictionary with success status and updated task data
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

        if title is not None:
            if len(title.strip()) == 0:
                return {
                    "success": False,
                    "error": {
                        "type": "ValidationError",
                        "message": "Title cannot be empty",
                        "code": "VALIDATION_003"
                    }
                }

            if len(title) > 200:
                return {
                    "success": False,
                    "error": {
                        "type": "ValidationError",
                        "message": "Title must be 200 characters or less",
                        "code": "VALIDATION_004"
                    }
                }

        if description is not None and len(description) > 1000:
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Description must be 1000 characters or less",
                    "code": "VALIDATION_005"
                }
            }

        if priority is not None and (priority < 1 or priority > 5):
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "Priority must be between 1 and 5",
                    "code": "VALIDATION_006"
                }
            }

        if completed is not None and not isinstance(completed, bool):
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "completed must be a boolean value",
                    "code": "VALIDATION_007"
                }
            }

        # Prepare update data
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if priority is not None:
            update_data['priority'] = priority
        if completed is not None:
            update_data['completed'] = completed

        # Update the task using the service
        task_service = TaskService()
        task = await task_service.update_task(
            task_id=task_id,
            user_id=user_id,
            **update_data
        )

        if not task:
            return {
                "success": False,
                "error": {
                    "type": "NotFoundError",
                    "message": "Task not found or user not authorized to update this task",
                    "code": "NOT_FOUND_001"
                }
            }

        return {
            "success": True,
            "data": {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
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