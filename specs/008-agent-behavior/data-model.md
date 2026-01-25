# Data Model: Todo AI Chatbot Agent Behavior

## Agent State Models

### Conversation Context
- **conversation_id**: UUID - Unique identifier for each conversation
- **user_id**: UUID - Associated user (enforced by JWT/auth)
- **messages**: Array of Message objects - Complete conversation history
- **last_tool_calls**: Array of ToolCall objects - Last executed tool calls
- **current_state**: Enum (IDLE, PROCESSING, AWAITING_CONFIRMATION, ERROR) - Current agent state
- **created_at**: DateTime - Timestamp of conversation creation
- **updated_at**: DateTime - Timestamp of last activity

### Message Object
- **id**: UUID - Unique message identifier
- **role**: Enum (USER, AGENT, SYSTEM) - Role of message sender
- **content**: String - Text content of the message
- **timestamp**: DateTime - When the message was created
- **tool_calls**: Array of ToolCall objects - Tool calls associated with this message
- **tool_responses**: Array of ToolResponse objects - Responses from tools called

### ToolCall Object
- **id**: String - Tool call identifier
- **name**: String - Name of the MCP tool being called (add_task, list_tasks, etc.)
- **arguments**: JSON - Arguments passed to the tool
- **timestamp**: DateTime - When the tool was called
- **status**: Enum (PENDING, SUCCESS, ERROR) - Status of the tool call

### ToolResponse Object
- **tool_call_id**: String - Reference to the associated tool call
- **result**: JSON - Result from the tool execution
- **error**: String (optional) - Error message if tool failed
- **timestamp**: DateTime - When the response was received

## Intent Classification Model

### Intent Categories
- **TASK_CREATION**: Intent to create a new task
  - Keywords: add, create, remember, write down, make
  - Required params: title (extracted from user input)
  - Optional params: description, due_date

- **TASK_LISTING**: Intent to view existing tasks
  - Keywords: see, show, list, check, view, display
  - Required params: none
  - Optional params: status filter (all, completed, pending), sort_order

- **TASK_COMPLETION**: Intent to mark a task as complete
  - Keywords: done, complete, finish, mark done, check off
  - Required params: task_id or task_identifier
  - Optional params: none

- **TASK_DELETION**: Intent to remove a task
  - Keywords: delete, remove, cancel, get rid of, erase
  - Required params: task_id or task_identifier
  - Optional params: none

- **TASK_UPDATE**: Intent to modify an existing task
  - Keywords: change, update, rename, edit, modify, fix
  - Required params: task_id or task_identifier
  - Optional params: updated_title, updated_description, updated_status

## Agent Configuration Model

### Agent Settings
- **intent_confidence_threshold**: Float (0.0-1.0) - Minimum confidence for direct action
- **max_ambiguity_attempts**: Integer - Max attempts to resolve ambiguous requests
- **confirmation_required**: Boolean - Whether destructive operations need explicit confirmation
- **context_window_size**: Integer - Number of previous messages to consider
- **multi_step_timeout**: Integer (seconds) - Timeout for multi-step operations

## Validation Rules

### Conversation Validation
- Each conversation must be associated with a valid user_id
- Messages must have valid roles (USER, AGENT, SYSTEM)
- Tool calls must reference valid MCP tools
- All timestamps must be in UTC

### Intent Validation
- TASK_CREATION requires a task title to be extracted
- TASK_COMPLETION/TASK_DELETION requires a valid task reference
- TASK_UPDATE requires both a task reference and at least one field to update
- Unknown intents should trigger clarification requests

## State Transition Rules

### Conversation State Transitions
- **IDLE** → **PROCESSING**: When receiving a new user message
- **PROCESSING** → **AWAITING_CONFIRMATION**: When ambiguity detected and user input needed
- **PROCESSING** → **ERROR**: When tool call fails or unexpected error occurs
- **AWAITING_CONFIRMATION** → **PROCESSING**: When user provides clarification
- **PROCESSING** → **IDLE**: When response is sent to user
- **ERROR** → **IDLE**: After error response is sent to user

### Tool Call State Transitions
- **PENDING** → **SUCCESS**: When MCP tool returns successfully
- **PENDING** → **ERROR**: When MCP tool fails or times out