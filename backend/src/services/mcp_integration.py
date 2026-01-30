"""
MCP integration wrapper for Todo AI Chatbot Agent
Handles communication with MCP tools
"""

import asyncio
import logging
from typing import Dict, Any, Optional
# Import the task service to make direct calls without token validation
from src.services.task_service import TaskService


logger = logging.getLogger(__name__)


class MCPIntegration:
    """Wrapper class for MCP tool invocations"""

    def __init__(self, mcp_server_url: str = None):
        """
        Initialize MCP integration

        Args:
            mcp_server_url: URL to the MCP tools server (not used since we call services directly)
        """
        # Initialize the task service for direct calls
        self.task_service = TaskService()

    async def call_add_task(self, user_id: str, title: str, description: str = None, due_date: str = None) -> Dict[str, Any]:
        """
        Call the add_task functionality

        Args:
            user_id: ID of the user making the request (already authenticated)
            title: Title of the task
            description: Optional description of the task
            due_date: Optional due date for the task (currently not used)

        Returns:
            Result from the task creation
        """
        try:
            # Call the task service directly with the authenticated user_id
            task = await self.task_service.create_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=1  # Default priority
            )

            if task is None:
                return {
                    "error": "Failed to create task - user may not have access or validation failed",
                    "task_id": None,
                    "title": title,
                    "status": "error"
                }

            return {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "task_id": None,
                "title": title,
                "status": "error"
            }

    async def call_list_tasks(self, user_id: str, status_filter: str = None, sort_order: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Call the list_tasks functionality

        Args:
            user_id: ID of the user making the request (already authenticated)
            status_filter: Filter tasks by status (all, pending, completed)
            sort_order: Sort order (asc, desc)
            limit: Maximum number of tasks to return

        Returns:
            Result from the task listing
        """
        try:
            # Determine filter_completed based on status_filter
            filter_completed = None
            if status_filter == "pending":
                filter_completed = False
            elif status_filter == "completed":
                filter_completed = True
            # For "all" or None, we'll get all tasks

            # Call the task service directly with the authenticated user_id
            if filter_completed is not None:
                tasks = await self.task_service.get_tasks_by_user_id(
                    user_id=user_id,
                    filter_completed=filter_completed
                )
            else:
                tasks = await self.task_service.get_tasks_by_user_id(
                    user_id=user_id
                )

            # Apply limit if specified
            if limit and len(tasks) > limit:
                tasks = tasks[:limit]

            # Convert tasks to the expected format
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                task_list.append(task_dict)

            return {
                "tasks": task_list,
                "count": len(task_list)
            }
        except Exception as e:
            return {
                "error": str(e),
                "tasks": []
            }

    async def call_complete_task(self, user_id: str, task_id: str = None, task_reference: str = None) -> Dict[str, Any]:
        """
        Call the complete_task functionality

        Args:
            user_id: ID of the user making the request (already authenticated)
            task_id: ID of the task to complete (optional if task_reference is provided)
            task_reference: Reference to the task by title/description (optional if task_id is provided)

        Returns:
            Result from the task completion
        """
        try:
            # If task_id is not provided but task_reference is, find the task by reference
            if not task_id and task_reference:
                # First, list all tasks to find the matching one
                list_result = await self.call_list_tasks(user_id=user_id)

                if "error" in list_result:
                    return {
                        "error": f"Could not find task '{task_reference}': {list_result.get('error', 'Unknown error')}",
                        "task_id": None,
                        "status": "error"
                    }

                # Find the task that matches the reference
                matching_task = None
                for task in list_result.get("tasks", []):
                    if task_reference.lower() in task.get("title", "").lower() or \
                       task_reference.lower() in task.get("description", "").lower():
                        matching_task = task
                        break

                if not matching_task:
                    return {
                        "error": f"No task found matching '{task_reference}'",
                        "task_id": None,
                        "status": "error"
                    }

                task_id = matching_task["id"]

            # Call the task service directly with the authenticated user_id
            task = await self.task_service.update_task_completion(
                task_id=task_id,
                user_id=user_id,
                completed=True
            )

            if task:
                return {
                    "task_id": str(task.id),
                    "completed": task.completed,
                    "title": task.title,
                    "status": "success"
                }
            else:
                return {
                    "error": "Task not found or not owned by user",
                    "task_id": task_id,
                    "status": "error"
                }
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "status": "error"
            }

    async def call_delete_task(self, user_id: str, task_id: str = None, task_reference: str = None) -> Dict[str, Any]:
        """
        Call the delete_task functionality

        Args:
            user_id: ID of the user making the request (already authenticated)
            task_id: ID of the task to delete (optional if task_reference is provided)
            task_reference: Reference to the task by title/description (optional if task_id is provided)

        Returns:
            Result from the task deletion
        """
        try:
            # If task_id is not provided but task_reference is, find the task by reference
            if not task_id and task_reference:
                # First, list all tasks to find the matching one
                list_result = await self.call_list_tasks(user_id=user_id)

                if "error" in list_result:
                    return {
                        "error": f"Could not find task '{task_reference}': {list_result.get('error', 'Unknown error')}",
                        "task_id": None,
                        "deleted": False
                    }

                # Find the task that matches the reference
                matching_task = None
                for task in list_result.get("tasks", []):
                    if task_reference.lower() in task.get("title", "").lower() or \
                       task_reference.lower() in task.get("description", "").lower():
                        matching_task = task
                        break

                if not matching_task:
                    return {
                        "error": f"No task found matching '{task_reference}'",
                        "task_id": None,
                        "deleted": False
                    }

                task_id = matching_task["id"]

            # Call the task service directly with the authenticated user_id
            success = await self.task_service.delete_task(
                user_id=user_id,
                task_id=task_id
            )

            if success:
                return {
                    "task_id": task_id,
                    "deleted": True,
                    "status": "success"
                }
            else:
                return {
                    "error": "Task not found or not owned by user",
                    "task_id": task_id,
                    "deleted": False
                }
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "deleted": False
            }

    async def call_update_task(self, user_id: str, task_id: str = None, task_reference: str = None,
                              title: str = None, description: str = None, due_date: str = None, status: str = None) -> Dict[str, Any]:
        """
        Call the update_task functionality

        Args:
            user_id: ID of the user making the request (already authenticated)
            task_id: ID of the task to update (optional if task_reference is provided)
            task_reference: Reference to the task by title/description (optional if task_id is provided)
            title: New title for the task
            description: New description for the task
            due_date: New due date for the task (currently not used)
            status: New status for the task

        Returns:
            Result from the task update
        """
        try:
            # If task_id is not provided but task_reference is, find the task by reference
            if not task_id and task_reference:
                # First, list all tasks to find the matching one
                list_result = await self.call_list_tasks(user_id=user_id)

                if "error" in list_result:
                    return {
                        "error": f"Could not find task '{task_reference}': {list_result.get('error', 'Unknown error')}",
                        "task_id": None,
                        "status": "error"
                    }

                # Find the task that matches the reference
                matching_task = None
                for task in list_result.get("tasks", []):
                    if task_reference.lower() in task.get("title", "").lower() or \
                       task_reference.lower() in task.get("description", "").lower():
                        matching_task = task
                        break

                if not matching_task:
                    return {
                        "error": f"No task found matching '{task_reference}'",
                        "task_id": None,
                        "status": "error"
                    }

                task_id = matching_task["id"]

            # Map status to completed boolean
            updates = {}
            if title is not None:
                updates["title"] = title
            if description is not None:
                updates["description"] = description
            if status is not None:
                updates["completed"] = (status.lower() == "completed") or (status.lower() == "true")

            # Call the task service directly with the authenticated user_id
            task = await self.task_service.update_task(
                task_id=task_id,
                user_id=user_id,
                **updates
            )

            if task:
                return {
                    "task_id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "status": "success"
                }
            else:
                return {
                    "error": "Task not found or not owned by user",
                    "task_id": task_id,
                    "status": "error"
                }
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "status": "error"
            }

    async def execute_tool_call(self, user_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call based on the tool name and arguments

        Args:
            user_id: ID of the user making the request (already authenticated)
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Result from the task operation
        """
        tool_map = {
            "add_task": self.call_add_task,
            "list_tasks": self.call_list_tasks,
            "complete_task": self.call_complete_task,
            "delete_task": self.call_delete_task,
            "update_task": self.call_update_task
        }

        if tool_name not in tool_map:
            logger.error(f"Unknown tool requested: {tool_name}")
            return {
                "error": f"Unknown tool: {tool_name}",
                "result": None
            }

        tool_func = tool_map[tool_name]

        try:
            # Prepare arguments for the specific tool function
            if tool_name == "add_task":
                result = await tool_func(
                    user_id=user_id,
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    due_date=arguments.get("due_date")
                )
            elif tool_name == "list_tasks":
                result = await tool_func(
                    user_id=user_id,
                    status_filter=arguments.get("status_filter"),
                    sort_order=arguments.get("sort_order"),
                    limit=arguments.get("limit")
                )
            elif tool_name == "complete_task":
                result = await tool_func(
                    user_id=user_id,
                    task_id=arguments.get("task_id"),
                    task_reference=arguments.get("task_reference")
                )
            elif tool_name == "delete_task":
                result = await tool_func(
                    user_id=user_id,
                    task_id=arguments.get("task_id"),
                    task_reference=arguments.get("task_reference")
                )
            elif tool_name == "update_task":
                result = await tool_func(
                    user_id=user_id,
                    task_id=arguments.get("task_id"),
                    task_reference=arguments.get("task_reference"),
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    due_date=arguments.get("due_date"),
                    status=arguments.get("status")
                )

            # Log successful execution
            logger.info(f"Successfully executed tool {tool_name}")
            return result

        except Exception as e:
            # Log error and return graceful degradation response
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "error": f"Failed to execute {tool_name}: {str(e)}",
                "result": None,
                "degraded": True
            }