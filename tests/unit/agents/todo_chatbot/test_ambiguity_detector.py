"""
Unit tests for Ambiguity Detector
"""

import pytest
from backend.src.agents.todo_chatbot.ambiguity_detector import AmbiguityDetector


@pytest.fixture
def ambiguity_detector():
    """Create an instance of AmbiguityDetector for testing"""
    return AmbiguityDetector()


def test_detect_vague_reference(ambiguity_detector):
    """Test detection of vague references"""
    message = "Complete the task"
    intent = "task_completion"

    result = ambiguity_detector.detect_ambiguity(message, intent)

    # Should detect that "the task" is vague
    assert result["is_ambiguous"] == True
    assert result["confidence"] > 0.5


def test_detect_partial_match(ambiguity_detector):
    """Test detection of partial matches"""
    message = "Delete the meeting"
    intent = "task_deletion"

    result = ambiguity_detector.detect_ambiguity(message, intent)

    # Should detect that "the meeting" could match multiple meetings
    assert result["is_ambiguous"] == True


def test_non_ambiguous_request(ambiguity_detector):
    """Test that non-ambiguous requests are not flagged"""
    message = "Add a task to buy groceries"
    intent = "task_creation"

    result = ambiguity_detector.detect_ambiguity(message, intent)

    # Task creation shouldn't be considered ambiguous by this detector
    assert result["is_ambiguous"] == False


def test_find_potential_targets(ambiguity_detector):
    """Test finding potential task targets based on message"""
    message = "complete the grocery shopping"
    available_tasks = [
        {"id": "1", "title": "grocery shopping", "description": "buy food"},
        {"id": "2", "title": "clean house", "description": "tidy up"},
        {"id": "3", "title": "call doctor", "description": "schedule appointment"}
    ]

    matches = ambiguity_detector.find_potential_targets(message, available_tasks)

    # Should find "grocery shopping" as the best match
    assert len(matches) > 0
    assert matches[0]["task"]["title"] == "grocery shopping"
    assert matches[0]["score"] > 0


def test_detect_ambiguity_for_completion_intent(ambiguity_detector):
    """Test ambiguity detection specifically for completion intents"""
    message = "Complete it"
    intent = "task_completion"

    result = ambiguity_detector.detect_ambiguity(message, intent)

    # "it" is a vague reference
    assert result["is_ambiguous"] == True
    assert result["type"] == "vague_reference"


def test_detect_ambiguity_for_deletion_intent(ambiguity_detector):
    """Test ambiguity detection specifically for deletion intents"""
    message = "Remove that one"
    intent = "task_deletion"

    result = ambiguity_detector.detect_ambiguity(message, intent)

    # "that one" is a vague reference
    assert result["is_ambiguous"] == True
    assert result["type"] == "vague_reference"