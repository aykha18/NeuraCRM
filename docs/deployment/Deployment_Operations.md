# Deployment & Operations

## 1. Infrastructure Architecture

### 1.1 Cloud Infrastructure Overview

```mermaid
graph TB
    subgraph "Railway Cloud Platform"
        APP[Application Server<br/>FastAPI + Uvicorn]
        DB[(PostgreSQL Database<br/>Railway Managed)]
        REDIS[(Redis Cache<br/>Railway Managed)]
        STORAGE[(File Storage<br/>Cloudflare R2)]
    end

    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4]
        RETELL[Retell AI<br/>Conversational AI]
        STRIPE[Stripe<br/>Payments]
        SENGRID[SendGrid<br/>Email]
        TWILIO[Twilio<br/>Telephony]
    end

    subgraph "Content Delivery"
        CF[Cloudflare CDN<br/>Global Distribution]
        WAF[Cloudflare WAF<br/>Security & DDoS]
    end

    subgraph "Monitoring & Observability"
        SENTRY[Sentry<br/>Error Tracking]
        LOGTAIL[Logtail<br/>Log Management]
        UPTIME[Upptime<br/>Uptime Monitoring]
        ANALYTICS[PostHog<br/>Product Analytics]
    end

    APP --> DB
    APP --> REDIS
    APP --> STORAGE

    APP --> OPENAI
    APP --> RETELL
    APP --> STRIPE
    APP --> SENGRID
    APP --> TWILIO

    CF --> APP
    WAF --> CF

    APP --> SENTRY
    APP --> LOGTAIL
    APP --> UPTIME
    APP --> ANALYTICS
```

### 1.2 Environment Configuration

#### Environment Variables Management

```bash
# .env.example
# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/neuracrm

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# External API Keys
OPENAI_API_KEY=sk-your-openai-key
RETELL_API_KEY=your-retell-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
SENDGRID_API_KEY=your-sendgrid-key

# Webhook Configuration
WEBHOOK_SECRET=your-webhook-secret
WEBHOOK_BASE_URL=https://your-domain.com

# File Storage
CLOUDFLARE_R2_ACCESS_KEY=your-r2-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret
CLOUDFLARE_R2_BUCKET=neuracrm-files

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOGTAIL_TOKEN=your-logtail-token
POSTHOG_API_KEY=your-posthog-key

# Email Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-password

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_CALL_CENTER=true
ENABLE_ANALYTICS=true
```

#### Railway Environment Setup

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments]
[environments.production]
DATABASE_URL = { fromSecret = "DATABASE_URL" }
REDIS_URL = { fromSecret = "REDIS_URL" }
SECRET_KEY = { fromSecret = "SECRET_KEY" }
OPENAI_API_KEY = { fromSecret = "OPENAI_API_KEY" }
# ... other secrets

