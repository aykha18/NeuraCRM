# Testing & Validation Plans

## 1. Testing Strategy Overview

### 1.1 Testing Pyramid
```
┌─────────────────────────────────────────────────────────────┐
│                    E2E Tests (Slow, High Value)             │
│                    ~10% of total tests                      │
├─────────────────────────────────────────────────────────────┤
│                 Integration Tests (Medium)                 │
│                    ~20% of total tests                      │
├─────────────────────────────────────────────────────────────┤
│                 Unit Tests (Fast, High Coverage)           │
│                    ~70% of total tests                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Testing Objectives
- **Reliability**: Ensure system stability under various conditions
- **Performance**: Validate response times and resource usage
- **Security**: Confirm protection against common vulnerabilities
- **Compliance**: Verify adherence to data protection regulations
- **User Experience**: Validate functionality meets user needs

### 1.3 Test Environments

| Environment | Purpose | Data Type | Access |
|-------------|---------|-----------|---------|
| **Local Development** | Unit testing, debugging | Mock/synthetic | Developers |
| **CI/CD Pipeline** | Automated testing | Mock/synthetic | Automated |
| **Staging** | Integration testing | Production-like | QA Team |
| **Production** | Monitoring, canary testing | Real user data | Read-only monitoring |

## 2. Unit Testing Strategy

### 2.1 Backend Unit Tests

#### Test Framework Setup
```python
# pytest configuration (pytest.ini)
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    ai: AI-related tests
```

#### Service Layer Testing
```python
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from api.services.lead_scoring import LeadScoringService
from api.models import Lead, Contact

class TestLeadScoringService:
    @pytest.fixture
    def db_session(self):
        """Create mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def scoring_service(self):
        """Create lead scoring service instance"""
        return LeadScoringService()

    @pytest.mark.unit
    def test_calculate_lead_score_perfect_fit(self, scoring_service, db_session):
        """Test scoring for a perfect lead"""
        # Arrange
        contact = Contact(
            company="Tech Giant Inc",
            industry="Technology"
        )

        lead = Lead(
            title="Enterprise Software Solution",
            contact=contact
        )

        # Mock database interactions
        db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = scoring_service.calculate_lead_score(lead, db_session)

        # Assert
        assert result['total_score'] >= 80
        assert result['confidence'] >= 0.8
        assert result['category'] == 'hot'

    @pytest.mark.unit
    def test_industry_scoring_technology(self, scoring_service):
        """Test industry scoring for technology sector"""
        contact = Contact(industry="Technology")

        score = scoring_service._score_industry(contact)

        assert score == 20  # Technology gets highest score

    @pytest.mark.unit
    @patch('api.services.lead_scoring.openai.ChatCompletion.create')
    def test_ai_insights_scoring_success(self, mock_openai, scoring_service):
        """Test AI insights scoring with successful API call"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = "4"
        mock_openai.return_value = mock_response

        lead = Lead(title="Test Lead")

        score = scoring_service._score_ai_insights(lead)

        assert score == 4  # Should return the AI score
        mock_openai.assert_called_once()

    @pytest.mark.unit
    @patch('api.services.lead_scoring.openai.ChatCompletion.create')
    def test_ai_insights_scoring_failure(self, mock_openai, scoring_service):
        """Test AI insights scoring with API failure"""
        # Mock OpenAI failure
        mock_openai.side_effect = Exception("API Error")

        lead = Lead(title="Test Lead")

        score = scoring_service._score_ai_insights(lead)

        assert score == 0  # Should return 0 on failure
