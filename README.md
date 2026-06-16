# SnipURL

Production-grade URL shortener built for **backend / system design interview prep**.

Phase 1: create short URL, store in PostgreSQL, redirect. ✅

Phase 2: Dockerize app + PostgreSQL with docker-compose. ✅

Phase 3: Redis cache-aside on redirect hot path. ✅

Phase 4: Kafka async click analytics (producer on redirect + consumer worker).

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

## Quick start

### 1. Create PostgreSQL database

```sql
CREATE USER snipurl WITH PASSWORD 'snipurl';
CREATE DATABASE snipurl OWNER snipurl;
```

### 2. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

### 6. Try it

- API docs: http://localhost:8000/docs
- Create URL: `POST /api/v1/urls` with body `{"url": "https://example.com"}`
- Redirect: `GET /{short_code}`

## Project structure

```
app/
├── main.py          # App entry point
├── config.py        # Environment settings
├── api/             # HTTP layer (routes only)
├── services/        # Business logic
├── models/          # Database tables (SQLAlchemy)
├── schemas/         # API contracts (Pydantic)
└── db/              # Connection + sessions
```

## Interview study guide

After running the app, practice explaining:

1. What happens when someone hits `POST /api/v1/urls`?
2. What happens when someone hits `GET /abc123`?
3. Why PostgreSQL over MongoDB here?
4. Why 302 redirect instead of 301?
5. How would you scale reads at 10x traffic?
