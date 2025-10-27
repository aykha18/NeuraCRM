# CRM MVP with AI Assistant – Product Requirements Document (PRD)

**Version**: 1.0  
**Tech Stack**: React (TypeScript), TailwindCSS, FastAPI, PostgreSQL, OpenAI API

---

## 🎯 Goal

Build a modern CRM MVP that replicates Bitrix24’s essential features and adds a unique edge using AI:

- 🔹 AI Sales Assistant
- 🔹 AI-Powered Daily Digest

---

## 🧱 Features Breakdown (Phase 1 - MVP)

### 1. CRM Core

| Feature | Description |
|--------|-------------|
| Lead Management | Create/read/update/delete leads |
| Contact Management | Store unified contact cards |
| Deal Pipeline | Kanban-style movement of deals |
| Dashboard | Display key metrics like leads, deals |
| Chat (Internal) | Real-time team communication |

### 2. AI Features

| Feature | Description |
|--------|-------------|
| Sales Assistant | GPT-4 powered assistant to suggest responses and summarize lead context |
| Daily Digest | AI-generated summary of tasks, leads, and follow-ups |

---

## 📁 Folder Structure

```
crm_ai_react_boilerplate/
├── frontend/ (React SPA)
├── backend/
│   ├── api/ (FastAPI app)
│   └── ai/ (GPT, Whisper integrations)
├── odoo_addons/ (optional if using Odoo later)
```

---

## 📋 Step-by-Step Implementation Tasks (Optimized for Cursor)

### ✅ Step 1: Frontend Skeleton

- Setup routing with React Router in `App.tsx`
- Create pages: `Dashboard`, `Leads`, `Contacts`, `Kanban`, `Chat`
- Create layout with sidebar/topbar using TailwindCSS

---

### ✅ Step 2: UI Components

- `KanbanBoard.tsx`: Drag-and-drop deal pipeline
- `ChatWindow.tsx`: Messaging UI
- `LeadList.tsx`: Lead table with actions
- `ContactCard.tsx`: Display contact info

---

### ✅ Step 3: Backend API (FastAPI)

- Routes:
  - `GET/POST /leads`
  - `GET/POST /contacts`
  - `POST /chat/`
  - `POST /digest/`
- Use Pydantic models
- Use PostgreSQL

---

### ✅ Step 4: Connect Frontend ↔ API

- `services/api.ts`: Axios or fetch
- Bind UI to API using React hooks
- Use SWR or React Query optionally

---

### ✅ Step 5: AI Sales Assistant

- Backend: `ai/sales_assistant.py`
  - `summarize_lead(notes)`
  - `suggest_response(context)`
- Route: `POST /ai/suggest_response`
- Frontend: `SalesAssistant.tsx` UI component

---

### ✅ Step 6: Daily Digest

- Backend: `ai/digest.py`
  - Summarize leads due, overdue, and high-priority deals
- Endpoint: `GET /digest/:user_id`
- Optional: Schedule via cron/APScheduler
- Frontend: Show on dashboard

---

### ✅ Step 7: Real-Time Chat (Optional)

- WebSocket with FastAPI or Socket.io
- `useEffect` in React to subscribe/send messages

---

### ✅ Step 8: Styling & UX

- Use Tailwind UI or ShadCN components
- Add icons (Lucide, HeroIcons)
- Mobile-first design polish

---

### ✅ Step 9: Deployment

- `docker-compose.yml`:
  - React (Nginx)
  - FastAPI (Uvicorn)
  - PostgreSQL
- Optional: deploy to Render, Railway, or EC2

---

## 🧠 AI Prompt Examples

### Sales Assistant Prompt

```
You are a CRM Sales Assistant. Summarize this lead’s notes and recommend a next action. Notes: [text]
```

### Daily Digest Prompt

```
Generate a morning briefing for the sales rep. Include pending follow-ups, hot leads, and new assignments.
```

---

## 🛠 Recommended Dev Tools

| Task | Tool |
|------|------|
| Code generation | Cursor Copilot |
| Refactoring | Cursor AI |
| Search | Bloop |
| Docs | Swagger UI (/docs in FastAPI) |
| Component preview | Vite + Tailwind UI or Storybook |
