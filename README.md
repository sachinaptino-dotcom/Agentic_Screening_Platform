# Local ATS

Local-only AI-powered ATS with FastAPI, PostgreSQL, FAISS, LangGraph, and Next.js.

## Run locally

1. Create DB:
   - `createdb ats_db`
2. Backend:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `alembic upgrade head`
   - `python seed.py`
   - `uvicorn main:app --reload --port 8000`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`
