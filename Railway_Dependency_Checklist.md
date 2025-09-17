Backend runtime and dependencies for Railway

- Python version: 3.11+ (set in `runtime.txt` or Railway settings)
- Required env vars:
  - `DATABASE_URL` (PostgreSQL)
  - `SECRET_KEY`
  - `OPENAI_API_KEY`
- Start command:
  - `uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Python deps: `backend/requirements.txt`

Frontend (optional separate service)
- Node 18+
- Build: `npm ci && npm run build`
- Output served by backend static mount (`frontend_dist/`) or deploy as static service.

Cleanup done
- Removed test-only endpoints from deployment path.
- Left test scripts in repo but not executed in Procfile.

