# Data Model: Todo AI Chatbot MCP Tools

## Entity Definitions

### User
- **Description**: Represents an authenticated user with ownership rights over tasks and conversations
- **Fields**:
  - `id`: UUID (primary key) - Unique identifier for the user
  - `email`: String (unique) - User's email address for identification
  - `created_at`: DateTime - Timestamp of user creation
  - `updated_at`: DateTime - Timestamp of last update

### Task
- **Description**: Represents a user's todo item with properties like title, description, completion status, and timestamps
- **Fields**:
  - `id`: UUID (primary key) - Unique identifier for the task
  - `user_id`: UUID (foreign key) - References the owning user
  - `title`: String - Title of the task
  - `description`: Text (optional) - Detailed description of the task
  - `completed`: Boolean - Whether the task is completed (default: false)
  - `priority`: Integer (optional) - Priority level of the task (1-5, where 5 is highest)
  - `due_date`: DateTime (optional) - Deadline for the task
  - `created_at`: DateTime - Timestamp of task creation
  - `updated_at`: DateTime - Timestamp of last update
- **Relationships**: Belongs to one User; User has many Tasks

### Conversation
- **Description**: Represents a persistent chat session between user and AI agent, stored with user ownership enforcement
- **Fields**:
  - `id`: UUID (primary key) - Unique identifier for the conversation
  - `user_id`: UUID (foreign key) - References the owning user
  - `title`: String (optional) - Title or summary of the conversation
  - `created_at`: DateTime - Timestamp of conversation creation
  - `updated_at`: DateTime - Timestamp of last update
- **Relationships**: Belongs to one User; User has many Conversations

### Message
- **Description**: Represents an individual message within a conversation thread
- **Fields**:
  - `id`: UUID (primary key) - Unique identifier for the message
  - `conversation_id`: UUID (foreign key) - References the containing conversation
  - `role`: String - Role of the message sender ('user' or 'assistant')
  - `content`: Text - The content of the message
  - `timestamp`: DateTime - When the message was sent
  - `tool_calls`: JSON (optional) - Details of any MCP tools called in this message
  - `tool_responses`: JSON (optional) - Responses from MCP tools
- **Relationships**: Belongs to one Conversation; Conversation has many Messages

## Validation Rules

### User Validation
- Email must be valid email format
- Email must be unique across all users

### Task Validation
- Title must be non-empty string (1-200 characters)
- Description must be 1000 characters or less when present
- Priority must be between 1 and 5 when present
- Due date must be a future date when present
- User_id must reference an existing user

### Conversation Validation
- Title must be 100 characters or less when present
- User_id must reference an existing user

### Message Validation
- Role must be either 'user' or 'assistant'
- Content must be non-empty string
- Conversation_id must reference an existing conversation

## State Transitions

### Task State Transitions
- `active` → `completed`: When complete_task MCP tool is called
- `completed` → `active`: When update_task MCP tool is called with completed=false

### Multi-tenant Isolation Rules
- All queries must filter by user_id
- Users can only modify their own data
- Foreign key constraints enforce relationship integrity
- Business logic layer validates user ownership before operations

## Indexes

### Recommended Database Indexes
- `users.email` - For quick user lookup by email
- `tasks.user_id` - For efficient user-specific task queries
- `tasks.completed` - For filtering completed vs active tasks
- `conversations.user_id` - For efficient user-specific conversation queries
- `messages.conversation_id` - For efficient conversation-specific message queries
- `messages.timestamp` - For chronological ordering of messages