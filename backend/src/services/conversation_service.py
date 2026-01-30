from sqlmodel import Session, select
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from ..models.conversation_model import Conversation, ConversationCreate
from ..models.message_model import Message, MessageCreate
from ..models.user import CurrentUser

class ConversationService:
    """
    Service class for handling conversation and message operations
    with proper authentication and authorization checks.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: str, conversation_data: ConversationCreate) -> Conversation:
        """
        Create a new conversation for a user

        Args:
            user_id: ID of the user creating the conversation
            conversation_data: Data for the new conversation

        Returns:
            Created Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=conversation_data.title,
            conversation_metadata=conversation_data.conversation_metadata
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return conversation

    def get_by_user(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Conversation]:
        """
        Get all conversations for a user (matching the task requirement)

        Args:
            user_id: ID of the user whose conversations to retrieve
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of Conversation objects
        """
        # Query from database
        statement = select(Conversation).where(Conversation.user_id == user_id).offset(offset).limit(limit)
        results = self.session.exec(statement)
        conversations = results.all()

        return conversations

    def get_user_conversations(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Conversation]:
        """
        Get all conversations for a user

        Args:
            user_id: ID of the user whose conversations to retrieve
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of Conversation objects
        """
        return self.get_by_user(user_id, limit, offset)

    def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID for a user

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the user requesting the conversation

        Returns:
            Conversation object if found and owned by user, None otherwise
        """
        # Query from database
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()

        return conversation

    def add_message_to_conversation(self, user_id: str, conversation_id: str, message_data: MessageCreate) -> Message:
        """
        Add a message to a conversation

        Args:
            user_id: ID of the user sending the message
            conversation_id: ID of the conversation to add message to
            message_data: Data for the new message

        Returns:
            Created Message object
        """
        # Verify that the conversation belongs to the user
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not owned by user {user_id}")

        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata
        )

        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        return message

    def get_conversation_messages(self, conversation_id: str, user_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        """
        Get messages from a specific conversation for a user

        Args:
            conversation_id: ID of the conversation to retrieve messages from
            user_id: ID of the user requesting the messages
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message objects
        """
        # Verify that the conversation belongs to the user
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or not owned by user {user_id}")

        # Query from database
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).offset(offset).limit(limit)

        results = self.session.exec(statement)
        messages = results.all()

        return messages

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation for a user

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user requesting deletion

        Returns:
            True if conversation was deleted, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        self.session.delete(conversation)
        self.session.commit()

        return True