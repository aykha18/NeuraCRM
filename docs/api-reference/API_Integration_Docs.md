# API & Integration Documentation

## 1. API Overview

### 1.1 Base URL
```
Production: https://neuracrm.up.railway.app
Staging: https://neuracrm-staging.up.railway.app
Development: http://localhost:8000
```

### 1.2 Authentication
All API requests require authentication using JWT Bearer tokens.

#### Authentication Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant DB as Database

    C->>A: POST /api/auth/login
    A->>DB: Validate credentials
    DB-->>A: User data
    A-->>C: JWT access token

    C->>A: GET /api/resource (Authorization: Bearer <token>)
    A->>A: Validate JWT
    A->>DB: Fetch resource
    DB-->>A: Resource data
    A-->>C: Protected resource
```

#### Headers Required
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
X-Organization-ID: 123  # For multi-tenant requests
```

### 1.3 Response Format
All responses follow a consistent JSON structure:

#### Success Response
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Example Resource",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  },
  "message": "Operation completed successfully"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

## 2. Authentication Endpoints

### 2.1 Login
Authenticate user and receive JWT token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@company.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 123,
      "name": "John Doe",
      "email": "user@company.com",
      "role": "admin",
      "organization_id": 456,
      "avatar_url": null
    }
  }
}
```

**cURL Example:**
```bash
curl -X POST https://neuracrm.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@company.com","password":"securepassword"}'
```

### 2.2 Get Current User
Get authenticated user information.

**Endpoint:** `GET /api/auth/me`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "user@company.com",
    "role": "admin",
    "organization_id": 456,
    "avatar_url": null
  }
}
```

### 2.3 Logout
Invalidate current session (client-side token removal).

**Endpoint:** `POST /api/auth/logout`

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

## 3. CRM Core Endpoints

### 3.1 Leads Management

#### Get Leads
**Endpoint:** `GET /api/leads`

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `status` (string): Filter by status
- `owner_id` (integer): Filter by owner
- `score_min` (integer): Minimum lead score
- `score_max` (integer): Maximum lead score

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "Enterprise Software Solution",
      "contact_id": 456,
      "owner_id": 789,
      "organization_id": 101,
      "status": "qualified",
      "source": "website",
      "score": 85,
      "score_factors": "{\"industry\": 20, \"company_size\": 15, \"engagement\": 25, \"decision_maker\": 15, \"urgency\": 10}",
      "score_confidence": 0.92,
      "created_at": "2024-01-01T00:00:00Z",
      "contact": {
        "id": 456,
        "name": "Jane Smith",
        "email": "jane@company.com",
        "company": "Tech Corp"
      }
    }
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

#### Create Lead
**Endpoint:** `POST /api/leads`

**Request Body:**
```json
{
  "title": "New Enterprise Opportunity",
  "contact_id": 456,
  "status": "new",
  "source": "referral",
  "notes": "High-priority enterprise lead"
}
```

#### Update Lead
**Endpoint:** `PUT /api/leads/{id}`

#### Delete Lead
**Endpoint:** `DELETE /api/leads/{id}`

#### Score Lead
**Endpoint:** `POST /api/leads/{id}/score`

**Response:**
```json
{
  "success": true,
  "data": {
    "lead_id": 123,
    "score": 85,
    "factors": {
      "industry": 20,
      "company_size": 15,
      "engagement": 25,
      "decision_maker": 15,
      "urgency": 10
    },
    "confidence": 0.92,
    "recommendations": [
      "Schedule discovery call within 24 hours",
      "Prepare technical demo",
      "Involve solution architect"
    ]
  }
}
```

### 3.2 Deals Management

#### Get Kanban Board
**Endpoint:** `GET /api/kanban/board`

**Response:**
```json
{
  "success": true,
  "data": {
    "stages": [
      {
        "id": 1,
        "name": "Prospecting",
        "order": 1,
        "wip_limit": 10,
        "deals": [
          {
            "id": 123,
            "title": "Enterprise Deal",
            "value": 50000.00,
            "owner_id": 456,
            "contact_id": 789,
            "stage_id": 1,
            "status": "open",
            "created_at": "2024-01-01T00:00:00Z"
          }
        ]
      }
    ]
  }
}
```

#### Move Deal
**Endpoint:** `PUT /api/kanban/deals/{deal_id}/move`