```

#### API Endpoint Testing
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authentication headers"""
    return {"Authorization": "Bearer test-token"}

class TestLeadAPI:
    @pytest.mark.unit
    def test_create_lead_success(self, client, auth_headers):
        """Test successful lead creation"""
        lead_data = {
            "title": "Test Lead",
            "contact_id": 1,
            "status": "new"
        }

        with patch('api.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, organization_id=1)

            response = client.post(
                "/api/leads",
                json=lead_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data['success'] is True
            assert data['data']['title'] == "Test Lead"

    @pytest.mark.unit
    def test_create_lead_validation_error(self, client, auth_headers):
        """Test lead creation with validation error"""
        invalid_data = {
            "title": "",  # Empty title should fail
            "contact_id": 1
        }

        response = client.post(
            "/api/leads",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert data['success'] is False
        assert 'validation_error' in data['error']['code'].lower()

    @pytest.mark.unit
    def test_get_lead_not_found(self, client, auth_headers):
        """Test retrieving non-existent lead"""
        response = client.get(
            "/api/leads/99999",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
```

### 2.2 Frontend Unit Tests

#### React Component Testing
```typescript
// LeadForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LeadForm } from '../components/LeadForm';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

// Mock API server
const server = setupServer(
  rest.post('/api/leads', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: { id: 1, title: 'Test Lead' }
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LeadForm', () => {
  it('renders form fields correctly', () => {
    render(<LeadForm onSuccess={() => {}} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contact/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
  });

  it('submits form successfully', async () => {
    const mockOnSuccess = jest.fn();
    render(<LeadForm onSuccess={mockOnSuccess} />);

    // Fill form
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'New Lead' }
    });

    fireEvent.change(screen.getByLabelText(/status/i), {
      target: { value: 'qualified' }
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    // Wait for success
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith({ id: 1, title: 'New Lead' });
    });

    expect(screen.getByText('Lead created successfully')).toBeInTheDocument();
  });

  it('displays validation errors', async () => {
    render(<LeadForm onSuccess={() => {}} />);

    // Submit empty form
    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(screen.getByText('Title is required')).toBeInTheDocument();
    });
  });
});
```

#### Custom Hook Testing
```typescript
// useLeadScoring.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useLeadScoring } from '../hooks/useLeadScoring';

const mockApi = {
  scoreLead: jest.fn()
};

jest.mock('../api/leads', () => ({
  scoreLead: () => mockApi.scoreLead()
}));

describe('useLeadScoring', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('scores lead successfully', async () => {
    const mockScore = { total_score: 85, confidence: 0.9 };
    mockApi.scoreLead.mockResolvedValue(mockScore);

    const { result } = renderHook(() => useLeadScoring());

    act(() => {
      result.current.scoreLead(1);
    });

    await waitFor(() => {
      expect(result.current.score).toEqual(mockScore);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
    });
  });

  it('handles scoring error', async () => {
    const mockError = new Error('Scoring failed');
    mockApi.scoreLead.mockRejectedValue(mockError);

    const { result } = renderHook(() => useLeadScoring());

    act(() => {
      result.current.scoreLead(1);
    });

    await waitFor(() => {
      expect(result.current.error).toEqual(mockError);
      expect(result.current.loading).toBe(false);
      expect(result.current.score).toBe(null);
    });
  });
});
```

## 3. Integration Testing Strategy

### 3.1 API Integration Tests

