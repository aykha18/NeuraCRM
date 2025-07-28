# Smart CRM - Fullstack Web Application Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SMART CRM APPLICATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐              │
│  │   FRONTEND      │ ◄──────────────────► │    BACKEND      │              │
│  │  (React/TS)     │                      │  (FastAPI/Py)   │              │
│  └─────────────────┘                      └─────────────────┘              │
│           │                                         │                       │
│           │                                         │                       │
│  ┌─────────────────┐                      ┌─────────────────┐              │
│  │   BROWSER       │                      │   DATABASE      │              │
│  │  (Chrome/FF)    │                      │  (PostgreSQL)   │              │
│  └─────────────────┘                      └─────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📋 Technology Stack

### Frontend (Client-Side)
- **React 19.1.0** - UI Library (Component-based architecture)
- **TypeScript 5.8.3** - Type-safe JavaScript
- **Vite 7.0.4** - Build tool & development server
- **Tailwind CSS 3.4.1** - Utility-first CSS framework
- **React Router 7.7.0** - Client-side routing
- **Framer Motion 12.23.6** - Animation library
- **Recharts 3.1.0** - Data visualization charts
- **Lucide React 0.525.0** - Icon library

### Backend (Server-Side)
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **PostgreSQL** - Relational database
- **Alembic** - Database migration tool
- **Pydantic** - Data validation & serialization
- **Uvicorn** - ASGI server

### AI/ML Components
- **Ollama** - Local LLM server (Gemma3 model)
- **Custom AI Router** - CRM-specific AI assistant

## 🏛️ Application Architecture Layers

### 1. Presentation Layer (Frontend)
```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout (sidebar + topbar)
│   ├── Sidebar.tsx     # Navigation sidebar
│   ├── Topbar.tsx      # Header with user info
│   ├── ChatWindow.tsx  # Chat interface
│   ├── DetailModal.tsx # Modal for data details
│   └── MessageBubble.tsx # Chat message component
├── pages/              # Page components (routes)
│   ├── Dashboard.tsx   # Main dashboard
│   ├── Leads.tsx       # Lead management
│   ├── Contacts.tsx    # Contact management
│   ├── Kanban.tsx      # Kanban board
│   ├── Chat.tsx        # Real-time chat
│   └── Ai.tsx          # AI assistant
├── services/           # API communication layer
│   ├── contacts.ts     # Contact API calls
│   └── leads.ts        # Lead API calls
└── hooks/              # Custom React hooks
    └── useWebSocket.ts # WebSocket connection
```

### 2. Business Logic Layer (Backend)
```
backend/
├── api/
│   ├── main.py         # FastAPI application entry point
│   ├── db.py           # Database connection & session
│   ├── models.py       # SQLAlchemy ORM models
│   └── routers/        # API route handlers
│       ├── ai.py       # AI assistant endpoints
│       ├── dashboard.py # Dashboard data endpoints
│       └── kanban.py   # Kanban board endpoints
├── alembic/            # Database migrations
└── scripts/            # Utility scripts
```

### 3. Data Layer
```
Database Schema:
├── users              # User accounts & authentication
├── contacts           # Customer contact information
├── leads              # Sales leads
├── deals              # Sales opportunities
├── stages             # Deal pipeline stages
├── activities         # Deal activities & history
├── messages           # Chat messages
├── channels           # Chat channels
├── attachments        # File attachments
└── tags               # Deal categorization
```

## 🔄 Data Flow & Interactions

### 1. User Authentication Flow
```
Browser → React App → FastAPI → Database
   ↑                                    ↓
   └────────── JWT Token ←──────────────┘
```

### 2. CRUD Operations Flow
```
1. User Action (Click/Form Submit)
   ↓
2. React Component → API Service
   ↓
3. HTTP Request → FastAPI Router
   ↓
4. Business Logic → SQLAlchemy ORM
   ↓
5. SQL Query → PostgreSQL Database
   ↓
6. Response ← Database ← ORM ← Router ← Service ← Component
```

### 3. Real-time Communication
```
Browser ←→ WebSocket ←→ FastAPI ←→ Database
   ↑                                    ↓
   └────────── Real-time Updates ←──────┘
```

## 🎯 Key Components Explained

### Frontend Components (React)

#### 1. **Layout Component** (`Layout.tsx`)
- **Purpose**: Main application shell
- **Responsibilities**: 
  - Provides consistent layout across all pages
  - Manages sidebar and topbar positioning
  - Handles responsive design