**Request Body:**
```json
{
  "stage_id": 2,
  "position": 1
}
```

#### Watch Deal
**Endpoint:** `POST /api/deals/{id}/watchers`

**Request Body:**
```json
{
  "user_id": 456
}
```

### 3.3 Contacts Management

#### Get Contacts
**Endpoint:** `GET /api/contacts`

#### Create Contact
**Endpoint:** `POST /api/contacts`

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "john@company.com",
  "phone": "+1-555-0123",
  "company": "Tech Solutions Inc",
  "title": "CTO"
}
```

#### Get Contact Activities
**Endpoint:** `GET /api/contacts/{id}/activities`

## 4. AI & Analytics Endpoints

### 4.1 AI Sales Assistant

#### Get AI Insights
**Endpoint:** `POST /api/ai/assistant`

**Request Body:**
```json
{
  "context": "lead_qualification",
  "lead_id": 123,
  "question": "What's the best approach for this lead?"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Based on the lead's profile as CTO of a 200-person tech company, I recommend focusing on ROI and technical integration. Schedule a discovery call within 24 hours and prepare a customized technical demo.",
    "confidence": 0.89,
    "suggestions": [
      "Emphasize 40% productivity increase",
      "Highlight enterprise security features",
      "Prepare integration roadmap"
    ],
    "next_steps": [
      "Send personalized email introduction",
      "Schedule technical discovery call",
      "Prepare ROI calculator demo"
    ]
  }
}
```

#### Chat with AI Assistant
**Endpoint:** `POST /api/ai/chat`

**Request Body:**
```json
{
  "message": "How should I handle this objection about pricing?",
  "context": {
    "deal_id": 123,
    "lead_score": 85,
    "industry": "technology"
  }
}
```

### 4.2 Lead Scoring

#### Score All Leads
**Endpoint:** `POST /api/ai/score-all-leads`

**Response:**
```json
{
  "success": true,
  "data": {
    "processed": 150,
    "successful": 148,
    "failed": 2,
    "average_score": 72.5,
    "high_priority_count": 23
  }
}
```

### 4.3 Sentiment Analysis

#### Analyze Text
**Endpoint:** `POST /api/sentiment-analysis/analyze`

**Request Body:**
```json
{
  "text": "I'm very disappointed with the service. The response time is unacceptable.",
  "context": "support_ticket"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "negative",
    "confidence": 0.94,
    "score": -0.78,
    "key_phrases": ["disappointed", "unacceptable", "response time"],
    "urgency": "high",
    "suggested_action": "Escalate to senior support agent"
  }
}
```

### 4.4 Predictive Analytics

#### Get Sales Forecast
**Endpoint:** `GET /api/forecasting-models`

**Query Parameters:**
- `months` (integer): Forecast period (default: 12, max: 24)

**Response:**
```json
{
  "success": true,
  "data": {
    "forecast": [
      {
        "period": "2024-02",
        "predicted_revenue": 125000.00,
        "confidence_lower": 110000.00,
        "confidence_upper": 140000.00,
        "trend": "increasing",
        "seasonality_factor": 1.15
      }
    ],
    "accuracy_metrics": {
      "mae": 8500.00,
      "rmse": 12000.00,
      "mape": 0.08
    },
    "insights": [
      "Strong Q1 seasonality expected",
      "15% growth trajectory maintained",
      "Consider increasing sales capacity"
    ]
  }
}
```

#### Customer Segmentation
**Endpoint:** `GET /api/customer-segments`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "High-Value Enterprise",
      "description": "Companies with >500 employees and >$100K annual contract value",
      "customer_count": 45,
      "total_deal_value": 4500000.00,
      "conversion_rate": 0.85,
      "insights": [
        "Prefer annual contracts",
        "Require custom integrations",
        "High retention rate (95%)"
      ],
      "recommendations": [
        "Assign dedicated account managers",
        "Offer premium support packages",
        "Schedule quarterly business reviews"
      ]
    }
  ]
}
```

## 5. Call Center Endpoints

### 5.1 PBX Provider Management

#### Get Providers
**Endpoint:** `GET /api/telephony/providers`

#### Configure Provider
**Endpoint:** `POST /api/telephony/providers`

