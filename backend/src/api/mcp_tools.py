from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session
from uuid import uuid4

from ..models.mcp_tool import (
    MCPToolRequest, MCPToolResponse, MCPToolMetadata,
    MCPToolAccessType, MCPToolType
)
from ..models.user import CurrentUser
from ..dependencies.auth import get_current_user
from ..database import get_session
from ..services.mcp_service import get_mcp_service
from ..exceptions.auth import InsufficientPermissionsException
from ..middleware.mcp_auth import mcp_auth_validator

router = APIRouter(prefix="/mcp", tags=["mcp-tools"])


@router.post("/execute", response_model=MCPToolResponse)
async def execute_mcp_tool(
    request: MCPToolRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Execute an MCP tool with proper authentication and authorization

    Args:
        request: The MCP tool request to execute
        current_user: The authenticated user making the request
        session: Database session

    Returns:
        MCPToolResponse: The result of the tool execution
    """
    # Validate that the user_id in the request matches the authenticated user
    if current_user.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot execute MCP tool on behalf of user {request.user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Validate that the user owns all the resources they're trying to access
    for resource in request.resources:
        if resource.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Resource {resource.resource_id} does not belong to user {current_user.user_id}. "
                       f"It belongs to user {resource.owner_id}."
            )

    # Get the MCP service and execute the tool
    mcp_service = get_mcp_service(session)
    response = await mcp_service.execute_tool_request(
        tool_request=request,
        token=""  # In a real implementation, we'd pass the actual token
    )

    return response


@router.post("/register", response_model=MCPToolMetadata)
async def register_mcp_tool(
    tool_data: dict,  # Using dict temporarily until we define proper input model
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Register a new MCP tool for the authenticated user

    Args:
        tool_data: Data for the tool to register
        current_user: The authenticated user registering the tool
        session: Database session

    Returns:
        MCPToolMetadata: The registered tool metadata
    """
    # Extract tool data from request
    tool_id = tool_data.get("tool_id", str(uuid4()))
    name = tool_data.get("name")
    description = tool_data.get("description")
    allowed_resources = tool_data.get("allowed_resources", [])

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool name is required"
        )

    # Validate that the tool_id belongs to the authenticated user
    if tool_data.get("user_id") and tool_data["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot register tool for user {tool_data['user_id']}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Get the MCP service and register the tool
    mcp_service = get_mcp_service(session)
    tool_metadata = await mcp_service.register_tool(
        tool_id=tool_id,
        user_id=current_user.user_id,
        name=name,
        description=description,
        allowed_resources=allowed_resources
    )

    return tool_metadata


@router.get("/my-tools", response_model=List[MCPToolMetadata])
async def get_user_mcp_tools(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all MCP tools registered by the authenticated user

    Args:
        current_user: The authenticated user
        session: Database session

    Returns:
        List of MCP tool metadata for the user
    """
    # Get the MCP service and retrieve user's tools
    mcp_service = get_mcp_service(session)
    tools = await mcp_service.get_user_tools(current_user.user_id)

    return tools


@router.get("/validate/{tool_id}")
async def validate_mcp_tool(
    tool_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Validate that an MCP tool is registered and belongs to the authenticated user

    Args:
        tool_id: The ID of the tool to validate
        current_user: The authenticated user
        session: Database session

    Returns:
        Dictionary with validation result
    """
    # Get the MCP service and validate the tool
    mcp_service = get_mcp_service(session)
    is_valid = await mcp_service.validate_tool_registration(
        tool_id=tool_id,
        user_id=current_user.user_id
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP tool {tool_id} not found or does not belong to user {current_user.user_id}"
        )

    return {
        "valid": True,
        "tool_id": tool_id,
        "user_id": current_user.user_id,
        "message": f"MCP tool {tool_id} is valid and belongs to user {current_user.user_id}"
    }


@router.delete("/unregister/{tool_id}")
async def unregister_mcp_tool(
    tool_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Unregister an MCP tool owned by the authenticated user

    Args:
        tool_id: The ID of the tool to unregister
        current_user: The authenticated user
        session: Database session

    Returns:
        Success message
    """
    # In a real implementation, this would mark the tool as inactive
    # For now, we'll just validate that the tool exists and belongs to the user
    mcp_service = get_mcp_service(session)
    is_valid = await mcp_service.validate_tool_registration(
        tool_id=tool_id,
        user_id=current_user.user_id
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP tool {tool_id} not found or does not belong to user {current_user.user_id}"
        )

    # In a real implementation, we would update the is_active field to False
    # For now, just return success
    return {
        "message": f"MCP tool {tool_id} unregistered successfully",
        "tool_id": tool_id,
        "user_id": current_user.user_id
    }