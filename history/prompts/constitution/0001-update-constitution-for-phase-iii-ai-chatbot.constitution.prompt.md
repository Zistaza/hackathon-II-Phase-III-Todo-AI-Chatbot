---
id: 0001
title: Update constitution for Phase III AI Chatbot
stage: constitution
date: 2026-01-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Zistaza
command: /sp.constitution
labels: ["constitution", "agentic-architecture", "todo-chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Project: Phase III – Todo AI Chatbot (Agentic MCP Architecture)

Objective:
Design and implement an AI-powered conversational Todo application that manages tasks through natural language using a stateless server architecture, OpenAI Agents SDK, and MCP (Model Context Protocol) tools, following the Agentic Dev Stack workflow and implemented exclusively via Claude Code and Spec-Kit Plus.

Development Principles:
- Agentic-first design: AI agent reasoning drives all task operations
- Statelessness: No server-side memory between requests; all state persisted in database
- Tool-based interaction: AI must interact with the application exclusively via MCP tools
- Separation of concerns: UI, agent logic, MCP tooling, and persistence are strictly decoupled
- Spec-driven development: Specs are the single source of truth; no manual coding

Core Architectural Standards:
- Single chat endpoint (`POST /api/{user_id}/chat`) handles all interactions
- Conversation context is reconstructed from database on every request
- MCP tools are stateless and persist all changes to the database
- AI agents may chain multiple MCP tools in a single turn
- Backend must be horizontally scalable and restart-safe

Technology Constraints:
- Frontend: OpenAI ChatKit
- Backend API: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK only
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth
- No alternative frameworks or unofficial SDKs permitted

Data & Persistence Rules:
- All user messages and assistant responses must be stored
- Conversation history must be replayable after server restart
- Database models are limited to:
  - Task (user_id, id, title, description, completed, created_at, updated_at)
  - Conversation (user_id, id, created_at, updated_at)
  - Message (user_id, id, conversation_id, role, content, created_at)
- No hidden or in-memory state allowed

MCP Tooling Standards:
- MCP server must expose tools exactly as specified:
  - add_task
  - list_tasks
  - complete_task
  - delete_task
  - update_task
- Tool inputs and outputs must strictly follow defined schemas
- Tools must validate user ownership and handle errors gracefully
- Tools must not contain conversational logic

Agent Behavior Standards:
- Natural language intent determines tool selection
- Agent must always confirm actions in friendly, human-readable language
- When ambiguity exists, agent must ask for clarification before acting
- Errors (e.g., task not found) must be handled gracefully and explained clearly
- Agent responses must include awareness of tool actions taken

Process Constraints:
- Follow Agentic Dev Stack strictly:
  1. Write specification
  2. Generate implementation plan
  3. Break into tasks
  4. Implement via Claude Code
- No manual code edits outside Claude Code
- Each architectural concern must be implemented via separate specs
- Specs may reference but must not override this constitution

Deliverable Standards:
- Repository structure must include:
  - /frontend (ChatKit UI)
  - /backend (FastAPI + Agents SDK + MCP)
  - /specs (architecture, database, MCP tools, agent behavior, API, frontend)
  - Database migration scripts
  - README with setup and deployment instructions
- System must support conversation resumption after server restarts
- Chatbot must fully manage todos through natural language

Success Criteria:
- All task operations performed exclusively through MCP tools
- Stateless server verified through restart testing
- Conversation context correctly reconstructed from database
- Agent demonstrates correct tool usage and confirmations
- Codebase adheres strictly to specs and this constitution
- Reviewers can trace every implementation decision back to a spec

## Response snapshot

Updated the project constitution to reflect the new "Phase III – Todo AI Chatbot (Agentic MCP Architecture)" requirements, replacing the previous "Phase II – Todo Full-Stack Web Application" constitution. The new constitution includes principles for agentic-first design, statelessness, tool-based interaction, and MCP tooling standards.

## Outcome

- ✅ Impact: Updated constitution to reflect Phase III AI Chatbot architecture with Agentic MCP requirements
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: Generate spec for the AI chatbot implementation
- 🧠 Reflection: Constitution now properly defines the agentic architecture with MCP tools and stateless design principles

## Evaluation notes (flywheel)

- Failure modes observed: Script permission issue prevented automated PHR creation; had to create manually
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ensure PHR scripts have proper execute permissions