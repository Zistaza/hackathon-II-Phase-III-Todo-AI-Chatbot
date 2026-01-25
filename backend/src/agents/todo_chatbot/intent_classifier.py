"""
Intent classifier for Todo AI Chatbot Agent
Detects user intents from natural language input
"""

import re
from enum import Enum
from typing import Tuple, Optional


class IntentType(Enum):
    """Types of intents the agent can recognize"""
    TASK_CREATION = "task_creation"
    TASK_LISTING = "task_listing"
    TASK_COMPLETION = "task_completion"
    TASK_DELETION = "task_deletion"
    TASK_UPDATE = "task_update"
    UNKNOWN = "unknown"


class IntentClassifier:
    """Classifies user intents from natural language commands"""

    def __init__(self):
        # Define keyword patterns for each intent
        self.intent_patterns = {
            IntentType.TASK_CREATION: [
                r'\b(add|create|remember|write down|make|put in|jot down|save)\b',
                r'\b(task|todo|thing to do|item|note|remind me to)\b',
                r'\b(new|another|more)\b'
            ],
            IntentType.TASK_LISTING: [
                r'\b(see|show|list|check|view|display|look at|what.*do.*need|what.*have)\b',
                r'\b(tasks|todos|things to do|items|list|my.*stuff)\b',
                r'\b(all|everything|completed|done|pending|incomplete)\b'
            ],
            IntentType.TASK_COMPLETION: [
                r'\b(done|complete|finish|mark.*done|check off|cross off|finished)\b',
                r'\b(task|the|it|that|this|that one|this one)\b'
            ],
            IntentType.TASK_DELETION: [
                r'\b(delete|remove|cancel|get rid of|erase|trash|throw away)\b',
                r'\b(task|the|it|that|this|that one|this one)\b'
            ],
            IntentType.TASK_UPDATE: [
                r'\b(change|update|rename|edit|modify|fix|alter|adjust)\b',
                r'\b(task|the|it|that|this|that one|this one)\b'
            ]
        }

        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for intent, patterns in self.intent_patterns.items():
            compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
            self.compiled_patterns[intent] = compiled

    def classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """
        Classify the intent of a user message and return confidence score

        Args:
            message: The user message to classify

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        message_lower = message.lower().strip()

        scores = {}
        for intent, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(message_lower):
                    score += 1
            # Normalize score by number of patterns for this intent
            scores[intent] = score / len(patterns) if patterns else 0

        # Find the intent with the highest score
        best_intent = max(scores.keys(), key=lambda x: scores[x])
        best_score = scores[best_intent]

        # If no patterns matched significantly, return unknown
        if best_score == 0:
            return IntentType.UNKNOWN, 0.0

        # Adjust confidence based on how many patterns matched
        # If only 1 out of 3 patterns matched, lower confidence
        if best_score < 0.33:
            confidence = 0.5  # Medium-low confidence
        elif best_score < 0.67:
            confidence = 0.7  # Medium-high confidence
        else:
            confidence = 0.9  # High confidence

        return best_intent, confidence

    def extract_task_details(self, message: str, intent: IntentType) -> dict:
        """
        Extract task details from the message based on the intent

        Args:
            message: The user message
            intent: The classified intent

        Returns:
            Dictionary with extracted details
        """
        result = {}

        if intent == IntentType.TASK_CREATION:
            # Look for task title in the message
            # Remove common task creation verbs to isolate the title
            message_clean = re.sub(r'\b(add|create|remember|write down|make|put in|jot down|save)\b', '', message, flags=re.IGNORECASE)
            # Remove common task references
            message_clean = re.sub(r'\b(a|an|the|task|todo|thing to do|item|note|remind me to)\b', '', message_clean, flags=re.IGNORECASE)
            # Clean up whitespace
            title = message_clean.strip()

            if title:
                result['title'] = title
            else:
                result['title'] = message  # Use full message as title if no specific title found

        elif intent == IntentType.TASK_COMPLETION or intent == IntentType.TASK_DELETION or intent == IntentType.TASK_UPDATE:
            # Look for task identifiers (by name, position, etc.)
            # Extract potential task references
            # This is a simplified version - in practice, you'd want more sophisticated extraction

            # Look for "the <task_name>" or similar patterns
            match = re.search(r'\b(the|a|an)\s+([^.!?]+?)(?:\s+(?:task|one|it|that))?\b', message, re.IGNORECASE)
            if match:
                task_ref = match.group(2).strip()
                if task_ref and len(task_ref) > 2:  # At least 3 characters to be meaningful
                    result['task_reference'] = task_ref

        elif intent == IntentType.TASK_LISTING:
            # Extract status filters
            if re.search(r'\b(completed|done|finished)\b', message, re.IGNORECASE):
                result['status_filter'] = 'completed'
            elif re.search(r'\b(pending|incomplete|not done|todo)\b', message, re.IGNORECASE):
                result['status_filter'] = 'pending'
            else:
                result['status_filter'] = 'all'

        return result

    def is_ambiguous_request(self, message: str, intent: IntentType) -> bool:
        """
        Check if a request is ambiguous and might require clarification

        Args:
            message: The user message
            intent: The classified intent

        Returns:
            True if the request is ambiguous, False otherwise
        """
        if intent not in [IntentType.TASK_COMPLETION, IntentType.TASK_DELETION, IntentType.TASK_UPDATE]:
            return False

        # Check for vague references that could apply to multiple tasks
        vague_terms = [
            r'\b(it|that|this|the task|the one|that one|this one)\b',
            r'\b(first|last|previous|recent)\b',
            r'\b(same|similar|that thing)\b'
        ]

        message_lower = message.lower()
        for term in vague_terms:
            if re.search(term, message_lower):
                return True

        # Check for partial matches that might apply to multiple tasks
        # Look for very generic references
        generic_refs = [
            r'\b(meeting|appointment|grocery|shopping|work|email|call)\b'
        ]

        for ref in generic_refs:
            # If the message only contains generic terms without specific identifiers
            if re.search(ref, message_lower):
                # Check if there are specific identifiers like numbers, names, etc.
                if not re.search(r'\b\d+\b|\b(name|title|called|named|titled)\b', message_lower):
                    return True

        return False