"""
Ambiguity detector for Todo AI Chatbot Agent
Detects ambiguous requests that require clarification or discovery
"""

from typing import Dict, Any, List
from enum import Enum


class AmbiguityType(Enum):
    """Types of ambiguities the detector can identify"""
    VAGUE_REFERENCE = "vague_reference"
    PARTIAL_MATCH = "partial_match"
    MULTIPLE_POSSIBLE_TARGETS = "multiple_possible_targets"
    MISSING_CONTEXT = "missing_context"


class AmbiguityDetector:
    """Detects ambiguities in user requests that require clarification"""

    def __init__(self):
        # Define patterns that indicate ambiguous references
        self.vague_reference_patterns = [
            r'\b(it|that|this|the task|the one|that one|this one)\b',
            r'\b(first|last|previous|recent|current)\b',
            r'\b(same|similar|that thing|that item)\b'
        ]

        # Generic task terms that might indicate partial matching
        self.generic_terms = [
            r'\b(meeting|appointment|grocery|shopping|work|email|call|reminder|task|todo)\b'
        ]

    def detect_ambiguity(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Detect if a request is ambiguous and needs clarification

        Args:
            message: The user message to analyze
            intent: The classified intent

        Returns:
            Dictionary containing ambiguity information or None if no ambiguity
        """
        message_lower = message.lower().strip()

        # Only check for ambiguity on certain intents
        if intent not in ['task_completion', 'task_deletion', 'task_update']:
            return {
                "is_ambiguous": False,
                "type": None,
                "confidence": 0.0,
                "suggested_resolution": None
            }

        # Check for vague references
        vague_detected = self._detect_vague_reference(message_lower)
        if vague_detected:
            return {
                "is_ambiguous": True,
                "type": AmbiguityType.VAGUE_REFERENCE.value,
                "confidence": 0.9,
                "suggested_resolution": "list_tasks_first"
            }

        # Check for partial matches
        partial_match_detected = self._detect_partial_match(message_lower)
        if partial_match_detected:
            return {
                "is_ambiguous": True,
                "type": AmbiguityType.PARTIAL_MATCH.value,
                "confidence": 0.7,
                "suggested_resolution": "list_matching_tasks"
            }

        # Check for missing context
        missing_context_detected = self._detect_missing_context(message_lower)
        if missing_context_detected:
            return {
                "is_ambiguous": True,
                "type": AmbiguityType.MISSING_CONTEXT.value,
                "confidence": 0.6,
                "suggested_resolution": "request_specific_identification"
            }

        return {
            "is_ambiguous": False,
            "type": None,
            "confidence": 0.0,
            "suggested_resolution": None
        }

    def _detect_vague_reference(self, message: str) -> bool:
        """Detect vague references like 'it', 'that', 'the task'"""
        import re
        for pattern in self.vague_reference_patterns:
            if re.search(pattern, message):
                return True
        return False

    def _detect_partial_match(self, message: str) -> bool:
        """Detect generic terms that might match multiple tasks"""
        import re
        # Look for generic terms without specific identifiers
        for term in self.generic_terms:
            if re.search(term, message):
                # Check if there are specific identifiers like numbers or unique names
                if not re.search(r'\b\d+\b|\b(name|title|called|named|specific)\b|\b[A-Za-z]{4,}\b', message):
                    return True
        return False

    def _detect_missing_context(self, message: str) -> bool:
        """Detect when important context is missing"""
        import re
        # Look for actions without clear targets
        action_patterns = [
            r'\bcomplete|finish|done|delete|remove|update|change\b'
        ]

        for pattern in action_patterns:
            if re.search(pattern, message):
                # If action is present but no clear target is specified
                if not re.search(r'\b"[^"]+"|\'[^\']+\'|\b[A-Za-z]{4,}\b|\b\d+\b', message):
                    return True
        return False

    def find_potential_targets(self, message: str, available_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential task targets based on the user message

        Args:
            message: The user message
            available_tasks: List of available tasks to match against

        Returns:
            List of potential matching tasks
        """
        message_lower = message.lower()
        potential_matches = []

        for task in available_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower()

            # Score based on how well the message matches the task
            score = 0

            # Check if any word from the message appears in the task title
            message_words = message_lower.split()
            for word in message_words:
                if len(word) > 2 and word in task_title:
                    score += 1
                if len(word) > 2 and word in task_description:
                    score += 0.5

            if score > 0:
                potential_matches.append({
                    'task': task,
                    'score': score,
                    'match_reason': f"Found '{word}' in task title/description"
                })

        # Sort by score descending
        potential_matches.sort(key=lambda x: x['score'], reverse=True)

        return potential_matches