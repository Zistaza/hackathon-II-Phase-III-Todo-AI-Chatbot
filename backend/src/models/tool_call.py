"""
ToolCall model for the Todo AI Chatbot application.
Represents actions initiated by the AI assistant to interact with external systems via MCP tools.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from enum import Enum


class ExecutionStatus(str, Enum):
    """Enumeration for tool call execution statuses."""
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class ToolCall(SQLModel, table=True):
    """
    Represents actions initiated by the AI assistant to interact with external systems via MCP tools.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False)
    message_id: Optional[str] = Field(default=None, foreign_key="messages.id")  # Nullable since not all tool calls are tied to a specific message
    tool_name: str = Field(max_length=255, nullable=False)  # Name of the MCP tool called
    tool_input: Dict[str, Any] = Field(default={}, sa_type=JSON)  # Input parameters passed to the tool (JSON)
    tool_output: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)  # Output received from the tool (JSON)
    execution_status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, nullable=False)  # Execution status
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # When the tool call was initiated

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="tool_calls")
    message: Optional["Message"] = Relationship(back_populates="tool_calls")


class ToolCallCreate(SQLModel):
    """Model for creating a new tool call."""
    conversation_id: str
    message_id: Optional[str] = None
    tool_name: str
    tool_input: Dict[str, Any] = {}
    execution_status: ExecutionStatus = ExecutionStatus.PENDING


class ToolCallUpdate(SQLModel):
    """Model for updating a tool call."""
    tool_output: Optional[Dict[str, Any]] = None
    execution_status: Optional[ExecutionStatus] = None


class ToolCallPublic(SQLModel):
    """Public model for tool call data."""
    id: int
    conversation_id: str
    message_id: Optional[str]
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]]
    execution_status: ExecutionStatus
    timestamp: datetime