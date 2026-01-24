# Research: Todo AI Chatbot Database Schema

## Overview
Research conducted to understand the current database structure and requirements for implementing the Todo AI Chatbot database schema with conversation persistence and MCP tool integration.

## Current Database Structure Analysis

### Existing Models
- **User Model** (`user_model.py`): Contains user information with ID, email, name, password, and timestamps
- **Task Model** (`task_model.py`): Contains tasks with foreign key relationship to users (user_id), title, description, completion status, and timestamps
- **MCP Tool Models** (`mcp_tool.py`): Contains MCP tool metadata and access logs with user relationships

### Missing Components
Based on the feature specification, the following components need to be implemented:
1. **Conversation Model**: To store chat conversation threads
2. **Message Model**: To store individual messages within conversations
3. **Updated Chat Models**: Currently only have Pydantic models, need SQLModel equivalents for persistence

## Key Findings

### 1. Current Chat Implementation
- Currently has Pydantic models in `chat.py` but no persistent storage
- Chat endpoints exist in `api/chat.py` but use simulated responses
- No conversation history storage capability
- Conversation ID is generated randomly in the API layer but not persisted

### 2. MCP Tool Integration
- MCP tools have proper database models and services
- MCP tools have user ownership enforcement through user_id
- MCP tools have access logging capabilities
- MCP tools follow multi-tenant isolation principles

### 3. Multi-Tenant Isolation
- Current task model properly enforces user ownership through foreign key to user_id
- Authentication flow properly validates user identity
- Database queries should filter by authenticated user_id

## Decisions Made

### 1. Entity Relationships
- **Conversation** will have a foreign key to **User** (user_id)
- **Message** will have a foreign key to **Conversation** (conversation_id)
- **Message** will have a foreign key to **User** (user_id) for ownership validation
- **Task** already has foreign key to **User** (user_id) - no changes needed

### 2. Indexing Strategy
- Index on user_id for all user-owned entities (Conversation, Message, Task)
- Index on conversation_id for Message table for efficient conversation retrieval
- Composite indexes where needed for common query patterns

### 3. Conversation State Management
- Store conversation context in database for stateless AI operations
- Retrieve full conversation history when AI agent needs context
- Support multiple conversations per user with conversation switching

## Implementation Approach

### Phase 0: Schema Design
- Define SQLModel entities for Conversation and Message
- Establish proper foreign key relationships
- Define indexes for efficient queries
- Ensure all queries enforce user_id filtering

### Phase 1: Database Implementation
- Create new models following the same pattern as existing models
- Add proper constraints and validation
- Implement database initialization with new tables

### Phase 2: MCP Tool Integration
- Update MCP tools to work with conversation and message data
- Ensure all MCP operations respect user ownership
- Add example queries for each MCP tool operation

### Phase 3: Conversation State Persistence
- Implement stateless conversation reconstruction
- Store conversation context for AI agent operations
- Enable efficient retrieval of conversation history

## Alternatives Considered

### 1. Storage Approach
- **Option A**: Store conversations in database (chosen) - Provides ACID properties, supports complex queries, integrates well with existing architecture
- **Option B**: Store conversations in document store - Would require additional infrastructure, more complex auth integration
- **Option C**: Store conversations in memory/cache - Would lose data on restart, not suitable for persistent chat history

### 2. Relationship Design
- **Option A**: Conversation → User (FK), Message → Conversation (FK), Message → User (FK) (chosen) - Ensures strong consistency, enables efficient queries
- **Option B**: Only Message → User (FK), derive conversation ownership from messages - Would complicate queries, harder to enforce conversation-level permissions
- **Option C**: Hierarchical approach with nested structures - Not compatible with relational model, harder to query

### 3. Indexing Strategy
- **Option A**: Primary indexes on user_id and conversation_id (chosen) - Supports main query patterns efficiently
- **Option B**: Additional indexes on message timestamps - May improve sorting but adds overhead
- **Option C**: Full-text search indexes - Premature optimization, can be added later if needed