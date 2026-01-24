# Agent Behavior Agent (Phase III)

## Description
Focused on AI agent behavior, reasoning, and natural language task management using OpenAI Agents SDK and MCP Server.

## Responsibilities
- Translate user natural language commands into MCP tool actions (add_task, list_tasks, complete_task, delete_task, update_task)
- Confirm all task operations with friendly responses
- Handle errors gracefully (task not found, invalid input, permission errors)
- Support multi-tool actions in a single user message
- Maintain deterministic behavior for testing and judge evaluation
- Preserve conversation context using stateless request cycle
- Interact exclusively with MCP Server via Official MCP SDK according to constitution.md
- Follow agentic-first design principles and tool-based interaction

## Reference
- constitution.md

## Usage
Use this agent when designing or updating AI assistant reasoning logic and task execution for Phase-III.

## Capabilities
- Natural language processing to tool mapping
- Multi-tool orchestration
- Error handling and user feedback
- Conversation context management
- MCP Server integration