# GuruSahaay

**Just-in-time classroom support for teachers** - A mobile-first web application supporting Kannada, Hindi, and English.

## Overview

GuruSahaay helps teachers get quick, actionable suggestions for classroom problems. Teachers can:
- Select predefined classroom problems
- Type questions in any supported language
- Speak questions using voice input
- Get suggestions from verified teacher content
- Upload helpful content for peers
- Earn points and rewards

## Architecture

```
gurusahaay/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── models/   # SQLAlchemy database models
│   │   ├── routes/   # API endpoints
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   └── services/ # Business logic
│   └── scripts/      # Database seeding
└── frontend/         # Next.js React frontend
    └── src/
        ├── app/      # Next.js App Router pages
        ├── components/
        ├── context/
        ├── hooks/
        └── lib/      # API client
```

## Core Design Principle

**Concept-based search, NOT raw text search.**

All user queries (in any language) are resolved to a canonical `concept_id` before searching for content. This enables multilingual search without vector embeddings.

```
User input → Detect language → Normalize → Match synonyms → Resolve concept_id → Query content
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
createdb gurusahaay

# Seed initial data
python -m scripts.seed_data

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Run development server
npm run dev
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Demo Credentials

- Phone: `9999999999`
- Password: `demo123`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Login with phone/password |
| `/auth/register` | POST | Register new teacher |
| `/auth/me` | GET | Get current user |
| `/concepts` | GET | List all concepts |
| `/help/request` | POST | Submit help request (text/voice) |
| `/suggestions` | GET | Get content for concept_id |
| `/content/upload` | POST | Upload new content |
| `/content/{id}/feedback` | POST | Add feedback |
| `/community/feed` | GET | Community content feed |
| `/points` | GET | Get points history |

## Content Resolution Strategy

1. **Primary**: Search verified internal content (teacher uploads)
2. **Fallback**: Unverified external content (with warning label)
3. **Never**: Open web search or AI-generated answers

## Supported Languages

- English (en)
- Kannada (kn) - ಕನ್ನಡ
- Hindi (hi) - हिंदी

## Tech Stack

### Backend
- FastAPI (Python)
- PostgreSQL + SQLAlchemy
- JWT Authentication
- Whisper (speech-to-text)

### Frontend
- Next.js 14 (App Router)
- React 18
- Tailwind CSS
- TypeScript

## License

MIT
