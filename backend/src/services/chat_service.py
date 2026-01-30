"""
Chat service for Todo AI Chatbot Agent
Handles conversation flow and persistence
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
import asyncio
from ..models.conversation import Conversation, Message, ConversationState
from ..database import engine
from sqlmodel import Session
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

        # Save to database using engine directly
        def _create_conversation_sync():
            with Session(engine) as session:
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                return conversation

        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _create_conversation_sync)
        return result

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID for the specific user"""
        def _get_conversation_sync():
            with Session(engine) as session:
                statement = select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
                result = session.execute(statement)
                return result.first()

        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get_conversation_sync)

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

        # Save to database using engine directly
        def _save_user_message_sync():
            with Session(engine) as session:
                # Get the conversation from the database to avoid detached instance issues
                db_conversation = session.get(Conversation, conversation.id)

                if not db_conversation:
                    raise ValueError(f"Conversation {conversation_id} not found in database")

                # Add to conversation history
                db_conversation.messages.append(user_message.dict())
                db_conversation.updated_at = datetime.utcnow()

                # Save to database
                session.add(db_conversation)
                session.commit()
                session.refresh(db_conversation)

                return user_message

        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _save_user_message_sync)
        return result

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

        # Save to database using engine directly
        def _save_agent_response_sync():
            with Session(engine) as session:
                # Get the conversation from the database to avoid detached instance issues
                db_conversation = session.get(Conversation, conversation.id)

                if not db_conversation:
                    raise ValueError(f"Conversation {conversation_id} not found in database")

                # Add to conversation history
                db_conversation.messages.append(agent_message.dict())
                db_conversation.updated_at = datetime.utcnow()

                # Save to database
                session.add(db_conversation)
                session.commit()
                session.refresh(db_conversation)

                return agent_message

        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _save_agent_response_sync)
        return result

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

        # Save to database using engine directly
        def _update_conversation_state_sync():
            with Session(engine) as session:
                # Get the conversation from the database to avoid detached instance issues
                db_conversation = session.get(Conversation, conversation.id)

                if not db_conversation:
                    raise ValueError(f"Conversation {conversation_id} not found in database")

                # Update state and timestamp
                db_conversation.current_state = new_state
                db_conversation.updated_at = datetime.utcnow()

                # Save to database
                session.add(db_conversation)
                session.commit()
                session.refresh(db_conversation)

                return db_conversation

        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _update_conversation_state_sync)
        return result

        return conversation