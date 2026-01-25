"""
ToolCall service for the Todo AI Chatbot application.
Handles operations for the ToolCall model including creation and retrieval.
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..models.tool_call import ToolCall, ToolCallCreate, ToolCallUpdate, ExecutionStatus
from ..models.conversation_model import Conversation
from ..models.message_model import Message


class ToolCallService:
    """
    Service class for handling tool call operations with proper authentication and authorization checks.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_tool_call(self, tool_call_data: ToolCallCreate) -> ToolCall:
        """
        Create a new tool call in the database.

        Args:
            tool_call_data: Data for the new tool call

        Returns:
            Created ToolCall object
        """
        # Verify that the conversation exists and belongs to the user
        conversation_statement = select(Conversation).where(
            Conversation.id == tool_call_data.conversation_id
        )
        conversation = self.session.exec(conversation_statement).first()

        if not conversation:
            raise ValueError(f"Conversation {tool_call_data.conversation_id} not found")

        # If message_id is provided, verify it belongs to the same conversation
        if tool_call_data.message_id:
            message_statement = select(Message).where(
                Message.id == tool_call_data.message_id,
                Message.conversation_id == tool_call_data.conversation_id
            )
            message = self.session.exec(message_statement).first()

            if not message:
                raise ValueError(f"Message {tool_call_data.message_id} not found in conversation {tool_call_data.conversation_id}")

        tool_call = ToolCall(
            conversation_id=tool_call_data.conversation_id,
            message_id=tool_call_data.message_id,
            tool_name=tool_call_data.tool_name,
            tool_input=tool_call_data.tool_input,
            execution_status=tool_call_data.execution_status
        )

        self.session.add(tool_call)
        self.session.commit()
        self.session.refresh(tool_call)

        return tool_call

    def update_tool_call(self, tool_call_id: int, tool_call_update: ToolCallUpdate) -> Optional[ToolCall]:
        """
        Update a tool call in the database.

        Args:
            tool_call_id: ID of the tool call to update
            tool_call_update: Updated data for the tool call

        Returns:
            Updated ToolCall object, or None if not found
        """
        statement = select(ToolCall).where(ToolCall.id == tool_call_id)
        tool_call = self.session.exec(statement).first()

        if not tool_call:
            return None

        # Update the fields
        if tool_call_update.tool_output is not None:
            tool_call.tool_output = tool_call_update.tool_output
        if tool_call_update.execution_status is not None:
            tool_call.execution_status = tool_call_update.execution_status

        self.session.add(tool_call)
        self.session.commit()
        self.session.refresh(tool_call)

        return tool_call

    def get_tool_calls_by_conversation(self, conversation_id: int) -> List[ToolCall]:
        """
        Get all tool calls for a specific conversation.

        Args:
            conversation_id: ID of the conversation to retrieve tool calls from

        Returns:
            List of ToolCall objects
        """
        statement = select(ToolCall).where(
            ToolCall.conversation_id == conversation_id
        ).order_by(ToolCall.timestamp)

        results = self.session.exec(statement)
        tool_calls = results.all()

        return tool_calls

    def get_tool_call_by_id(self, tool_call_id: int) -> Optional[ToolCall]:
        """
        Get a specific tool call by ID.

        Args:
            tool_call_id: ID of the tool call to retrieve

        Returns:
            ToolCall object if found, None otherwise
        """
        statement = select(ToolCall).where(ToolCall.id == tool_call_id)
        tool_call = self.session.exec(statement).first()

        return tool_call

    def get_tool_calls_by_message(self, message_id: int) -> List[ToolCall]:
        """
        Get all tool calls associated with a specific message.

        Args:
            message_id: ID of the message to retrieve tool calls for

        Returns:
            List of ToolCall objects
        """
        statement = select(ToolCall).where(
            ToolCall.message_id == message_id
        ).order_by(ToolCall.timestamp)

        results = self.session.exec(statement)
        tool_calls = results.all()

        return tool_calls