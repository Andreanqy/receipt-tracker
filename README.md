# Receipt Tracker

A Telegram bot that automatically tracks expenses by scanning receipt photos. Send a photo to the bot — the service extracts purchase details via [proverkacheka.com](https://proverkacheka.com), categorizes items using Claude AI, and stores everything in PostgreSQL. Request spending statistics for any period directly in the chat.

## Features

- Telegram bot as the primary interface (no web frontend)
- Receipt photo upload with automatic storage in MinIO
- Purchase details fetching from proverkacheka.com API
- Per-item expense breakdown with AI-powered categorization (Claude Haiku)
- Spending analytics by category and day
- Pie chart visualization with color-coded categories

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | FastAPI 0.136 |
| ORM | SQLAlchemy 2.0 (async) |
| DB driver | asyncpg |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | JWT (PyJWT, HS256) + bcrypt |
| Object storage | MinIO (S3-compatible, via aioboto3) |
| Task queue | Celery + Redis 7 |
| Bot framework | aiogram 3 |
| AI categorization | Anthropic Claude Haiku |
| Config | pydantic-settings (.env) |
| Package manager | Poetry |
| Container | Docker + Docker Compose |

## Project Structure

```
app/
├── api/
│   ├── auth.py        # /auth endpoints
│   ├── receipts.py    # /receipts endpoints
│   ├── analytics.py   # /analytics endpoints
│   └── deps.py        # JWT dependency
├── core/
│   └── security.py    # password hashing, JWT
├── crud/
│   ├── user.py
│   ├── receipt.py
│   └── analytics.py
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/
│   ├── s3.py          # MinIO client
│   └── categorization.py  # Anthropic API
├── tasks/
│   ├── celery_app.py
│   └── receipt.py     # receipt processing task
├── config.py
├── database.py
└── main.py
bot/
├── handlers/
│   ├── start.py       # /start — registration
│   ├── receipt.py     # photo upload
│   └── analytics.py   # /summary — statistics
├── services/
│   └── api.py         # HTTP client to FastAPI
└── main.py
migrations/
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd receipt-tracker
   ```

2. Create `.env` from the example:
   ```bash
   cp .env.example .env
   ```

3. Start all services:
   ```bash
   docker compose up --build
   ```

   On first startup the entrypoint automatically applies Alembic migrations.

## Bot Usage

1. Find the bot in Telegram and send `/start` — account is created automatically
2. Send a receipt photo (as a photo, not a file) — the bot confirms receipt and processes it in the background
3. When processing is complete, the bot sends a breakdown of items and total
4. Press **"Получить статистику"** or use `/summary` — choose a preset period or enter a custom date range

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Register a new user |
| `POST` | `/auth/login` | — | Login, returns JWT |
| `GET` | `/auth/me` | Bearer | Current user info |

### Receipts

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/receipts/upload` | Bearer | Upload receipt image |
| `GET` | `/receipts/{id}/image` | Bearer | Presigned URL for receipt photo |

### Analytics

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/analytics/summary` | Bearer | Spending summary for a period |

**Summary** `GET /analytics/summary?from=2026-01-01&to=2026-12-31`
```json
{
  "total_sum": "4250.00",
  "total_receipts": 12,
  "by_category": [
    {"category": "Продукты питания: бакалея", "sum": "1200.00"}
  ],
  "by_day": [
    {"date": "2026-01-15", "sum": "450.00"}
  ]
}
```

## Environment Variables

| Variable | Description |
|---|---|
| `POSTGRES_USER` | PostgreSQL user |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | Database name |
| `POSTGRES_HOST` | DB host (`db` inside Docker) |
| `POSTGRES_PORT` | DB port |
| `REDIS_HOST` | Redis host (`redis` inside Docker) |
| `REDIS_PORT` | Redis port |
| `MINIO_ROOT_USER` | MinIO access key |
| `MINIO_ROOT_PASSWORD` | MinIO secret key |
| `MINIO_ENDPOINT` | MinIO endpoint (`storage:9000` inside Docker) |
| `MINIO_BUCKET_NAME` | Bucket for receipt images |
| `SECRET_KEY` | JWT signing secret |
| `TELEGRAM_BOT_SECRET_KEY` | Telegram bot token |
| `API_URL` | Internal FastAPI URL (`http://web:8000` inside Docker) |
| `PROVERKACHEKA_TOKEN` | proverkacheka.com API token |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `ANTHROPIC_BASE_URL` | Optional Anthropic base URL (for resellers) |
| `USE_QR_FILE` | Send photo to proverkacheka instead of local QR parsing (`True`) |
| `DEBUG` | SQLAlchemy query logging (`False`) |

## Database Schema

```
users
├── id                UUID PK
├── email             VARCHAR(255) UNIQUE
├── hashed_password   VARCHAR(255)
├── telegram_chat_id  BIGINT UNIQUE
└── bot_token         VARCHAR(500)

receipts
├── id              UUID PK
├── user_id         UUID FK → users (CASCADE)
├── total_sum       NUMERIC(10,2)
├── operation_time  TIMESTAMP
├── qr_raw_data     VARCHAR(500)
├── filepath        VARCHAR(500)
└── status          ENUM(PROCESSING, COMPLETED, FAILED)

receipt_items
├── id          UUID PK
├── receipt_id  UUID FK → receipts (CASCADE)
├── name        VARCHAR(255)
├── price       NUMERIC(10,2)
├── quantity    NUMERIC(10,3)
├── sum         NUMERIC(10,2)
└── category    VARCHAR(100)
```

## Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```

## Infrastructure

| Service | Image | Port |
|---|---|---|
| `web` | local build | 8000 |
| `bot` | local build | — |
| `celery_worker` | local build | — |
| `db` | postgres:16-alpine | 5432 |
| `redis` | redis:7-alpine | 6379 |
| `storage` | minio/minio | 9000 / 9001 |
