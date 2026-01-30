"""
Message service for the Todo AI Chatbot application.
Handles operations for the Message model including creation and retrieval.
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..models.message_model import Message, MessageCreate
from ..models.conversation_model import Conversation


class MessageService:
    """
    Service class for handling message operations with proper authentication and authorization checks.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_message(self, message_data: MessageCreate) -> Message:
        """
        Create a new message in the database.

        Args:
            message_data: Data for the new message

        Returns:
            Created Message object
        """
        # Verify that the conversation exists and belongs to the user
        conversation_statement = select(Conversation).where(
            Conversation.id == message_data.conversation_id,
            Conversation.user_id == message_data.user_id
        )
        conversation = self.session.exec(conversation_statement).first()

        if not conversation:
            raise ValueError(f"Conversation {message_data.conversation_id} not found or not owned by user {message_data.user_id}")

        message = Message(
            conversation_id=message_data.conversation_id,
            user_id=message_data.user_id,
            role=message_data.role,
            content=message_data.content,
            message_metadata=message_data.message_metadata
        )

        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        return message

    def get_messages_by_conversation(self, conversation_id: str, user_id: str) -> List[Message]:
        """
        Get all messages for a specific conversation that belong to the user.

        Args:
            conversation_id: ID of the conversation to retrieve messages from
            user_id: ID of the user requesting the messages

        Returns:
            List of Message objects
        """
        # Verify that the conversation belongs to the user
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(conversation_statement).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not owned by user {user_id}")

        # Get all messages for this conversation
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp)

        results = self.session.exec(statement)
        messages = results.all()

        return messages

    def get_message_by_id(self, message_id: str, user_id: str) -> Optional[Message]:
        """
        Get a specific message by ID for a user.

        Args:
            message_id: ID of the message to retrieve
            user_id: ID of the user requesting the message

        Returns:
            Message object if found and owned by user, None otherwise
        """
        statement = select(Message).join(Conversation).where(
            Message.id == message_id,
            Conversation.user_id == user_id
        )
        message = self.session.exec(statement).first()

        return message