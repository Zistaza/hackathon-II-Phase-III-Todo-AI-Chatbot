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
from ..models.task_model import Task, TaskCreate, TaskUpdate
from ..models.conversation_model import Conversation
from ..models.message_model import Message
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
        elif "task" in tool_type.lower():
            # Handle task-related operations
            if tool_request.action == "add_task":
                return await self._handle_add_task(tool_request)
            elif tool_request.action == "list_tasks":
                return await self._handle_list_tasks(tool_request)
            elif tool_request.action == "update_task":
                return await self._handle_update_task(tool_request)
            elif tool_request.action == "complete_task":
                return await self._handle_complete_task(tool_request)
            elif tool_request.action == "delete_task":
                return await self._handle_delete_task(tool_request)
            else:
                return await self._handle_task_operation(tool_request)
        elif "conversation" in tool_type.lower():
            # Handle conversation-related operations
            if tool_request.action == "create_conversation":
                return await self._handle_create_conversation(tool_request)
            elif tool_request.action == "get_conversations":
                return await self._handle_get_conversations(tool_request)
            elif tool_request.action == "get_conversation":
                return await self._handle_get_conversation(tool_request)
            elif tool_request.action == "add_message":
                return await self._handle_add_message(tool_request)
            elif tool_request.action == "get_messages":
                return await self._handle_get_messages(tool_request)
            elif tool_request.action == "delete_conversation":
                return await self._handle_delete_conversation(tool_request)
            else:
                return await self._handle_conversation_operation(tool_request)
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

    async def _handle_add_task(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle add_task operation with user_id filtering
        """
        user_id = tool_request.user_id

        # Extract task parameters from the request
        title = tool_request.parameters.get('title', 'Untitled Task')
        description = tool_request.parameters.get('description', '')

        # Create a new task for the user
        new_task = Task(
            title=title,
            description=description,
            completed=False,
            user_id=user_id
        )

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)

        return {
            "task_id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "status": "created",
            "user_id": user_id
        }

    async def _handle_list_tasks(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle list_tasks operation with user_id filtering
        """
        user_id = tool_request.user_id

        # Query tasks for the specific user only
        statement = select(Task).where(Task.user_id == user_id)
        tasks = self.session.exec(statement).all()

        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            })

        return {
            "tasks": task_list,
            "total_count": len(task_list),
            "user_id": user_id
        }

    async def _handle_update_task(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle update_task operation with user_id filtering
        """
        user_id = tool_request.user_id
        task_id = tool_request.parameters.get('task_id')

        # Find the task that belongs to the user
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = self.session.exec(statement).first()

        if not task:
            return {
                "error": f"Task {task_id} not found or not owned by user {user_id}",
                "status": "failed"
            }

        # Update task with provided parameters
        if 'title' in tool_request.parameters:
            task.title = tool_request.parameters['title']
        if 'description' in tool_request.parameters:
            task.description = tool_request.parameters['description']
        if 'completed' in tool_request.parameters:
            task.completed = tool_request.parameters['completed']

        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "status": "updated",
            "user_id": user_id
        }

    async def _handle_complete_task(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle complete_task operation with user_id filtering
        """
        user_id = tool_request.user_id
        task_id = tool_request.parameters.get('task_id')

        # Find the task that belongs to the user
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = self.session.exec(statement).first()

        if not task:
            return {
                "error": f"Task {task_id} not found or not owned by user {user_id}",
                "status": "failed"
            }

        # Complete the task
        task.completed = True
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return {
            "task_id": task.id,
            "completed": task.completed,
            "status": "completed",
            "user_id": user_id
        }

    async def _handle_delete_task(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle delete_task operation with user_id filtering
        """
        user_id = tool_request.user_id
        task_id = tool_request.parameters.get('task_id')

        # Find the task that belongs to the user
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = self.session.exec(statement).first()

        if not task:
            return {
                "error": f"Task {task_id} not found or not owned by user {user_id}",
                "status": "failed"
            }

        # Delete the task
        self.session.delete(task)
        self.session.commit()

        return {
            "task_id": task_id,
            "status": "deleted",
            "user_id": user_id
        }

    async def _handle_task_operation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle generic task operations
        """
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "operation": tool_request.action,
            "user_id": tool_request.user_id,
            "parameters_used": tool_request.parameters,
            "status": "completed"
        }

    async def _handle_create_conversation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle create_conversation operation with user_id filtering
        """
        user_id = tool_request.user_id

        # Extract conversation parameters from the request
        title = tool_request.parameters.get('title', 'Untitled Conversation')
        metadata = tool_request.parameters.get('metadata', {})

        # Create a new conversation for the user
        conversation_data = ConversationCreate(
            title=title,
            metadata=metadata
        )

        conversation_service = ConversationService(self.session)
        conversation = conversation_service.create_conversation(
            user_id=user_id,
            conversation_data=conversation_data
        )

        return {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "status": "created",
            "user_id": user_id
        }

    async def _handle_get_conversations(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle get_conversations operation with user_id filtering
        """
        user_id = tool_request.user_id
        limit = tool_request.parameters.get('limit', 10)
        offset = tool_request.parameters.get('offset', 0)

        conversation_service = ConversationService(self.session)
        conversations = conversation_service.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "metadata": conv.conversation_metadata
            })

        return {
            "conversations": conversation_list,
            "total_count": len(conversation_list),
            "user_id": user_id
        }

    async def _handle_get_conversation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle get_conversation operation with user_id filtering
        """
        user_id = tool_request.user_id
        conversation_id = tool_request.parameters.get('conversation_id')

        conversation_service = ConversationService(self.session)
        conversation = conversation_service.get_conversation_by_id(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:
            return {
                "error": f"Conversation {conversation_id} not found or not owned by user {user_id}",
                "status": "failed"
            }

        return {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "metadata": conversation.conversation_metadata,
            "status": "retrieved",
            "user_id": user_id
        }

    async def _handle_add_message(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle add_message operation with user_id and conversation_id filtering
        """
        user_id = tool_request.user_id
        conversation_id = tool_request.parameters.get('conversation_id')
        content = tool_request.parameters.get('content', '')
        role = tool_request.parameters.get('role', 'user')
        metadata = tool_request.parameters.get('metadata', {})

        message_data = MessageCreate(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            metadata=metadata
        )

        conversation_service = ConversationService(self.session)
        message = conversation_service.add_message_to_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            message_data=message_data
        )

        return {
            "message_id": message.id,
            "content": message.content,
            "role": message.role,
            "status": "created",
            "user_id": user_id,
            "conversation_id": conversation_id
        }

    async def _handle_get_messages(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle get_messages operation with user_id and conversation_id filtering
        """
        user_id = tool_request.user_id
        conversation_id = tool_request.parameters.get('conversation_id')
        limit = tool_request.parameters.get('limit', 50)
        offset = tool_request.parameters.get('offset', 0)

        conversation_service = ConversationService(self.session)
        messages = conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "metadata": msg.metadata
            })

        return {
            "messages": message_list,
            "total_count": len(message_list),
            "conversation_id": conversation_id,
            "user_id": user_id
        }

    async def _handle_delete_conversation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle delete_conversation operation with user_id filtering
        """
        user_id = tool_request.user_id
        conversation_id = tool_request.parameters.get('conversation_id')

        conversation_service = ConversationService(self.session)
        success = conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not success:
            return {
                "error": f"Conversation {conversation_id} not found or not owned by user {user_id}",
                "status": "failed"
            }

        return {
            "conversation_id": conversation_id,
            "status": "deleted",
            "user_id": user_id
        }

    async def _handle_conversation_operation(self, tool_request: MCPToolRequest) -> Dict[str, Any]:
        """
        Handle generic conversation operations
        """
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "operation": tool_request.action,
            "user_id": tool_request.user_id,
            "parameters_used": tool_request.parameters,
            "status": "completed"
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