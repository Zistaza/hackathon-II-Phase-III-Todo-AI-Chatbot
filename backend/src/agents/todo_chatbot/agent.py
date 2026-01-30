"""
Main agent class for Todo AI Chatbot Agent
Coordinates intent classification, tool selection, and response generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .intent_classifier import IntentClassifier, IntentType
from .tool_selector import ToolSelector
from .ambiguity_detector import AmbiguityDetector
from src.services.mcp_integration import MCPIntegration


class AgentConfig:
    """Configuration for the agent"""

    def __init__(self):
        self.intent_confidence_threshold = 0.6  # Minimum confidence for direct action (lowered for natural language)
        self.max_ambiguity_attempts = 3  # Max attempts to resolve ambiguous requests
        self.confirmation_required = True  # Whether destructive operations need explicit confirmation
        self.context_window_size = 10  # Number of previous messages to consider
        self.multi_step_timeout = 300  # Timeout for multi-step operations (seconds)
        self.enable_logging = True  # Enable detailed logging
        self.rate_limit_requests = 10  # Max requests per minute per user
        self.response_timeout = 30  # Timeout for MCP tool responses in seconds


class Agent:
    """Main agent class that processes user messages and orchestrates MCP tools"""

    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.intent_classifier = IntentClassifier()
        self.tool_selector = ToolSelector()
        self.ambiguity_detector = AmbiguityDetector()
        self.mcp_integration = MCPIntegration()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        if self.config.enable_logging:
            logging.basicConfig(level=logging.INFO)

    async def process_message(self, user_id: str, conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and return the agent's response

        Args:
            user_id: ID of the requesting user
            conversation_id: ID of the conversation
            message: The user message to process

        Returns:
            Dictionary containing the agent's response and any tool calls made
        """
        # Log the incoming request
        if self.config.enable_logging:
            self.logger.info(f"Processing message for user {user_id}, conversation {conversation_id}")
        # Classify intent from the message
        intent, confidence = self.intent_classifier.classify_intent(message)

        # Extract relevant details from the message
        extracted_params = self.intent_classifier.extract_task_details(message, intent)

        # Check for ambiguity using both the intent classifier and the dedicated detector
        is_ambiguous_intent = self.intent_classifier.is_ambiguous_request(message, intent)

        # Use the ambiguity detector for more sophisticated detection
        ambiguity_check = self.ambiguity_detector.detect_ambiguity(message, intent.value)
        is_ambiguous_detector = ambiguity_check["is_ambiguous"]

        # Prepare response structure
        response_data = {
            "conversation_id": conversation_id,
            "response": "",
            "tool_calls": [],
            "next_action": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Handle based on intent and confidence
        if intent == IntentType.UNKNOWN:
            response_data["response"] = "I'm not sure what you'd like to do. Could you clarify your request?"
            return response_data

        # If the request is ambiguous, handle it specially
        if is_ambiguous_intent or is_ambiguous_detector:
            return await self._handle_ambiguous_request(
                user_id, conversation_id, message, intent, extracted_params, ambiguity_check
            )

        # If the intent is task completion, deletion, or update but we only have a reference (not an ID),
        # we should list tasks first to find the correct one
        if intent in [IntentType.TASK_COMPLETION, IntentType.TASK_DELETION, IntentType.TASK_UPDATE] and \
           "task_reference" in extracted_params and "task_id" not in extracted_params:
            # Need to resolve the task reference by listing tasks first
            return await self._resolve_task_reference(
                user_id, conversation_id, message, intent, extracted_params
            )

        # If confidence is high enough, proceed with tool selection
        if confidence >= self.config.intent_confidence_threshold:
            # Select appropriate tool based on intent
            tool_call = self.tool_selector.select_tool(intent, extracted_params)

            if tool_call:
                # Execute the tool call with the user_id
                tool_result = await self.mcp_integration.execute_tool_call(
                    user_id, tool_call["name"], tool_call["arguments"]
                )

                # Add to response
                response_data["tool_calls"].append({
                    "id": f"call_{len(response_data['tool_calls'])}",
                    "name": tool_call["name"],
                    "arguments": tool_call["arguments"],
                    "status": "success" if "error" not in tool_result else "error",
                    "result": tool_result
                })

                # Generate natural language response based on tool result
                response_data["response"] = self._generate_response_for_tool_result(
                    intent, tool_result, tool_call["arguments"]
                )
            else:
                response_data["response"] = "I couldn't understand the details of your request. Could you provide more information?"
        else:
            # Low confidence - ask for clarification
            response_data["response"] = f"I'm not entirely sure what you mean. Did you want to {self._intent_to_natural_language(intent)}?"

        return response_data

    async def _handle_ambiguous_request(self, user_id: str, conversation_id: str,
                                       message: str, intent: IntentType,
                                       extracted_params: Dict[str, Any],
                                       ambiguity_check: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle requests that are ambiguous and might require clarification

        Args:
            user_id: ID of the requesting user
            conversation_id: ID of the conversation
            message: The original user message
            intent: The classified intent
            extracted_params: Parameters extracted from the message
            ambiguity_check: Results from the ambiguity detector
            token: JWT token for authentication

        Returns:
            Dictionary containing the agent's response and any tool calls made
        """
        response_data = {
            "conversation_id": conversation_id,
            "response": "",
            "tool_calls": [],
            "next_action": "await_confirmation",
            "timestamp": datetime.utcnow().isoformat()
        }

        # For ambiguous requests, first list relevant tasks to provide context (discovery-first pattern)
        list_args = {"status_filter": "all"}
        list_result = await self.mcp_integration.execute_tool_call(user_id, "list_tasks", list_args)

        response_data["tool_calls"].append({
            "id": f"call_{len(response_data['tool_calls'])}",
            "name": "list_tasks",
            "arguments": list_args,
            "status": "success" if "error" not in list_result else "error",
            "result": list_result
        })

        # Check if we got tasks back
        if "tasks" in list_result and len(list_result["tasks"]) > 0:
            # Generate a response asking for clarification based on the type of ambiguity
            task_titles = [task.get("title", f"Task {task.get('id', 'unknown')}") for task in list_result["tasks"]]

            if len(task_titles) == 1:
                response_data["response"] = f"I found one task that might match: '{task_titles[0]}'. Is this the one you meant?"
            elif ambiguity_check and ambiguity_check.get("type") == "multiple_possible_targets":
                response_data["response"] = f"I found {len(task_titles)} tasks that might match your request. Could you specify which one you mean? Options: {', '.join(task_titles[:5])}"
                if len(task_titles) > 5:
                    response_data["response"] += f" ...and {len(task_titles) - 5} more."
            else:
                response_data["response"] = f"I found {len(task_titles)} tasks that might match: {', '.join(task_titles[:3])}. Could you specify which one you're referring to?"

            # If we have more than 3 tasks, indicate there are more
            if len(task_titles) > 3:
                response_data["response"] += f" ...and {len(task_titles) - 3} more."
        else:
            # No matching tasks found
            response_data["response"] = f"I couldn't find any tasks matching your request. Would you like to create a new task instead?"

        return response_data

    def _generate_response_for_tool_result(self, intent: IntentType, tool_result: Dict[str, Any],
                                          tool_args: Dict[str, Any]) -> str:
        """
        Generate a natural language response based on the tool result

        Args:
            intent: The original intent
            tool_result: Result from the MCP tool
            tool_args: Arguments passed to the tool

        Returns:
            Natural language response string
        """
        if "error" in tool_result:
            return f"Sorry, I encountered an error: {tool_result['error']}"

        if intent == IntentType.TASK_CREATION:
            if "task_id" in tool_result:
                return f"I've created the task: '{tool_result.get('title', tool_args.get('title', 'unnamed'))}'"
            else:
                return "I've created your task."

        elif intent == IntentType.TASK_LISTING:
            tasks = tool_result.get("tasks", [])
            if not tasks:
                return "You don't have any tasks right now."
            elif len(tasks) == 1:
                return f"You have 1 task: '{tasks[0].get('title', 'unnamed')}'"
            else:
                # For "all" requests, show all task titles; for other requests, limit to first 3
                status_filter = tool_args.get("status_filter", "all")
                if status_filter == "all":
                    # Show all tasks when user asks for "all my tasks"
                    task_titles = [task.get('title', 'unnamed') for task in tasks]
                    return f"You have {len(tasks)} tasks: {', '.join(task_titles)}"
                else:
                    # For filtered requests (pending/completed), show first few
                    task_titles = [task.get('title', 'unnamed') for task in tasks[:3]]
                    return f"You have {len(tasks)} tasks. The first few are: {', '.join(task_titles)}"

        elif intent == IntentType.TASK_COMPLETION:
            return f"I've marked the task as completed."

        elif intent == IntentType.TASK_DELETION:
            if tool_result.get("deleted"):
                return "I've deleted the task."
            else:
                return "I couldn't delete the task."

        elif intent == IntentType.TASK_UPDATE:
            return f"I've updated the task: '{tool_result.get('title', 'unnamed')}'"

        return "Operation completed successfully."

    async def _resolve_task_reference(self, user_id: str, conversation_id: str, message: str,
                                   intent: IntentType, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve task references by listing tasks first, then performing the intended action

        Args:
            user_id: ID of the requesting user
            conversation_id: ID of the conversation
            message: The original user message
            intent: The classified intent
            extracted_params: Parameters extracted from the message

        Returns:
            Dictionary containing the agent's response and any tool calls made
        """
        response_data = {
            "conversation_id": conversation_id,
            "response": "",
            "tool_calls": [],
            "next_action": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }

        # First, list tasks to find the matching one
        list_args = {"status_filter": "all"}
        list_result = await self.mcp_integration.execute_tool_call(user_id, "list_tasks", list_args)

        response_data["tool_calls"].append({
            "id": f"call_{len(response_data['tool_calls'])}",
            "name": "list_tasks",
            "arguments": list_args,
            "status": "success" if "error" not in list_result else "error",
            "result": list_result
        })

        if "error" in list_result:
            response_data["response"] = f"I couldn't list your tasks: {list_result['error']}"
            return response_data

        # Find the task that matches the reference
        task_reference = extracted_params.get("task_reference", "").lower()
        matching_task = None

        for task in list_result.get("tasks", []):
            if task is None or not hasattr(task, 'get'):
                continue  # Skip None tasks or tasks that don't have get method (not dict-like)

            task_title = (task.get("title") or "").lower()
            task_desc = (task.get("description") or "").lower()

            if task_reference in task_title or task_reference in task_desc:
                matching_task = task
                break

        if not matching_task:
            response_data["response"] = f"I couldn't find a task matching '{extracted_params.get('task_reference')}'. Here are your tasks: {[t.get('title', 'Unnamed') for t in list_result.get('tasks', [])][:5]}"
            return response_data

        # Now perform the intended action on the found task
        if intent == IntentType.TASK_COMPLETION:
            tool_call = {
                "name": "complete_task",
                "arguments": {
                    "task_id": matching_task["id"],
                    "title": matching_task.get("title", "")
                }
            }
        elif intent == IntentType.TASK_DELETION:
            tool_call = {
                "name": "delete_task",
                "arguments": {
                    "task_id": matching_task["id"],
                    "title": matching_task.get("title", "")
                }
            }
        elif intent == IntentType.TASK_UPDATE:
            # Use the original extracted params but with the found task_id
            update_args = extracted_params.copy()
            update_args["task_id"] = matching_task["id"]
            del update_args["task_reference"]  # Remove reference since we now have the ID

            tool_call = {
                "name": "update_task",
                "arguments": update_args
            }
        else:
            # Fallback
            response_data["response"] = f"I found the task '{matching_task.get('title', 'unnamed')}', but I'm not sure what to do with it."
            return response_data

        # Execute the tool call
        tool_result = await self.mcp_integration.execute_tool_call(
            user_id, tool_call["name"], tool_call["arguments"]
        )

        # Add to response
        response_data["tool_calls"].append({
            "id": f"call_{len(response_data['tool_calls'])}",
            "name": tool_call["name"],
            "arguments": tool_call["arguments"],
            "status": "success" if "error" not in tool_result else "error",
            "result": tool_result
        })

        # Generate natural language response based on tool result
        response_data["response"] = self._generate_response_for_tool_result(
            intent, tool_result, tool_call["arguments"]
        )

        return response_data

    def _intent_to_natural_language(self, intent: IntentType) -> str:
        """
        Convert intent to natural language description

        Args:
            intent: The intent to convert

        Returns:
            Natural language description of the intent
        """
        intent_descriptions = {
            IntentType.TASK_CREATION: "add a new task",
            IntentType.TASK_LISTING: "see your tasks",
            IntentType.TASK_COMPLETION: "complete a task",
            IntentType.TASK_DELETION: "delete a task",
            IntentType.TASK_UPDATE: "update a task"
        }

        return intent_descriptions.get(intent, "perform an action")