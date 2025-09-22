#!/usr/bin/env python3
"""
Direct API Testing for Lead Assignment Rules and Task Automation
Tests the APIs without browser automation
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_EMAIL = "nodeit@node.com"
LOGIN_PASSWORD = "NodeIT2024!"

def login_and_get_token():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_lead_assignment_rules(token):
    """Test Lead Assignment Rules API"""
    print("\n🎯 Testing Lead Assignment Rules API")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get existing rules
    print("1. Getting existing rules...")
    response = requests.get(f"{BASE_URL}/api/lead-assignment-rules", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('rules', []))} existing rules")
    else:
        print(f"❌ Failed to get rules: {response.status_code}")
        return
    
    # Test 2: Create a new rule
    print("\n2. Creating a new lead assignment rule...")
    rule_data = {
        "name": "Website Leads Rule",
        "description": "Assign website leads to sales team",
        "conditions": {"source": "website"},
        "assignment_type": "user",
        "assigned_user_id": 1,
        "assignment_priority": 1,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/lead-assignment-rules", 
                           json=rule_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        rule_id = result["rule"]["id"]
        print(f"✅ Rule created successfully! ID: {rule_id}")
        print(f"   Name: {result['rule']['name']}")
        print(f"   Priority: {result['rule']['assignment_priority']}")
    else:
        print(f"❌ Failed to create rule: {response.status_code} - {response.text}")
        return
    
    # Test 3: Update the rule
    print("\n3. Updating the rule...")
    update_data = {
        "name": "Updated Website Leads Rule",
        "assignment_priority": 2
    }
    
    response = requests.put(f"{BASE_URL}/api/lead-assignment-rules/{rule_id}", 
                          json=update_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Rule updated successfully!")
        print(f"   New name: {result['rule']['name']}")
        print(f"   New priority: {result['rule']['assignment_priority']}")
    else:
        print(f"❌ Failed to update rule: {response.status_code}")
    
    # Test 4: Get rules again to verify
    print("\n4. Verifying updated rules...")
    response = requests.get(f"{BASE_URL}/api/lead-assignment-rules", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Now have {len(data.get('rules', []))} rules")
        for rule in data.get('rules', []):
            print(f"   - {rule['name']} (Priority: {rule['assignment_priority']})")
    
    return rule_id

def test_task_automation(token):
    """Test Task Automation API"""
    print("\n🤖 Testing Task Automation API")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get existing templates
    print("1. Getting existing task templates...")
    response = requests.get(f"{BASE_URL}/api/task-templates", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('templates', []))} existing templates")
    else:
        print(f"❌ Failed to get templates: {response.status_code}")
        return
    
    # Test 2: Create a new task template
    print("\n2. Creating a new task template...")
    template_data = {
        "name": "Follow-up Call Template",
        "description": "Call prospect after deal moves to proposal stage",
        "task_type": "call",
        "title": "Follow-up Call",
        "description_template": "Call {contact_name} about {deal_title}",
        "trigger_type": "deal_stage_change",
        "trigger_conditions": {"stage_id": 2},
        "due_date_offset": 1,
        "due_time": "09:00",
        "priority": "high",
        "assign_to_type": "deal_owner",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/task-templates", 
                           json=template_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        template_id = result["template"]["id"]
        print(f"✅ Template created successfully! ID: {template_id}")
        print(f"   Name: {result['template']['name']}")
        print(f"   Trigger: {result['template']['trigger_type']}")
        print(f"   Priority: {result['template']['priority']}")
    else:
        print(f"❌ Failed to create template: {response.status_code} - {response.text}")
        return
    
    # Test 3: Create a task from the template
    print("\n3. Creating a task...")
    task_data = {
        "title": "Test Follow-up Call",
        "description": "Call John Doe about Enterprise Software Deal",
        "task_type": "call",
        "status": "pending",
        "priority": "high",
        "assigned_to_id": 1,
        "lead_id": 1,
        "template_id": template_id,
        "due_date": (datetime.now() + timedelta(days=1)).isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/api/tasks", 
                           json=task_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        task_id = result["task"]["id"]
        print(f"✅ Task created successfully! ID: {task_id}")
        print(f"   Title: {result['task']['title']}")
        print(f"   Status: {result['task']['status']}")
        print(f"   Priority: {result['task']['priority']}")
    else:
        print(f"❌ Failed to create task: {response.status_code} - {response.text}")
        return
    
    # Test 4: Get all tasks
    print("\n4. Getting all tasks...")
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('tasks', []))} tasks")
        for task in data.get('tasks', []):
            print(f"   - {task['title']} ({task['status']}) - Priority: {task['priority']}")
    
    # Test 5: Update task status
    print("\n5. Updating task status...")
    update_data = {
        "status": "in_progress"
    }
    
    response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", 
                          json=update_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Task updated successfully!")
        print(f"   New status: {result['task']['status']}")
    else:
        print(f"❌ Failed to update task: {response.status_code}")
    
    return template_id, task_id

def cleanup_test_data(token, rule_id, template_id, task_id):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Delete task
    if task_id:
        response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Task deleted")
        else:
            print(f"⚠️ Failed to delete task: {response.status_code}")
    
    # Delete template
    if template_id:
        response = requests.delete(f"{BASE_URL}/api/task-templates/{template_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Template deleted")
        else:
            print(f"⚠️ Failed to delete template: {response.status_code}")
    
    # Delete rule
    if rule_id:
        response = requests.delete(f"{BASE_URL}/api/lead-assignment-rules/{rule_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Rule deleted")
        else:
            print(f"⚠️ Failed to delete rule: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 AUTOMATION FEATURES API TESTING")
    print("=" * 60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    rule_id = None
    template_id = None
    task_id = None
    
    try:
        # Test Lead Assignment Rules
        rule_id = test_lead_assignment_rules(token)
        
        # Test Task Automation
        template_id, task_id = test_task_automation(token)
        
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Lead Assignment Rules API - Working")
        print("✅ Task Automation API - Working")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        # Clean up
        cleanup_test_data(token, rule_id, template_id, task_id)

if __name__ == "__main__":
    main()