#### Database Integration Testing
```python
import pytest
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import Lead, Contact, Organization
from api.services.lead_scoring import LeadScoringService

@pytest.fixture
def db_session():
    """Create test database session"""
    db = next(get_db())
    # Set up test data
    yield db
    # Clean up test data
    db.rollback()

@pytest.mark.integration
class TestLeadScoringIntegration:
    def test_full_lead_scoring_workflow(self, db_session):
        """Test complete lead scoring workflow with database"""
        # Create test organization
        org = Organization(name="Test Org", domain="test.com")
        db_session.add(org)
        db_session.commit()

        # Create test contact
        contact = Contact(
            name="John Doe",
            email="john@test.com",
            company="Test Company",
            organization_id=org.id
        )
        db_session.add(contact)
        db_session.commit()

        # Create test lead
        lead = Lead(
            title="Test Lead",
            contact_id=contact.id,
            organization_id=org.id
        )
        db_session.add(lead)
        db_session.commit()

        # Score the lead
        scoring_service = LeadScoringService()
        result = scoring_service.calculate_lead_score(lead, db_session)

        # Verify scoring worked
        assert 'total_score' in result
        assert isinstance(result['total_score'], (int, float))
        assert 0 <= result['total_score'] <= 100

        # Verify database was updated
        db_session.refresh(lead)
        assert lead.score == result['total_score']
        assert lead.score_updated_at is not None

    def test_lead_scoring_with_activities(self, db_session):
        """Test lead scoring with activity history"""
        from api.models import Activity

        # Create test data (organization, contact, lead)
        org = Organization(name="Test Org", domain="test.com")
        contact = Contact(name="Jane Doe", email="jane@test.com", organization_id=org.id)
        lead = Lead(title="Active Lead", contact_id=contact.id, organization_id=org.id)

        db_session.add_all([org, contact, lead])
        db_session.commit()

        # Add activities
        activities = [
            Activity(lead_id=lead.id, type="email_open", timestamp=datetime.utcnow()),
            Activity(lead_id=lead.id, type="website_visit", timestamp=datetime.utcnow()),
            Activity(lead_id=lead.id, type="email_click", timestamp=datetime.utcnow()),
        ]
        db_session.add_all(activities)
        db_session.commit()

        # Score lead
        scoring_service = LeadScoringService()
        result = scoring_service.calculate_lead_score(lead, db_session)

        # Should have higher score due to engagement
        assert result['total_score'] > 20  # Base score for engaged lead
```

#### External API Integration Testing
```python
import pytest
from unittest.mock import patch, Mock
import aiohttp
from api.services.retell_ai import RetellAIService

@pytest.mark.integration
class TestRetellAIIntegration:
    @pytest.fixture
    async def retell_service(self):
        """Create Retell AI service with test configuration"""
        service = RetellAIService()
        service.api_key = "test-key"
        service.base_url = "https://api.retellai.com"
        return service

    @pytest.mark.asyncio
    async def test_create_agent_success(self, retell_service):
        """Test successful agent creation"""
        mock_response_data = {"agent_id": "test-agent-123"}

        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response

            agent_config = Mock()
            agent_config.name = "Test Agent"
            agent_config.voice_id = "voice-123"

            result = await retell_service.create_agent(agent_config)

            assert result == "test-agent-123"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_agent_api_failure(self, retell_service):
        """Test agent creation with API failure"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock failed response
            mock_response = Mock()
            mock_response.status = 500
            mock_post.return_value.__aenter__.return_value = mock_response

            agent_config = Mock()
            result = await retell_service.create_agent(agent_config)

            assert result is None

    @pytest.mark.asyncio
    async def test_create_phone_call_integration(self, retell_service):
        """Test phone call creation with full integration"""
        mock_call_data = {"call_id": "call-123"}

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(return_value=mock_call_data)
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await retell_service.create_phone_call(
                agent_id="agent-123",
                to_number="+1234567890"
            )

            assert result == "call-123"
```

### 3.2 Frontend Integration Tests

#### Component Integration Testing
```typescript
// LeadManagement.integration.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LeadManagement } from '../components/LeadManagement';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

// Mock API endpoints
const server = setupServer(
  rest.get('/api/leads', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: [
        { id: 1, title: 'Lead 1', status: 'new' },
        { id: 2, title: 'Lead 2', status: 'qualified' }
      ],
      meta: { total: 2, page: 1, per_page: 20 }
    }));
  }),

  rest.post('/api/leads', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: { id: 3, title: 'New Lead', status: 'new' }
    }));
  }),

  rest.put('/api/leads/1', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: { id: 1, title: 'Updated Lead', status: 'qualified' }
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LeadManagement Integration', () => {
  it('loads and displays leads', async () => {
    render(<LeadManagement />);

    // Wait for leads to load
    await waitFor(() => {
      expect(screen.getByText('Lead 1')).toBeInTheDocument();
      expect(screen.getByText('Lead 2')).toBeInTheDocument();
    });
  });

  it('creates new lead successfully', async () => {
    render(<LeadManagement />);

    // Click create button
    fireEvent.click(screen.getByText('Create Lead'));

    // Fill form
    fireEvent.change(screen.getByLabelText('Title'), {
      target: { value: 'New Lead' }
    });

    // Submit form
    fireEvent.click(screen.getByText('Create'));

    // Verify new lead appears
    await waitFor(() => {
      expect(screen.getByText('New Lead')).toBeInTheDocument();
    });
  });

  it('updates lead status', async () => {
    render(<LeadManagement />);

    // Wait for leads to load
    await waitFor(() => {
      expect(screen.getByText('Lead 1')).toBeInTheDocument();
    });

    // Click on lead to edit
    fireEvent.click(screen.getByText('Lead 1'));

    // Change status
    fireEvent.change(screen.getByLabelText('Status'), {
      target: { value: 'qualified' }
    });

    // Save changes
    fireEvent.click(screen.getByText('Save'));

    // Verify status update
    await waitFor(() => {
      expect(screen.getByText('qualified')).toBeInTheDocument();
    });
  });
});
```