[environments.staging]
DATABASE_URL = { fromSecret = "DATABASE_URL_STAGING" }
REDIS_URL = { fromSecret = "REDIS_URL_STAGING" }
# ... other staging secrets
```

## 2. CI/CD Pipeline

### 2.1 GitHub Actions Workflow

#### Complete CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: 🚀 Deploy NeuraCRM

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Security and Quality Checks
  security:
    name: 🔒 Security Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

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

  # Backend Testing
  test-backend:
    name: 🧪 Test Backend
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
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Cache pip dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio httpx

      - name: Run database migrations
        run: |
          python -c "
          from api.db import create_tables
          create_tables()
          "

      - name: Run tests
        run: |
          pytest \
            --cov=api \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=80 \
            --junitxml=test-results.xml

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: backend

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results-backend
          path: test-results.xml

  # Frontend Testing
  test-frontend:
    name: 🎨 Test Frontend
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linting
        run: |
          cd frontend
          npm run lint

      - name: Run type checking
        run: |
          cd frontend
          npm run type-check

      - name: Run tests
        run: |
          cd frontend
          npm run test:ci

      - name: Build frontend
        run: |
          cd frontend
          npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist/

  # E2E Testing
  test-e2e:
    name: 🤖 Test E2E
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
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
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Cache Playwright browsers
        uses: actions/cache@v3
        with:
          path: ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright-${{ hashFiles('**/package-lock.json') }}

      - name: Install dependencies
        run: |
          npm ci
          npx playwright install

      - name: Run E2E tests
        run: npx playwright test
        env:
          BASE_URL: http://localhost:8000

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-results
          path: test-results/

  # Docker Build
  build:
    name: 🐳 Build Docker Image
    runs-on: ubuntu-latest
    needs: [security, test-backend, test-frontend, test-e2e]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Deploy to Staging
  deploy-staging:
    name: 🚀 Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
      - name: Deploy to Railway (Staging)
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.RAILWAY_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            https://backboard.railway.app/graphql \
            -d '{
              "query": "mutation { deploy(projectId: \"${{ secrets.RAILWAY_PROJECT_ID }}\", environmentId: \"${{ secrets.RAILWAY_STAGING_ENV_ID }}\") { id } }"
            }'

      - name: Wait for deployment
        run: sleep 300

      - name: Health check
        run: |
          curl -f https://neuracrm-staging.up.railway.app/api/health || exit 1

      - name: Run smoke tests
        run: |
          npm run test:smoke -- --baseUrl=https://neuracrm-staging.up.railway.app

  # Deploy to Production
  deploy-production:
    name: 🚀 Deploy to Production
    runs-on: ubuntu-latest
    needs: [build, deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Deploy to Railway (Production)
        run: |
          curl -X POST \
            -H "Authorization: Bearer ${{ secrets.RAILWAY_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            https://backboard.railway.app/graphql \
            -d '{
              "query": "mutation { deploy(projectId: \"${{ secrets.RAILWAY_PROJECT_ID }}\", environmentId: \"${{ secrets.RAILWAY_PRODUCTION_ENV_ID }}\") { id } }"
            }'

      - name: Wait for deployment
        run: sleep 300

      - name: Health check
        run: |
          curl -f https://neuracrm.up.railway.app/api/health || exit 1

      - name: Run smoke tests
        run: |
          npm run test:smoke -- --baseUrl=https://neuracrm.up.railway.app

      - name: Notify deployment success
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "🚀 NeuraCRM deployed successfully to production"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        if: success()

      - name: Notify deployment failure
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: "❌ NeuraCRM deployment failed"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        if: failure()
```

### 2.2 Docker Configuration

#### Multi-stage Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.5.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libpq-dev \
        gcc \
        g++ \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project requirement files
WORKDIR $PYSETUP_PATH
COPY ./backend/poetry.lock ./backend/pyproject.toml ./

# Install runtime dependencies
RUN poetry install --only=main --no-dev

# Production stage
FROM python:3.9-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/pysetup/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Copy virtual environment from python-base
COPY --from=python-base /opt/pysetup/.venv /opt/pysetup/.venv

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

# Copy application code
WORKDIR /app
COPY ./backend .

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### Docker Compose for Local Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: neuracrm
      POSTGRES_USER: neuracrm
      POSTGRES_PASSWORD: neuracrm
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/sample_data.sql:/docker-entrypoint-initdb.d/sample_data.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U neuracrm"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://neuracrm:neuracrm@db:5432/neuracrm
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key
      - ENVIRONMENT=development
      - DEBUG=True
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/__pycache__
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

volumes:
  postgres_data:
  redis_data:
```

## 3. Monitoring & Observability

### 3.1 Application Monitoring

#### Health Check Endpoints
```python
# backend/api/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db import get_db
import redis
import os

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }

    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Redis check
    try:
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # External services check
    external_services = ["openai", "retell_ai", "stripe"]
    for service in external_services:
        api_key = os.getenv(f"{service.upper()}_API_KEY")
        if api_key:
            health_status["checks"][service] = "configured"
        else:
            health_status["checks"][service] = "not_configured"
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"

    return health_status

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

#### Prometheus Metrics Configuration
```python
# backend/api/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Business metrics
LEAD_CREATED = Counter(
    'leads_created_total',
    'Total leads created'
)

DEAL_CONVERTED = Counter(
    'deals_converted_total',
    'Total deals converted'
)

AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['service', 'status']
)

# System metrics
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

QUEUE_SIZE = Gauge(
    'call_queue_size',
    'Current call queue size'
)

def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def track_business_metrics(event_type: str, **kwargs):
    """Track business-specific metrics"""
    if event_type == 'lead_created':
        LEAD_CREATED.inc()
    elif event_type == 'deal_converted':
        DEAL_CONVERTED.inc()
    elif event_type == 'ai_request':
        AI_REQUESTS.labels(
            service=kwargs.get('service'),
            status=kwargs.get('status')
        ).inc()
```

### 3.2 Logging Configuration

