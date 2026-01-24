from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import uuid4
from datetime import datetime
import asyncio

from ..models.chat import ChatMessage, ChatResponse, ChatHistoryRequest, ChatHistoryResponse
from ..models.user import CurrentUser
from ..dependencies.auth import get_current_user
from ..middleware.chat_auth import chat_auth_middleware
from ..exceptions.auth import InsufficientPermissionsException

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{user_id}", response_model=ChatResponse)
async def send_chat_message(
    user_id: str,
    message: ChatMessage,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Send a chat message and receive an AI response

    Args:
        user_id: The ID of the user sending the message (from URL path)
        message: The chat message to send
        current_user: The authenticated user (extracted from JWT token)

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

    # Process the message with a simulated AI response
    # In a real implementation, this would call an AI service
    response_content = await process_chat_message_with_ai(message, current_user)

    # Generate a unique message ID for the response
    response_message_id = str(uuid4())
    conversation_id = str(uuid4())  # In a real app, this would come from conversation context

    # Create and return the response
    response = ChatResponse(
        response=response_content,
        message_id=response_message_id,
        timestamp=datetime.utcnow(),
        conversation_id=conversation_id
    )

    return response


@router.get("/{user_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    request: ChatHistoryRequest = Depends(),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get chat history for the specified user

    Args:
        user_id: The ID of the user whose chat history to retrieve (from URL path)
        request: Request parameters for pagination
        current_user: The authenticated user (extracted from JWT token)

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

    # In a real implementation, this would fetch from a database
    # For now, return empty history
    return ChatHistoryResponse(
        messages=[],
        total_count=0,
        has_more=False
    )


@router.delete("/{user_id}/conversation/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Delete a specific conversation for the user

    Args:
        user_id: The ID of the user whose conversation to delete (from URL path)
        conversation_id: The ID of the conversation to delete
        current_user: The authenticated user (extracted from JWT token)

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

    # In a real implementation, this would delete from a database
    # For now, just return success
    return {"message": f"Conversation {conversation_id} deleted successfully"}


async def process_chat_message_with_ai(message: ChatMessage, user: CurrentUser) -> str:
    """
    Process a chat message with AI to generate a response.

    Args:
        message: The chat message to process
        user: The user who sent the message

    Returns:
        str: The AI-generated response
    """
    # Simulate AI processing delay
    await asyncio.sleep(0.1)

    # In a real implementation, this would call an AI service like OpenAI
    # For now, return a simple echo response
    response_content = f"I received your message: '{message.content}'. This is a simulated AI response for user {user.email}."

    return response_content