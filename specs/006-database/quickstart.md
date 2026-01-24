# Quickstart: Todo AI Chatbot Database Schema

## Overview
Quick setup guide for implementing the Todo AI Chatbot database schema with conversation persistence and MCP tool integration.

## Prerequisites

### Environment Setup
```bash
# Install Python dependencies
pip install sqlmodel fastapi psycopg2-binary

# Set up environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/todo_ai_chatbot"
export BETTER_AUTH_SECRET="your-secret-key-here"
```

### Database Preparation
```sql
-- Create the database (if not already created)
CREATE DATABASE todo_ai_chatbot;

-- Extension for UUID generation (if using PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Database Initialization

### 1. Create New Models
Create the following files in `backend/src/models/`:

**conversation_model.py**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class ConversationBase(SQLModel):
    """
    Base model for conversation with common fields
    """
    title: Optional[str] = Field(default=None, max_length=255)
    metadata: Optional[dict] = Field(default=None)  # JSON field for additional settings


class Conversation(ConversationBase, table=True):
    """
    Conversation model for database storage

    Fields:
    - id: Unique conversation identifier
    - user_id: Reference to the user who owns this conversation
    - title: Conversation title (optional)
    - created_at: Conversation creation timestamp
    - updated_at: Last update timestamp
    - metadata: Additional conversation metadata
    """
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None)  # JSON field


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
    metadata: Optional[dict] = None


class ConversationPublic(ConversationBase):
    """
    Public model for conversation data (includes ID and timestamps)
    """
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
```

