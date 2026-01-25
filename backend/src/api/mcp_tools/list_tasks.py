"""
MCP Tool for listing tasks from a user's todo list.
"""
from typing import Dict, Any, Optional, List
from sqlmodel import Session
from src.models.task_model import Task
from src.services.task_service import TaskService
from src.utils.jwt_validator import JWTValidator
from src.utils.multi_tenant_checker import MultiTenantChecker


async def list_tasks(
    filter_completed: Optional[bool] = False,
    token: str = None
) -> Dict[str, Any]:
    """
    Retrieve all tasks for the authenticated user.

    Args:
        filter_completed: Whether to filter out completed tasks (optional, default: false)
        token: JWT token for authentication

    Returns:
        Dictionary with success status and list of tasks
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
        if filter_completed is not None and not isinstance(filter_completed, bool):
            return {
                "success": False,
                "error": {
                    "type": "ValidationError",
                    "message": "filter_completed must be a boolean value",
                    "code": "VALIDATION_001"
                }
            }

        # Get tasks using the service
        task_service = TaskService()
        tasks = await task_service.get_tasks_by_user_id(
            user_id=user_id,
            filter_completed=filter_completed
        )

        # Format tasks for response
        tasks_data = []
        for task in tasks:
            task_data = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
            tasks_data.append(task_data)

        return {
            "success": True,
            "data": {
                "tasks": tasks_data
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