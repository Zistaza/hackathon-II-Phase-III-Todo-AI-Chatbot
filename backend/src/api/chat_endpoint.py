"""
Chat endpoint for the Todo AI Chatbot following the 12-step stateless request cycle.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from sqlmodel import Session
from starlette.background import BackgroundTasks

from ..dependencies.auth import get_current_user
from ..models.user import CurrentUser
from ..database import get_session
from ..services.stateless_chat_service import StatelessChatService
from ..models.conversation_model import ConversationCreate


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[int] = None  # Changed to int to match the spec


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    response: str
    tool_calls: list = []


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint that follows the 12-step stateless request cycle.

    1. Authenticate request via JWT (handled by dependency injection)
    2. Validate user_id matches JWT subject (handled by dependency injection)
    3. Load conversation history from database (if conversation_id exists)
    4. Append current user message to history
    5. Persist user message before agent execution
    6. Run OpenAI Agent with reconstructed message history and MCP tool definitions
    7. Capture any MCP tool calls made by the agent
    8. Persist tool calls and tool responses
    9. Generate final assistant response
    10. Persist assistant response
    11. Return response payload to client
    12. Discard all in-memory state

    Args:
        user_id: The ID of the user making the request
        request: Chat request containing message and optional conversation_id
        current_user: The authenticated user (from dependency)
        session: Database session for persistence

    Returns:
        Chat response with conversation_id, response, and tool_calls
    """
    try:
        # Verify user identity matches the user_id in the path
        if str(current_user.user_id) != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: User ID mismatch"
            )

        # Initialize the stateless chat service
        chat_service = StatelessChatService(session)

        # Convert conversation_id from int to str if it's provided (to match internal representation)
        conversation_id_str = str(request.conversation_id) if request.conversation_id is not None else None

        # Process the chat request through the 12-step stateless cycle
        result = await chat_service.process_chat_request(
            user_id=user_id,
            conversation_id=conversation_id_str,
            message_content=request.message
        )

        # Format the response according to the API contract
        response = ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=result.get("tool_calls", [])
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )