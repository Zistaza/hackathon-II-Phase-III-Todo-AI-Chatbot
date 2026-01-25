"""
Error handler for Todo AI Chatbot Agent
Handles MCP tool errors and invalid inputs
"""

from typing import Dict, Any


class ErrorHandler:
    """Handles errors and provides clear explanations to users"""

    def __init__(self):
        # Define error patterns and their explanations
        self.error_explanations = {
            "invalid_input": "The information you provided wasn't in the right format. Please check your input and try again.",
            "task_not_found": "I couldn't find the task you're looking for. It might have been deleted or you might need to be more specific.",
            "authentication_failed": "There was a problem with your authentication. Please make sure you're logged in.",
            "authorization_failed": "You don't have permission to perform this action.",
            "tool_unavailable": "The service needed to complete this action is temporarily unavailable. Please try again later.",
            "rate_limited": "You've made too many requests recently. Please wait a moment before trying again.",
            "internal_error": "Something went wrong on our end. We're looking into it. Please try again later."
        }

    def handle_mcp_tool_error(self, tool_name: str, error_message: str, arguments: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle errors from MCP tools and generate user-friendly explanations

        Args:
            tool_name: Name of the tool that failed
            error_message: Error message from the tool
            arguments: Arguments that were passed to the tool

        Returns:
            Dictionary containing explanation and suggested recovery
        """
        # Default error response
        response = {
            "explanation": f"An error occurred while trying to {self._tool_to_action(tool_name)}.",
            "recovery_suggestion": "Please try your request again or rephrase it."
        }

        # Map specific error messages to user-friendly explanations
        error_lower = error_message.lower() if error_message else ""

        if "not found" in error_lower or "does not exist" in error_lower:
            response["explanation"] = f"I couldn't find the task you're looking for. It may have been deleted or you might need to be more specific about which task you mean."
            response["recovery_suggestion"] = "Try listing your tasks first to see what's available, then refer to a specific task by name or number."
        elif "invalid" in error_lower or "malformed" in error_lower:
            response["explanation"] = "The information you provided wasn't in the right format."
            response["recovery_suggestion"] = "Please check your input and try again with clear details."
        elif "permission" in error_lower or "unauthorized" in error_lower:
            response["explanation"] = "You don't have permission to perform this action."
            response["recovery_suggestion"] = "Make sure you're logged in and have the necessary permissions."
        elif "authentication" in error_lower:
            response["explanation"] = "There was a problem with your authentication."
            response["recovery_suggestion"] = "Please log out and log back in, then try again."
        elif "timeout" in error_lower or "connection" in error_lower:
            response["explanation"] = "The service needed to complete this action is temporarily unavailable."
            response["recovery_suggestion"] = "Please wait a moment and try again."
        elif "duplicate" in error_lower or "already exists" in error_lower:
            response["explanation"] = "It looks like that task already exists."
            response["recovery_suggestion"] = "Perhaps you meant to update an existing task instead of creating a new one?"

        return response

    def handle_invalid_input(self, user_input: str, error_details: str = None) -> Dict[str, str]:
        """
        Handle invalid user input and provide guidance

        Args:
            user_input: The invalid input from the user
            error_details: Additional details about why the input was invalid

        Returns:
            Dictionary containing explanation and guidance
        """
        response = {
            "explanation": "I couldn't understand your request.",
            "guidance": "Try rephrasing your request in simpler terms."
        }

        # Analyze the input to provide more specific guidance
        input_lower = user_input.lower()

        # Check for common issues
        if len(input_lower.strip()) < 3:
            response["explanation"] = "Your message is too short for me to understand."
            response["guidance"] = "Please provide more details about what you'd like to do."
        elif "?" in input_lower and any(word in input_lower for word in ["can", "could", "would", "should"]):
            response["explanation"] = "I can help you manage your tasks."
            response["guidance"] = "Instead of asking if I can do something, just tell me what you'd like me to do. For example: 'Add a task to buy groceries' or 'Show my tasks'."
        elif any(word in input_lower for word in ["hello", "hi", "hey", "greetings"]):
            response["explanation"] = "I'm ready to help you manage your tasks!"
            response["guidance"] = "Tell me what you'd like to do with your tasks. For example: 'Add a task to call John' or 'Show my completed tasks'."
        else:
            response["explanation"] = "I'm not sure what you meant."
            response["guidance"] = "Try using clear, simple language. You can ask me to add, list, complete, delete, or update tasks."

        return response

    def handle_task_not_found(self, search_criteria: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle cases where a task couldn't be found

        Args:
            search_criteria: The criteria used to search for the task

        Returns:
            Dictionary containing explanation and alternatives
        """
        response = {
            "explanation": "I couldn't find a task matching your description.",
            "alternatives": ["List all your tasks to see what's available", "Create a new task instead", "Try being more specific about the task name"]
        }

        # Provide more specific alternatives based on search criteria
        if "title" in search_criteria:
            response["explanation"] = f"I couldn't find a task with the title '{search_criteria['title']}'."
            response["alternatives"].insert(0, f"Check if the task title is spelled correctly")

        if "status" in search_criteria:
            response["alternatives"].insert(1, f"Try looking for tasks with a different status")

        return response

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
            "list_tasks": "list your tasks",
            "complete_task": "complete a task",
            "delete_task": "delete a task",
            "update_task": "update a task"
        }

        return tool_actions.get(tool_name, f"use the {tool_name} function")