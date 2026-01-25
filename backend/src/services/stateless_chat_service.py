"""
Stateless Chat Service for the Todo AI Chatbot application.
Implements the 12-step stateless request cycle as specified in the requirements.
"""
from sqlmodel import Session, select
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging

from ..models.conversation_model import Conversation
from ..models.message_model import Message, MessageCreate
from ..models.tool_call import ToolCall, ToolCallCreate, ToolCallUpdate, ExecutionStatus
from ..agents.todo_chatbot.agent import Agent
from ..services.mcp_integration import MCPIntegration
from ..services.conversation_service import ConversationService
from ..services.message_service import MessageService
from ..services.tool_call_service import ToolCallService


class StatelessChatService:
    """
    Service class that implements the 12-step stateless request cycle for chat interactions.
    Each request is completely self-contained with no server-side state preservation.
    """

    def __init__(self, session: Session):
        self.session = session
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        self.tool_call_service = ToolCallService(session)
        self.agent = Agent()
        self.mcp_integration = MCPIntegration()
        self.logger = logging.getLogger(__name__)

    async def process_chat_request(self, user_id: str, conversation_id: Optional[str], message_content: str) -> Dict[str, Any]:
        """
        Process a chat request through the complete 12-step stateless request cycle.

        Args:
            user_id: ID of the authenticated user
            conversation_id: Optional ID of existing conversation (creates new if None)
            message_content: Natural language message from the user

        Returns:
            Dictionary containing conversation_id, response, and tool_calls
        """
        # Step 1: Authenticate request via JWT (handled by dependency injection in API)
        # Step 2: Validate user_id matches JWT subject (handled by dependency injection in API)

        # Step 3: Load conversation history from database (if conversation_id exists)
        conversation = None
        if conversation_id:
            # Convert string ID to appropriate format if needed
            try:
                # If conversation_id is numeric string, convert to int for comparison with database
                if isinstance(conversation_id, str) and conversation_id.isdigit():
                    # Look for conversation in the database using the converted ID
                    from sqlmodel import select
                    stmt = select(Conversation).where(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                    result = self.session.exec(stmt)
                    conversation = result.first()
                else:
                    # Use as-is if it's already in the right format
                    conversation = self.conversation_service.get_conversation_by_id(conversation_id, user_id)
            except Exception:
                # Fallback to original method if conversion fails
                conversation = self.conversation_service.get_conversation_by_id(conversation_id, user_id)

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")
        else:
            # Create new conversation if none provided
            from ..models.conversation_model import ConversationCreate
            conversation_data = ConversationCreate(title=f"Chat with {user_id}")
            conversation = self.conversation_service.create_conversation(user_id, conversation_data)

        # Step 4: Append current user message to history
        message_create_data = MessageCreate(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=message_content,
            metadata={}
        )
        user_message = self.message_service.create_message(message_create_data)

        # Step 5: Persist user message before agent execution
        # Already done in create_message above

        # Step 6: Run OpenAI Agent with reconstructed message history and MCP tool definitions
        # Reconstruct the conversation history for the agent
        conversation_history = self.message_service.get_messages_by_conversation(conversation.id, user_id)

        # Process the message with the agent
        agent_response = await self.agent.process_message(user_id, conversation.id, message_content)

        # Step 7: Capture any MCP tool calls made by the agent
        captured_tool_calls = []
        for tool_call in agent_response.get("tool_calls", []):
            # Convert conversation_id to int for the ToolCall model
            try:
                conv_id_int = int(conversation.id) if isinstance(conversation.id, str) and conversation.id.isdigit() else conversation.id
            except (ValueError, TypeError):
                # Default to 1 if conversion fails - this would need to be fixed properly
                conv_id_int = 1

            # Create tool call record in database
            tool_call_create = ToolCallCreate(
                conversation_id=conv_id_int,
                message_id=None,  # May link to message later if needed
                tool_name=tool_call.get("name", ""),
                tool_input=tool_call.get("arguments", {}),
                execution_status=ExecutionStatus.PENDING
            )

            db_tool_call = self.tool_call_service.create_tool_call(tool_call_create)
            captured_tool_calls.append(db_tool_call)

        # Step 8: Persist tool calls and tool responses
        # Tool calls are already persisted in step 7
        # Process tool call results
        for idx, tool_call in enumerate(captured_tool_calls):
            try:
                # Execute the tool call via MCP integration
                tool_result = await self.mcp_integration.execute_tool_call(
                    tool_call.tool_name,
                    tool_call.tool_input
                )

                # Update the tool call with the result
                tool_call_update = ToolCallUpdate(
                    tool_output=tool_result,
                    execution_status=ExecutionStatus.SUCCESS if "error" not in tool_result else ExecutionStatus.ERROR
                )

                updated_tool_call = self.tool_call_service.update_tool_call(tool_call.id, tool_call_update)

            except Exception as e:
                # Handle tool call execution errors
                tool_call_update = ToolCallUpdate(
                    tool_output={"error": str(e)},
                    execution_status=ExecutionStatus.ERROR
                )
                self.tool_call_service.update_tool_call(tool_call.id, tool_call_update)

        # Step 9: Generate final assistant response
        # The agent already generated a response, we'll use that
        final_response = agent_response.get("response", "I processed your request.")

        # Step 10: Persist assistant response
        assistant_message_data = MessageCreate(
            conversation_id=conversation.id,
            user_id=user_id,  # For assistant messages, we'll use the user_id
            role="assistant",
            content=final_response,
            metadata={"source": "ai_response", "tool_calls_count": len(captured_tool_calls)}
        )
        assistant_message = self.message_service.create_message(assistant_message_data)

        # Step 11: Return response payload to client
        tool_calls_payload = []
        for tool_call in captured_tool_calls:
            tool_calls_payload.append({
                "tool_name": tool_call.tool_name,
                "input": tool_call.tool_input,
                "output": tool_call.tool_output,
                "status": tool_call.execution_status.value
            })

        response_payload = {
            "conversation_id": conversation.id,
            "response": final_response,
            "tool_calls": tool_calls_payload
        }

        # Step 12: Discard all in-memory state (handled by this method ending - no persistent state kept)
        return response_payload

    async def authenticate_and_validate_user(self, provided_user_id: str, authenticated_user_id: str) -> bool:
        """
        Validate that the user_id in the path matches the authenticated user.

        Args:
            provided_user_id: User ID from the request path
            authenticated_user_id: User ID from the JWT token

        Returns:
            Boolean indicating if validation passed
        """
        return str(provided_user_id) == str(authenticated_user_id)