## 4. End-to-End Testing Strategy

### 4.1 E2E Test Scenarios

#### Critical User Journeys
```typescript
// critical-journeys.e2e.test.ts
import { test, expect } from '@playwright/test';

test.describe('Critical User Journeys', () => {
  test('complete lead to deal conversion', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');

    // Navigate to leads
    await page.click('[data-testid="leads-nav"]');

    // Create new lead
    await page.click('[data-testid="create-lead-button"]');
    await page.fill('[data-testid="lead-title"]', 'E2E Test Lead');
    await page.selectOption('[data-testid="lead-status"]', 'qualified');
    await page.click('[data-testid="save-lead-button"]');

    // Verify lead creation
    await expect(page.locator('[data-testid="lead-title"]')).toContainText('E2E Test Lead');

    // Convert to deal
    await page.click('[data-testid="convert-to-deal-button"]');
    await page.fill('[data-testid="deal-value"]', '50000');
    await page.click('[data-testid="create-deal-button"]');

    // Verify deal creation
    await expect(page.locator('[data-testid="deal-title"]')).toContainText('E2E Test Lead');

    // Move deal through pipeline
    await page.dragAndDrop('[data-testid="deal-card"]', '[data-testid="qualified-stage"]');
    await expect(page.locator('[data-testid="qualified-stage"]')).toContainText('E2E Test Lead');
  });

  test('AI-powered lead scoring workflow', async ({ page }) => {
    // Login and navigate to lead
    await page.goto('/leads/123');

    // Trigger AI scoring
    await page.click('[data-testid="score-lead-button"]');

    // Wait for scoring to complete
    await page.waitForSelector('[data-testid="lead-score"]');

    // Verify score display
    const scoreElement = page.locator('[data-testid="lead-score"]');
    await expect(scoreElement).toBeVisible();

    // Verify recommendations
    await expect(page.locator('[data-testid="ai-recommendations"]')).toBeVisible();

    // Verify scoring factors
    await expect(page.locator('[data-testid="scoring-factors"]')).toContainText('Industry');
    await expect(page.locator('[data-testid="scoring-factors"]')).toContainText('Engagement');
  });

  test('call center agent workflow', async ({ page }) => {
    // Agent login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'agent@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');

    // Navigate to calls
    await page.click('[data-testid="calls-nav"]');

    // Verify call interface
    await expect(page.locator('[data-testid="call-interface"]')).toBeVisible();

    // Simulate incoming call (mock)
    await page.evaluate(() => {
      window.postMessage({ type: 'incoming-call', data: { from: '+1234567890' } }, '*');
    });

    // Verify call popup
    await expect(page.locator('[data-testid="incoming-call-popup"]')).toBeVisible();

    // Answer call
    await page.click('[data-testid="answer-call-button"]');

    // Verify active call interface
    await expect(page.locator('[data-testid="active-call"]')).toBeVisible();

    // End call
    await page.click('[data-testid="end-call-button"]');

    // Verify call logging
    await expect(page.locator('[data-testid="call-log"]')).toBeVisible();
  });
});
```

