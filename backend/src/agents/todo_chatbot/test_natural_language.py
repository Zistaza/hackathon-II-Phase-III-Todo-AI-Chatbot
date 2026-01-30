#!/usr/bin/env python3
"""
Test script to verify natural language commands are working properly
"""

import asyncio
import sys
import os

# Add the parent directory to the path so relative imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from agents.todo_chatbot.agent import Agent, AgentConfig
from agents.todo_chatbot.intent_classifier import IntentType

async def test_natural_language_commands():
    """Test the natural language command processing"""

    print("Testing Natural Language Commands for Todo AI Chatbot...")
    print("=" * 60)

    # Initialize the agent
    config = AgentConfig()
    agent = Agent(config)

    # Define test cases based on the requirements
    test_cases = [
        {
            "input": "Add a task to buy groceries",
            "expected_intent": IntentType.TASK_CREATION,
            "description": "Add a task to buy groceries"
        },
        {
            "input": "Show me all my tasks",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show all tasks"
        },
        {
            "input": "What's pending?",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show pending tasks"
        },
        {
            "input": "Mark task 3 as complete",
            "expected_intent": IntentType.TASK_COMPLETION,
            "description": "Complete task 3"
        },
        {
            "input": "Delete the meeting task",
            "expected_intent": IntentType.TASK_DELETION,
            "description": "Delete meeting task"
        },
        {
            "input": "Change task 1 to 'Call mom tonight'",
            "expected_intent": IntentType.TASK_UPDATE,
            "description": "Update task 1 title"
        },
        {
            "input": "I need to remember to pay bills",
            "expected_intent": IntentType.TASK_CREATION,
            "description": "Add task to pay bills"
        },
        {
            "input": "What have I completed?",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show completed tasks"
        }
    ]

    print("Running intent classification tests...\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Input: \"{test_case['input']}\"")

        # Classify intent
        intent, confidence = agent.intent_classifier.classify_intent(test_case['input'])
        extracted_params = agent.intent_classifier.extract_task_details(test_case['input'], intent)

        print(f"Detected Intent: {intent.value}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Extracted Params: {extracted_params}")

        # Check if intent matches expectation
        if intent == test_case['expected_intent']:
            print("✅ PASS: Correct intent detected")
        else:
            print(f"❌ FAIL: Expected {test_case['expected_intent'].value}, got {intent.value}")

        # Additional checks based on intent type
        if intent == IntentType.TASK_CREATION:
            if 'title' in extracted_params:
                print(f"   Task title: '{extracted_params['title']}'")
            else:
                print("   ❌ No title extracted for task creation")

        elif intent == IntentType.TASK_COMPLETION:
            if 'task_id' in extracted_params:
                print(f"   Task ID: {extracted_params['task_id']}")
            elif 'task_reference' in extracted_params:
                print(f"   Task reference: '{extracted_params['task_reference']}'")

        elif intent == IntentType.TASK_LISTING:
            if 'status_filter' in extracted_params:
                print(f"   Status filter: {extracted_params['status_filter']}")

        print("-" * 40)

    print("\nTesting additional variations...\n")

    # Additional variations to test robustness
    additional_tests = [
        "Create a new task called 'Walk the dog'",
        "List all my tasks please",
        "Complete task #5",
        "Remove the shopping task",
        "Update the workout task to 'Evening workout'",
        "I want to add a task: clean the house",
        "Show my completed tasks",
        "Mark task number 2 as done"
    ]

    for i, test_input in enumerate(additional_tests, 1):
        print(f"Additional Test {i}: \"{test_input}\"")
        intent, confidence = agent.intent_classifier.classify_intent(test_input)
        extracted_params = agent.intent_classifier.extract_task_details(test_input, intent)

        print(f"  Intent: {intent.value}, Confidence: {confidence:.2f}")
        if extracted_params:
            print(f"  Params: {extracted_params}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_natural_language_commands())