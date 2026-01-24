from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChatRole(str, Enum):
    """
    Enumeration of possible roles in a chat conversation
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """
    Model representing a chat message sent by the user

    Fields:
    - content: The content of the message
    - role: The role of the message sender (user, assistant, system)
    - timestamp: When the message was created (optional, set by server)
    """
    content: str
    role: ChatRole = ChatRole.USER
    timestamp: Optional[datetime] = None


class ChatResponse(BaseModel):
    """
    Model representing a response from the chat API

    Fields:
    - response: The content of the response from the AI assistant
    - message_id: Unique identifier for the response message
    - timestamp: When the response was generated
    - conversation_id: ID of the conversation this message belongs to
    """
    response: str
    message_id: str
    timestamp: datetime
    conversation_id: str


class ChatHistoryRequest(BaseModel):
    """
    Model for requesting chat history

    Fields:
    - limit: Maximum number of messages to return
    - offset: Number of messages to skip (for pagination)
    """
    limit: int = 10
    offset: int = 0


class ChatHistoryResponse(BaseModel):
    """
    Model representing chat history response

    Fields:
    - messages: List of chat messages in the conversation
    - total_count: Total number of messages in the conversation
    - has_more: Whether there are more messages available
    """
    messages: List[ChatMessage]
    total_count: int
    has_more: bool