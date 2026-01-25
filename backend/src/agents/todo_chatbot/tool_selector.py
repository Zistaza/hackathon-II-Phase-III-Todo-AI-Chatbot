"""
Tool selector for Todo AI Chatbot Agent
Selects appropriate MCP tools based on intent and context
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from .intent_classifier import IntentType


class ToolSelector:
    """Selects appropriate MCP tools based on classified intent and extracted parameters"""

    def __init__(self):
        # Define mapping from intents to tools
        self.intent_to_tool = {
            IntentType.TASK_CREATION: "add_task",
            IntentType.TASK_LISTING: "list_tasks",
            IntentType.TASK_COMPLETION: "complete_task",
            IntentType.TASK_DELETION: "delete_task",
            IntentType.TASK_UPDATE: "update_task"
        }

    def select_tool(self, intent: IntentType, extracted_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select the appropriate tool based on intent and extracted parameters

        Args:
            intent: The classified intent
            extracted_params: Parameters extracted from the user message

        Returns:
            Dictionary containing tool name and arguments, or None if no suitable tool
        """
        if intent not in self.intent_to_tool:
            return None

        tool_name = self.intent_to_tool[intent]
        tool_args = self._prepare_arguments(tool_name, extracted_params)

        # Validate required arguments
        if not self._validate_arguments(tool_name, tool_args):
            return None

        return {
            "name": tool_name,
            "arguments": tool_args
        }

    def _prepare_arguments(self, tool_name: str, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare arguments for the selected tool based on extracted parameters

        Args:
            tool_name: Name of the tool to prepare arguments for
            extracted_params: Parameters extracted from the user message

        Returns:
            Dictionary of prepared arguments
        """
        args = {}

        if tool_name == "add_task":
            # Required: title
            # Optional: description, due_date
            args["title"] = extracted_params.get("title", "")
            if "description" in extracted_params:
                args["description"] = extracted_params["description"]
            if "due_date" in extracted_params:
                args["due_date"] = extracted_params["due_date"]

        elif tool_name == "list_tasks":
            # Optional: status_filter, sort_order, limit
            if "status_filter" in extracted_params:
                args["status_filter"] = extracted_params["status_filter"]
            if "sort_order" in extracted_params:
                args["sort_order"] = extracted_params["sort_order"]
            if "limit" in extracted_params:
                args["limit"] = extracted_params["limit"]

        elif tool_name == "complete_task":
            # Required: task_id or task_reference
            if "task_id" in extracted_params:
                args["task_id"] = extracted_params["task_id"]
            elif "task_reference" in extracted_params:
                args["task_reference"] = extracted_params["task_reference"]

        elif tool_name == "delete_task":
            # Required: task_id or task_reference
            if "task_id" in extracted_params:
                args["task_id"] = extracted_params["task_id"]
            elif "task_reference" in extracted_params:
                args["task_reference"] = extracted_params["task_reference"]

        elif tool_name == "update_task":
            # Required: task_id or task_reference
            # Optional: title, description, due_date, status
            if "task_id" in extracted_params:
                args["task_id"] = extracted_params["task_id"]
            elif "task_reference" in extracted_params:
                args["task_reference"] = extracted_params["task_reference"]

            if "title" in extracted_params:
                args["title"] = extracted_params["title"]
            if "description" in extracted_params:
                args["description"] = extracted_params["description"]
            if "due_date" in extracted_params:
                args["due_date"] = extracted_params["due_date"]
            if "status" in extracted_params:
                args["status"] = extracted_params["status"]

        return args

    def _validate_arguments(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """
        Validate that required arguments are present for the tool

        Args:
            tool_name: Name of the tool to validate
            args: Arguments to validate

        Returns:
            True if arguments are valid, False otherwise
        """
        if tool_name == "add_task":
            # Title is required
            return "title" in args and args["title"].strip() != ""
        elif tool_name in ["complete_task", "delete_task"]:
            # task_id or task_reference is required
            return "task_id" in args or "task_reference" in args
        elif tool_name == "update_task":
            # task_id or task_reference is required, plus at least one field to update
            has_id = "task_id" in args or "task_reference" in args
            has_updates = any(k in args for k in ["title", "description", "due_date", "status"])
            return has_id and has_updates
        else:
            # list_tasks has no required arguments
            return True

    def handle_ambiguous_request(self, intent: IntentType, extracted_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle ambiguous requests by returning a sequence of tool calls

        For ambiguous requests, we might need to:
        1. List tasks first to identify options
        2. Then perform the intended action

        Args:
            intent: The classified intent
            extracted_params: Parameters extracted from the user message

        Returns:
            List of tool call dictionaries to execute in sequence
        """
        tool_calls = []

        # First, list tasks to identify options (discovery-first pattern)
        list_args = {"status_filter": "all"}  # Show all tasks to resolve ambiguity
        tool_calls.append({
            "name": "list_tasks",
            "arguments": list_args
        })

        # Then, prepare the original intent tool call with the reference
        # (which will need to be resolved after seeing the list)
        original_tool = self.select_tool(intent, extracted_params)
        if original_tool:
            tool_calls.append(original_tool)

        return tool_calls

    def handle_multi_step_flow(self, intent: IntentType, extracted_params: Dict[str, Any],
                              available_tasks: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Handle multi-step flows that require multiple tool calls

        Args:
            intent: The classified intent
            extracted_params: Parameters extracted from the user message
            available_tasks: Available tasks to help resolve the intent

        Returns:
            List of tool call dictionaries to execute in sequence
        """
        tool_calls = []

        # For certain intents, we might need to list tasks first to identify the target
        if intent in [IntentType.TASK_COMPLETION, IntentType.TASK_DELETION, IntentType.TASK_UPDATE] and available_tasks is None:
            # If we don't have available tasks, list them first
            list_args = {"status_filter": "all"}
            tool_calls.append({
                "name": "list_tasks",
                "arguments": list_args
            })

        # Add the main intent tool call
        main_tool = self.select_tool(intent, extracted_params)
        if main_tool:
            tool_calls.append(main_tool)

        return tool_calls

    def prioritize_tools(self, possible_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize tools when multiple could apply based on context

        Args:
            possible_tools: List of possible tools that could apply

        Returns:
            Prioritized list of tool calls
        """
        # Default behavior: return tools in the order provided
        # In a more sophisticated implementation, you might add logic here
        # to reorder tools based on context or confidence

        # For now, implement basic priority rules:
        # - If both list_tasks and another action are present, list_tasks first
        # - This supports the discovery-first pattern for ambiguous requests

        ordered_tools = []
        action_tools = []
        list_tool = None

        for tool in possible_tools:
            if tool["name"] == "list_tasks":
                list_tool = tool
            else:
                action_tools.append(tool)

        # Add list tool first if present
        if list_tool:
            ordered_tools.append(list_tool)

        # Then add action tools
        ordered_tools.extend(action_tools)

        return ordered_tools