"""
Unit tests for Intent Classifier
"""

import pytest
from backend.src.agents.todo_chatbot.intent_classifier import IntentClassifier, IntentType


@pytest.fixture
def intent_classifier():
    """Create an instance of IntentClassifier for testing"""
    return IntentClassifier()


def test_task_creation_intent(intent_classifier):
    """Test that task creation intents are correctly identified"""
    messages = [
        "Add a task to buy groceries",
        "Create a task to call mom",
        "Remember to schedule dentist appointment",
        "Write down that I need to finish the report"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.TASK_CREATION
        assert confidence > 0.0  # Should have some confidence


def test_task_listing_intent(intent_classifier):
    """Test that task listing intents are correctly identified"""
    messages = [
        "Show me my tasks",
        "List all my tasks",
        "What do I need to do?",
        "Check my todos",
        "View my pending tasks"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.TASK_LISTING
        assert confidence > 0.0


def test_task_completion_intent(intent_classifier):
    """Test that task completion intents are correctly identified"""
    messages = [
        "Complete the shopping task",
        "Mark the meeting as done",
        "Finish the assignment",
        "I'm done with the project"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.TASK_COMPLETION
        assert confidence > 0.0


def test_task_deletion_intent(intent_classifier):
    """Test that task deletion intents are correctly identified"""
    messages = [
        "Delete the reminder",
        "Remove the appointment",
        "Cancel the meeting",
        "Get rid of the old task"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.TASK_DELETION
        assert confidence > 0.0


def test_task_update_intent(intent_classifier):
    """Test that task update intents are correctly identified"""
    messages = [
        "Change the due date of the report",
        "Update the grocery list",
        "Rename the meeting task",
        "Edit the description of the project"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.TASK_UPDATE
        assert confidence > 0.0


def test_unknown_intent(intent_classifier):
    """Test that unknown intents are properly classified"""
    messages = [
        "What is the weather today?",
        "Tell me a joke",
        "How are you?",
        "Random text that doesn't relate to tasks"
    ]

    for message in messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == IntentType.UNKNOWN
        assert confidence == 0.0


def test_extract_task_details_creation(intent_classifier):
    """Test extraction of task details for creation intent"""
    message = "Add a task to buy milk and bread"
    details = intent_classifier.extract_task_details(message, IntentType.TASK_CREATION)

    assert "title" in details
    assert "buy milk and bread" in details["title"].lower()


def test_extract_task_details_listing(intent_classifier):
    """Test extraction of task details for listing intent"""
    message = "Show me my completed tasks"
    details = intent_classifier.extract_task_details(message, IntentType.TASK_LISTING)

    assert "status_filter" in details
    assert details["status_filter"] == "completed"


def test_is_ambiguous_request(intent_classifier):
    """Test detection of ambiguous requests"""
    # Non-ambiguous requests
    non_ambiguous = [
        ("Complete the task 'buy groceries'", IntentType.TASK_COMPLETION),
        ("Delete the meeting with John", IntentType.TASK_DELETION),
        ("Update the project deadline", IntentType.TASK_UPDATE)
    ]

    for message, intent in non_ambiguous:
        is_ambiguous = intent_classifier.is_ambiguous_request(message, intent)
        assert not is_ambiguous

    # Ambiguous requests
    ambiguous = [
        ("Complete the task", IntentType.TASK_COMPLETION),
        ("Delete it", IntentType.TASK_DELETION),
        ("Update that one", IntentType.TASK_UPDATE)
    ]

    for message, intent in ambiguous:
        is_ambiguous = intent_classifier.is_ambiguous_request(message, intent)
        assert is_ambiguous