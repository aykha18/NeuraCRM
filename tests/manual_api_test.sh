#!/bin/bash
# Manual API Testing Script for Lead Assignment Rules and Task Automation
# Run this script to test the APIs manually

BASE_URL="http://127.0.0.1:8000"
EMAIL="nodeit@node.com"
PASSWORD="NodeIT2024!"

echo "🚀 MANUAL API TESTING SCRIPT"
echo "=============================="

# Step 1: Login and get token
echo "🔐 Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Login Response: $LOGIN_RESPONSE"

# Extract token (you'll need to copy this manually)
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get authentication token"
    exit 1
fi

echo "✅ Login successful!"

# Step 2: Test Lead Assignment Rules
echo ""
echo "🎯 Step 2: Testing Lead Assignment Rules API"
echo "============================================="

# Get existing rules
echo "Getting existing rules..."
curl -s -X GET "$BASE_URL/api/lead-assignment-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# Create a new rule
echo ""
echo "Creating a new rule..."
RULE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/lead-assignment-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Leads Rule",
    "description": "Assign website leads to sales team",
    "conditions": {"source": "website"},
    "assignment_type": "user",
    "assigned_user_id": 1,
    "assignment_priority": 1,
    "is_active": true
  }')

echo "Rule creation response: $RULE_RESPONSE"

# Extract rule ID
RULE_ID=$(echo $RULE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Created rule ID: $RULE_ID"

# Step 3: Test Task Automation
echo ""
echo "🤖 Step 3: Testing Task Automation API"
echo "======================================"

# Get existing templates
echo "Getting existing task templates..."
curl -s -X GET "$BASE_URL/api/task-templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

# Create a new template
echo ""
echo "Creating a new task template..."
TEMPLATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/task-templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "is_active": true
  }')

echo "Template creation response: $TEMPLATE_RESPONSE"

# Extract template ID
TEMPLATE_ID=$(echo $TEMPLATE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Created template ID: $TEMPLATE_ID"

# Create a task
echo ""
echo "Creating a task..."
TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Follow-up Call",
    "description": "Call John Doe about Enterprise Software Deal",
    "task_type": "call",
    "status": "pending",
    "priority": "high",
    "assigned_to_id": 1,
    "lead_id": 1,
    "template_id": '$TEMPLATE_ID'
  }')

echo "Task creation response: $TASK_RESPONSE"

# Extract task ID
TASK_ID=$(echo $TASK_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "Created task ID: $TASK_ID"

# Get all tasks
echo ""
echo "Getting all tasks..."
curl -s -X GET "$BASE_URL/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "🎉 Manual API testing completed!"
echo "Check the responses above to verify everything is working."


