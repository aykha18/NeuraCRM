# Contributing Guidelines

## Welcome to NeuraCRM! 🎉

Thank you for your interest in contributing to NeuraCRM! This document provides comprehensive guidelines for contributors, whether you're fixing bugs, adding features, improving documentation, or helping with testing.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Style and Standards](#code-style-and-standards)
4. [Development Workflow](#development-workflow)
5. [Pull Request Process](#pull-request-process)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Issue Reporting](#issue-reporting)
9. [Community Guidelines](#community-guidelines)
10. [Recognition](#recognition)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - Backend development
- **Node.js 18+** - Frontend development
- **PostgreSQL 13+** - Database
- **Redis 7+** - Caching and sessions
- **Git** - Version control
- **Docker & Docker Compose** - Containerized development (optional)

### Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/NeuraCRM.git
   cd NeuraCRM
   ```
3. **Set up the development environment** (see detailed instructions below)
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes** following our guidelines
6. **Run tests** to ensure everything works
7. **Submit a pull request**

## Development Environment Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Set up database**:
   ```bash
   # Create PostgreSQL database
   createdb neuracrm

   # Run database migrations
   alembic upgrade head

   # Load sample data (optional)
   python setup_db.py
   ```

6. **Start the backend server**:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

### Docker Development (Alternative)

For a fully containerized development environment:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### IDE Configuration

#### VS Code Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode-remote.remote-containers"
  ]
}
```

#### VS Code Settings

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "html",
    "typescriptreact": "HTML"
  }
}
```

## Code Style and Standards

### Python Backend Standards

#### Code Formatting
We use **Black** for code formatting:

```bash
# Format code
black .

# Check formatting
black --check .
```

#### Import Sorting
We use **isort** for import organization:

```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

#### Linting
We use **flake8** for code linting:

```bash
# Run linting
flake8 .

# Configuration in setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,venv,.venv
```

#### Type Hints
All new code must include proper type hints:

```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

def get_user(user_id: int) -> Optional[User]:
    """Get user by ID with proper typing."""
    return db.query(User).filter(User.id == user_id).first()

class UserCreate(BaseModel):
    name: str
    email: str
    role: Optional[str] = "agent"
```

### JavaScript/TypeScript Frontend Standards

#### Code Formatting
We use **Prettier** for code formatting:

```bash
# Format code
npm run format

# Check formatting
npm run format:check
```

#### Linting
We use **ESLint** for code linting:

```bash
# Run linting
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

#### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "ES6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

### Commit Message Standards

We follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples
```bash
feat(auth): add JWT token refresh functionality

fix(api): resolve memory leak in lead scoring service

docs(readme): update installation instructions

test(leads): add integration tests for lead conversion

refactor(deals): simplify deal pipeline logic
```

### Branch Naming Convention

```
feature/feature-name
fix/bug-description
docs/update-documentation
refactor/component-name
test/add-test-coverage
chore/maintenance-task
```

## Development Workflow

### 1. Choose an Issue

1. Check the [GitHub Issues](https://github.com/aykha18/NeuraCRM/issues) page
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to indicate you're working on it
4. Wait for maintainer approval before starting work

### 2. Create a Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 3. Implement Your Changes

1. **Write tests first** (TDD approach recommended)
2. **Implement the feature/fix**
3. **Ensure all tests pass**
4. **Update documentation if needed**
5. **Test manually** in the browser

### 4. Run Quality Checks

Before committing, run all quality checks:

```bash
# Backend checks
cd backend
black --check .
isort --check-only .
flake8 .
pytest --cov=api --cov-report=term-missing --cov-fail-under=80

# Frontend checks
cd frontend
npm run lint
npm run type-check
npm run test
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with conventional format
git commit -m "feat: add user profile page

- Add profile component with avatar upload
- Implement profile data fetching
- Add form validation for profile updates

Closes #123"
```

## Pull Request Process

### Creating a Pull Request

1. **Ensure your branch is up to date**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create PR on GitHub**:
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch as the compare branch
   - Fill out the PR template

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context about the PR.
```

### PR Review Process

1. **Automated Checks**: CI/CD pipeline runs all tests and quality checks
2. **Peer Review**: At least one maintainer reviews the code
3. **Approval**: PR is approved or changes are requested
4. **Merge**: PR is merged using "Squash and merge" to maintain clean history

### Review Guidelines

#### For Reviewers
- **Be constructive**: Focus on code quality and learning
- **Explain reasoning**: Why are you suggesting changes?
- **Be timely**: Review within 24-48 hours
- **Test locally**: Run the code and verify functionality

#### For Contributors
- **Respond promptly**: Address review comments within 24 hours
- **Explain decisions**: If you disagree with suggestions, explain why
- **Make requested changes**: Implement feedback or discuss alternatives
- **Re-request review**: After making changes, request re-review

## Testing Guidelines

### Unit Testing

#### Backend Unit Tests
```python
# tests/test_lead_scoring.py
import pytest
from unittest.mock import Mock
from api.services.lead_scoring import LeadScoringService

class TestLeadScoringService:
    def test_calculate_lead_score_high_value(self):
        """Test scoring for a high-value lead"""
        service = LeadScoringService()

        # Mock lead data
        lead = Mock()
        lead.contact.company = "Fortune 500 Company"
        lead.contact.industry = "Technology"

        # Mock database interactions
        db = Mock()

        result = service.calculate_lead_score(lead, db)

        assert result['total_score'] >= 80
        assert result['category'] == 'hot'
```

#### Frontend Unit Tests
```typescript
// src/components/__tests__/LeadForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LeadForm } from '../LeadForm';

describe('LeadForm', () => {
  it('submits form with valid data', async () => {
    const mockOnSubmit = jest.fn();
    render(<LeadForm onSubmit={mockOnSubmit} />);

    // Fill out form
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'New Lead' }
    });

    fireEvent.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'New Lead',
        status: 'new'
      });
    });
  });
});
```

### Integration Testing

#### API Integration Tests
```python
# tests/integration/test_lead_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_lead_integration(client: TestClient, db: Session):
    """Test complete lead creation workflow"""
    # Setup test data
    org = create_test_organization(db)
    user = create_test_user(db, org)

    # Authenticate
    token = get_auth_token(client, user)

    # Create lead
    lead_data = {
        "title": "Integration Test Lead",
        "contact_id": 1,
        "status": "new"
    }

    response = client.post(
        "/api/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()

    # Verify in database
    lead = db.query(Lead).filter(Lead.id == data["data"]["id"]).first()
    assert lead.title == "Integration Test Lead"
```

### End-to-End Testing

#### Playwright E2E Tests
```typescript
// tests/e2e/lead-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Lead Management', () => {
  test('user can create and convert lead to deal', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');

    // Navigate to leads
    await page.click('[data-testid="leads-nav"]');

    // Create lead
    await page.click('[data-testid="create-lead-button"]');
    await page.fill('[data-testid="lead-title"]', 'E2E Test Lead');
    await page.click('[data-testid="save-lead-button"]');

    // Verify lead created
    await expect(page.locator('[data-testid="lead-title"]')).toContainText('E2E Test Lead');

    // Convert to deal
    await page.click('[data-testid="convert-to-deal-button"]');
    await page.fill('[data-testid="deal-value"]', '50000');
    await page.click('[data-testid="create-deal-button"]');

    // Verify deal created
    await expect(page.locator('[data-testid="deal-title"]')).toContainText('E2E Test Lead');
  });
});
```

### Test Coverage Requirements

- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical paths**: 90%+ coverage
- **New features**: 85%+ coverage before merge

## Documentation

### Code Documentation

#### Python Docstrings
```python
def calculate_lead_score(self, lead: Lead, db: Session) -> Dict[str, Any]:
    """
    Calculate comprehensive lead score using multiple factors.

    This method evaluates leads across multiple dimensions including
    industry, company size, engagement patterns, decision maker position,
    and urgency signals to provide a holistic scoring assessment.

    Args:
        lead: Lead object to score
        db: Database session for additional data queries

    Returns:
        Dictionary containing:
        - total_score: Overall score (0-100)
        - factor_scores: Breakdown by scoring factor
        - confidence: AI confidence in scoring (0.0-1.0)
        - category: Score category (cold, warm, hot)
        - recommendations: Actionable recommendations

    Raises:
        ValueError: If lead data is invalid or incomplete

    Example:
        >>> result = scoring_service.calculate_lead_score(lead, db)
        >>> print(f"Score: {result['total_score']}")
        Score: 85
    """
```

#### TypeScript JSDoc
```typescript
/**
 * Lead scoring service for AI-powered lead evaluation
 *
 * Provides comprehensive lead scoring using machine learning
 * and business rules to prioritize sales efforts.
 */
export class LeadScoringService {
  /**
   * Calculate lead score using multiple evaluation criteria
   *
   * @param leadId - Unique identifier of the lead
   * @param options - Additional scoring options
   * @returns Promise resolving to scoring result
   *
   * @example
   * ```typescript
   * const result = await scoringService.scoreLead(123, {
   *   includeAiInsights: true
   * });
   * console.log(`Lead score: ${result.totalScore}`);
   * ```
   */
  async scoreLead(leadId: number, options?: ScoringOptions): Promise<ScoringResult> {
    // Implementation
  }
}
```

### API Documentation

#### OpenAPI/Swagger Annotations
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

router = APIRouter()

class LeadCreate(BaseModel):
    """Schema for creating a new lead"""
    title: str = Field(..., min_length=1, max_length=200, description="Lead title or summary")
    contact_id: Optional[int] = Field(None, description="Associated contact ID")
    status: str = Field("new", enum=["new", "contacted", "qualified", "unqualified"], description="Lead status")
    source: Optional[str] = Field(None, description="Lead source channel")

@router.post(
    "/leads",
    response_model=LeadResponse,
    summary="Create a new lead",
    description="""
    Create a new sales lead with initial information.

    This endpoint allows sales representatives to capture new leads
    from various sources including website forms, business cards,
    referrals, and cold outreach.

    **Required permissions:** leads:create
    """,
    responses={
        201: {"description": "Lead created successfully"},
        400: {"description": "Invalid lead data"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"}
    }
)
async def create_lead(
    lead: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new lead in the CRM system."""
    # Implementation
```

### README Updates

When adding new features, update the README.md:

1. **Feature descriptions** in the features section
2. **API endpoints** in the API documentation section
3. **Setup instructions** if new dependencies are added
4. **Screenshots/demo** for UI changes

## Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
A clear and concise description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots to help explain the problem.

**Environment**
- OS: [e.g., Windows 10, macOS 11]
- Browser: [e.g., Chrome 91, Firefox 89]
- Version: [e.g., v1.2.3]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

Use this template for feature requests:

```markdown
**Feature Summary**
Brief description of the feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
Describe the solution you'd like.

**Alternatives Considered**
Describe any alternative solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

### Security Issues

For security vulnerabilities:

1. **DO NOT** create a public GitHub issue
2. Email security@neuracrm.com with details
3. Allow 48 hours for initial response
4. Work with maintainers on coordinated disclosure

## Community Guidelines

### Code of Conduct

#### Our Standards
- **Be respectful**: Treat all contributors with respect
- **Be collaborative**: Help others learn and grow
- **Be patient**: Not everyone knows everything
- **Be constructive**: Focus on solutions, not problems
- **Be inclusive**: Welcome contributors from all backgrounds

#### Unacceptable Behavior
- Harassment or discrimination
- Personal attacks or insults
- Trolling or disruptive comments
- Publishing private information
- Spam or off-topic content

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Discord**: Real-time chat for contributors (invite link in README)
- **Email**: support@neuracrm.com for security issues

### Getting Help

1. **Check existing documentation** first
2. **Search GitHub Issues** for similar problems
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** if you found a bug
5. **Contact maintainers** for urgent issues

## Recognition

### Contributor Recognition

We recognize contributions in several ways:

#### GitHub Recognition
- **Contributors** listed in repository contributors
- **Pull request** acknowledgments in release notes
- **Issues** tagged with contributor labels

#### Community Recognition
- **Discord roles** for active contributors
- **Newsletter mentions** for significant contributions
- **Swag** for major contributors (t-shirts, stickers)

#### Professional Recognition
- **LinkedIn shoutouts** for exceptional contributions
- **Speaking opportunities** at meetups/webinars
- **Co-authorship** on related publications

### Contribution Levels

- **First-time contributor**: Welcome message and guidance
- **Regular contributor**: Discord role and recognition
- **Core contributor**: Decision-making influence
- **Maintainer**: Repository administration rights

### Hacktoberfest & Other Programs

We participate in:
- **Hacktoberfest**: October contribution challenge
- **Google Summer of Code**: Student mentorship program
- **Outreachy**: Internship program for underrepresented groups

## License and Legal

### Contributor License Agreement

By contributing to NeuraCRM, you agree that:

1. Your contributions are licensed under the same license as the project
2. You have the right to grant this license
3. Your contributions don't infringe on third-party rights
4. You agree to follow our code of conduct

### Intellectual Property

- **Project license**: Proprietary (see LICENSE file)
- **Third-party code**: Must be compatible and properly attributed
- **AI-generated code**: Must be reviewed and approved by maintainers

---

Thank you for contributing to NeuraCRM! Your efforts help make this platform better for businesses worldwide. 🚀

For questions or assistance, don't hesitate to reach out to the maintainers or community.