**Request Body:**
```json
{
  "name": "Asterisk Server",
  "provider_type": "asterisk",
  "host": "pbx.company.com",
  "port": 5060,
  "username": "neuracrm",
  "password": "encrypted_password",
  "context": "from-internal"
}
```

#### Test Connection
**Endpoint:** `POST /api/telephony/providers/{id}/test`

### 5.2 Call Management

#### Get Calls
**Endpoint:** `GET /api/calls`

**Query Parameters:**
- `status` (string): Filter by status (ringing, answered, completed, failed)
- `direction` (string): Filter by direction (inbound, outbound, internal)
- `agent_id` (integer): Filter by agent
- `start_date` (string): ISO date format
- `end_date` (string): ISO date format

#### Initiate Call
**Endpoint:** `POST /api/calls`

**Request Body:**
```json
{
  "agent_id": "agent_123",
  "to_number": "+1234567890",
  "from_number": "+0987654321",
  "metadata": {
    "lead_id": 456,
    "contact_id": 789,
    "campaign_id": 101
  }
}
```

#### Transfer Call
**Endpoint:** `PUT /api/calls/{call_id}/transfer`

**Request Body:**
```json
{
  "extension": "2001",
  "transfer_type": "blind"  // blind, attended, conference
}
```

### 5.3 Call Analytics

#### Get Call Analytics
**Endpoint:** `GET /api/telephony/analytics`

**Query Parameters:**
- `period_type` (string): daily, weekly, monthly, quarterly
- `start_date` (string): ISO date
- `end_date` (string): ISO date

**Response:**
```json
{
  "success": true,
  "data": {
    "total_calls": 1250,
    "answered_calls": 1100,
    "abandoned_calls": 150,
    "average_wait_time": 45,
    "average_talk_time": 285,
    "service_level": 0.88,
    "agent_utilization": 0.72,
    "queue_performance": {
      "sales_queue": {
        "calls": 450,
        "answered": 420,
        "avg_wait": 32,
        "service_level": 0.93
      }
    }
  }
}
```

## 6. Support System Endpoints

### 6.1 Ticket Management

#### Get Support Tickets
**Endpoint:** `GET /api/support/tickets`

**Query Parameters:**
- `status` (string): open, in_progress, resolved, closed
- `priority` (string): low, medium, high, urgent, critical
- `assigned_to` (integer): Agent ID
- `customer_id` (integer): Customer contact ID

#### Create Ticket
**Endpoint:** `POST /api/support/tickets`

**Request Body:**
```json
{
  "title": "Login Issues",
  "description": "Users unable to access dashboard after recent update",
  "priority": "high",
  "category": "technical",
  "customer_email": "support@customer.com",
  "customer_name": "John Customer"
}
```

#### Add Comment
**Endpoint:** `POST /api/support/tickets/{id}/comments`

**Request Body:**
```json
{
  "content": "I've identified the issue. Working on a fix.",
  "is_internal": false
}
```

### 6.2 Knowledge Base

#### Search Articles
**Endpoint:** `GET /api/knowledge-base/search`

**Query Parameters:**
- `query` (string): Search term
- `category` (string): Filter by category
- `limit` (integer): Max results (default: 20)

#### Create Article
**Endpoint:** `POST /api/knowledge-base/articles`

**Request Body:**
```json
{
  "title": "How to Reset Password",
  "content": "<p>To reset your password...</p>",
  "category": "getting_started",
  "tags": ["password", "login", "security"]
}
```

## 7. Financial Management Endpoints

### 7.1 Invoice Management

#### Get Invoices
**Endpoint:** `GET /api/invoices`

#### Create Invoice
**Endpoint:** `POST /api/invoices`

**Request Body:**
```json
{
  "deal_id": 123,
  "customer_account_id": 456,
  "issue_date": "2024-01-15",
  "due_date": "2024-02-15",
  "subtotal": 10000.00,
  "tax_rate": 0.08,
  "description": "Enterprise Software License",
  "terms_conditions": "Payment due within 30 days"
}
```

#### Process Payment
**Endpoint:** `POST /api/invoices/{id}/payments`

**Request Body:**
```json
{
  "amount": 10000.00,
  "payment_method": "credit_card",
  "payment_reference": "txn_1234567890"
}
```

### 7.2 Financial Reports

#### Profit & Loss Report
**Endpoint:** `GET /api/financial/reports/profit-loss`