#### 2. **Page Components** (Dashboard, Leads, Contacts, etc.)
- **Purpose**: Individual page views
- **Responsibilities**:
  - Fetch data from API services
  - Render page-specific UI
  - Handle user interactions

#### 3. **Service Layer** (`services/`)
- **Purpose**: API communication abstraction
- **Responsibilities**:
  - HTTP requests to backend
  - Data transformation
  - Error handling

### Backend Components (FastAPI)

#### 1. **Routers** (`api/routers/`)
- **Purpose**: API endpoint handlers
- **Responsibilities**:
  - Define HTTP routes (GET, POST, PUT, DELETE)
  - Handle request/response logic
  - Data validation with Pydantic

#### 2. **Models** (`api/models.py`)
- **Purpose**: Database schema definition
- **Responsibilities**:
  - SQLAlchemy ORM models
  - Database relationships
  - Data constraints

#### 3. **Database Layer** (`api/db.py`)
- **Purpose**: Database connection management
- **Responsibilities**:
  - Connection pooling
  - Session management
  - Transaction handling

## 🔧 Development Workflow (Traditional Software Dev Approach)

### Phase 1: Product Scope Definition
```
✅ Define CRM features:
   - Lead management
   - Contact management
   - Deal pipeline (Kanban)
   - Real-time chat
   - AI assistant
   - Dashboard analytics
```

### Phase 2: Technical Design
```
✅ Architecture Decisions:
   - Frontend: React + TypeScript + Tailwind
   - Backend: FastAPI + SQLAlchemy + PostgreSQL
   - Real-time: WebSocket connections
   - AI: Local Ollama integration
   - State Management: React Query + Local state
```

### Phase 3: Task Breakdown
```
📋 Development Tasks:
1. Database Schema Design
2. Backend API Development
3. Frontend Component Development
4. Real-time Features
5. AI Integration
6. Testing & Deployment
```

### Phase 4: Implementation Order
```
🚀 Development Sequence:
1. Set up project structure
2. Create database models
3. Implement basic CRUD APIs
4. Build frontend components
5. Add real-time features
6. Integrate AI assistant
7. Add analytics & dashboard
8. Testing & optimization
```

## 🔗 Key Interactions Between Components

### 1. **Frontend ↔ Backend Communication**
```typescript
// Frontend service call
const response = await fetch('/api/leads', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
});

// Backend route handler
@app.get("/api/leads")
def get_leads():
    db = SessionLocal()
    leads = db.query(Lead).all()
    return leads
```

### 2. **Database ↔ ORM ↔ API**
```python
# SQLAlchemy ORM query
leads = db.query(Lead).filter(Lead.owner_id == user_id).all()

# FastAPI response
return [LeadOut.from_orm(lead) for lead in leads]
```

### 3. **Real-time Updates**
```typescript
// WebSocket connection
const socket = new WebSocket('ws://localhost:8000/ws');

// Real-time data updates
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateUI(data);
};
```

## 🎨 UI/UX Architecture

### Component Hierarchy
```
App
├── Router
│   └── Layout
│       ├── Sidebar (Navigation)
│       ├── Topbar (User info)
│       └── Page Content
│           ├── Dashboard
│           ├── Leads
│           ├── Contacts
│           ├── Kanban
│           ├── Chat
│           └── AI Assistant
```

### State Management
```
Local State (useState) → Component-specific data
React Query → Server state & caching
Context API → Global app state
WebSocket → Real-time updates
```

## 🔒 Security & Performance

### Security Measures
- **CORS Configuration**: Cross-origin request handling
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Authentication**: JWT tokens (planned)

### Performance Optimizations
- **React Query**: Automatic caching & background updates
- **Code Splitting**: Lazy loading of components
- **Database Indexing**: Optimized queries
- **WebSocket**: Real-time without polling

## 📊 Database Design (Your Expertise Area)

### Entity Relationships
```
User (1) ←→ (Many) Leads
User (1) ←→ (Many) Contacts  
User (1) ←→ (Many) Deals
Contact (1) ←→ (Many) Leads
Contact (1) ←→ (Many) Deals
Deal (1) ←→ (Many) Activities
Deal (Many) ←→ (Many) Tags
```

### Key Tables & Purpose
- **users**: Authentication & user management
- **contacts**: Customer relationship data
- **leads**: Sales opportunity tracking
- **deals**: Revenue pipeline management
- **activities**: Audit trail & history
- **messages**: Real-time communication
- **stages**: Sales pipeline configuration

This architecture follows modern web development patterns while leveraging your database expertise. The separation of concerns makes it maintainable and scalable for future enhancements. 