**message_model.py**:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
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
    metadata: Optional[dict] = Field(default=None)  # JSON field for additional settings


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
    - metadata: Additional message metadata
    """
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", nullable=False)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    role: str = Field(max_length=50, nullable=False)
    content: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(default=None)  # JSON field


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
    metadata: Optional[dict] = None


class MessagePublic(MessageBase):
    """
    Public model for message data (includes ID and timestamps)
    """
    id: str
    timestamp: datetime
```

### 2. Update Database Initialization
Update `backend/src/database.py` to include the new models:

```python
def init_db():
    """
    Initialize the database by creating all tables
    """
    from .models.user_model import User  # Import models to register them
    from .models.task_model import Task  # Import Task model to register it
    from .models.conversation_model import Conversation  # Import new model
    from .models.message_model import Message  # Import new model
    from .models.mcp_tool import MCPToolMetadata  # Import existing model
    from sqlmodel import SQLModel

    # Create all tables
    SQLModel.metadata.create_all(engine)
```

### 3. Create Conversation Service
Create `backend/src/services/conversation_service.py`:

```python
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
            metadata=conversation_data.metadata
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return conversation

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
        statement = select(Conversation).where(Conversation.user_id == user_id).offset(offset).limit(limit)
        results = self.session.exec(statement)
        return results.all()

    def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID for a user

        Args:
            conversation_id: ID of the conversation to retrieve
            user_id: ID of the user requesting the conversation

        Returns:
            Conversation object if found and owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return self.session.exec(statement).first()

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

        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).offset(offset).limit(limit)

        results = self.session.exec(statement)
        return results.all()

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
```

### 4. Create Conversation API Endpoints
Create `backend/src/api/conversations.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from uuid import uuid4

from ..models.conversation_model import Conversation, ConversationCreate, ConversationPublic
from ..models.message_model import Message, MessageCreate, MessagePublic
from ..models.user import CurrentUser
from ..dependencies.auth import get_current_user
from ..database import get_session
from ..services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationPublic)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new conversation for the authenticated user
    """
    # Validate that the user_id in the JWT token matches the authenticated user
    if current_user.user_id != conversation_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot create conversation for user {conversation_data.user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    conversation_service = ConversationService(session)
    conversation = conversation_service.create_conversation(
        user_id=current_user.user_id,
        conversation_data=conversation_data
    )

    return conversation


@router.get("/", response_model=List[ConversationPublic])
def get_user_conversations(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0
):
    """
    Get all conversations for the authenticated user
    """
    conversation_service = ConversationService(session)
    conversations = conversation_service.get_user_conversations(
        user_id=current_user.user_id,
        limit=limit,
        offset=offset
    )

    return conversations


@router.get("/{conversation_id}", response_model=ConversationPublic)
def get_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific conversation for the authenticated user
    """
    conversation_service = ConversationService(session)
    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found or not owned by user {current_user.user_id}"
        )

    return conversation


@router.post("/{conversation_id}/messages", response_model=MessagePublic)
def add_message_to_conversation(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add a message to a specific conversation
    """
    # Validate that the user_id in the JWT token matches the authenticated user
    if current_user.user_id != message_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot add message for user {message_data.user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    conversation_service = ConversationService(session)
    message = conversation_service.add_message_to_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        message_data=message_data
    )

    return message


@router.get("/{conversation_id}/messages", response_model=List[MessagePublic])
def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0
):
    """
    Get messages from a specific conversation
    """
    conversation_service = ConversationService(session)
    messages = conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        limit=limit,
        offset=offset
    )

    return messages


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific conversation
    """
    conversation_service = ConversationService(session)
    success = conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found or not owned by user {current_user.user_id}"
        )

    return {"message": f"Conversation {conversation_id} deleted successfully"}
```

### 5. Update Main Application
Update `backend/src/main.py` to include the new conversation routes:

```python
from fastapi import FastAPI
from .api import auth, tasks, chat, mcp_tools, conversations

app = FastAPI(title="Todo AI Chatbot API")

# Include all API routes
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(mcp_tools.router)
app.include_router(conversations.router)
```

### 6. Update Chat API for Conversation Integration
Update the existing `backend/src/api/chat.py` to use the new conversation models:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import uuid4
from datetime import datetime
import asyncio

from ..models.chat import ChatMessage, ChatResponse, ChatHistoryRequest, ChatHistoryResponse
from ..models.conversation_model import ConversationCreate
from ..models.message_model import MessageCreate
from ..models.user import CurrentUser
from ..dependencies.auth import get_current_user
from ..database import get_session
from ..services.conversation_service import ConversationService
from ..services.mcp_service import get_mcp_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{user_id}", response_model=ChatResponse)
async def send_chat_message(
    user_id: str,
    message: ChatMessage,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Send a chat message and receive an AI response
    """
    # Validate that the user_id in the path matches the user_id in the JWT token
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot access chat for user {user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Set timestamp if not provided
    if message.timestamp is None:
        message.timestamp = datetime.utcnow()

    # Create or get conversation
    conversation_service = ConversationService(session)

    # For this example, we'll create a new conversation for each chat
    # In practice, you might want to associate with an existing conversation
    conversation_data = ConversationCreate(title=f"Chat with {current_user.email}")
    conversation = conversation_service.create_conversation(
        user_id=current_user.user_id,
        conversation_data=conversation_data
    )

    # Add user message to conversation
    user_message_data = MessageCreate(
        conversation_id=conversation.id,
        user_id=current_user.user_id,
        role=message.role.value,
        content=message.content,
        metadata={"source": "chat_api"}
    )
    user_message = conversation_service.add_message_to_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation.id,
        message_data=user_message_data
    )

    # Process the message with AI
    response_content = await process_chat_message_with_ai(message, current_user, conversation_service, conversation.id)

    # Add AI response to conversation
    ai_message_data = MessageCreate(
        conversation_id=conversation.id,
        user_id=current_user.user_id,  # AI acts on behalf of the user
        role="assistant",
        content=response_content,
        metadata={"source": "ai_response"}
    )
    ai_message = conversation_service.add_message_to_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation.id,
        message_data=ai_message_data
    )

    # Create and return the response
    response = ChatResponse(
        response=response_content,
        message_id=ai_message.id,
        timestamp=ai_message.timestamp,
        conversation_id=conversation.id
    )

    return response


