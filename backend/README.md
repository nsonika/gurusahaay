# GuruSahaay Backend

FastAPI backend for the GuruSahaay teacher support platform.

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Setup PostgreSQL

```bash
# Create database
createdb gurusahaay

# Or using psql
psql -c "CREATE DATABASE gurusahaay;"
```

### 5. Seed initial data

```bash
python -m scripts.seed_data
```

### 6. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Credentials

- Phone: `9999999999`
- Password: `demo123`

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | Login with phone/password |
| `/auth/me` | GET | Get current user |
| `/concepts` | GET | List all concepts |
| `/help/request` | POST | Submit help request (text/voice) |
| `/suggestions` | GET | Get content for concept_id |
| `/content/upload` | POST | Upload new content |
| `/content/{id}/feedback` | POST | Add feedback |
| `/community/feed` | GET | Community content feed |
| `/points` | GET | Get points history |

## Architecture

### Concept-Based Search (CRITICAL)

This system uses **concept-based search**, NOT raw text search:

1. User input (Kannada/Hindi/English) → Detect language
2. Normalize text (strip suffixes)
3. Match against `CONCEPT_SYNONYMS` table
4. Resolve to canonical `concept_id`
5. Query content by `concept_id`

This enables multilingual search without vector embeddings.

### Content Resolution Order

1. **Internal verified content** (teacher uploads, verified)
2. **Any verified content** (including verified external)
3. **Unverified external content** (fallback, with warning)
