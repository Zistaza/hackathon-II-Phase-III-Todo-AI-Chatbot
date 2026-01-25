from sqlmodel import Session, select
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
import time

from ..models.conversation_model import Conversation, ConversationCreate
from ..models.message_model import Message, MessageCreate
from ..models.user import CurrentUser

# Simple in-memory cache for conversation data
CONVERSATION_CACHE = {}
CACHE_TTL_SECONDS = 300  # 5 minutes TTL


class ConversationService:
    """
    Service class for handling conversation and message operations
    with proper authentication and authorization checks.
    """

    def __init__(self, session: Session):
        self.session = session

    def _get_cache_key(self, user_id: str, conversation_id: str = None, operation: str = "general"):
        """Generate a cache key for the given parameters"""
        if conversation_id:
            return f"{operation}:{user_id}:{conversation_id}"
        return f"{operation}:{user_id}"

    def _is_cache_valid(self, cache_entry):
        """Check if a cache entry is still valid based on TTL"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        return (time.time() - cache_entry['timestamp']) < CACHE_TTL_SECONDS

    def _get_from_cache(self, key: str):
        """Get value from cache if it exists and is valid"""
        cache_entry = CONVERSATION_CACHE.get(key)
        if self._is_cache_valid(cache_entry):
            return cache_entry['value']
        # Remove expired entry
        if cache_entry:
            del CONVERSATION_CACHE[key]
        return None

    def _set_cache(self, key: str, value):
        """Set value in cache with timestamp"""
        CONVERSATION_CACHE[key] = {
            'value': value,
            'timestamp': time.time()
        }

    def _invalidate_cache_for_user(self, user_id: str):
        """Invalidate all cached entries for a specific user"""
        keys_to_remove = []
        for key in CONVERSATION_CACHE:
            if f":{user_id}:" in key or key.endswith(f":{user_id}"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del CONVERSATION_CACHE[key]

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
            metadata=conversation_data.metadata
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        # Invalidate user's conversation cache
        self._invalidate_cache_for_user(user_id)

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
        # Try to get from cache first
        cache_key = self._get_cache_key(user_id, operation=f"conversations_{limit}_{offset}")
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # Query from database
        statement = select(Conversation).where(Conversation.user_id == user_id).offset(offset).limit(limit)
        results = self.session.exec(statement)
        conversations = results.all()

        # Cache the result
        self._set_cache(cache_key, conversations)

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
        # Try to get from cache first
        cache_key = self._get_cache_key(user_id, conversation_id, operation="conversation")
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # Query from database
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()

        # Cache the result if found
        if conversation:
            self._set_cache(cache_key, conversation)

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

        # Invalidate message cache for this conversation
        # We need to remove all cached message lists for this conversation
        keys_to_remove = []
        for key in CONVERSATION_CACHE:
            if f":{user_id}:{conversation_id}:" in key and "messages_" in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del CONVERSATION_CACHE[key]

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

        # Try to get from cache first
        cache_key = self._get_cache_key(user_id, conversation_id, operation=f"messages_{limit}_{offset}")
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # Query from database
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).offset(offset).limit(limit)

        results = self.session.exec(statement)
        messages = results.all()

        # Cache the result
        self._set_cache(cache_key, messages)

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

        # Invalidate user's conversation cache
        self._invalidate_cache_for_user(user_id)

        return True