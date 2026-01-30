---
name: database-iii-skill
description: Handle database operations securely and efficiently for Phase-III Todo AI Chatbot, including schema design, multi-tenant isolation, state persistence, and migrations using Neon PostgreSQL and SQLModel.
---

# Database Skill (Phase III)

## Instructions

1. **Schema design**
   - Define tables for `tasks`, `conversations`, and `messages`
   - Ensure proper data types, constraints, and relationships
   - Include indexes for efficient queries where needed
   - Enforce multi-tenant isolation by including `user_id` in all tables

2. **State persistence**
   - Persist all conversation and chat messages in the database
   - Store task states with timestamps (`created_at`, `updated_at`) and status flags (`completed`)
   - Ensure stateless backend can fully reconstruct conversation context from database

3. **Database migrations**
   - Implement migration scripts to evolve schema without data loss
   - Validate schema changes before applying to production
   - Track migration history to allow rollbacks if needed

4. **Multi-tenant data isolation**
   - Validate `user_id` on every query and mutation
   - Prevent cross-user data access
   - Include safeguards in ORM queries and raw SQL statements

5. **Schema validation & evolution**
   - Verify table structures match defined SQLModel entities
   - Ensure compatibility with future schema changes
   - Test queries for correctness and performance

6. **Serverless PostgreSQL best practices**
   - Optimize connections for serverless environments
   - Minimize idle connections and pooling overhead
   - Ensure reliable storage in Neon Serverless PostgreSQL

## Best Practices
- Always validate input data before database operations
- Use SQLModel ORM for all CRUD operations
- Log all migration operations and schema changes
- Enforce multi-tenant isolation at query level
- Keep conversation and task data fully persistent and replayable

## Example Structure
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str
    conversation_id: int
    role: str  # user / assistant
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
