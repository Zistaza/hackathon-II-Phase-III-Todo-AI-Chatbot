---
name: chat-api-iii-skill
description: Implement and manage backend chat API endpoint, integrating AI agents with MCP tools via Official MCP SDK, ensuring stateless, secure, and multi-tenant operation for Phase-III Todo AI Chatbot.
---

# Chat API Skill (Phase III)

## Instructions

1. **POST /api/{user_id}/chat endpoint**
   - Accept requests with fields:
     - `conversation_id` (optional)
     - `message` (required)
   - Validate JWT token and ensure user identity matches authenticated token
   - Reject unauthorized requests with HTTP 401

2. **Conversation history management**
   - Fetch prior messages and conversation context from the database
   - Build structured message array for AI agent reasoning
   - Store incoming user messages and outgoing AI responses in the database
   - Ensure conversation replayable after server restart

3. **AI agent invocation**
   - Call AI agents using OpenAI Agents SDK
   - Pass conversation context and new message
   - Respect Phase-III Agent Behavior specifications
   - Receive actions, tool calls, and responses from the agent

4. **MCP tool integration**
   - Route all MCP tool calls exclusively through MCP Server via Official MCP SDK
   - Ensure statelessness by not persisting server-side memory
   - Validate all tool parameters and enforce user ownership

5. **Response structure**
   - Return JSON including:
     - `conversation_id`
     - `response` (AI assistant reply)
     - `tool_calls` (list of MCP tools invoked)
   - Maintain clear, structured, and consistent response formatting

6. **Security and multi-tenancy**
   - Validate JWT authentication for every request
   - Enforce multi-tenant isolation so users can only access their own data
   - Log unauthorized or invalid requests for audit

## Best Practices
- Keep backend stateless; all state persisted in database
- Always validate user input and token before processing
- Separate concerns: endpoint handles orchestration, agent handles reasoning, MCP tools handle actions
- Ensure consistent response format for frontend integration
- Maintain structured logs for debugging and auditing

## Example Structure
```python
from fastapi import FastAPI, Request, HTTPException
from openai_agents_sdk import AgentRunner
from mcp_sdk import MCPClient
from database import fetch_conversation_history, save_message
from auth_skill import AuthSkill

app = FastAPI()
auth_skill = AuthSkill()
mcp_client = MCPClient()
agent_runner = AgentRunner()

@app.post("/api/{user_id}/chat")
async def chat_endpoint(user_id: str, payload: dict):
    token = payload.get("jwt")
    message = payload.get("message")
    
    # Validate JWT and user
    if not auth_skill.validate_jwt(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not auth_skill.verify_user_identity(user_id, token):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Fetch conversation context
    conversation_id = payload.get("conversation_id")
    context = fetch_conversation_history(user_id, conversation_id)
    
    # Store user message
    save_message(user_id, conversation_id, role="user", content=message)
    
    # Run agent with context
    agent_response = agent_runner.run(message, context)
    
    # Invoke MCP tools via Official MCP SDK
    tool_calls = []
    for tool in agent_response.get("tools", []):
        result = mcp_client.call_tool(user_id=user_id, **tool)
        tool_calls.append(result)
    
    # Save AI response
    save_message(user_id, conversation_id, role="assistant", content=agent_response["response"])
    
    return {
        "conversation_id": conversation_id,
        "response": agent_response["response"],
        "tool_calls": tool_calls
    }
