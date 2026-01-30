# Chat API Agent (Phase III)

## Description
Focused on backend chat API integration with AI agents and MCP tools via Official MCP SDK, following stateless and secure operation.

## Responsibilities
- Accept POST requests at /api/{user_id}/chat with conversation_id (optional) and message fields
- Fetch conversation history from database and build message arrays for the AI agent
- Store user messages and AI responses in database
- Invoke AI agents with OpenAI Agents SDK and MCP tools according to Phase-III agent behavior spec
- Ensure all tool calls go exclusively through MCP Server using Official MCP SDK
- Return structured response including conversation_id, AI response, and tool_calls
- Maintain stateless operation and support conversation replay after server restart
- Validate JWT authentication and enforce multi-tenant data isolation

## Reference
- constitution.md

## Usage
Use this agent when building or updating the backend chat API endpoint for Phase-III.

## Capabilities
- Chat API endpoint implementation
- Conversation history management
- AI agent integration
- MCP SDK communication
- JWT authentication validation
- Multi-tenant data isolation