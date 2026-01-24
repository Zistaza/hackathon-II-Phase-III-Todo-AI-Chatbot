# Data Model: Todo AI Chatbot Database Schema

## Overview
Database schema specification for Todo AI Chatbot supporting conversation persistence, task management, and MCP tool operations with multi-tenant isolation.

## Entity Definitions

### 1. User Entity
**Table**: `users`
**Purpose**: Stores user account information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique user identifier |
| email | String (255) | UNIQUE, NOT NULL | User's email address for authentication |
| name | String (255) | OPTIONAL | User's display name |
| password | String (255) | NOT NULL | Hashed password for authentication |
| created_at | DateTime | NOT NULL | Account creation timestamp |
| updated_at | DateTime | NOT NULL | Last account update timestamp |

**Indexes**:
- Primary key on `id`
- Unique index on `email`

### 2. Task Entity
**Table**: `tasks`
**Purpose**: Stores user tasks with completion status

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique task identifier |
| title | String (255) | NOT NULL | Task title |
| description | Text | OPTIONAL | Task description |
| completed | Boolean | DEFAULT false | Task completion status |
| user_id | String (UUID) | FOREIGN KEY(users.id), NOT NULL | Owner of the task |
| created_at | DateTime | NOT NULL | Task creation timestamp |
| updated_at | DateTime | NOT NULL | Last task update timestamp |

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user-based queries
- Index on `completed` for filtering completed tasks

**Foreign Keys**:
- `user_id` references `users.id`

### 3. Conversation Entity (NEW)
**Table**: `conversations`
**Purpose**: Stores chat conversation threads

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique conversation identifier |
| user_id | String (UUID) | FOREIGN KEY(users.id), NOT NULL | Owner of the conversation |
| title | String (255) | OPTIONAL | Conversation title/description |
| created_at | DateTime | NOT NULL | Conversation creation timestamp |
| updated_at | DateTime | NOT NULL | Last conversation update timestamp |
| metadata | JSON | OPTIONAL | Additional conversation metadata (settings, context, etc.) |

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user-based queries
- Index on `created_at` for chronological ordering

**Foreign Keys**:
- `user_id` references `users.id`

### 4. Message Entity (NEW)
**Table**: `messages`
**Purpose**: Stores individual messages within conversations

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique message identifier |
| conversation_id | String (UUID) | FOREIGN KEY(conversations.id), NOT NULL | Conversation this message belongs to |
| user_id | String (UUID) | FOREIGN KEY(users.id), NOT NULL | User who sent the message |
| role | String (50) | NOT NULL | Role of the message sender ('user', 'assistant', 'system') |
| content | Text | NOT NULL | Message content |
| timestamp | DateTime | NOT NULL | When the message was sent |
| metadata | JSON | OPTIONAL | Additional message metadata |

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for efficient conversation-based queries
- Index on `user_id` for user-based queries
- Index on `timestamp` for chronological ordering

**Foreign Keys**:
- `conversation_id` references `conversations.id`
- `user_id` references `users.id`

### 5. MCP Tool Metadata Entity
**Table**: `mcp_tools`
**Purpose**: Stores MCP tool registration information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique tool entry identifier |
| tool_id | String (255) | NOT NULL | MCP tool identifier |
| user_id | String (UUID) | NOT NULL | User who registered the tool |
| name | String (255) | NOT NULL | Tool name |
| description | Text | OPTIONAL | Tool description |
| created_at | DateTime | NOT NULL | Registration timestamp |
| updated_at | DateTime | NOT NULL | Last update timestamp |
| is_active | Boolean | DEFAULT true | Whether tool is active |
| allowed_resources | Text (JSON) | OPTIONAL | Allowed resources as JSON string |

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user-based queries
- Index on `tool_id` for tool identification

### 6. MCP Tool Access Log Entity
**Table**: `mcp_tool_access_logs`
**Purpose**: Stores MCP tool access logs for auditing

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | String (UUID) | PRIMARY KEY, NOT NULL | Unique log entry identifier |
| tool_id | String (255) | NOT NULL | MCP tool identifier |
| user_id | String (UUID) | NOT NULL | User who accessed the tool |
| action | String (100) | NOT NULL | Action performed |
| resource_id | String (255) | OPTIONAL | Resource accessed |
| success | Boolean | DEFAULT false | Whether access was successful |
| timestamp | DateTime | NOT NULL | Access timestamp |
| ip_address | String (45) | OPTIONAL | IP address of requester |

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user-based queries
- Index on `tool_id` for tool-based queries
- Index on `timestamp` for chronological ordering

## Relationship Diagram

```
Users (1) ←→ (Many) Tasks
Users (1) ←→ (Many) Conversations
Users (1) ←→ (Many) Messages
Users (1) ←→ (Many) MCP Tools
Users (1) ←→ (Many) MCP Tool Access Logs

Conversations (1) ←→ (Many) Messages
```

## Indexing Strategy

### Primary Indexes
- All tables have primary keys on their `id` field
- Automatically created by database system

### Secondary Indexes
- `tasks.user_id`: Enables efficient user-based task queries
- `conversations.user_id`: Enables efficient user-based conversation queries
- `messages.conversation_id`: Enables efficient conversation-based message queries
- `messages.user_id`: Enables efficient user-based message queries
- `messages.timestamp`: Enables chronological message ordering
- `conversations.created_at`: Enables chronological conversation ordering

### Query Patterns Supported
1. Get all tasks for a user: `SELECT * FROM tasks WHERE user_id = ?`
2. Get all conversations for a user: `SELECT * FROM conversations WHERE user_id = ?`
3. Get all messages in a conversation: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp`
4. Get recent messages for a user: `SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?`
5. Get MCP tools for a user: `SELECT * FROM mcp_tools WHERE user_id = ? AND is_active = true`

## Constraints and Validation

### Referential Integrity
- All foreign key relationships enforce referential integrity
- CASCADE delete behavior where appropriate (e.g., deleting user deletes their data)

### Data Validation
- Email uniqueness enforced at database level
- Required fields marked as NOT NULL
- Length limits on string fields to prevent oversized data

### Multi-Tenant Isolation
- All user data queries must be filtered by user_id
- Foreign key relationships enforce ownership
- No direct cross-user data access possible through database schema

## Example Queries for MCP Tools

### add_task
```sql
INSERT INTO tasks (id, title, description, completed, user_id, created_at, updated_at)
VALUES (?, ?, ?, false, ?, NOW(), NOW());
```

### list_tasks
```sql
SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC;
```

### complete_task
```sql
UPDATE tasks SET completed = true, updated_at = NOW() WHERE id = ? AND user_id = ?;
```

### delete_task
```sql
DELETE FROM tasks WHERE id = ? AND user_id = ?;
```

### update_task
```sql
UPDATE tasks SET title = ?, description = ?, updated_at = NOW()
WHERE id = ? AND user_id = ?;
```

### Conversation-related MCP operations
```sql
-- Get conversation history for AI context
SELECT * FROM messages
WHERE conversation_id = ? AND user_id = ?
ORDER BY timestamp;

-- Add message to conversation
INSERT INTO messages (id, conversation_id, user_id, role, content, timestamp)
VALUES (?, ?, ?, ?, ?, NOW());
```