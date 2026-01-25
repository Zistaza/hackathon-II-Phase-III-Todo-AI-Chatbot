"""
Chat router for Todo AI Chatbot Agent
Defines the API endpoints for chat functionality
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta
from collections import defaultdict
from ..dependencies.auth import get_current_user
from ..services.chat_service import ChatService
from ..services.mcp_integration import MCPIntegration
from ..models.conversation import ConversationState
from ..agents.todo_chatbot.agent import Agent, AgentConfig


router = APIRouter(prefix="/api/{user_id}", tags=["chat"])

# Initialize services
chat_service = ChatService()
mcp_integration = MCPIntegration()
agent = Agent(AgentConfig())

# Rate limiting storage
user_request_times = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_MINUTE = 10  # Configurable rate limit


@router.post("/chat")
async def process_chat_message(
    user_id: str,
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Process a chat message from the user and return the agent's response

    Args:
        user_id: The ID of the user making the request
        request: The chat request containing the message
        current_user: The authenticated user (from JWT)

    Returns:
        The agent's response with any tool calls made
    """

    # Verify that the user_id in the URL matches the authenticated user
    if current_user.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    # Implement rate limiting
    current_time = datetime.utcnow()
    user_request_times[user_id] = [
        req_time for req_time in user_request_times[user_id]
        if current_time - req_time < timedelta(seconds=RATE_LIMIT_WINDOW)
    ]

    if len(user_request_times[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_MINUTE} requests per minute."
        )

    # Add current request to tracking
    user_request_times[user_id].append(current_time)

    # Extract message from request
    message = request.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Get or create conversation ID
    conversation_id = request.get("conversation_id", str(uuid4()))

    # Check if conversation exists, create if not
    conversation = await chat_service.get_conversation(conversation_id, user_id)
    if not conversation:
        conversation = await chat_service.create_conversation(user_id)
        conversation_id = conversation.conversation_id

    # Save user message to conversation history
    await chat_service.save_user_message(conversation_id, user_id, message)

    # Update conversation state to processing
    await chat_service.update_conversation_state(conversation_id, user_id, ConversationState.PROCESSING)

    try:
        # Call the agent to process the message
        response_data = await agent.process_message(user_id, conversation_id, message)

        # Ensure conversation_id is consistent
        response_data["conversation_id"] = conversation_id

        # Save agent response to conversation history
        await chat_service.save_agent_response(
            conversation_id,
            user_id,
            response_data["response"],
            response_data.get("tool_calls", [])
        )
    except Exception as e:
        # Handle any errors during agent processing
        error_response = {
            "conversation_id": conversation_id,
            "response": f"Sorry, I encountered an error processing your request: {str(e)}",
            "tool_calls": [],
            "next_action": "completed",
            "timestamp": "2026-01-26T00:00:00Z"
        }

        # Save error response to conversation history
        await chat_service.save_agent_response(
            conversation_id,
            user_id,
            error_response["response"],
            error_response["tool_calls"]
        )

        # Update conversation state back to idle
        await chat_service.update_conversation_state(conversation_id, user_id, ConversationState.IDLE)

        return error_response

    # Update conversation state back to idle
    await chat_service.update_conversation_state(conversation_id, user_id, ConversationState.IDLE)

    return response_data