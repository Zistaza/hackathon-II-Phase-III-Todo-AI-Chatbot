<!-- SYNC IMPACT REPORT:
Version change: 1.0.0 -> 2.0.0
Modified principles: Phase II – Todo Full-Stack Web Application → Phase III – Todo AI Chatbot (Agentic MCP Architecture)
Added sections: Agentic-first design, Statelessness, Tool-based interaction, MCP Tooling Standards, Agent Behavior Standards, OpenAI Agents SDK, MCP Server requirements
Removed sections: Previous API contract (replaced with new chat-based approach)
Templates requiring updates: ⚠ pending - .specify/templates/plan-template.md, .specify/templates/spec-template.md, .specify/templates/tasks-template.md
Follow-up TODOs: None
-->

# Phase III – Todo AI Chatbot (Agentic MCP Architecture) Constitution

## Core Principles

### Spec-Driven Development
All implementation must originate from written specifications; every feature starts with a clear spec document that defines requirements, acceptance criteria, and test cases before any code is written

### Separation of Concerns
UI, agent logic, MCP tooling, and persistence responsibilities are isolated; each layer has clear boundaries and interfaces without cross-contamination of concerns

### Security by Default (NON-NEGOTIABLE)
Every request is authenticated and authorized via JWT; backend must reject unauthenticated requests with HTTP 401; all database queries must be filtered by authenticated user ID

### Multi-Tenant Isolation
Users can only access and modify their own data; user ID in the URL must match the user ID in the JWT; cross-user data access is strictly forbidden

### Agentic-first Design
AI agent reasoning drives all task operations; the system must be designed around the OpenAI Agents SDK and its decision-making capabilities; all user interactions flow through the AI agent

### Statelessness
No server-side memory between requests; all state must be persisted in the database; the backend must be horizontally scalable and restart-safe with full conversation context reconstruction from database

### Tool-based Interaction
AI must interact with the application exclusively via MCP (Model Context Protocol) tools; no direct API calls from agents; all operations must occur through the defined MCP tool interface

### Deterministic APIs
Backend behavior must be predictable, validated, and testable; the single chat endpoint must follow the defined contract with appropriate response handling

### Cloud-Native Design
Stateless backend, serverless-friendly database usage; minimal viable implementations avoiding premature optimization

## Technology Standards

Frontend: OpenAI ChatKit; Backend: Python FastAPI; AI Framework: OpenAI Agents SDK; MCP Server: Official MCP SDK only; ORM: SQLModel; Database: Neon Serverless PostgreSQL; Authentication: Better Auth with JWT; Environment secrets must be managed via environment variables; Shared JWT secret must be configured via BETTER_AUTH_SECRET

## Development Workflow

All features must be implemented according to written specs; The system must support conversation resumption after server restarts; The chatbot must fully manage todos through natural language; All task operations performed exclusively through MCP tools

## Governance

All implementation must follow the defined API contracts and MCP tool schemas.

### REST API Contract (LOCKED)

All implementations must conform to the following REST API contract:
- POST /api/{user_id}/chat — Single chat endpoint handles all AI interactions

No endpoint renaming, path restructuring, or contract deviation is allowed without a constitution amendment.

### MCP Tooling Standards (LOCKED)

All implementations must conform to the following MCP tools contract:
- add_task — Creates a new task in the database
- list_tasks — Lists all tasks for the authenticated user
- complete_task — Marks a task as completed
- delete_task — Deletes a task from the database
- update_task — Updates task properties

No tool renaming, schema modification, or contract deviation is allowed without a constitution amendment.

No hardcoded secrets or credentials in code; Backend must remain stateless; No direct database access from frontend; MCP tools must not contain conversational logic.

## Success Criteria

- All API endpoints require valid JWT authentication
- Users can only access and modify their own tasks
- Tasks persist reliably in Neon PostgreSQL
- Conversation history is replayable after server restart
- MCP tools validate user ownership and handle errors gracefully
- Agent demonstrates correct tool usage and confirmations
- Chatbot fully manages todos through natural language
- Application is demo-ready and judge-verifiable

## Authority Hierarchy

Constitution > Specifications > Plans > Tasks > Code

Any conflict must be resolved in favor of the higher authority document.

**Version**: 2.0.0 | **Ratified**: 2026-01-24 | **Last Amended**: 2026-01-24