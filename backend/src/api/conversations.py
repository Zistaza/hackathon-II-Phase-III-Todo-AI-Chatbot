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