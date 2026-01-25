"""
Chat endpoint for MCP tool integration with AI agents.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

from .mcp_tools.add_task import add_task
from .mcp_tools.list_tasks import list_tasks
from .mcp_tools.complete_task import complete_task
from .mcp_tools.delete_task import delete_task
from .mcp_tools.update_task import update_task
from src.dependencies.auth import get_current_user
from src.models.user import CurrentUser


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    mcp_tool_calls: Optional[list] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    mcp_results: Optional[list] = None
    success: bool = True


@router.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Main chat endpoint that handles user messages and MCP tool integration.

    Args:
        user_id: The ID of the user making the request
        request: Chat request containing message and optional MCP tool calls
        current_user: The authenticated user (from dependency)

    Returns:
        Chat response with potential MCP tool results
    """
    try:
        # Verify user identity matches the user_id in the path
        if str(current_user.user_id) != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: User ID mismatch"
            )

        # Extract JWT token from request headers for MCP tool calls
        # In a real implementation, this would come from the request context
        # For now, we'll assume it's available in the request context
        token = getattr(request, 'authorization', None)

        mcp_results = []

        # Process MCP tool calls if any are provided
        if request.mcp_tool_calls:
            for tool_call in request.mcp_tool_calls:
                tool_result = await process_mcp_tool_call(tool_call, token)
                mcp_results.append(tool_result)

        # In a real implementation, we would also process the natural language
        # message and potentially infer MCP tool calls from it
        # For now, we'll just return the results of explicitly called tools

        response = ChatResponse(
            response=f"Processed message for user {user_id}",
            mcp_results=mcp_results if mcp_results else None,
            success=True
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def process_mcp_tool_call(tool_call: Dict[str, Any], token: str) -> Dict[str, Any]:
    """
    Process an individual MCP tool call.

    Args:
        tool_call: Dictionary containing tool name and arguments
        token: JWT token for authentication

    Returns:
        Result of the MCP tool call
    """
    tool_name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})

    if tool_name == "add_task":
        return await add_task(
            title=arguments.get("title"),
            description=arguments.get("description"),
            priority=arguments.get("priority"),
            token=token
        )
    elif tool_name == "list_tasks":
        return await list_tasks(
            filter_completed=arguments.get("filter_completed", False),
            token=token
        )
    elif tool_name == "complete_task":
        return await complete_task(
            task_id=arguments.get("task_id"),
            completed=arguments.get("completed", True),
            token=token
        )
    elif tool_name == "delete_task":
        return await delete_task(
            task_id=arguments.get("task_id"),
            token=token
        )
    elif tool_name == "update_task":
        return await update_task(
            task_id=arguments.get("task_id"),
            title=arguments.get("title"),
            description=arguments.get("description"),
            priority=arguments.get("priority"),
            completed=arguments.get("completed"),
            token=token
        )
    else:
        return {
            "success": False,
            "error": {
                "type": "ValidationError",
                "message": f"Unknown MCP tool: {tool_name}",
                "code": "VALIDATION_001"
            }
        }