"""
MCP integration wrapper for Todo AI Chatbot Agent
Handles communication with MCP tools
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from ..utils.http_client import HttpClient  # Assuming this utility exists


logger = logging.getLogger(__name__)


class MCPIntegration:
    """Wrapper class for MCP tool invocations"""

    def __init__(self, mcp_server_url: str = None):
        """
        Initialize MCP integration

        Args:
            mcp_server_url: URL to the MCP tools server
        """
        import os
        self.mcp_server_url = mcp_server_url or os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        self.client = HttpClient(base_url=self.mcp_server_url)

    async def call_add_task(self, title: str, description: str = None, due_date: str = None) -> Dict[str, Any]:
        """
        Call the add_task MCP tool

        Args:
            title: Title of the task
            description: Optional description of the task
            due_date: Optional due date for the task

        Returns:
            Result from the MCP tool
        """
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            response = await self.client.post("/mcp/tools/add_task", json=payload)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "task_id": None,
                "title": title,
                "status": "error"
            }

    async def call_list_tasks(self, status_filter: str = None, sort_order: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Call the list_tasks MCP tool

        Args:
            status_filter: Filter tasks by status (all, pending, completed)
            sort_order: Sort order (asc, desc)
            limit: Maximum number of tasks to return

        Returns:
            Result from the MCP tool
        """
        payload = {}
        if status_filter is not None:
            payload["status_filter"] = status_filter
        if sort_order is not None:
            payload["sort_order"] = sort_order
        if limit is not None:
            payload["limit"] = limit

        try:
            response = await self.client.post("/mcp/tools/list_tasks", json=payload)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "tasks": []
            }

    async def call_complete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Call the complete_task MCP tool

        Args:
            task_id: ID of the task to complete

        Returns:
            Result from the MCP tool
        """
        payload = {
            "task_id": task_id
        }

        try:
            response = await self.client.post("/mcp/tools/complete_task", json=payload)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "status": "error"
            }

    async def call_delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Call the delete_task MCP tool

        Args:
            task_id: ID of the task to delete

        Returns:
            Result from the MCP tool
        """
        payload = {
            "task_id": task_id
        }

        try:
            response = await self.client.post("/mcp/tools/delete_task", json=payload)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "deleted": False
            }

    async def call_update_task(self, task_id: str, title: str = None, description: str = None,
                              due_date: str = None, status: str = None) -> Dict[str, Any]:
        """
        Call the update_task MCP tool

        Args:
            task_id: ID of the task to update
            title: New title for the task
            description: New description for the task
            due_date: New due date for the task
            status: New status for the task

        Returns:
            Result from the MCP tool
        """
        payload = {
            "task_id": task_id
        }

        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if due_date is not None:
            payload["due_date"] = due_date
        if status is not None:
            payload["status"] = status

        try:
            response = await self.client.post("/mcp/tools/update_task", json=payload)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "status": "error"
            }

    async def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call based on the tool name and arguments

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Result from the MCP tool
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
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    due_date=arguments.get("due_date")
                )
            elif tool_name == "list_tasks":
                result = await tool_func(
                    status_filter=arguments.get("status_filter"),
                    sort_order=arguments.get("sort_order"),
                    limit=arguments.get("limit")
                )
            elif tool_name == "complete_task":
                result = await tool_func(task_id=arguments.get("task_id"))
            elif tool_name == "delete_task":
                result = await tool_func(task_id=arguments.get("task_id"))
            elif tool_name == "update_task":
                result = await tool_func(
                    task_id=arguments.get("task_id"),
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