#### Playwright Configuration
```javascript
// playwright.config.js
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

### 4.2 Performance Testing

#### Load Testing with Artillery
```yaml
# performance-test.yml
config:
  target: 'https://neuracrm.up.railway.app'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 50
      name: "Load testing"
    - duration: 60
      arrivalRate: 100
      name: "Spike testing"
  defaults:
    headers:
      Authorization: 'Bearer {{token}}'

scenarios:
  - name: 'Lead management workflow'
    weight: 40
    flow:
      - get:
          url: '/api/leads'
          expect:
            - statusCode: 200
      - post:
          url: '/api/leads'
          json:
            title: 'Performance Test Lead {{ $randomInt }}'
            contact_id: 1
            status: 'new'
          expect:
            - statusCode: 201
      - put:
          url: '/api/leads/{{ leadId }}'
          json:
            status: 'qualified'
          expect:
            - statusCode: 200

  - name: 'AI scoring load'
    weight: 30
    flow:
      - post:
          url: '/api/ai/lead-scoring'
          json:
            lead_id: '{{ leadId }}'
          expect:
            - statusCode: 200
      - get:
          url: '/api/leads/{{ leadId }}'
          expect:
            - statusCode: 200

  - name: 'Call center operations'
    weight: 30
    flow:
      - get:
          url: '/api/calls'
          expect:
            - statusCode: 200
      - post:
          url: '/api/calls'
          json:
            agent_id: 'agent-123'
            to_number: '+1234567890'
            from_number: '+0987654321'
          expect:
            - statusCode: 201
```

#### JMeter Test Plan
```xml
<!-- performance-test.jmx -->
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.4.1">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="NeuraCRM Performance Test">
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Load Test Group">
        <intProp name="ThreadGroup.num_threads">100</intProp>
        <intProp name="ThreadGroup.ramp_time">30</intProp>
        <longProp name="ThreadGroup.duration">600</longProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>

        <hashTree>
          <!-- HTTP Request Defaults -->
          <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults">
            <stringProp name="HTTPSampler.domain">neuracrm.up.railway.app</stringProp>
            <stringProp name="HTTPSampler.port">443</stringProp>
            <stringProp name="HTTPSampler.protocol">https</stringProp>
          </ConfigTestElement>

          <!-- Authentication -->
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">Bearer ${AUTH_TOKEN}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>

          <!-- API Calls -->
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Get Leads">
            <stringProp name="HTTPSampler.path">/api/leads</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          </HTTPSamplerProxy>

          <!-- Response Assertion -->
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Code Assertion">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="9093888">200</stringProp>
            </collectionProp>
            <stringProp name="Assertion.custom_message"></stringProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
          </ResponseAssertion>
        </hashTree>
      </ThreadGroup>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

## 5. Security Testing

### 5.1 Authentication & Authorization Testing

#### JWT Token Testing
```python
import pytest
from jose import jwt
from api.auth import create_access_token, verify_password

class TestAuthenticationSecurity:
    def test_password_hashing(self):
        """Test password hashing security"""
        password = "testpassword123"

        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Verify hash
        assert bcrypt.checkpw(password.encode('utf-8'), hashed)
        assert not bcrypt.checkpw("wrongpassword".encode('utf-8'), hashed)

    def test_jwt_token_integrity(self):
        """Test JWT token creation and verification"""
        data = {"user_id": 123, "organization_id": 456}

        # Create token
        token = create_access_token(data)

        # Decode and verify
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert decoded["user_id"] == 123
        assert decoded["organization_id"] == 456
        assert "exp" in decoded

    def test_jwt_token_expiry(self):
        """Test JWT token expiry"""
        import time
        from datetime import timedelta

        # Create expired token
        expired_token = create_access_token(
            {"user_id": 123},
            expires_delta=timedelta(seconds=-1)
        )

        # Should fail verification
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_password_complexity(self):
        """Test password complexity requirements"""
        weak_passwords = ["123", "password", "abc", ""]

        for password in weak_passwords:
            # Should reject weak passwords
            assert not self._is_password_strong(password)

    def _is_password_strong(self, password: str) -> bool:
        """Check password strength"""
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        return True
```

