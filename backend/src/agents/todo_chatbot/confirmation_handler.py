"""
Confirmation handler for Todo AI Chatbot Agent
Generates success confirmations and error explanations
"""

from typing import Dict, Any, List


class ConfirmationHandler:
    """Handles success confirmations and error explanations for users"""

    def __init__(self):
        # Templates for different types of confirmations
        self.success_templates = {
            "add_task": [
                "I've added the task: '{title}'",
                "Task created: '{title}'",
                "Added '{title}' to your list"
            ],
            "list_tasks": [
                "You have {count} tasks.",
                "Here are your {count} tasks:",
                "I found {count} tasks for you:"
            ],
            "complete_task": [
                "I've marked '{title}' as completed.",
                "Completed task: '{title}'",
                "Task '{title}' is now marked as done."
            ],
            "delete_task": [
                "I've deleted the task: '{title}'",
                "Removed '{title}' from your list",
                "Deleted task: '{title}'"
            ],
            "update_task": [
                "I've updated the task: '{title}'",
                "Updated task: '{title}'",
                "Changes saved for '{title}'"
            ]
        }

        # Templates for error explanations
        self.error_templates = {
            "tool_failure": "I couldn't {action} because: {error_msg}",
            "validation_error": "{error_msg}. Please check your input and try again.",
            "ambiguous_request": "I'm not sure which task you mean. Could you be more specific?",
            "multiple_matches": "I found multiple tasks that match your description. Could you clarify which one you mean?"
        }

    def generate_success_confirmation(self, tool_name: str, result: Dict[str, Any],
                                   original_args: Dict[str, Any] = None) -> str:
        """
        Generate a natural language confirmation for successful operations

        Args:
            tool_name: Name of the tool that succeeded
            result: Result from the tool execution
            original_args: Original arguments passed to the tool

        Returns:
            Natural language confirmation message
        """
        if tool_name not in self.success_templates:
            return "Operation completed successfully."

        templates = self.success_templates[tool_name]

        # Choose an appropriate template based on the result
        if tool_name == "add_task":
            title = result.get("title", original_args.get("title", "unnamed task"))
            return templates[0].format(title=title)

        elif tool_name == "list_tasks":
            count = len(result.get("tasks", []))
            return templates[0].format(count=count)

        elif tool_name == "complete_task":
            title = result.get("title", original_args.get("task_reference", "the task"))
            return templates[0].format(title=title)

        elif tool_name == "delete_task":
            title = result.get("title", original_args.get("task_reference", "the task"))
            return templates[0].format(title=title)

        elif tool_name == "update_task":
            title = result.get("title", original_args.get("task_reference", "the task"))
            return templates[0].format(title=title)

        # Default to first template if specific logic not implemented
        return templates[0]

    def generate_error_explanation(self, error_type: str, error_details: Dict[str, Any]) -> str:
        """
        Generate a user-friendly explanation for errors

        Args:
            error_type: Type of error that occurred
            error_details: Details about the error

        Returns:
            Natural language error explanation
        """
        if error_type not in self.error_templates:
            return "An unexpected error occurred. Please try again."

        template = self.error_templates[error_type]

        # Fill in template with specific details
        if error_type == "tool_failure":
            action = self._tool_to_action(error_details.get("tool_name", "unknown"))
            error_msg = error_details.get("error_message", "an unknown error occurred")
            return template.format(action=action, error_msg=error_msg)

        elif error_type == "validation_error":
            error_msg = error_details.get("error_message", "there was a validation issue")
            return template.format(error_msg=error_msg)

        elif error_type == "ambiguous_request":
            return template

        elif error_type == "multiple_matches":
            return template

        return template

    def generate_confirmation_request(self, action: str, target: str, details: Dict[str, Any] = None) -> str:
        """
        Generate a confirmation request for potentially destructive operations

        Args:
            action: The action to be confirmed (e.g., "delete", "update")
            target: The target of the action (e.g., task name)
            details: Additional details about the action

        Returns:
            Confirmation request message
        """
        action_prompts = {
            "delete": f"Are you sure you want to delete '{target}'? This action cannot be undone.",
            "update": f"Are you sure you want to update '{target}' with the following changes: {self._format_changes(details)}?",
            "complete": f"Are you sure you want to mark '{target}' as complete?",
        }

        return action_prompts.get(action, f"Confirm: {action} {target}?")

    def generate_operation_summary(self, tool_calls: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of multiple operations performed

        Args:
            tool_calls: List of tool calls made
            results: List of results from the tool calls

        Returns:
            Summary of operations performed
        """
        if not tool_calls:
            return "No operations were performed."

        success_count = sum(1 for result in results if "error" not in result)
        total_count = len(tool_calls)

        if success_count == total_count:
            if total_count == 1:
                tool_name = tool_calls[0]["name"]
                result = results[0]
                return self.generate_success_confirmation(tool_name, result, tool_calls[0].get("arguments", {}))
            else:
                return f"All {success_count} operations completed successfully."
        else:
            return f"Completed {success_count} out of {total_count} operations. Some encountered issues."

    def _tool_to_action(self, tool_name: str) -> str:
        """
        Convert tool name to a user-friendly action description

        Args:
            tool_name: Name of the tool

        Returns:
            User-friendly action description
        """
        tool_actions = {
            "add_task": "add a task",
            "list_tasks": "list tasks",
            "complete_task": "complete a task",
            "delete_task": "delete a task",
            "update_task": "update a task"
        }

        return tool_actions.get(tool_name, f"perform an action")

    def _format_changes(self, changes: Dict[str, Any]) -> str:
        """
        Format changes for display in confirmation messages

        Args:
            changes: Dictionary of changes to be made

        Returns:
            Formatted string describing the changes
        """
        if not changes:
            return "no changes"

        change_parts = []
        for key, value in changes.items():
            if key != "task_id":  # Skip the ID as it's not a meaningful change
                change_parts.append(f"{key}: {value}")

        if not change_parts:
            return "no changes"

        return ", ".join(change_parts)