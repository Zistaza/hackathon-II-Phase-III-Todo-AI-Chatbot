"""
Chat service for Todo AI Chatbot Agent
Handles conversation flow and persistence
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
import asyncio
from ..models.conversation import Conversation, Message, ConversationState
from ..database import get_session
from sqlmodel import select


class ChatService:
    """Service class for handling chat conversations and persistence"""

    def __init__(self):
        # Simple in-memory cache for conversation history
        self.conversation_cache = {}
        self.cache_ttl = 300  # 5 minutes TTL

    async def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for the user"""
        conversation = Conversation(
            user_id=user_id,
            current_state=ConversationState.IDLE
        )

        # Save to database
        async with get_session() as session:
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID for the specific user"""
        async with get_session() as session:
            statement = select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await session.exec(statement)
            return result.first()

    async def save_user_message(self, conversation_id: str, user_id: str, message_content: str) -> Message:
        """Save a user message to the conversation history"""
        # Get conversation
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")

        # Create message
        user_message = Message(
            role="user",
            content=message_content
        )

        # Add to conversation history
        conversation.messages.append(user_message.dict())
        conversation.updated_at = datetime.utcnow()

        # Save to database
        async with get_session() as session:
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

        return user_message

    async def save_agent_response(self, conversation_id: str, user_id: str, response_content: str,
                                 tool_calls: List[Dict] = None) -> Message:
        """Save an agent response to the conversation history"""
        # Get conversation
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")

        # Create message
        agent_message = Message(
            role="agent",
            content=response_content
        )

        # Add tool calls if provided
        if tool_calls:
            agent_message.tool_calls = tool_calls

        # Add to conversation history
        conversation.messages.append(agent_message.dict())
        conversation.updated_at = datetime.utcnow()

        # Save to database
        async with get_session() as session:
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

        return agent_message

    async def reconstruct_conversation_history(self, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Reconstruct full conversation history from database with caching"""
        # Check cache first
        cache_key = f"{conversation_id}:{user_id}"
        cached_result = self.conversation_cache.get(cache_key)

        if cached_result:
            # Check if cache is still valid
            cached_time, cached_data = cached_result
            if (datetime.utcnow() - cached_time).total_seconds() < self.cache_ttl:
                return cached_data

        # Get from database
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")

        history = conversation.messages

        # Cache the result
        self.conversation_cache[cache_key] = (datetime.utcnow(), history)

        return history

    async def update_conversation_state(self, conversation_id: str, user_id: str,
                                      new_state: ConversationState) -> Conversation:
        """Update the state of a conversation"""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")

        conversation.current_state = new_state
        conversation.updated_at = datetime.utcnow()

        # Save to database
        async with get_session() as session:
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

        return conversation