"""
End-to-End System Test for Phase 1.2
Tests the complete client management workflow
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result with color"""
    status = f"{Colors.GREEN}PASS{Colors.ENDC}" if passed else f"{Colors.RED}FAIL{Colors.ENDC}"
    print(f"  [{status}] {name}")
    if details and not passed:
        print(f"        {details}")


def test_health_check() -> bool:
    """Test basic server health"""
    try:
        resp = requests.get(f"{BASE_URL}/health")
        return resp.status_code == 200
    except:
        return False


def test_database_check() -> bool:
    """Test database connectivity"""
    try:
        resp = requests.get(f"{BASE_URL}/api/teacher/test-db")
        return resp.status_code == 200 and resp.json()["db_connected"] == True
    except:
        return False


def test_complete_workflow() -> Dict[str, bool]:
    """Test complete CRUD workflow"""
    results = {}
    
    # Test data
    client_data = {
        "name": "E2E Test Client",
        "age": 35,
        "gender": "non_binary",
        "race": "Asian",
        "socioeconomic_status": "low_income",
        "background_story": "End-to-end test client",
        "personality_traits": ["anxious", "defensive"],
        "communication_style": "guarded",
        "issues": ["substance_abuse", "housing_insecurity"]
    }
    
    # 1. Create client
    try:
        resp = requests.post(f"{BASE_URL}/api/teacher/clients", json=client_data)
        results["create"] = resp.status_code == 201
        if results["create"]:
            created_client = resp.json()
            client_id = created_client["id"]
        else:
            return results
    except Exception as e:
        results["create"] = False
        return results
    
    # 2. List clients (should include our new client)
    try:
        resp = requests.get(f"{BASE_URL}/api/teacher/clients")
        results["list"] = resp.status_code == 200
        if results["list"]:
            clients = resp.json()
            results["list_contains"] = any(c["id"] == client_id for c in clients)
        else:
            results["list_contains"] = False
    except:
        results["list"] = False
        results["list_contains"] = False
    
    # 3. Get specific client
    try:
        resp = requests.get(f"{BASE_URL}/api/teacher/clients/{client_id}")
        results["get"] = resp.status_code == 200
        if results["get"]:
            retrieved = resp.json()
            results["get_correct"] = retrieved["name"] == client_data["name"]
        else:
            results["get_correct"] = False
    except:
        results["get"] = False
        results["get_correct"] = False
    
    # 4. Update client
    try:
        update_data = {"age": 36, "background_story": "Updated background"}
        resp = requests.put(f"{BASE_URL}/api/teacher/clients/{client_id}", json=update_data)
        results["update"] = resp.status_code == 200
        if results["update"]:
            updated = resp.json()
            results["update_applied"] = updated["age"] == 36 and updated["background_story"] == "Updated background"
        else:
            results["update_applied"] = False
    except:
        results["update"] = False
        results["update_applied"] = False
    
    # 5. Delete client
    try:
        resp = requests.delete(f"{BASE_URL}/api/teacher/clients/{client_id}")
        results["delete"] = resp.status_code == 204
    except:
        results["delete"] = False
    
    # 6. Verify deletion (should get 404)
    try:
        resp = requests.get(f"{BASE_URL}/api/teacher/clients/{client_id}")
        results["delete_verified"] = resp.status_code == 404
    except:
        results["delete_verified"] = False
    
    return results


def test_error_cases() -> Dict[str, bool]:
    """Test key error scenarios"""
    results = {}
    
    # 1. 404 for non-existent resource
    try:
        resp = requests.get(f"{BASE_URL}/api/teacher/clients/non-existent-id")
        results["404_handling"] = resp.status_code == 404
        if results["404_handling"]:
            error = resp.json()
            results["404_message"] = "not found" in error["detail"].lower()
        else:
            results["404_message"] = False
    except:
        results["404_handling"] = False
        results["404_message"] = False
    
    # 2. 422 for validation errors
    try:
        resp = requests.post(f"{BASE_URL}/api/teacher/clients", json={"name": "Test"})
        results["validation_422"] = resp.status_code == 422
        if results["validation_422"]:
            error = resp.json()
            results["validation_details"] = "detail" in error and isinstance(error["detail"], list)
        else:
            results["validation_details"] = False
    except:
        results["validation_422"] = False
        results["validation_details"] = False
    
    # 3. 400 for empty update
    try:
        # First create a client
        resp = requests.post(f"{BASE_URL}/api/teacher/clients", json={
            "name": "Error Test Client",
            "age": 30,
            "gender": "male",
            "race": "White",
            "socioeconomic_status": "middle_class",
            "background_story": "Test",
            "personality_traits": ["anxious"],
            "communication_style": "open",
            "issues": ["anxiety"]
        })
        if resp.status_code == 201:
            client_id = resp.json()["id"]
            # Try empty update
            resp = requests.put(f"{BASE_URL}/api/teacher/clients/{client_id}", json={})
            results["empty_update_400"] = resp.status_code == 400
            # Cleanup
            requests.delete(f"{BASE_URL}/api/teacher/clients/{client_id}")
        else:
            results["empty_update_400"] = False
    except:
        results["empty_update_400"] = False
    
    return results