**Query Parameters:**
- `start_date` (string): Period start
- `end_date` (string): Period end
- `group_by` (string): month, quarter, year

## 8. Integration Guides

### 8.1 Webhook Integration

#### Setup Webhooks
Configure webhook endpoints for real-time notifications:

```json
{
  "url": "https://your-app.com/webhooks/neuracrm",
  "secret": "your_webhook_secret",
  "events": [
    "deal.created",
    "deal.updated",
    "lead.scored",
    "call.completed",
    "invoice.paid"
  ]
}
```

#### Webhook Payload Example
```json
{
  "event": "deal.updated",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "deal_id": 123,
    "old_stage": "prospecting",
    "new_stage": "qualified",
    "changed_by": 456,
    "organization_id": 789
  },
  "signature": "sha256=abc123..."
}
```

### 8.2 Zapier Integration

#### Available Triggers
- New Lead Created
- Deal Stage Changed
- Invoice Paid
- Support Ticket Created
- Call Completed

#### Available Actions
- Create Contact
- Update Deal
- Send Email
- Create Task
- Generate Invoice

### 8.3 Salesforce Integration

#### Setup OAuth Flow
```javascript
// Redirect to Salesforce OAuth
const authUrl = `https://login.salesforce.com/services/oauth2/authorize?` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `response_type=code&` +
  `scope=api refresh_token`;

window.location.href = authUrl;
```

#### Sync Configuration
```json
{
  "sync_direction": "bidirectional",
  "field_mapping": {
    "neuracrm_lead": "salesforce_lead",
    "neuracrm_deal": "salesforce_opportunity",
    "neuracrm_contact": "salesforce_contact"
  },
  "sync_frequency": "15_minutes",
  "conflict_resolution": "neuracrm_wins"
}
```

### 8.4 Stripe Integration

#### Webhook Events
Handle these Stripe webhook events:
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

#### Payment Processing
```javascript
// Create payment intent
const paymentIntent = await stripe.paymentIntents.create({
  amount: 100000, // $1000.00
  currency: 'usd',
  customer: customerId,
  metadata: {
    invoice_id: 123,
    organization_id: 456
  }
});
```

## 9. Rate Limiting

### Rate Limits by Endpoint Category

| Category | Limit | Window |
|----------|-------|--------|
| Authentication | 10 requests | 1 minute |
| CRM Read Operations | 1000 requests | 1 minute |
| CRM Write Operations | 100 requests | 1 minute |
| AI Operations | 50 requests | 1 minute |
| File Uploads | 20 requests | 1 minute |
| Bulk Operations | 5 requests | 1 minute |

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
X-RateLimit-Retry-After: 60
```

## 10. Error Codes

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `AUTHENTICATION_FAILED` | 401 | Invalid credentials |
| `AUTHORIZATION_FAILED` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

### AI-Specific Errors

| Code | Description |
|------|-------------|
| `AI_SERVICE_UNAVAILABLE` | AI service temporarily down |
| `AI_QUOTA_EXCEEDED` | API quota exceeded |
| `AI_INVALID_CONTEXT` | Invalid context for AI operation |
| `AI_PROCESSING_TIMEOUT` | AI processing took too long |

## 11. SDKs and Libraries

### JavaScript SDK
```javascript
import { NeuraCRM } from '@neuracrm/sdk';

const client = new NeuraCRM({
  apiKey: 'your_api_key',
  baseUrl: 'https://neuracrm.up.railway.app'
});

// Authenticate
await client.auth.login('user@company.com', 'password');

// Get leads
const leads = await client.leads.list({ status: 'qualified' });

// Create deal
const deal = await client.deals.create({
  title: 'New Enterprise Deal',
  value: 50000,
  contact_id: 123
});
```

### Python SDK
```python
from neuracrm import NeuraCRM

client = NeuraCRM(
    api_key='your_api_key',
    base_url='https://neuracrm.up.railway.app'
)

# Authenticate
client.auth.login('user@company.com', 'password')

# Get leads with AI scoring
leads = client.leads.list(status='qualified', include_scores=True)

# Create and score lead
lead = client.leads.create({
    'title': 'New Opportunity',
    'contact_id': 123
})
score = client.ai.score_lead(lead['id'])
```

This comprehensive API documentation provides everything needed to integrate with and extend NeuraCRM's capabilities, supporting both direct API usage and third-party integrations.