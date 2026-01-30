#!/usr/bin/env python3
"""
Comprehensive test of the natural language commands for Todo AI Chatbot
"""

import asyncio
import sys
import os

# Add the parent directory to the path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

# Import modules directly using their file paths
import importlib.util
agent_spec = importlib.util.spec_from_file_location("agent", os.path.join(current_dir, "agent.py"))
agent_module = importlib.util.module_from_spec(agent_spec)
agent_spec.loader.exec_module(agent_module)

intent_classifier_spec = importlib.util.spec_from_file_location("intent_classifier", os.path.join(current_dir, "intent_classifier.py"))
intent_classifier_module = importlib.util.module_from_spec(intent_classifier_spec)
intent_classifier_spec.loader.exec_module(intent_classifier_module)

Agent = agent_module.Agent
AgentConfig = agent_module.AgentConfig
IntentType = intent_classifier_module.IntentType

async def test_natural_language_commands():
    """Test the natural language command processing"""

    print("Testing Natural Language Commands for Todo AI Chatbot...")
    print("=" * 70)

    # Initialize the agent
    config = AgentConfig()
    agent = Agent(config)

    # Define test cases based on the requirements
    test_cases = [
        {
            "input": "Add a task to buy groceries",
            "expected_intent": IntentType.TASK_CREATION,
            "description": "Add a task to buy groceries",
            "should_have_title": True
        },
        {
            "input": "Show me all my tasks",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show all tasks",
            "should_be_all_status": True
        },
        {
            "input": "What's pending?",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show pending tasks",
            "should_be_pending_status": True
        },
        {
            "input": "Mark task 3 as complete",
            "expected_intent": IntentType.TASK_COMPLETION,
            "description": "Complete task 3",
            "should_have_task_id": True
        },
        {
            "input": "Delete the meeting task",
            "expected_intent": IntentType.TASK_DELETION,
            "description": "Delete meeting task",
            "should_have_task_reference": True
        },
        {
            "input": "Change task 1 to 'Call mom tonight'",
            "expected_intent": IntentType.TASK_UPDATE,
            "description": "Update task 1 title",
            "should_have_task_id": True,
            "should_have_new_title": True
        },
        {
            "input": "I need to remember to pay bills",
            "expected_intent": IntentType.TASK_CREATION,
            "description": "Add task to pay bills",
            "should_have_title": True
        },
        {
            "input": "What have I completed?",
            "expected_intent": IntentType.TASK_LISTING,
            "description": "Show completed tasks",
            "should_be_completed_status": True
        }
    ]

    print("Running intent classification tests...\n")

    all_passed = True

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
            all_passed = False

        # Additional checks based on intent type and test expectations
        if test_case.get('should_have_title') and intent == IntentType.TASK_CREATION:
            if 'title' in extracted_params and extracted_params['title'].strip():
                print(f"   ✅ Task title extracted: '{extracted_params['title']}'")
            else:
                print("   ❌ FAIL: No title extracted for task creation")
                all_passed = False

        elif test_case.get('should_have_task_id') and intent in [IntentType.TASK_COMPLETION, IntentType.TASK_DELETION, IntentType.TASK_UPDATE]:
            if 'task_id' in extracted_params:
                print(f"   ✅ Task ID extracted: {extracted_params['task_id']}")
            else:
                print("   ❌ FAIL: No task ID extracted")
                all_passed = False

        elif test_case.get('should_have_task_reference') and intent in [IntentType.TASK_DELETION]:
            if 'task_reference' in extracted_params:
                print(f"   ✅ Task reference extracted: '{extracted_params['task_reference']}'")
            else:
                print("   ❌ FAIL: No task reference extracted")
                all_passed = False

        elif test_case.get('should_have_new_title') and intent == IntentType.TASK_UPDATE:
            if 'title' in extracted_params and extracted_params['title'].strip():
                print(f"   ✅ New title extracted: '{extracted_params['title']}'")
            else:
                print("   ❌ FAIL: No new title extracted for update")
                all_passed = False

        elif test_case.get('should_be_all_status') and intent == IntentType.TASK_LISTING:
            if extracted_params.get('status_filter') == 'all':
                print(f"   ✅ Status filter correctly set to: {extracted_params['status_filter']}")
            else:
                print(f"   ❌ FAIL: Expected status filter 'all', got '{extracted_params.get('status_filter')}'")
                all_passed = False

        elif test_case.get('should_be_pending_status') and intent == IntentType.TASK_LISTING:
            if extracted_params.get('status_filter') == 'pending':
                print(f"   ✅ Status filter correctly set to: {extracted_params['status_filter']}")
            else:
                print(f"   ❌ FAIL: Expected status filter 'pending', got '{extracted_params.get('status_filter')}'")
                all_passed = False

        elif test_case.get('should_be_completed_status') and intent == IntentType.TASK_LISTING:
            if extracted_params.get('status_filter') == 'completed':
                print(f"   ✅ Status filter correctly set to: {extracted_params['status_filter']}")
            else:
                print(f"   ❌ FAIL: Expected status filter 'completed', got '{extracted_params.get('status_filter')}'")
                all_passed = False

        print("-" * 50)

    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
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

    return all_passed

if __name__ == "__main__":
    result = asyncio.run(test_natural_language_commands())
    print(f"\nFinal Result: {'✅ SUCCESS' if result else '❌ FAILURE'}")