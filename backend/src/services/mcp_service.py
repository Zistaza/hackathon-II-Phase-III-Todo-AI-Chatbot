from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from uuid import uuid4
from datetime import datetime
import asyncio

from ..models.mcp_tool import (
    MCPToolRequest, MCPToolResponse, MCPToolMetadata,
    MCPToolAccessLog, MCPToolAccessType, MCPToolType
)
from ..models.user import CurrentUser
from ..database import get_session
from ..utils.mcp_auth import validate_mcp_tool_access, get_current_user_from_token


class MCPTOOL_SERVICE:
    """
    Service class for handling MCP tool operations with proper authentication
    and authorization checks.
    """

    def __init__(self, session: Session):
        self.session = session

    async def execute_tool_request(
        self,
        tool_request: MCPToolRequest,
        token: str
    ) -> MCPToolResponse:
        """
        Execute an MCP tool request with proper authentication and authorization

        Args:
            tool_request: The MCP tool request to execute
            token: JWT token for authentication

        Returns:
            MCPToolResponse: The result of the tool execution
        """
        try:
            # Validate that the user can access the requested resources
            for resource in tool_request.resources:
                validate_mcp_tool_access(
                    token=token,
                    resource_owner_id=resource.owner_id
                )

            # Log the access attempt
            await self.log_tool_access(
                tool_id=tool_request.tool_id,
                user_id=tool_request.user_id,
                action=tool_request.action,
                resource_ids=[r.resource_id for r in tool_request.resources],
                success=True
            )

            # Execute the specific tool based on tool_id
            result = await self._execute_specific_tool(tool_request)

            return MCPToolResponse(
                success=True,
                message="Tool executed successfully",
                data=result
            )

        except Exception as e:
            # Log the failed access attempt
            await self.log_tool_access(
                tool_id=tool_request.tool_id,
                user_id=tool_request.user_id,
                action=tool_request.action,
                resource_ids=[r.resource_id for r in tool_request.resources],
                success=False
            )

            return MCPToolResponse(
                success=False,
                message=str(e),
                data=None
            )

    async def _execute_specific_tool(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Execute the specific tool based on its type

        Args:
            tool_request: The tool request to execute

        Returns:
            Dict with the result of the tool execution
        """
        # In a real implementation, this would route to specific tool handlers
        # For now, we'll simulate different tool behaviors

        tool_type = tool_request.tool_id  # Using tool_id as a proxy for tool type in this example

        if "code_generator" in tool_type.lower():
            return await self._handle_code_generation(tool_request)
        elif "data_analyzer" in tool_type.lower():
            return await self._handle_data_analysis(tool_request)
        elif "file_manager" in tool_type.lower():
            return await self._handle_file_management(tool_request)
        else:
            # Default handler for unknown tool types
            await asyncio.sleep(0.1)  # Simulate processing time
            return {
                "tool_id": tool_request.tool_id,
                "action": tool_request.action,
                "resources_accessed": [r.resource_id for r in tool_request.resources],
                "parameters_used": tool_request.parameters
            }

    async def _handle_code_generation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle code generation tool requests
        """
        await asyncio.sleep(0.2)  # Simulate processing time
        return {
            "generated_code": f"// Generated code for {tool_request.action}",
            "resources_accessed": [r.resource_id for r in tool_request.resources],
            "status": "success"
        }

    async def _handle_data_analysis(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle data analysis tool requests
        """
        await asyncio.sleep(0.3)  # Simulate processing time
        return {
            "analysis_results": f"Analysis of {len(tool_request.resources)} resources completed",
            "summary": "No significant issues found",
            "resources_analyzed": [r.resource_id for r in tool_request.resources],
            "status": "completed"
        }

    async def _handle_file_management(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle file management tool requests
        """
        await asyncio.sleep(0.15)  # Simulate processing time
        return {
            "operation": tool_request.action,
            "files_processed": [r.resource_id for r in tool_request.resources],
            "result": "Operation completed successfully",
            "status": "success"
        }

    async def log_tool_access(
        self,
        tool_id: str,
        user_id: str,
        action: str,
        resource_ids: List[str],
        success: bool,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log MCP tool access for audit purposes

        Args:
            tool_id: ID of the tool that was accessed
            user_id: ID of the user who accessed the tool
            action: Action that was performed
            resource_ids: IDs of resources that were accessed
            success: Whether the access was successful
            ip_address: IP address of the requester
        """
        try:
            log_entry = MCPToolAccessLog(
                tool_id=tool_id,
                user_id=user_id,
                action=action,
                resource_id=','.join(resource_ids) if resource_ids else None,
                success=success,
                ip_address=ip_address
            )

            self.session.add(log_entry)
            self.session.commit()
        except Exception as e:
            # Log the error but don't fail the main operation
            print(f"Error logging tool access: {e}")

    async def register_tool(
        self,
        tool_id: str,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        allowed_resources: Optional[List[str]] = None
    ) -> MCPToolMetadata:
        """
        Register a new MCP tool for a user

        Args:
            tool_id: Unique ID for the tool
            user_id: ID of the user registering the tool
            name: Name of the tool
            description: Optional description of the tool
            allowed_resources: Optional list of allowed resource types

        Returns:
            MCPToolMetadata: The registered tool metadata
        """
        tool_metadata = MCPToolMetadata(
            tool_id=tool_id,
            user_id=user_id,
            name=name,
            description=description,
            allowed_resources=str(allowed_resources) if allowed_resources else None
        )

        self.session.add(tool_metadata)
        self.session.commit()
        self.session.refresh(tool_metadata)

        return tool_metadata

    async def get_user_tools(self, user_id: str) -> List[MCPToolMetadata]:
        """
        Get all tools registered by a specific user

        Args:
            user_id: ID of the user whose tools to retrieve

        Returns:
            List of MCP tool metadata for the user
        """
        statement = select(MCPToolMetadata).where(MCPToolMetadata.user_id == user_id)
        results = self.session.exec(statement)
        return results.all()

    async def validate_tool_registration(
        self,
        tool_id: str,
        user_id: str
    ) -> bool:
        """
        Validate that a tool is registered and belongs to the specified user

        Args:
            tool_id: ID of the tool to validate
            user_id: ID of the user who should own the tool

        Returns:
            bool: True if tool is registered and belongs to user
        """
        statement = select(MCPToolMetadata).where(
            MCPToolMetadata.tool_id == tool_id,
            MCPToolMetadata.user_id == user_id,
            MCPToolMetadata.is_active == True
        )
        tool = self.session.exec(statement).first()

        return tool is not None


# Global function to get MCP service instance
def get_mcp_service(session: Session) -> MCPTOOL_SERVICE:
    """
    Get an instance of the MCP tool service

    Args:
        session: Database session

    Returns:
        MCPTOOL_SERVICE: Instance of the MCP tool service
    """
    return MCPTOOL_SERVICE(session=session)