#### Authorization Testing
```python
class TestAuthorization:
    def test_organization_data_isolation(self, client, auth_headers):
        """Test that users can only access their organization data"""
        # Create lead in org 1
        lead_data = {
            "title": "Org 1 Lead",
            "contact_id": 1,
            "organization_id": 1
        }

        response = client.post("/api/leads", json=lead_data, headers=auth_headers)
        assert response.status_code == 201
        lead_id = response.json()["data"]["id"]

        # Try to access from different organization (should fail)
        # This would require mocking different org context

    def test_role_based_permissions(self, client):
        """Test role-based access control"""
        # Admin can access all endpoints
        admin_headers = {"Authorization": "Bearer admin-token"}

        response = client.get("/api/organizations", headers=admin_headers)
        assert response.status_code == 200

        # Regular user cannot access admin endpoints
        user_headers = {"Authorization": "Bearer user-token"}

        response = client.get("/api/organizations", headers=user_headers)
        assert response.status_code == 403
```

### 5.2 API Security Testing

#### Input Validation Testing
```python
class TestInputValidation:
    def test_sql_injection_prevention(self, client, auth_headers):
        """Test SQL injection prevention"""
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../../etc/passwd"
        ]

        for payload in malicious_payloads:
            lead_data = {
                "title": payload,
                "contact_id": 1
            }

            response = client.post("/api/leads", json=lead_data, headers=auth_headers)

            # Should either sanitize or reject malicious input
            if response.status_code == 201:
                # If accepted, ensure it's sanitized
                created_lead = response.json()["data"]
                assert "<script>" not in created_lead["title"]
                assert "DROP TABLE" not in created_lead["title"]
            else:
                # Should be rejected with validation error
                assert response.status_code == 422

    def test_xss_prevention(self, client, auth_headers):
        """Test XSS attack prevention"""
        xss_payload = '<img src=x onerror=alert(1)>'

        lead_data = {
            "title": "Test Lead",
            "description": xss_payload
        }

        response = client.post("/api/leads", json=lead_data, headers=auth_headers)
        assert response.status_code == 201

        # Verify XSS is sanitized in response
        lead = response.json()["data"]
        assert "<img" not in lead.get("description", "")
        assert "onerror" not in lead.get("description", "")
```

#### Rate Limiting Testing
```python
class TestRateLimiting:
    def test_api_rate_limiting(self, client, auth_headers):
        """Test API rate limiting"""
        # Make multiple requests rapidly
        responses = []
        for i in range(150):  # Exceed rate limit
            response = client.get("/api/leads", headers=auth_headers)
            responses.append(response.status_code)

        # Should see 429 Too Many Requests
        assert 429 in responses

        # Check rate limit headers
        limited_response = None
        for response in responses:
            if hasattr(response, 'headers') and response.status_code == 429:
                limited_response = response
                break

        assert limited_response is not None
        assert 'X-RateLimit-Reset' in limited_response.headers
        assert 'Retry-After' in limited_response.headers
```

## 6. Test Automation & CI/CD

### 6.1 CI/CD Pipeline Configuration

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run backend tests
      run: |
        pytest --cov=api --cov-report=xml --cov-report=term-missing --cov-fail-under=80

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  frontend-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run frontend tests
      run: npm run test:ci

    - name: Build frontend
      run: npm run build

  e2e-test:
    runs-on: ubuntu-latest
    needs: [test, frontend-test]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install Playwright
      run: npx playwright install

    - name: Run E2E tests
      run: npx playwright test

  security-scan:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results
      uses: github/codecov-action@v3
      if: always()
      with:
        file: trivy-results.sarif

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test, frontend-test, e2e-test, security-scan]
    if: github.ref == 'refs/heads/develop'

    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Railway deployment commands

  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, frontend-test, e2e-test, security-scan]
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Railway deployment commands
```

### 6.2 Test Reporting & Analytics

#### Coverage Reporting
```python
# tests/conftest.py
import pytest
import coverage
from pytest_cov.plugin import CovPlugin

