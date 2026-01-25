"""
Conversation model for Todo AI Chatbot Agent
Defines the data structure for storing conversation history and messages
"""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class ToolCallStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ToolCall(SQLModel, table=False):
    """Tool call representation within a message"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str  # Name of the MCP tool being called (add_task, list_tasks, etc.)
    arguments: dict  # Arguments passed to the tool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ToolCallStatus = ToolCallStatus.PENDING


class ToolResponse(SQLModel, table=False):
    """Tool response representation"""
    tool_call_id: str  # Reference to the associated tool call
    result: Optional[dict] = None  # Result from the tool execution
    error: Optional[str] = None  # Error message if tool failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=False):
    """Message object in conversation"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole  # Role of message sender (USER, AGENT, SYSTEM)
    content: str  # Text content of the message
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tool_calls: List[ToolCall] = []  # Tool calls associated with this message
    tool_responses: List[ToolResponse] = []  # Responses from tools called


class ConversationState(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    ERROR = "error"


class Conversation(SQLModel, table=True):
    """Conversation entity for storing chat history"""
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str  # Associated user (enforced by JWT/auth)
    messages: List[dict] = Field(default=[])  # Complete conversation history as JSON
    last_tool_calls: List[dict] = Field(default=[])  # Last executed tool calls as JSON
    current_state: ConversationState = ConversationState.IDLE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True