#### Structured Logging Setup
```python
# backend/api/logging_config.py
import logging
import logging.config
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging"""

    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = record.created
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['message'] = record.getMessage()

            # Add request context if available
            if hasattr(record, 'request_id'):
                log_record['request_id'] = record.request_id
            if hasattr(record, 'user_id'):
                log_record['user_id'] = record.user_id
            if hasattr(record, 'organization_id'):
                log_record['organization_id'] = record.organization_id

    # Logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJsonFormatter,
                'format': '%(timestamp)s %(level)s %(logger)s %(message)s'
            },
            'console': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'logs/neuracrm.log',
                'formatter': 'json'
            },
            'logtail': {
                'class': 'logtail.LogtailHandler',
                'formatter': 'json',
                'source_token': os.getenv('LOGTAIL_TOKEN')
            }
        },
        'loggers': {
            'api': {
                'handlers': ['console', 'file', 'logtail'],
                'level': 'INFO',
                'propagate': False
            },
            'sqlalchemy': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False
            }
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO'
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)

    # Add request context middleware
    from fastapi import Request
    import uuid

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = str(uuid.uuid4())
        logger = logging.getLogger('api')

        # Add request context to logger
        logger.request_id = request_id
        logger.user_id = getattr(request.state, 'user_id', None)
        logger.organization_id = getattr(request.state, 'organization_id', None)

        response = await call_next(request)
        return response
```

### 3.3 Error Tracking & Alerting

#### Sentry Configuration
```python
# backend/api/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

def setup_sentry():
    """Configure Sentry error tracking"""
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('ENVIRONMENT', 'development'),
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration()
        ],
        # Performance monitoring
        traces_sample_rate=0.1,
        # Release tracking
        release=os.getenv('RELEASE_VERSION'),
        # User context
        send_default_pii=True,
        # Error filtering
        before_send=before_send,
        # Breadcrumbs
        max_breadcrumbs=50
    )

def before_send(event, hint):
    """Filter and enrich error events"""
    # Ignore certain types of errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if exc_type == KeyboardInterrupt:
            return None

    # Add custom context
    if 'request' in event:
        # Add user and organization context
        user_id = getattr(event['request'], 'user_id', None)
        org_id = getattr(event['request'], 'organization_id', None)

        if user_id:
            event['user'] = {'id': user_id}
        if org_id:
            event['tags'] = event.get('tags', {})
            event['tags']['organization_id'] = org_id

    return event
```

#### Alert Manager Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@neuracrm.com'
  smtp_auth_username: 'alerts@neuracrm.com'
  smtp_auth_password: 'your-smtp-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team'
  routes:
  - match:
      severity: critical
    receiver: 'team'
  - match:
      severity: warning
    receiver: 'team'

receivers:
- name: 'team'
  email_configs:
  - to: 'team@neuracrm.com'
    send_resolved: true
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    send_resolved: true
```

## 4. Security Operations

### 4.1 Secret Management

#### Railway Secrets Configuration
```bash
# Set up Railway secrets
railway secrets set SECRET_KEY "your-production-secret-key"
railway secrets set DATABASE_URL "postgresql://..."
railway secrets set REDIS_URL "redis://..."
railway secrets set OPENAI_API_KEY "sk-..."
railway secrets set RETELL_API_KEY "retell-..."
railway secrets set STRIPE_SECRET_KEY "sk_live_..."
railway secrets set SENTRY_DSN "https://..."
railway secrets set LOGTAIL_TOKEN "your-logtail-token"
```

#### Environment-Specific Secrets
```python
# backend/api/config.py
from pydantic import BaseSettings, Field
import os

class Settings(BaseSettings):
    # Application settings
    secret_key: str = Field(..., env='SECRET_KEY')
    environment: str = Field('development', env='ENVIRONMENT')
    debug: bool = Field(False, env='DEBUG')

    # Database settings
    database_url: str = Field(..., env='DATABASE_URL')

    # Redis settings
    redis_url: str = Field(..., env='REDIS_URL')

    # External API keys
    openai_api_key: str = Field(None, env='OPENAI_API_KEY')
    retell_api_key: str = Field(None, env='RETELL_API_KEY')
    stripe_secret_key: str = Field(None, env='STRIPE_SECRET_KEY')
    stripe_publishable_key: str = Field(None, env='STRIPE_PUBLISHABLE_KEY')
    sendgrid_api_key: str = Field(None, env='SENDGRID_API_KEY')

    # Monitoring
    sentry_dsn: str = Field(None, env='SENTRY_DSN')
    logtail_token: str = Field(None, env='LOGTAIL_TOKEN')

    class Config:
        env_file = '.env'
        case_sensitive = False

