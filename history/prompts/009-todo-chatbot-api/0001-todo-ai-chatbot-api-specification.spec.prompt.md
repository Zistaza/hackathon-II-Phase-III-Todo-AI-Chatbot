---
id: 0001
title: Todo AI Chatbot API Specification
stage: spec
date: 2026-01-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: 009-todo-chatbot-api
branch: 009-todo-chatbot-api
user: emizee
command: /sp.specify
labels: ["spec", "api", "chatbot", "todo", "ai"]
links:
  spec: "./../../../specs/009-todo-chatbot-api/spec.md"
  ticket: null
  adr: null
  pr: null
files:
 - ./../../../specs/009-todo-chatbot-api/spec.md
 - ./../../../specs/009-todo-chatbot-api/checklists/requirements.md
tests:
 - none
---

## Prompt

Phase III – Todo AI Chatbot: Chat API Specification

Target audience:
Backend engineers implementing the FastAPI chat endpoint, AI integrators wiring OpenAI Agents SDK with MCP tools, and judges evaluating statelessness, correctness, and adherence to the Phase III constitution.

Objective:
Define the complete, authoritative specification for the single chat API endpoint that powers the Todo AI Chatbot. This spec must clearly describe request/response contracts, authentication rules, stateless request-cycle behavior, conversation persistence, agent execution flow, MCP tool invocation handling, and error scenarios — without including implementation code.

Technology Stack (MANDATORY):
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT)

Scope of this specification:
- The POST /api/{user_id}/chat endpoint
- Conversation lifecycle management
- Interaction between FastAPI, OpenAI Agents SDK, and MCP server
- Stateless orchestration per request
- Authentication, authorization, and multi-tenant isolation
- Deterministic and testable API behavior

Success criteria:
- A backend engineer can implement the chat endpoint strictly from this spec without guesswork
- A judge can trace how a user message flows from request → agent → MCP tools → response
- Statelessness is unambiguous and verifiable
- Multi-tenant isolation and JWT enforcement are explicitly defined
- All MCP tool invocations are captured and returned deterministically
- The API behavior is fully testable using black-box tests

Functional requirements:
- Expose exactly one endpoint: POST /api/{user_id}/chat (LOCKED)
- Require valid JWT authentication for every request
- Enforce user_id in path must match authenticated JWT user
- Accept user messages and optional conversation_id
- Create a new conversation if conversation_id is not provided
- Persist all user messages, tool calls, and assistant responses
- Reconstruct conversation history on every request
- Invoke the OpenAI Agent using reconstructed history
- Allow the agent to call MCP tools only (no direct DB or API access)
- Return assistant response and tool_calls in the response payload

Non-functional requirements:
- Backend must be stateless between requests
- API must be horizontally scalable and restart-safe
- Deterministic response structure for identical inputs
- No server-side memory, caches, or session storage
- Clear error handling and HTTP status codes

Request contract:
- Path parameter: user_id (string, required)
- Body:
  - message (string, required): natural language user input
  - conversation_id (integer, optional): existing conversation reference

Response contract:
- conversation_id (integer): active conversation ID
- response (string): AI assistant's natural language reply
- tool_calls (array): MCP tools invoked during processing (may be empty)

Stateless request-cycle behavior (MANDATORY):
1. Authenticate request via JWT
2. Validate user_id matches JWT subject
3. Load conversation history from database (if conversation_id exists)
4. Append current user message to history
5. Persist user message before agent execution
6. Run OpenAI Agent with:
   - Reconstructed message history
   - MCP tool definitions
7. Capture any MCP tool calls made by the agent
8. Persist tool calls and tool responses
9. Generate final assistant response
10. Persist assistant response
11. Return response payload to client
12. Discard all in-memory state

Error handling requirements:
- 401 Unauthorized: Missing or invalid JWT
- 403 Forbidden: JWT user does not match user_id in path
- 404 Not Found: Conversation ID does not exist for user
- 422 Unprocessable Entity: Invalid request payload
- 500 Internal Server Error: MCP tool failure or agent execution error
- All errors must return safe, user-friendly messages

Explicit non-goals (NOT building):
- No frontend or UI logic
- No database schema definitions or migrations
- No MCP tool implementation details
- No agent reasoning or intent classification logic
- No streaming responses
- No WebSocket or long-polling support
- No caching or session-based state

Constraints (NON-NEGOTIABLE):
- Must comply with Phase III Constitution
- Must use OpenAI Agents SDK concepts (agent, runner, tool calls)
- Must use MCP tools exclusively for task operations
- No direct database access by the agent
- No additional API endpoints beyond POST /api/{user_id}/chat
- Specification only — no implementation code

Deliverables:
- Markdown specification document
- Clear section headers aligned with Phase III constitution
- Explicit request/response schemas
- Step-by-step stateless execution flow
- Error scenarios with expected behavior
- Acceptance criteria suitable for automated testing

References:
- Phase III – Todo AI Chatbot Constitution.md
- 008-agent-behavior specification
- 007-mcp-tools specification
- OpenAI Agents SDK documentation
- MCP (Model Context Protocol) standards

## Response snapshot

Successfully created a comprehensive specification for the Todo AI Chatbot Chat API according to the provided template and requirements. The specification includes user scenarios, functional requirements, key entities, and success criteria, with all mandatory sections completed.

## Outcome

- ✅ Impact: Created complete specification document for Todo AI Chatbot API that meets all requirements
- 🧪 Tests: none
- 📁 Files: specs/009-todo-chatbot-api/spec.md, specs/009-todo-chatbot-api/checklists/requirements.md
- 🔁 Next prompts: /sp.clarify to address any remaining questions or /sp.plan to begin implementation planning
- 🧠 Reflection: The specification provides clear guidance for backend engineers to implement the chat endpoint without guesswork.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All specification requirements met
- Prompt variant (if applicable): Standard spec creation prompt
- Next experiment (smallest change to try): Review with stakeholders for completeness
