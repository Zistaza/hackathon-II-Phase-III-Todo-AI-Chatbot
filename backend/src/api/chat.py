from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import uuid4
from datetime import datetime
import asyncio
from sqlmodel import Session

from ..models.chat import ChatMessage, ChatResponse, ChatHistoryRequest, ChatHistoryResponse
from ..models.conversation_model import ConversationCreate
from ..models.message_model import MessageCreate
from ..models.user import CurrentUser
from ..dependencies.auth import get_current_user
from ..database import get_session
from ..services.conversation_service import ConversationService
from ..middleware.chat_auth import chat_auth_middleware
from ..exceptions.auth import InsufficientPermissionsException

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

    Args:
        user_id: The ID of the user sending the message (from URL path)
        message: The chat message to send
        current_user: The authenticated user (extracted from JWT token)
        session: Database session for persistence

    Returns:
        ChatResponse: The AI's response to the user's message

    Raises:
        HTTPException: If user is not authorized to access this user's chat
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

    # Get or create a conversation for this user
    conversation_service = ConversationService(session)

    # For this implementation, we'll get the user's most recent conversation or create a new one
    user_conversations = conversation_service.get_user_conversations(user_id=current_user.user_id, limit=1)
    if user_conversations:
        conversation = user_conversations[0]  # Use the most recent conversation
        conversation_id = conversation.id
    else:
        # Create a new conversation if none exists
        conversation_data = ConversationCreate(title=f"Chat with {current_user.email}")
        conversation = conversation_service.create_conversation(
            user_id=current_user.user_id,
            conversation_data=conversation_data
        )
        conversation_id = conversation.id

    # Add user message to conversation
    user_message_data = MessageCreate(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        role=message.role.value if hasattr(message.role, 'value') else message.role,
        content=message.content,
        metadata={"source": "chat_api", "sender_type": "user"}
    )
    user_message = conversation_service.add_message_to_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        message_data=user_message_data
    )

    # Process the message with AI using conversation context
    response_content = await process_chat_message_with_ai(message, current_user, conversation_service, conversation_id)

    # Add AI response to conversation
    ai_message_data = MessageCreate(
        conversation_id=conversation_id,
        user_id=current_user.user_id,  # AI acts on behalf of the user
        role="assistant",
        content=response_content,
        metadata={"source": "ai_response", "sender_type": "assistant"}
    )
    ai_message = conversation_service.add_message_to_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        message_data=ai_message_data
    )

    # Create and return the response
    response = ChatResponse(
        response=response_content,
        message_id=ai_message.id,
        timestamp=ai_message.timestamp,
        conversation_id=conversation_id
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

    Args:
        user_id: The ID of the user whose chat history to retrieve (from URL path)
        request: Request parameters for pagination
        current_user: The authenticated user (extracted from JWT token)
        session: Database session for querying

    Returns:
        ChatHistoryResponse: The chat history for the user
    """
    # Validate that the user_id in the path matches the user_id in the JWT token
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot access chat history for user {user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Get user's conversations and messages using the conversation service
    conversation_service = ConversationService(session)

    # Get user's conversations
    conversations = conversation_service.get_user_conversations(
        user_id=current_user.user_id,
        limit=request.limit,
        offset=request.offset
    )

    # If conversations exist, get messages from the most recent one
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
            # Import ChatRole from models.chat if needed
            from ..models.chat import ChatRole
            role_enum = ChatRole(msg.role) if msg.role in ['user', 'assistant', 'system'] else ChatRole.USER
            chat_msg = ChatMessage(
                content=msg.content,
                role=role_enum,
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


@router.delete("/{user_id}/conversation/{conversation_id}")
async def delete_conversation_endpoint(
    user_id: str,
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific conversation for the user

    Args:
        user_id: The ID of the user whose conversation to delete (from URL path)
        conversation_id: The ID of the conversation to delete
        current_user: The authenticated user (extracted from JWT token)
        session: Database session for deletion

    Returns:
        dict: Success message
    """
    # Validate that the user_id in the path matches the user_id in the JWT token
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Cannot delete conversations for user {user_id}. "
                   f"You are authenticated as user {current_user.user_id}"
        )

    # Use the conversation service to delete the conversation
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


async def process_chat_message_with_ai(message: ChatMessage, user: CurrentUser, conversation_service: ConversationService, conversation_id: str) -> str:
    """
    Process a chat message with AI to generate a response, including conversation context.

    Args:
        message: The chat message to process
        user: The user who sent the message
        conversation_service: Service to retrieve conversation context
        conversation_id: ID of the conversation to get context from

    Returns:
        str: The AI-generated response
    """
    # Retrieve conversation history to provide context to the AI
    # Get recent messages for context (last 10 messages as an example)
    try:
        recent_messages = conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user.user_id,
            limit=10,
            offset=0
        )

        # Prepare context from recent messages
        context_summary = ""
        if recent_messages:
            context_summary = f"\n\nContext from recent conversation: {[msg.content[:50] + '...' for msg in recent_messages[-5:]]}"  # Last 5 messages
    except Exception:
        # If there's an issue getting context, continue without it
        context_summary = ""

    # Simulate AI processing delay
    await asyncio.sleep(0.1)

    # In a real implementation, this would call an AI service like OpenAI
    # with the conversation history as context
    # For now, return a response that acknowledges the conversation context
    response_content = f"I received your message: '{message.content}'. Based on our conversation context, this is an AI response for user {user.email}.{context_summary}"

    return response_content