# Global settings instance
settings = Settings()
```

### 4.2 Backup & Disaster Recovery

#### Automated Backup Strategy
```bash
#!/bin/bash
# backup.sh - Automated backup script

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database backup
echo "Starting database backup..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz s3://neuracrm-backups/database/

# Clean up old backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
echo "Verifying backup integrity..."
gunzip -c $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz | head -n 10 > /dev/null
if [ $? -eq 0 ]; then
    echo "Backup verification successful"
else
    echo "Backup verification failed"
    exit 1
fi

echo "Backup completed successfully"
```

#### Disaster Recovery Plan
```yaml
# disaster-recovery.yml
version: '1.0'

metadata:
  name: NeuraCRM Disaster Recovery Plan
  version: 1.0
  last_updated: 2024-01-01

objectives:
  - Minimize data loss to < 1 hour
  - Restore service within 4 hours
  - Maintain 99.9% uptime SLA

recovery_strategies:
  database_failover:
    description: "PostgreSQL automatic failover"
    rto: "15 minutes"
    rpo: "5 minutes"
    procedure:
      - Detect primary database failure
      - Promote standby replica
      - Update application connection strings
      - Verify data consistency

  application_failover:
    description: "Railway platform failover"
    rto: "30 minutes"
    rpo: "0 minutes"
    procedure:
      - Railway detects service failure
      - Automatic container restart
      - Load balancer routes to healthy instances
      - Monitor service restoration

  data_recovery:
    description: "Point-in-time recovery"
    rto: "2 hours"
    rpo: "1 hour"
    procedure:
      - Identify last good backup
      - Restore database to standby server
      - Validate data integrity
      - Switch application to recovered database

testing_schedule:
  monthly:
    - Backup integrity verification
    - Failover testing
  quarterly:
    - Full disaster recovery simulation
    - Data restoration testing
  annually:
    - Complete business continuity test
    - Third-party dependency failover testing

communication_plan:
  internal:
    - Slack alerts to DevOps team
    - Email notifications to management
  external:
    - Status page updates
    - Customer communication for major incidents
  escalation:
    - Level 1: DevOps on-call
    - Level 2: Engineering manager
    - Level 3: CTO and CEO
```

## 5. Performance Optimization

### 5.1 Database Optimization

#### Query Optimization
```sql
-- Add performance indexes
CREATE INDEX CONCURRENTLY idx_leads_composite_search
    ON leads (organization_id, status, score, created_at DESC);

CREATE INDEX CONCURRENTLY idx_deals_pipeline_view
    ON deals (organization_id, owner_id, stage_id, status, value);

CREATE INDEX CONCURRENTLY idx_calls_analytics
    ON calls (organization_id, start_time, direction, status, duration);

-- Partition large tables
CREATE TABLE calls_y2024m01 PARTITION OF calls
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Optimize slow queries
EXPLAIN ANALYZE
SELECT l.*, c.name as contact_name
FROM leads l
LEFT JOIN contacts c ON l.contact_id = c.id
WHERE l.organization_id = $1
  AND l.status = 'qualified'
ORDER BY l.score DESC
LIMIT 50;
```

#### Connection Pooling
```python
# backend/api/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

def create_engine_with_pool(database_url: str):
    """Create SQLAlchemy engine with optimized connection pooling"""
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,          # Core connections
        max_overflow=20,       # Additional connections
        pool_timeout=30,       # Connection timeout
        pool_recycle=3600,     # Recycle connections after 1 hour
        pool_pre_ping=True,    # Test connections before use
        echo=False             # Disable SQL logging in production
    )

# Async engine for FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    database_url.replace('postgresql://', 'postgresql+asyncpg://'),
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

### 5.2 Caching Strategy

