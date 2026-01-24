---
name: agent-behavior-iii-skill
description: Map user natural language commands to MCP tools, manage multi-tool operations, preserve conversation context, and ensure deterministic AI agent behavior for Phase-III Todo AI Chatbot.
---

# Agent Behavior Skill (Phase III)

## Instructions

1. **Natural language to tool mapping**
   - Analyze user messages and determine which MCP tool(s) to invoke:
     - `add_task` — for creation commands
     - `list_tasks` — for viewing tasks
     - `complete_task` — for completion commands
     - `delete_task` — for removal commands
     - `update_task` — for modification commands
   - Support variations in user phrasing
   - Maintain consistent mapping with Phase-III specifications

2. **Multi-tool orchestration**
   - Handle messages that require multiple MCP tool actions in a single turn
   - Sequence tool calls deterministically
   - Aggregate results and return consolidated response to user

3. **Confirmation and feedback**
   - Provide friendly confirmations after every tool operation
   - Include relevant information such as task title or status
   - Ensure responses are clear, structured, and consistent

4. **Error handling**
   - Detect and handle errors such as:
     - Task not found
     - Invalid parameters
     - Unauthorized actions
   - Provide informative feedback to user without exposing internal errors

5. **Conversation context management**
   - Preserve context using stateless request cycle
   - Fetch prior conversation messages from database for context
   - Pass context to agent reasoning to ensure coherent responses
   - Ensure replayable conversations after server restart

6. **MCP Server integration**
   - Call MCP tools exclusively via Official MCP SDK
   - Avoid embedding direct database queries or conversational logic inside tools
   - Follow tool-based interaction principle strictly

7. **Deterministic behavior**
   - Ensure AI agent behaves consistently across repeated identical requests
   - Support testing and judge evaluation with predictable outputs

## Best Practices
- Always validate and sanitize user input before invoking MCP tools
- Follow agentic-first design: reasoning drives all task operations
- Maintain stateless architecture; no server-side memory
- Provide clear, structured, and friendly responses for every action
- Log actions and results for audit and debugging purposes

## Example Structure
```python
from openai_agents_sdk import Agent, Runner
from mcp_sdk import MCPClient

class AgentBehaviorSkill:
    def __init__(self):
        self.mcp_client = MCPClient()
    
    def handle_message(self, user_id: str, message: str, conversation_context: list):
        # Determine tool(s) to invoke based on natural language
        tools_to_call = self.map_message_to_tools(message)
        
        results = []
        for tool_call in tools_to_call:
            result = self.mcp_client.call_tool(user_id=user_id, **tool_call)
            results.append(result)
        
        # Construct friendly confirmation message
        response = self.build_confirmation_message(results)
        return response

    def map_message_to_tools(self, message: str) -> list:
        # NLP logic to map message to MCP tools
        pass

    def build_confirmation_message(self, results: list) -> str:
        # Aggregate results and generate user-friendly response
        pass