@router.get("/{user_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    request: ChatHistoryRequest = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get chat history for the specified user
    """
    # Validate that the user_id in the path matches the user_id in the JWT token
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot access chat history for user {user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Get user's conversations and messages
    conversation_service = ConversationService(session)
    conversations = conversation_service.get_user_conversations(
        user_id=current_user.user_id,
        limit=request.limit,
        offset=request.offset
    )

    # For this example, we'll return messages from the most recent conversation
    # In practice, you might want to return messages from all conversations
    if conversations:
        latest_conversation = conversations[0]  # Most recent first
        messages = conversation_service.get_conversation_messages(
            conversation_id=latest_conversation.id,
            user_id=current_user.user_id,
            limit=request.limit,
            offset=request.offset
        )

        # Convert to ChatMessage format
        chat_messages = []
        for msg in messages:
            chat_msg = ChatMessage(
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp
            )
            chat_messages.append(chat_msg)

        return ChatHistoryResponse(
            messages=chat_messages,
            total_count=len(chat_messages),
            has_more=len(chat_messages) >= request.limit
        )

    # Return empty history if no conversations
    return ChatHistoryResponse(
        messages=[],
        total_count=0,
        has_more=False
    )


async def process_chat_message_with_ai(message: ChatMessage, user: CurrentUser, conversation_service: ConversationService, conversation_id: str) -> str:
    """
    Process a chat message with AI to generate a response, including conversation context.
    """
    # Retrieve conversation history to provide context to the AI
    # In a real implementation, this would call an AI service like OpenAI
    # with the conversation history as context

    # For this example, we'll simulate retrieving the conversation context
    # and return a response that acknowledges the conversation history

    # Get recent messages for context (last 10 messages as an example)
    recent_messages = conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=user.user_id,
        limit=10,
        offset=0
    )

    # In a real implementation, pass these messages to an AI service
    # For now, return a simulated response
    response_content = f"I received your message: '{message.content}'. Based on our conversation context, this is an AI response for user {user.email}."

    return response_content
```

## MCP Tool Integration

### Example MCP Tool Operations with Conversation Data

The new database schema enables MCP tools to operate on conversation and message data:

```python
# Example MCP tool that creates a task from a conversation message
async def handle_create_task_from_message(tool_request: MCPToolRequest, session: Session):
    # Extract message ID from parameters
    message_id = tool_request.parameters.get('message_id')

    # Verify user owns the message
    statement = select(Message).where(
        Message.id == message_id,
        Message.user_id == tool_request.user_id
    )
    message = session.exec(statement).first()

    if not message:
        raise ValueError(f"Message {message_id} not found or not owned by user")

    # Create task based on message content
    task_title = f"Action item: {message.content[:50]}..."
    new_task = Task(
        title=task_title,
        description=f"Created from conversation message: {message.content}",
        user_id=tool_request.user_id
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return {"task_created": new_task.id, "message_used": message.id}
```

## Testing the Implementation

### 1. Run Database Initialization
```bash
# Make sure your database is running and DATABASE_URL is set
python -c "from backend.src.database import init_db; init_db()"
```

### 2. Start the API Server
```bash
cd backend
uvicorn src.main:app --reload
```

### 3. Test API Endpoints
```bash
# Create a conversation
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Conversation"}'

# Add a message to the conversation
curl -X POST http://localhost:8000/api/conversations/CONVERSATION_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello, AI assistant!"}'

# Get conversation history
curl -X GET http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Use chat API with persistent conversations
curl -X POST http://localhost:8000/api/chat/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Please create a task for me", "role": "user"}'
```

## MCP Tool Operations with Conversation Context

The enhanced MCP service now supports conversation-related operations:

### Create Conversation via MCP Tool
```bash
curl -X POST http://localhost:8000/api/mcp/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "conversation-tool",
    "user_id": "YOUR_USER_ID",
    "action": "create_conversation",
    "resources": [],
    "parameters": {
      "title": "MCP-Generated Conversation",
      "metadata": {"source": "mcp_tool"}
    }
  }'
```

### Add Message via MCP Tool
```bash
curl -X POST http://localhost:8000/api/mcp/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "conversation-tool",
    "user_id": "YOUR_USER_ID",
    "action": "add_message",
    "resources": [],
    "parameters": {
      "conversation_id": "CONVERSATION_ID",
      "content": "Message from MCP tool",
      "role": "assistant",
      "metadata": {"source": "mcp_tool"}
    }
  }'
```

## Testing the Implementation

### 1. Run Database Initialization
```bash
# Make sure your database is running and DATABASE_URL is set
python -c "from backend.src.database import init_db; init_db()"
```

### 2. Start the API Server
```bash
cd backend
uvicorn src.main:app --reload
```

### 3. Test API Endpoints
```bash
# Create a conversation
curl -X POST http://localhost:8000/conversations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Conversation"}'

# Add a message to the conversation
curl -X POST http://localhost:8000/conversations/CONVERSATION_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello, AI assistant!"}'
```