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
        # Define keyword patterns for each intent - enhanced to recognize more natural language
        self.intent_patterns = {
            IntentType.TASK_CREATION: [
                r'\b(add|create|remember|write down|make|put in|jot down|save|need to|have to|should|want to|going to|i need to|i want to|i should|plan to|need|set reminder for|remind me to|put on my list|on my list|get done|get started|start|begin|initiate)\b',
                r'\b(task|todo|thing to do|item|note|to do|to-do|list|my list|for later|something|anything|it|that|this|what i need to|what to|for|about|regarding)\b'
            ],
            IntentType.TASK_LISTING: [
                r'\b(see|show|list|check|view|display|look at|what.*do.*need|what.*have|what.*got|my|all|everything|tell me about|what\'s|whats|give me|fetch|retrieve|get me|look up|find my|browse|go through|review|examine)\b',
                r'\b(tasks|todos|things to do|items|list|my.*stuff|to do list|todo list|what i|progress|status|current|standing|pending|completed|done|finished|active|remaining)\b'
            ],
            IntentType.TASK_COMPLETION: [
                r'\b(done|complete|finish|marked as done|check off|cross off|finished|knocked out|ticked off|closed|wrapped up|accomplished|achieved|fulfilled|carried out|carry out|did|completed|tick|check)\b',
                r'\b(task|the|it|that|this|that one|this one|number|no\.?\s*\d+|#\d+|first|second|third|last|previous|next|specific|particular|certain|selected|given)\b'
            ],
            IntentType.TASK_DELETION: [
                r'\b(delete|remove|cancel|get rid of|erase|trash|throw away|scrub|eliminate|dispose|drop|omit|exclude|discard|get rid|bye bye|take off|off my list|off the list|scratch|cancel|abort|stop|quit)\b',
                r'\b(task|the|it|that|this|that one|this one|meeting|appointment|event|item|thing|one|specific|particular|certain|selected|given)\b'
            ],
            IntentType.TASK_UPDATE: [
                r'\b(change|update|rename|edit|modify|fix|alter|adjust|revise|refine|correct|improve|switch|swap|replace|transform|convert|make different|redo|rework|rewrite|rephrase|update|refresh|upgrade|change to|turn into|switch to)\b',
                r'\b(task|the|it|that|this|that one|this one|to|into|be|become|called|named|titled|named as|called as|labeled|to be|so that|in order to|to make it|making it)\b'
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

        # Apply contextual adjustments to handle edge cases
        # Special handling for messages that start with deletion words but contain creation-like phrases
        # Example: "delete the 'add task go' task" should be TASK_DELETION, not TASK_CREATION
        start_words = message_lower.split()
        if start_words:
            first_word = start_words[0]

            # If the message starts with a deletion word and contains task reference patterns
            if first_word in ['delete', 'remove']:
                # Check if it contains task reference patterns like "the '...' task"
                if re.search(r'\bthe\s+[\'"][^\'"]+[\'"]\s+task\b', message_lower) or \
                   re.search(r'\bthe\s+\w+\s+task\b', message_lower) or \
                   re.search(r'\b[a-z\s\']*task\b', message_lower):
                    # Increase deletion score if deletion patterns were matched
                    if IntentType.TASK_DELETION in scores and scores[IntentType.TASK_DELETION] > 0:
                        # Reduce creation score to prevent misclassification
                        if IntentType.TASK_CREATION in scores:
                            # Only reduce creation score if deletion has some matching patterns
                            scores[IntentType.TASK_CREATION] = max(0, scores[IntentType.TASK_CREATION] - 0.5)

        # Find the intent with the highest score after adjustments
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
            # First, check if there are quotes around the task title
            quote_match = re.search(r'["\']([^"\']+)["\']', message)
            if quote_match:
                # If there are quotes, use the content inside quotes as the title
                result['title'] = quote_match.group(1).strip()
            else:
                # Look for "to [verb]" pattern like "to buy groceries"
                to_pattern = re.search(r'\b(to|for|about|regarding)\s+([^.!?]+?)(?:\s+(?:task|todo|thing|item|later|tomorrow|today|tonight|now|soon|later|week|day|morning|evening|night|afternoon|reminders?|notes?))?', message, re.IGNORECASE)
                if to_pattern and len(to_pattern.group(2).strip()) > 2:
                    result['title'] = to_pattern.group(2).strip()
                else:
                    # Remove common task creation verbs to isolate the title
                    message_clean = re.sub(r'\b(add|create|remember|write down|make|put in|jot down|save|need to|have to|should|want to|going to|i need to|i want to|i should|plan to|remind me to|put on my list|on my list|get done|get started|start|begin|initiate)\b', '', message, flags=re.IGNORECASE)
                    # Remove common task references
                    message_clean = re.sub(r'\b(a|an|the|task|todo|thing to do|item|note|remind me to|to do|to-do|list|my|that|it|this|for later|something|anything)\b', '', message_clean, flags=re.IGNORECASE)
                    # Clean up extra whitespace and punctuation
                    title = re.sub(r'\s+', ' ', message_clean).strip().strip('!.,?;')

                    if title and len(title.strip()) > 2:
                        result['title'] = title.strip()
                    else:
                        result['title'] = message.strip()  # Use full message as title if no specific title found

        elif intent == IntentType.TASK_COMPLETION or intent == IntentType.TASK_DELETION or intent == IntentType.TASK_UPDATE:
            # Look for task identifiers (by name, position, number, etc.)

            # Look for numbered task references like "task 3", "task #3", "task number 3"
            number_match = re.search(r'(?:task|number|#)\s*(\d+)', message, re.IGNORECASE)
            if number_match:
                result['task_id'] = number_match.group(1)
            else:
                # For TASK_UPDATE, handle the specific update pattern first: "update X to Y" or "change X to Y"
                if intent == IntentType.TASK_UPDATE:
                    # Look for patterns like "update [task_ref] to [new_value]" or "change [task_ref] to [new_value]"
                    # Use a pattern that captures everything before the last " to " to handle cases like "Change task to pay amount to 'Call me'"
                    update_pattern = re.search(r'\b(update|change|modify|rename)\s+(.+)\s+to\s+(.+)$', message, re.IGNORECASE)
                    if update_pattern:
                        task_part = update_pattern.group(2).strip()
                        value_part = update_pattern.group(3).strip()

                        # Extract the new title/value from the value part (could be quoted or not)
                        quote_in_value = re.search(r'["\']([^"\']+)["\']', value_part)
                        if quote_in_value:
                            new_title = quote_in_value.group(1).strip()
                        else:
                            new_title = value_part.strip()

                        # Extract task reference from the task part (could be quoted or not)
                        # First, look for quoted task names within the task part
                        quote_in_task = re.search(r'["\']([^"\']+)["\']', task_part)
                        if quote_in_task:
                            task_ref = quote_in_task.group(1).strip()
                        else:
                            # If no quotes, try to extract the meaningful task name
                            # Handle patterns like "task [name]" where we want just the name
                            task_ref_match = re.match(r'^task\s+(.+)$', task_part, re.IGNORECASE)
                            if task_ref_match:
                                task_ref = task_ref_match.group(1).strip()
                            else:
                                # Handle complex cases like "task to pay amount" -> "to pay amount"
                                # Remove leading "task " and trailing " task" if they exist
                                task_ref = re.sub(r'^task\s+|\s+task$', '', task_part, flags=re.IGNORECASE).strip()

                        if task_ref and len(task_ref) > 2:
                            result['task_reference'] = task_ref
                        if new_title and len(new_title) > 0:
                            result['title'] = new_title
                    else:
                        # Fallback to general patterns for TASK_UPDATE
                        # Look for "the <task_name>" or specific task references
                        specific_match = re.search(r'\b(?:the|a|an)\s+([^.!?,"]+?)(?:\s+(?:task|one|it|that|item|meeting|appointment|reminder|todo|to do|thing))?\b', message, re.IGNORECASE)
                        if specific_match:
                            task_ref = specific_match.group(1).strip()
                            if task_ref and len(task_ref) > 2:  # At least 3 characters to be meaningful
                                result['task_reference'] = task_ref

                        # Look for patterns to extract the new value after "to"
                        to_pattern = re.search(r'\b(to|into|as|be)\s+["\']([^"\']+)["\']', message, re.IGNORECASE)
                        if to_pattern:
                            result['title'] = to_pattern.group(2).strip()
                        else:
                            # Alternative: look for "to [word+]" pattern
                            to_word_pattern = re.search(r'\bto\s+([^.!,?"\']+?)(?:\s+(?:task|the|it|that|this|now|later|tomorrow|today|tonight|week|day|morning|evening|night|afternoon|etc|etc\.))', message, re.IGNORECASE)
                            if to_word_pattern:
                                result['title'] = to_word_pattern.group(1).strip()
                            else:
                                # Additional pattern: "Change task 1 to 'Call mom tonight'" - extract after 'to'
                                after_to_pattern = re.search(r'to\s+["\']?([^"\'.!?,]+)["\']?', message, re.IGNORECASE)
                                if after_to_pattern:
                                    result['title'] = after_to_pattern.group(1).strip()

                # For TASK_COMPLETION and TASK_DELETION, or if TASK_UPDATE fallback is needed
                if intent != IntentType.TASK_UPDATE or ('task_reference' not in result and 'task_id' not in result):
                    # Look for "the <task_name>" or specific task references
                    specific_match = re.search(r'\b(?:the|a|an)\s+([^.!?,"]+?)(?:\s+(?:task|one|it|that|item|meeting|appointment|reminder|todo|to do|thing))?\b', message, re.IGNORECASE)
                    if specific_match:
                        task_ref = specific_match.group(1).strip()
                        if task_ref and len(task_ref) > 2:  # At least 3 characters to be meaningful
                            result['task_reference'] = task_ref
                    else:
                        # Look for quoted task names
                        quote_match = re.search(r'["\']([^"\']+)["\']', message)
                        if quote_match:
                            result['task_reference'] = quote_match.group(1).strip()
                        else:
                            # Extract any remaining meaningful text as reference
                            # Remove action words and keep the rest
                            message_clean = re.sub(r'\b(done|complete|finish|marked as done|check off|cross off|finished|knocked out|ticked off|closed|wrapped up|accomplished|achieved|fulfilled|carried out|carry out|did|completed|tick|check|delete|remove|cancel|get rid of|erase|trash|throw away|scrub|eliminate|dispose|drop|omit|exclude|discard|get rid|bye bye|take off|off my list|off the list|scratch|cancel|abort|stop|quit|change|update|rename|edit|modify|fix|alter|adjust|revise|refine|correct|improve|switch|swap|replace|transform|convert|make different|redo|rework|rewrite|rephrase|update|refresh|upgrade|change to|turn into|switch to)\b', '', message, re.IGNORECASE)

                            # Remove common articles and references
                            message_clean = re.sub(r'\b(the|a|an|it|that|this|task|one|specific|particular|certain|selected|given|meeting|appointment|event|item|thing|one|first|second|third|last|previous|next)\b', '', message_clean, re.IGNORECASE)

                            # Clean up extra whitespace and punctuation
                            task_ref = re.sub(r'\s+', ' ', message_clean).strip().strip('!.,?;')

                            if task_ref and len(task_ref) > 2:
                                result['task_reference'] = task_ref

        elif intent == IntentType.TASK_LISTING:
            # Extract status filters with enhanced patterns
            message_lower = message.lower()
            if re.search(r'\b(completed|done|finished|completed tasks|done tasks|finished tasks|what.*i.*have.*completed|what.*i.*have.*done|what.*i.*have.*finished|what.*i.*done|what.*i.*completed|what.*i.*finished|what\'?s?.*completed|what\'?s?.*done|what\'?s?.*finished)\b', message_lower):
                result['status_filter'] = 'completed'
            elif re.search(r'\b(pending|incomplete|not done|todo|to do|what.*i.*have.*pending|what.*i.*have.*left|what.*i.*have.*remaining|what.*i.*pending|what.*i.*left|what.*i.*remaining|what\'?s?.*pending|what\'?s?.*left|what\'?s?.*remaining|what\'?s?.*to do|what\'?s?.*todo|what\'?s?.*unfinished)\b', message_lower):
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