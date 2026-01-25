# Implementation Plan: Todo AI Chatbot - Chat API

**Branch**: `009-todo-chatbot-api` | **Date**: 2026-01-26 | **Spec**: [Todo AI Chatbot API Specification](./spec.md)
**Input**: Feature specification from `/specs/009-todo-chatbot-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a stateless chat API endpoint that integrates OpenAI Agents SDK with MCP tools to provide AI-powered todo management. The system follows a strict 12-step stateless request-cycle to ensure horizontal scalability and multi-tenant isolation through JWT validation. The backend processes natural language user input, orchestrates agent execution with conversation history, captures MCP tool calls, and returns deterministic responses.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Better Auth
**Storage**: Neon Serverless PostgreSQL via SQLModel ORM
**Testing**: pytest for unit/integration tests
**Target Platform**: Linux server (cloud-native)
**Project Type**: web (backend API with potential frontend integration)
**Performance Goals**: 95% of requests complete within 5 seconds under normal load
**Constraints**: Stateless operation, no server-side memory/caches/session storage, JWT authentication required for all requests
**Scale/Scope**: Horizontally scalable to support multiple concurrent users with multi-tenant isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Security by Default**: All requests authenticated via JWT; backend rejects unauthenticated requests with HTTP 401
- ✅ **Multi-Tenant Isolation**: User ID in path must match user ID in JWT; cross-user data access forbidden
- ✅ **Deterministic APIs**: Follows exact 12-step stateless request-cycle with predictable behavior
- ✅ **Cloud-Native Design**: Stateless backend, serverless-friendly database usage with Neon PostgreSQL
- ✅ **Technology Standards**: Uses required stack (Python FastAPI, SQLModel, Neon PostgreSQL, Better Auth with JWT)
- ✅ **REST API Contract**: Implements POST /api/{user_id}/chat endpoint as specified

## Project Structure

### Documentation (this feature)

```text
specs/009-todo-chatbot-api/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py      # Conversation entity
│   │   ├── message.py          # Message entity
│   │   └── tool_call.py        # Tool call entity
│   ├── services/
│   │   ├── auth.py           # JWT validation and user verification
│   │   ├── conversation.py   # Conversation management
│   │   ├── agent.py          # OpenAI Agent orchestration
│   │   └── mcp_tools.py      # MCP tool integration
│   ├── api/
│   │   └── chat.py           # Main chat endpoint implementation
│   └── main.py               # Application entry point
└── tests/
    ├── unit/
    │   ├── test_auth.py
    │   ├── test_conversation.py
    │   └── test_agent.py
    ├── integration/
    │   └── test_chat_endpoint.py
    └── contract/
        └── test_stateless_behavior.py
```

**Structure Decision**: Web application structure with dedicated backend for the chat API. The backend contains models for conversation management, services for business logic, and API endpoints. Tests are organized by type (unit, integration, contract) to ensure proper validation of stateless behavior and multi-tenant isolation.

## Architecture Sketch

```
┌─────────────────┐    1. POST /api/{user_id}/chat    ┌──────────────────┐
│   ChatKit       │ ─────────────────────────────────▶ │  FastAPI         │
│   Frontend      │                                    │  Backend         │
└─────────────────┘                                    └──────────────────┘
                                                               │
                    2. JWT Validation & User ID Match          │
                    ┌───────────────────────────────────────── │
                    ▼                                          ▼
         ┌─────────────────────────────────────────────────────────────┐
         │                     Conversation History                    │
         │  ┌─────────────────┐    ┌─────────────────────────────────┐ │
         │  │   Database      │───▶│  Reconstruct for Agent        │ │
         │  │ Neon PostgreSQL │    │  (Messages + Tool Calls)      │ │
         │  └─────────────────┘    └─────────────────────────────────┘ │
         └─────────────────────────────────────────────────────────────┘
                                    │
                    3. Agent Execution with MCP Tools
                                    ▼
         ┌─────────────────────────────────────────────────────────────┐
         │                    Agent Processing                       │
         │  ┌─────────────────┐    ┌─────────────────────────────────┐ │
         │  │ OpenAI Agent    │───▶│  MCP Tools (via MCP Server)   │ │
         │  │  SDK            │    │  (Todo Operations)            │ │
         │  └─────────────────┘    └─────────────────────────────────┘ │
         └─────────────────────────────────────────────────────────────┘
                                    │
                    4. Capture Responses & Persist
                                    ▼
         ┌─────────────────────────────────────────────────────────────┐
         │                    Response Assembly                        │
         │  ┌─────────────────┐    ┌─────────────────────────────────┐ │
         │  │   Database      │◀───│  Persist Messages & Tool Calls │ │
         │  │ Neon PostgreSQL │    │  Generate Assistant Response   │ │
         │  └─────────────────┘    └─────────────────────────────────┘ │
         └─────────────────────────────────────────────────────────────┘
                                    │
                    5. Return Response (conversation_id, response, tool_calls)
                                    ▼
                         ┌─────────────────────────┐
                         │    Client Response      │
                         └─────────────────────────┘
```

## Functional Flow

The system implements the exact 12-step stateless request-cycle as specified:
1. Authenticate request via JWT
2. Validate user_id matches JWT subject
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

## Stateless Execution

Critical design decision to maintain statelessness between requests:
- No server-side memory, caches, or session storage
- Conversation history reconstructed from database on each request
- All state persisted to database before returning response
- Horizontal scalability and restart-safety ensured

## Error Handling

Comprehensive error handling with specific HTTP status codes:
- 401 Unauthorized: Missing or invalid JWT
- 403 Forbidden: JWT user does not match user_id in path
- 404 Not Found: Conversation ID does not exist for user
- 422 Unprocessable Entity: Invalid request payload
- 500 Internal Server Error: MCP tool failure or agent execution error
- All errors return safe, user-friendly messages

## Security & Multi-Tenant Isolation

- Strict JWT validation ensures user_id in path matches JWT subject
- Database queries filtered by authenticated user ID
- No cross-user data access possible
- MCP tools provide controlled access to todo operations

## Testing Strategy

### Unit Tests
- JWT validation and user verification
- Conversation management logic
- Agent orchestration functions
- MCP tool integration

### Integration Tests
- Full chat endpoint functionality
- Database persistence flows
- MCP tool call execution

### Contract Tests
- Stateless behavior validation (identical requests produce identical responses)
- Multi-tenant isolation verification
- Error handling scenarios
- 12-step request-cycle compliance

## Risk & Edge Cases

- Malformed JSON in request body
- JWT expiration during conversation
- MCP tool failures during AI processing
- Extremely long conversation history
- Non-existent conversation ID access
- Concurrent requests from same user

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None      | None       | All constitution requirements satisfied |