#### Multi-Level Caching
```python
# backend/api/cache.py
import redis
import json
from typing import Any, Optional
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 300  # 5 minutes

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            data = json.dumps(value)
            return self.redis.setex(key, ttl, data)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        return False

    async def delete(self, key: str) -> bool:
        """Delete from cache"""
        try:
            return self.redis.delete(key) > 0
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
        return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed: {e}")
        return 0

# Cache key patterns
CACHE_KEYS = {
    'lead': 'lead:{lead_id}',
    'contact': 'contact:{contact_id}',
    'deal': 'deal:{deal_id}',
    'user': 'user:{user_id}',
    'organization_leads': 'org:{org_id}:leads:{page}:{filters}',
    'ai_response': 'ai:{request_hash}',
    'analytics': 'analytics:{org_id}:{type}:{period}'
}

# Usage in API endpoints
@router.get("/leads/{lead_id}")
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    cache_key = CACHE_KEYS['lead'].format(lead_id=lead_id)

    # Try cache first
    cached_lead = await cache_manager.get(cache_key)
    if cached_lead:
        return {"success": True, "data": cached_lead}

    # Fetch from database
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "id": lead.id,
        "title": lead.title,
        "status": lead.status,
        "score": lead.score
    }

    # Cache for 10 minutes
    await cache_manager.set(cache_key, lead_data, ttl=600)

    return {"success": True, "data": lead_data}
```

### 5.3 CDN & Static Asset Optimization

#### Cloudflare Configuration
```javascript
// Cloudflare Worker for API optimization
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // API requests - add caching headers
  if (url.pathname.startsWith('/api/')) {
    // Static API responses (like options, constants)
    if (url.pathname.includes('/options') || url.pathname.includes('/constants')) {
      return fetch(request, {
        cf: {
          cacheTtl: 3600,  // Cache for 1 hour
          cacheEverything: true
        }
      })
    }

    // Dynamic API responses - add CORS and security headers
    const response = await fetch(request)
    const newResponse = new Response(response.body, response)

    // Add security headers
    newResponse.headers.set('X-Content-Type-Options', 'nosniff')
    newResponse.headers.set('X-Frame-Options', 'DENY')
    newResponse.headers.set('X-XSS-Protection', '1; mode=block')
    newResponse.headers.set('Strict-Transport-Security', 'max-age=31536000')

    return newResponse
  }

  // Static assets - optimize delivery
  if (url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|ico|svg)$/)) {
    return fetch(request, {
      cf: {
        cacheTtl: 86400,  // Cache for 24 hours
        cacheEverything: true,
        polish: 'lossy'   // Optimize images
      }
    })
  }

  return fetch(request)
}
```

## 6. Scaling & Capacity Planning

### 6.1 Auto-scaling Configuration

#### Railway Auto-scaling
```yaml
# railway-autoscale.yml
services:
  backend:
    minInstances: 2
    maxInstances: 10
    targetCPUUtilization: 70
    targetMemoryUtilization: 80
    scaleUpThreshold: 5  # minutes
    scaleDownThreshold: 10  # minutes

  database:
    plan: 'Business'  # Railway managed scaling
    maxConnections: 1000

  redis:
    plan: 'Business'  # Railway managed scaling
    maxMemory: '10GB'
```

### 6.2 Capacity Planning Metrics

#### User Load Projections
```python
# capacity_planning.py
def calculate_capacity_requirements():
    """Calculate infrastructure requirements based on user load"""

    # Current metrics
    current_users = 1000
    peak_concurrent_users = 200
    api_requests_per_user_per_day = 500
    average_response_time = 150  # ms

    # Growth projections
    monthly_growth_rate = 0.15  # 15% MoM growth
    months_projection = 12

    # Calculate future load
    future_users = current_users * (1 + monthly_growth_rate) ** months_projection
    future_peak_concurrent = peak_concurrent_users * (1 + monthly_growth_rate) ** months_projection
    future_api_requests = future_users * api_requests_per_user_per_day

    # Infrastructure requirements
    requests_per_second = future_api_requests / (30 * 24 * 60 * 60)  # RPS
    required_instances = math.ceil(requests_per_second / 1000)  # 1000 RPS per instance
    required_db_connections = required_instances * 10  # 10 connections per instance
    required_redis_memory = future_users * 0.1  # 100KB per user for cache

    return {
        'future_users': future_users,
        'peak_concurrent_users': future_peak_concurrent,
        'api_requests_per_second': requests_per_second,
        'required_backend_instances': required_instances,
        'required_db_connections': required_db_connections,
        'required_redis_memory_gb': required_redis_memory / (1024**3)
    }
```

This comprehensive deployment and operations documentation provides the complete technical foundation for running NeuraCRM in production, ensuring reliability, security, and scalability while maintaining operational excellence.