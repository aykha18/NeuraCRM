# Smart CRM - Detailed Component Interaction Diagram

## 🔄 Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BROWSER (Client-Side)                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   React App     │    │   React Router  │    │   Components    │    │   Services      │              │
│  │   (App.tsx)     │───►│   (Navigation)  │───►│   (UI Elements) │───►│   (API Calls)   │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│           │                       │                       │                       │                     │
│           │                       │                       │                       │                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   State Mgmt    │    │   Hooks         │    │   WebSocket     │    │   HTTP Client   │              │
│  │   (useState)    │    │   (Custom)      │    │   (Real-time)   │    │   (fetch/axios) │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│                                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP/WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND (Server-Side)                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   FastAPI App   │    │   CORS Middleware│    │   Routers       │    │   Pydantic      │              │
│  │   (main.py)     │───►│   (Security)    │───►│   (Endpoints)   │───►│   (Validation)  │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│           │                       │                       │                       │                     │
│           │                       │                       │                       │                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   AI Router     │    │   Dashboard     │    │   Kanban Router │    │   Database      │              │
│  │   (Ollama)      │    │   Router        │    │   (Deals)       │    │   (Session)     │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│                                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                    │ SQLAlchemy ORM
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATABASE (PostgreSQL)                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   Users Table   │    │   Contacts      │    │   Leads Table   │    │   Deals Table   │              │
│  │   (Auth)        │    │   Table         │    │   (Opportunities│    │   (Pipeline)    │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│           │                       │                       │                       │                     │
│           │                       │                       │                       │                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐              │
│  │   Activities    │    │   Messages      │    │   Stages Table  │    │   Tags Table    │              │
│  │   (History)     │    │   (Chat)        │    │   (Pipeline)    │    │   (Categories)  │              │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘              │
│                                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Component Interaction Details

### 1. **User Journey: Viewing Leads**

```
User clicks "Leads" in Sidebar
         │
         ▼
┌─────────────────┐
│   Leads.tsx     │ ← Page Component
│   (useState)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  leads.ts       │ ← Service Layer
│  (API call)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  /api/leads     │ ← FastAPI Router
│  (GET endpoint) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  SQLAlchemy     │ ← ORM Query
│  db.query(Lead) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │ ← Database
│  SELECT * FROM  │
│  leads          │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  JSON Response  │ ← Data flows back up
│  (Lead list)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  React renders  │ ← UI Update
│  Lead table     │
└─────────────────┘
```

### 2. **Real-time Chat Flow**

```
User types message
         │
         ▼
┌─────────────────┐
│  Chat.tsx       │ ← Chat Component
│  (useState)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  useWebSocket   │ ← WebSocket Hook
│  (send message) │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  WebSocket      │ ← Real-time connection
│  (ws://...)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │ ← WebSocket handler
│  (WebSocket)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Database       │ ← Store message
│  (INSERT)       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Broadcast      │ ← Send to all users
│  (WebSocket)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Other users    │ ← Real-time update
│  receive msg    │
└─────────────────┘
```

### 3. **AI Assistant Flow**

```
User asks AI question
         │
         ▼
┌─────────────────┐
│  Ai.tsx         │ ← AI Page Component
│  (useState)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  ai.ts          │ ← AI Service
│  (API call)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  /api/ai/       │ ← AI Router
│  assistant      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  CRM Context    │ ← Get user data
│  (Database)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Ollama API     │ ← Local LLM
│  (Gemma3)       │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  AI Response    │ ← Processed answer
│  (JSON)         │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  React renders  │ ← Display answer
│  AI response    │
└─────────────────┘
```

## 🔧 Development Tasks Breakdown

### **Phase 1: Foundation (Week 1-2)**
```
✅ Database Setup
   ├── PostgreSQL installation
   ├── Schema design
   ├── Alembic migrations
   └── Sample data

✅ Backend Foundation
   ├── FastAPI app setup
   ├── Database connection
   ├── Basic CRUD operations
   └── CORS configuration
```

### **Phase 2: Core Features (Week 3-4)**
```
✅ Frontend Foundation
   ├── React app setup
   ├── Routing configuration
   ├── Basic components
   └── API integration

✅ Lead Management
   ├── Lead CRUD operations
   ├── Lead listing page
   ├── Lead detail modal
   └── Lead form validation
```

### **Phase 3: Advanced Features (Week 5-6)**
```
✅ Contact Management
   ├── Contact CRUD operations
   ├── Contact listing page
   ├── Contact-Lead relationships
   └── Contact search/filter

✅ Kanban Board
   ├── Deal pipeline stages
   ├── Drag & drop functionality
   ├── Deal status updates
   └── Visual pipeline management
```

### **Phase 4: Real-time & AI (Week 7-8)**
```
✅ Real-time Chat
   ├── WebSocket setup
   ├── Chat interface
   ├── Message persistence
   └── Real-time updates

✅ AI Assistant
   ├── Ollama integration
   ├── CRM context injection
   ├── AI chat interface
   └── Response processing
```

### **Phase 5: Polish & Deploy (Week 9-10)**
```
✅ Dashboard & Analytics
   ├── Data visualization
   ├── Charts and graphs
   ├── Performance metrics
   └── User activity tracking

✅ Testing & Deployment
   ├── Unit testing
   ├── Integration testing
   ├── Performance optimization
   └── Production deployment
```

## 🎨 Frontend Component Architecture

```
App.tsx (Root)
├── Router
│   └── Layout.tsx (Main Layout)
│       ├── Sidebar.tsx (Navigation)
│       │   ├── NavItem (Dashboard)
│       │   ├── NavItem (Leads)
│       │   ├── NavItem (Contacts)
│       │   ├── NavItem (Kanban)
│       │   ├── NavItem (Chat)
│       │   └── NavItem (AI)
│       │
│       ├── Topbar.tsx (Header)
│       │   ├── UserInfo
│       │   ├── Notifications
│       │   └── Settings
│       │
│       └── Page Content (Routes)
│           ├── Dashboard.tsx
│           │   ├── StatsCards
│           │   ├── Charts
│           │   └── RecentActivity
│           │
│           ├── Leads.tsx
│           │   ├── LeadTable
│           │   ├── LeadFilters
│           │   ├── LeadForm
│           │   └── DetailModal
│           │
│           ├── Contacts.tsx
│           │   ├── ContactTable
│           │   ├── ContactFilters
│           │   ├── ContactForm
│           │   └── DetailModal
│           │
│           ├── Kanban.tsx
│           │   ├── KanbanBoard
│           │   ├── StageColumn
│           │   ├── DealCard
│           │   └── DragDrop
│           │
│           ├── Chat.tsx
│           │   ├── ChatWindow
│           │   ├── MessageList
│           │   ├── MessageInput
│           │   └── MessageBubble
│           │
│           └── Ai.tsx
│               ├── ChatInterface
│               ├── AIResponse
│               ├── ContextInfo
│               └── Settings
```

## 🔄 State Management Flow

```
Global State (Context)
├── User Authentication
├── Current User Info
├── App Settings
└── Theme Preferences

Server State (React Query)
├── Leads Data
├── Contacts Data
├── Deals Data
├── Messages Data
└── Analytics Data

Local State (useState)
├── Form Data
├── UI State (modals, loading)
├── Filters & Search
└── Component-specific data

Real-time State (WebSocket)
├── Live Messages
├── Deal Updates
├── User Status
└── Notifications
```

This detailed architecture shows how your database expertise translates to web development, with clear separation between data layer, business logic, and presentation layer. 