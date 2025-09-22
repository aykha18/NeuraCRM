#!/usr/bin/env python3
"""
Quick Test Script - Test the automation features in one go
"""

import requests
import json

# Quick test function
def quick_test():
    print("🚀 QUICK AUTOMATION FEATURES TEST")
    print("=" * 40)
    
    # Login
    login_data = {"email": "nodeit@node.com", "password": "NodeIT2024!"}
    response = requests.post("http://127.0.0.1:8000/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Test Lead Assignment Rules
    print("\n🎯 Testing Lead Assignment Rules...")
    
    # Create rule
    rule_data = {
        "name": "Quick Test Rule",
        "description": "Test rule for quick testing",
        "conditions": {"source": "website"},
        "assignment_type": "user",
        "assigned_user_id": 1,
        "assignment_priority": 1,
        "is_active": True
    }
    
    response = requests.post("http://127.0.0.1:8000/api/lead-assignment-rules", 
                           json=rule_data, headers=headers)
    
    if response.status_code == 200:
        rule_id = response.json()["rule"]["id"]
        print(f"✅ Rule created (ID: {rule_id})")
    else:
        print(f"❌ Rule creation failed: {response.status_code}")
        return
    
    # Test Task Templates
    print("\n🤖 Testing Task Templates...")
    
    template_data = {
        "name": "Quick Test Template",
        "description": "Test template for quick testing",
        "task_type": "call",
        "title": "Test Call",
        "trigger_type": "deal_stage_change",
        "trigger_conditions": {"stage_id": 2},
        "due_date_offset": 1,
        "priority": "high",
        "assign_to_type": "deal_owner",
        "is_active": True
    }
    
    response = requests.post("http://127.0.0.1:8000/api/task-templates", 
                           json=template_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Template response: {result}")
        template_id = result["template"]["id"]
        print(f"✅ Template created (ID: {template_id})")
    else:
        print(f"❌ Template creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Test Task Creation
    print("\n📋 Testing Task Creation...")
    
    task_data = {
        "title": "Quick Test Task",
        "description": "Test task for quick testing",
        "task_type": "call",
        "status": "pending",
        "priority": "high",
        "assigned_to_id": 1,
        "template_id": template_id
    }
    
    response = requests.post("http://127.0.0.1:8000/api/tasks", 
                           json=task_data, headers=headers)
    
    if response.status_code == 200:
        task_id = response.json()["task"]["id"]
        print(f"✅ Task created (ID: {task_id})")
    else:
        print(f"❌ Task creation failed: {response.status_code}")
        return
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    requests.delete(f"http://127.0.0.1:8000/api/tasks/{task_id}", headers=headers)
    requests.delete(f"http://127.0.0.1:8000/api/task-templates/{template_id}", headers=headers)
    requests.delete(f"http://127.0.0.1:8000/api/lead-assignment-rules/{rule_id}", headers=headers)
    print("✅ Cleanup completed")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Lead Assignment Rules - Working")
    print("✅ Task Templates - Working") 
    print("✅ Task Creation - Working")

if __name__ == "__main__":
    quick_test()
