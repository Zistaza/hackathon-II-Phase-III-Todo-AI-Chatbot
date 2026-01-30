from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON
from typing import Optional, List
from datetime import datetime
import uuid


class MessageBase(SQLModel):
    """
    Base model for message with common fields
    """
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    role: str = Field(max_length=50, nullable=False)  # 'user', 'assistant', 'system'
    content: str = Field(nullable=False)  # Message content
    message_metadata: Optional[dict] = Field(default=None, sa_type=JSON)  # JSON field for additional settings


class Message(MessageBase, table=True):
    """
    Message model for database storage

    Fields:
    - id: Unique message identifier
    - conversation_id: Reference to the conversation this message belongs to
    - user_id: Reference to the user who sent this message
    - role: Role of the message sender ('user', 'assistant', 'system')
    - content: Message content
    - timestamp: When the message was sent
    - message_metadata: Additional message metadata
    """
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False, index=True)  # Add index for efficient queries
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True)  # Add index for efficient queries
    role: str = Field(max_length=50, nullable=False)
    content: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)  # Add index for chronological queries

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    tool_calls: List["ToolCall"] = Relationship(back_populates="message")


class MessageCreate(MessageBase):
    """
    Model for creating a new message
    """
    conversation_id: str
    user_id: str
    role: str
    content: str


class MessageUpdate(SQLModel):
    """
    Model for updating message information
    """
    content: Optional[str] = None
    message_metadata: Optional[dict] = None


class MessagePublic(MessageBase):
    """
    Public model for message data (includes ID and timestamps)
    """
    id: str
    timestamp: datetime