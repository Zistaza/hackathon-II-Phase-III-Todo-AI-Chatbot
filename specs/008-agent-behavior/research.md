# Research: Todo AI Chatbot Agent Behavior

## Intent Classification Strategy

### Primary Intents Identified
1. **Task Creation** - Triggered by: "add", "create", "remember", "write down", "make"
2. **Task Listing** - Triggered by: "see", "show", "list", "check", "view", "display"
3. **Task Completion** - Triggered by: "done", "complete", "finish", "mark done", "check off"
4. **Task Deletion** - Triggered by: "delete", "remove", "cancel", "get rid of", "erase"
5. **Task Update** - Triggered by: "change", "update", "rename", "edit", "modify", "fix"

### Confidence Thresholds
- High Confidence (>80%): Direct tool selection without ambiguity checks
- Medium Confidence (60-80%): Additional validation or disambiguation
- Low Confidence (<60%): Request clarification from user

## Ambiguity Patterns and Resolution Strategies

### Common Ambiguity Patterns
1. **Vague Task References**: "Delete the meeting task" when multiple meetings exist
2. **Partial Matches**: "Complete the grocery task" when multiple grocery-related tasks exist
3. **Missing Context**: "Update it" without specifying what "it" refers to
4. **Temporal Ambiguity**: "Complete yesterday's task" when multiple tasks exist from yesterday

### Safe Resolution Strategies
1. **Discovery First**: When ambiguity detected, call `list_tasks` to identify options
2. **Clarification Requests**: Ask specific questions when discovery doesn't resolve
3. **Confirmation Required**: For destructive operations (delete, update), always confirm specific target
4. **Default Filters**: Apply sensible defaults (e.g., show incomplete tasks first)

## Non-Goals and Forbidden Behaviors

### Explicit Non-Goals
- Direct database access: Agent MUST use only MCP tools
- Direct API calls: Agent MUST NOT make REST calls directly
- Session state maintenance: Agent MUST be stateless between requests
- User authentication: Agent relies on existing JWT authentication

### Forbidden Behaviors
- Accessing data belonging to other users
- Bypassing MCP tools for direct operations
- Storing persistent state between conversations
- Performing operations without proper user context

## Decision Tables for Intent-to-Tool Mapping

### Primary Mapping Table
| User Intent Keywords | MCP Tool | Parameters Required | Confidence Level |
|---------------------|----------|-------------------|------------------|
| add, create, remember, write down | add_task | title, description (optional) | High |
| see, show, list, check, view | list_tasks | status filter (optional) | High |
| done, complete, finish, mark done | complete_task | task_id | Medium-High |
| delete, remove, cancel, erase | delete_task | task_id | Medium-High |
| change, update, rename, edit | update_task | task_id, updated_fields | Medium-High |

### Priority Rules for Multiple Matching Tools
1. **Task Creation vs Update**: When both could apply, favor creation if no clear reference to existing task
2. **Deletion vs Update**: When both could apply, favor update if user seems to want modification vs removal
3. **Listing vs Specific Action**: When user asks to see tasks before taking action, honor listing request first

## Historical Context Usage

### Context Dependency Levels
- **Critical Context**: Previous task IDs referenced in follow-up commands
- **Helpful Context**: User preferences, recurring task patterns
- **Optional Context**: General conversation flow for natural responses

### Stateless Operation Requirements
- Each request must be self-contained with conversation history
- Agent cannot assume memory of previous interactions
- All necessary context must be reconstructed from stored history

## Trade-offs Analysis

### Safety vs Smoothness Trade-offs
- **Strict Safety**: Always ask for confirmation before destructive operations (preferred)
- **Smooth Experience**: Auto-confirm for obvious cases (avoided due to potential errors)

### Accuracy vs Responsiveness Trade-offs
- **High Accuracy**: Multiple validation steps, more clarifications (preferred)
- **Fast Response**: Quick tool selection with less validation (avoided due to error risk)

## Integration Patterns

### MCP Tool Interaction Patterns
- **Synchronous Calls**: Wait for MCP tool response before proceeding
- **Error Propagation**: MCP errors bubble up to user with explanation
- **Result Processing**: Transform MCP responses into natural language

### Conversation Flow Patterns
- **Request-Response Cycle**: New user message → Agent processing → Tool calls → Response generation
- **Multi-turn Handling**: Complex requests may require multiple tool calls in sequence
- **History Reconstruction**: Full conversation history provided with each request