from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from typing import Optional, List
from datetime import datetime
import uuid


class ConversationBase(SQLModel):
    """
    Base model for conversation with common fields
    """
    title: Optional[str] = Field(default=None, max_length=255)
    conversation_metadata: Optional[dict] = Field(default=None, sa_type=JSON)  # JSON field for additional settings


class Conversation(ConversationBase, table=True):
    """
    Conversation model for database storage

    Fields:
    - id: Unique conversation identifier
    - user_id: Reference to the user who owns this conversation
    - title: Conversation title (optional)
    - created_at: Conversation creation timestamp
    - updated_at: Last update timestamp
    - conversation_metadata: Additional conversation metadata
    """
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)  # Add index for efficient queries
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index for chronological queries
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    tool_calls: List["ToolCall"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """
    Model for creating a new conversation
    """
    title: Optional[str] = None


class ConversationUpdate(SQLModel):
    """
    Model for updating conversation information
    """
    title: Optional[str] = None
    conversation_metadata: Optional[dict] = Field(default=None, sa_type=JSON)


class ConversationPublic(ConversationBase):
    """
    Public model for conversation data (includes ID and timestamps)
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime