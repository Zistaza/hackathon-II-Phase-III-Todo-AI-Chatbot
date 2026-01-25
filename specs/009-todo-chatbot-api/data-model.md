# Data Model: Todo AI Chatbot - Chat API

## Key Entities

### Conversation
Represents a thread of messages between a user and the AI assistant.

**Fields:**
- `id`: Integer (primary key, auto-increment)
- `user_id`: String (foreign key reference to user, required)
- `created_at`: DateTime (timestamp when conversation started)
- `updated_at`: DateTime (timestamp of last activity)
- `title`: String (optional, generated from first message or user-provided)

**Relationships:**
- One-to-many with Message (conversation has many messages)
- One-to-many with ToolCall (conversation has many tool calls)

**Validation:**
- `user_id` must match authenticated user's ID
- `created_at` is set on creation
- `updated_at` is updated on each interaction

### Message
Represents individual exchanges in a conversation, including user input, AI responses, and MCP tool interactions.

**Fields:**
- `id`: Integer (primary key, auto-increment)
- `conversation_id`: Integer (foreign key reference to conversation, required)
- `role`: String (enum: "user", "assistant", "system", "tool")
- `content`: String (the actual message content, required)
- `timestamp`: DateTime (when the message was created)
- `metadata`: JSON (optional, for storing additional context like tool call IDs)

**Relationships:**
- Many-to-one with Conversation (message belongs to one conversation)

**Validation:**
- `role` must be one of the allowed values
- `content` must not be empty
- `conversation_id` must reference an existing conversation for the user

### ToolCall
Represents actions initiated by the AI assistant to interact with external systems via MCP tools.

**Fields:**
- `id`: Integer (primary key, auto-increment)
- `conversation_id`: Integer (foreign key reference to conversation, required)
- `message_id`: Integer (foreign key reference to associated message, nullable)
- `tool_name`: String (name of the MCP tool called, required)
- `tool_input`: JSON (input parameters passed to the tool)
- `tool_output`: JSON (output received from the tool)
- `execution_status`: String (enum: "pending", "success", "error", required)
- `timestamp`: DateTime (when the tool call was initiated)

**Relationships:**
- Many-to-one with Conversation (tool call belongs to one conversation)
- Many-to-one with Message (optional, tool call associated with a message)

**Validation:**
- `tool_name` must be one of the registered MCP tools
- `execution_status` must be one of the allowed values
- `conversation_id` must reference an existing conversation for the user

### User
Represents authenticated individuals with JWT tokens, serving as the tenant isolation boundary.

**Fields:**
- `id`: String (unique identifier from JWT, required)
- `email`: String (user's email address)
- `created_at`: DateTime (account creation timestamp)
- `last_login`: DateTime (last successful authentication)

**Relationships:**
- One-to-many with Conversation (user has many conversations)

**Validation:**
- `id` must be unique and match JWT subject
- `email` format must be valid

## State Transitions

### Message States
- New message created with role and content
- Messages are immutable once persisted

### ToolCall States
- `pending` → `success` or `error` (based on tool execution result)
- State transition happens during agent processing

## Constraints

### Multi-Tenancy
- All queries must filter by `user_id` to ensure data isolation
- Cross-user access prevention enforced at application and database levels

### Data Integrity
- Foreign key constraints ensure referential integrity
- Timestamps automatically managed by the system
- Conversation and message ordering maintained by database

### Security
- Sensitive data encrypted at rest
- JWT validation required for all operations
- Audit trail maintained for all data access