@pytest.fixture(scope="session", autouse=True)
def coverage_setup():
    """Set up coverage reporting"""
    cov = coverage.Coverage(
        source=['api'],
        omit=[
            '*/tests/*',
            '*/venv/*',
            '*/__pycache__/*',
            '*/migrations/*'
        ]
    )
    cov.start()

    yield

    cov.stop()
    cov.save()
    cov.report(show_missing=True)

    # Generate HTML report
    cov.html_report(directory='htmlcov')

    # Fail if coverage below threshold
    if cov.report() < 80:
        pytest.fail("Coverage below 80%")
```

#### Test Results Dashboard
```python
# tests/dashboard.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

class TestDashboard:
    def __init__(self):
        self.results = []

    def parse_junit_results(self, xml_file: str) -> Dict:
        """Parse JUnit XML test results"""
        tree = ET.parse(xml_file)
        root = tree.getroot()

        results = {
            'timestamp': datetime.now().isoformat(),
            'testsuites': []
        }

        for testsuite in root:
            suite_data = {
                'name': testsuite.get('name'),
                'tests': int(testsuite.get('tests', 0)),
                'failures': int(testsuite.get('failures', 0)),
                'errors': int(testsuite.get('errors', 0)),
                'skipped': int(testsuite.get('skipped', 0)),
                'time': float(testsuite.get('time', 0)),
                'testcases': []
            }

            for testcase in testsuite:
                case_data = {
                    'name': testcase.get('name'),
                    'classname': testcase.get('classname'),
                    'time': float(testcase.get('time', 0)),
                    'status': 'passed'
                }

                # Check for failure/error
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')

                if failure is not None:
                    case_data['status'] = 'failed'
                    case_data['message'] = failure.text
                elif error is not None:
                    case_data['status'] = 'error'
                    case_data['message'] = error.text
                elif skipped is not None:
                    case_data['status'] = 'skipped'

                suite_data['testcases'].append(case_data)

            results['testsuites'].append(suite_data)

        return results

    def generate_report(self, results: Dict) -> str:
        """Generate HTML test report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Results Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .testsuite {{ margin: 20px 0; border: 1px solid #ddd; padding: 10px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .error {{ color: orange; }}
                .skipped {{ color: gray; }}
            </style>
        </head>
        <body>
            <h1>Test Results Dashboard</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Generated: {results['timestamp']}</p>
        """

        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0

        for suite in results['testsuites']:
            total_tests += suite['tests']
            total_failed += suite['failures']
            total_errors += suite['errors']
            total_skipped += suite['skipped']
            total_passed += suite['tests'] - suite['failures'] - suite['errors'] - suite['skipped']

            html += f"""
            <div class="testsuite">
                <h3>{suite['name']}</h3>
                <p>Tests: {suite['tests']}, Passed: <span class="passed">{suite['tests'] - suite['failures'] - suite['errors'] - suite['skipped']}</span>,
                   Failed: <span class="failed">{suite['failures']}</span>,
                   Errors: <span class="error">{suite['errors']}</span>,
                   Skipped: <span class="skipped">{suite['skipped']}</span></p>
                <p>Time: {suite['time']:.2f}s</p>
            </div>
            """

        html += f"""
            <h3>Overall Results</h3>
            <p>Total Tests: {total_tests}</p>
            <p>Passed: <span class="passed">{total_passed}</span></p>
            <p>Failed: <span class="failed">{total_failed}</span></p>
            <p>Errors: <span class="error">{total_errors}</span></p>
            <p>Skipped: <span class="skipped">{total_skipped}</span></p>
            <p>Success Rate: {((total_passed / total_tests) * 100):.1f}%</p>
        """

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def save_report(self, html: str, filename: str):
        """Save HTML report to file"""
        with open(filename, 'w') as f:
            f.write(html)
```

This comprehensive testing and validation plan ensures NeuraCRM maintains high quality, security, and reliability across all components and features.