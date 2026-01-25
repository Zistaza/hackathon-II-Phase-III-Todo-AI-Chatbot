#!/usr/bin/env python3
"""
Basic validation script to test the MCP tools implementation.
This script tests the basic functionality of the implemented MCP tools.
"""

import asyncio
import sys
import os

# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from api.mcp_tools.add_task import add_task
        from api.mcp_tools.list_tasks import list_tasks
        from api.mcp_tools.complete_task import complete_task
        from api.mcp_tools.delete_task import delete_task
        from api.mcp_tools.update_task import update_task
        from api.chat_endpoint import chat_endpoint, process_mcp_tool_call
        from services.task_service import TaskService
        from utils.jwt_validator import JWTValidator
        from utils.multi_tenant_checker import MultiTenantChecker

        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_mcp_tool_functions_exist():
    """Test that all MCP tool functions exist and are callable."""
    print("\nTesting MCP tool functions...")

    from api.mcp_tools.add_task import add_task
    from api.mcp_tools.list_tasks import list_tasks
    from api.mcp_tools.complete_task import complete_task
    from api.mcp_tools.delete_task import delete_task
    from api.mcp_tools.update_task import update_task

    functions = [
        ("add_task", add_task),
        ("list_tasks", list_tasks),
        ("complete_task", complete_task),
        ("delete_task", delete_task),
        ("update_task", update_task)
    ]

    all_callable = True
    for name, func in functions:
        if callable(func):
            print(f"✓ {name} is callable")
        else:
            print(f"✗ {name} is not callable")
            all_callable = False

    return all_callable

def test_service_classes_exist():
    """Test that service classes exist."""
    print("\nTesting service classes...")

    from services.task_service import TaskService

    try:
        service = TaskService()
        print("✓ TaskService can be instantiated")

        # Check if required methods exist
        required_methods = [
            'create_task', 'get_tasks_by_user_id', 'get_task_by_id',
            'update_task_completion', 'update_task', 'delete_task'
        ]

        all_methods_exist = True
        for method_name in required_methods:
            if hasattr(service, method_name) and callable(getattr(service, method_name)):
                print(f"✓ TaskService.{method_name} exists")
            else:
                print(f"✗ TaskService.{method_name} missing")
                all_methods_exist = False

        return all_methods_exist
    except Exception as e:
        print(f"✗ TaskService instantiation error: {e}")
        return False

def test_utility_classes_exist():
    """Test that utility classes exist."""
    print("\nTesting utility classes...")

    from utils.jwt_validator import JWTValidator
    from utils.multi_tenant_checker import MultiTenantChecker

    # Check JWTValidator
    if hasattr(JWTValidator, 'validate_token'):
        print("✓ JWTValidator.validate_token exists")
    else:
        print("✗ JWTValidator.validate_token missing")
        return False

    # Check MultiTenantChecker
    if hasattr(MultiTenantChecker, 'verify_user_access'):
        print("✓ MultiTenantChecker.verify_user_access exists")
    else:
        print("✗ MultiTenantChecker.verify_user_access missing")
        return False

    return True

async def run_tests():
    """Run all validation tests."""
    print("Starting MCP Tools Implementation Validation\n")

    all_tests_passed = True

    # Run each test
    all_tests_passed &= test_imports()
    all_tests_passed &= test_mcp_tool_functions_exist()
    all_tests_passed &= test_service_classes_exist()
    all_tests_passed &= test_utility_classes_exist()

    print(f"\n{'='*50}")
    if all_tests_passed:
        print("✓ All validation tests passed!")
        print("MCP Tools implementation is structurally sound.")
    else:
        print("✗ Some validation tests failed!")
        print("Please check the implementation.")
    print(f"{'='*50}")

    return all_tests_passed

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)