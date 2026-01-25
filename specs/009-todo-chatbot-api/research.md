# Research Summary: Todo AI Chatbot - Chat API

## Key Decisions Made

### 1. Stateless Request-Cycle Execution
**Decision**: Implement the exact 12-step stateless request-cycle as specified in the feature requirements.
**Rationale**: Ensures horizontal scalability, restart-safety, and deterministic behavior across identical requests.
**Alternatives considered**:
- Stateful approach with in-memory caching (rejected due to scalability concerns)
- Simplified cycle (rejected due to non-compliance with spec)

### 2. MCP Tool Call Management
**Decision**: Use OpenAI Agents SDK with MCP tools exclusively for task operations, with no direct database access.
**Rationale**: Maintains clear separation of concerns and adheres to the security constraint of no direct database access by the agent.
**Alternatives considered**:
- Direct database access by agent (rejected due to security constraints)
- Mixed approach with some direct access (rejected due to complexity and security risks)

### 3. JWT Validation and Multi-Tenant Isolation
**Decision**: Implement strict JWT validation to ensure user_id in path matches authenticated JWT subject.
**Rationale**: Critical for security and compliance with multi-tenant isolation requirements.
**Alternatives considered**:
- Session-based authentication (rejected due to stateless requirement)
- Simplified validation (rejected due to security concerns)

### 4. Horizontal Scalability and Restart-Safe Strategies
**Decision**: Design completely stateless backend with no server-side memory, caches, or session storage.
**Rationale**: Enables horizontal scaling and ensures restart safety as required by spec.
**Alternatives considered**:
- Caching strategies (rejected due to stateless requirement)
- Session-based approaches (rejected due to stateless requirement)

### 5. Error Handling Approaches
**Decision**: Implement comprehensive error handling with specific HTTP status codes (401, 403, 404, 422, 500) and safe, user-friendly messages.
**Rationale**: Provides clear feedback to clients and maintains security by avoiding information leakage.
**Alternatives considered**:
- Generic error responses (rejected due to lack of specificity)
- Detailed internal error messages (rejected due to security concerns)

## Architecture Components

### System Components
- **FastAPI Backend**: Handles HTTP requests, JWT authentication, conversation management, and agent orchestration
- **OpenAI Agents SDK**: Processes conversation history and invokes MCP tools based on user input
- **MCP Server**: Provides standardized interface for todo operations through MCP tools
- **SQLModel ORM**: Manages data persistence with Neon Serverless PostgreSQL
- **Neon Serverless PostgreSQL**: Stores conversations, messages, and tool call history
- **Better Auth**: Handles JWT token generation and validation

### Interaction Flow
1. User sends request to POST /api/{user_id}/chat
2. FastAPI validates JWT and ensures user_id matches JWT subject
3. Conversation history is loaded from database
4. Current user message is appended to history
5. User message is persisted in database
6. OpenAI Agent is invoked with reconstructed history and MCP tool definitions
7. Agent processes input and may call MCP tools
8. MCP tool calls and responses are captured and persisted
9. Final assistant response is generated and persisted
10. Response payload is returned to client
11. All in-memory state is discarded

## Technology Stack Alignment

### Confirmed Technologies
- **Backend**: Python FastAPI (as required by spec)
- **AI Framework**: OpenAI Agents SDK (as required by spec)
- **MCP Server**: Official MCP SDK (as required by spec)
- **ORM**: SQLModel (as required by spec)
- **Database**: Neon Serverless PostgreSQL (as required by spec)
- **Authentication**: Better Auth with JWT (as required by spec)
- **Frontend**: OpenAI ChatKit (as required by spec)

## Open Questions Resolved

All requirements from the feature specification have been researched and understood. The implementation approach will follow the 12-step stateless request-cycle exactly as specified.

## References Consulted

- Phase III – Todo AI Chatbot Constitution
- 008-agent-behavior specification
- 007-mcp-tools specification
- OpenAI Agents SDK documentation
- MCP (Model Context Protocol) standards