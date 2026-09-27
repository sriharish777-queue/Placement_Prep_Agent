# AI Placement Preparation & Career Copilot

An adaptive AI platform for personalized placement preparation. Upload your resume, analyze job descriptions, identify skill gaps, and follow a dynamically adapting preparation plan.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS + Framer Motion |
| Backend | FastAPI + Python 3.11 |
| Database | MongoDB (Motor async driver) |
| AI / LLM | OpenAI GPT-4o-mini + text-embedding-3-small |
| Vector DB | ChromaDB (local persistent) |
| Automation | n8n workflows |
| Container | Docker + Docker Compose |

## Features

- **Resume Intelligence** — AI parses PDF/DOCX resumes, extracts skills, projects, experience
- **Job Description Analysis** — Extract required skills and match against your resume
- **Skill Gap Engine** — Priority-ordered list of what to learn, with match percentage
- **Adaptive Preparation Plan** — 7/14/30-day daily plans that adjust based on your performance
- **AI Question Generator** — DSA, SQL, Java, Python, OOP, DBMS, OS, CN, Aptitude, System Design
- **Answer Evaluator** — Scores correctness, depth, communication, missing concepts
- **Mock Interview** — Technical, HR, Behavioral, System Design — with follow-up questions
- **RAG Career Assistant** — Semantic search over placement knowledge base
- **Placement Readiness Score** — Overall + per-topic scores with trend analysis
- **n8n Automation** — Daily reminders, weekly reports, adaptive replan triggers

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 2. Configure environment
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
```

### 3. Start all services
```bash
docker-compose up --build
```

### 4. Access the app
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| n8n | http://localhost:5678 |

### 5. Seed the RAG knowledge base
```
POST http://localhost:8000/api/v1/rag/seed
```
Or click "Seed Knowledge Base" in the AI Assistant page.

## Local Development (without Docker)

### Backend
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### MongoDB
```bash
# Run MongoDB locally or use MongoDB Atlas
# Set MONGODB_URL in backend/.env
```

## Workflow

```
Register → Upload Resume → Analyze Job Description
        ↓
    Skill Gap Analysis (match %, priority order)
        ↓
    Generate 30-Day Plan
        ↓
    Daily Practice (AI questions + evaluation)
        ↓
    Mock Interviews (adaptive follow-up)
        ↓
    Adaptive Engine adjusts next day's plan
        ↓
    Readiness Score improves
```

## API Reference

Full interactive docs: `http://localhost:8000/docs`

Key endpoints:
- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/resume/upload` — Upload PDF/DOCX resume
- `POST /api/v1/skill-gap/analyze` — Run skill gap analysis
- `POST /api/v1/plan/generate` — Generate preparation plan
- `POST /api/v1/questions/generate` — Generate practice questions
- `POST /api/v1/interview/start` — Start mock interview
- `GET  /api/v1/performance/readiness/{user_id}` — Get readiness score
- `POST /api/v1/rag/query` — Ask the RAG assistant
- `GET  /api/v1/dashboard/{user_id}` — Dashboard summary
