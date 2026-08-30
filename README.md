# Creda AI

Creda AI is a first-stage, defensive scam and phishing checker. Paste a message or URL and it returns a transparent risk score with the exact signals that contributed to it. It deliberately uses local heuristics only—no external APIs or keys.

## What is included

- FastAPI API and single-page dashboard
- Offline checks for urgency, sensitive-data requests, suspicious URLs, risky domains, look-alike domains, and link shorteners
- Explainable risk scoring (low, medium, high)
- Persistent scan history in PostgreSQL
- Docker Compose setup for the complete stack

## Run it with Docker

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:8000. PostgreSQL data is retained in the `postgres_data` Docker volume. Stop services with `docker compose down`.

## Run locally (optional)

The app defaults to SQLite if `DATABASE_URL` is not set, which is convenient for a quick local trial.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API

`POST /api/scans`

```json
{"content":"Your account will be suspended. Verify now: http://secure-login.xyz"}
```

`GET /api/scans` returns the latest saved checks. Interactive API documentation is available at `/docs`.

## Important note

This is a risk-assessment aid, not a guarantee that content is safe or fraudulent. Avoid entering passwords, OTPs, PINs, or financial data into unfamiliar links.