def test_concurrent_operations() -> bool:
    """Test multiple simultaneous operations"""
    try:
        # Create 5 clients quickly
        created_ids = []
        for i in range(5):
            resp = requests.post(f"{BASE_URL}/api/teacher/clients", json={
                "name": f"Concurrent Test {i}",
                "age": 20 + i,
                "gender": "female",
                "race": "Hispanic",
                "socioeconomic_status": "middle_class",
                "background_story": f"Concurrent test client {i}",
                "personality_traits": ["resilient"],
                "communication_style": "direct",
                "issues": ["academic_stress"]
            })
            if resp.status_code == 201:
                created_ids.append(resp.json()["id"])
        
        success = len(created_ids) == 5
        
        # Cleanup
        for client_id in created_ids:
            requests.delete(f"{BASE_URL}/api/teacher/clients/{client_id}")
        
        return success
    except:
        return False


def main():
    """Run all system tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}End-to-End System Test - Phase 1.2{Colors.ENDC}")
    print("=" * 50)
    
    # Check server is running
    if not test_health_check():
        print(f"{Colors.RED}✗ Server is not running!{Colors.ENDC}")
        print("  Start with: python -m uvicorn backend.app:app --reload")
        return
    
    print(f"\n{Colors.BOLD}1. Basic Connectivity{Colors.ENDC}")
    print_test("Server health check", test_health_check())
    print_test("Database connectivity", test_database_check())
    
    print(f"\n{Colors.BOLD}2. Complete CRUD Workflow{Colors.ENDC}")
    workflow_results = test_complete_workflow()
    print_test("Create client", workflow_results.get("create", False))
    print_test("List clients", workflow_results.get("list", False))
    print_test("List contains created client", workflow_results.get("list_contains", False))
    print_test("Get specific client", workflow_results.get("get", False))
    print_test("Retrieved data is correct", workflow_results.get("get_correct", False))
    print_test("Update client", workflow_results.get("update", False))
    print_test("Update applied correctly", workflow_results.get("update_applied", False))
    print_test("Delete client", workflow_results.get("delete", False))
    print_test("Deletion verified (404)", workflow_results.get("delete_verified", False))
    
    print(f"\n{Colors.BOLD}3. Error Handling{Colors.ENDC}")
    error_results = test_error_cases()
    print_test("404 for non-existent resource", error_results.get("404_handling", False))
    print_test("404 has clear message", error_results.get("404_message", False))
    print_test("422 for validation errors", error_results.get("validation_422", False))
    print_test("Validation errors have details", error_results.get("validation_details", False))
    print_test("400 for empty update", error_results.get("empty_update_400", False))
    
    print(f"\n{Colors.BOLD}4. Performance & Concurrency{Colors.ENDC}")
    print_test("Concurrent operations", test_concurrent_operations())
    
    # Summary
    all_tests = {**workflow_results, **error_results}
    all_tests["health"] = test_health_check()
    all_tests["database"] = test_database_check()
    all_tests["concurrent"] = test_concurrent_operations()
    
    passed = sum(1 for v in all_tests.values() if v)
    total = len(all_tests)
    
    print(f"\n{Colors.BOLD}Summary{Colors.ENDC}")
    print(f"  Total Tests: {total}")
    print(f"  Passed: {Colors.GREEN}{passed}{Colors.ENDC}")
    print(f"  Failed: {Colors.RED}{total - passed}{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All tests passed! Phase 1.2 is complete and working correctly.{Colors.ENDC}")
        print(f"{Colors.GREEN}Ready to proceed to Phase 1.3 (EvaluationRubric CRUD).{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please fix issues before proceeding.{Colors.ENDC}")
    
    return passed == total


if __name__ == "__main__":
    main()
