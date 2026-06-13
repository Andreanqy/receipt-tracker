# Receipt Tracker

A backend service that automatically tracks expenses by scanning receipt QR codes. Upload a photo — the service extracts the QR code, fetches full purchase details (items, prices, store, date, total) from the [proverkacheka.com](https://proverkacheka.com) API, and stores everything in PostgreSQL.

## Features

- User registration and authentication (JWT)
- Receipt image upload with automatic storage in MinIO
- QR code extraction and parsing *(in progress)*
- Purchase details fetching from proverkacheka.com *(in progress)*
- Per-item expense breakdown *(in progress)*

## Tech Stack

- **Python 3.13** + **FastAPI**
- **PostgreSQL 16** — main database
- **SQLAlchemy 2.0** (async) + **Alembic** — ORM and migrations
- **MinIO** — S3-compatible object storage for receipt images
- **Redis** — planned for background task queue
- **JWT** (PyJWT) + **bcrypt** — authentication
- **Docker** + **Docker Compose** — containerized infrastructure
- **Poetry** — dependency management

## Project Structure

```
app/
├── api/           # Route handlers (auth, receipts) + dependencies
├── core/          # Security utilities (hashing, JWT)
├── crud/          # Database operations
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response schemas
├── services/      # External service clients (S3/MinIO)
├── config.py      # App settings via pydantic-settings
├── database.py    # Async engine and session factory
└── main.py        # FastAPI app entrypoint
migrations/        # Alembic migration versions
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
   Fill in `POSTGRES_PASSWORD` and `SECRET_KEY` with real values.

3. Start all services:
   ```bash
   docker compose up --build
   ```

   On first startup the entrypoint automatically applies Alembic migrations.

4. API is available at `http://localhost:8000`
   Interactive docs: `http://localhost:8000/docs`

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | — | Register a new user |
| `POST` | `/auth/login` | — | Login, returns JWT |
| `GET` | `/auth/me` | Bearer | Current user info |

**Register** `POST /auth/register`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Login** `POST /auth/login` — `application/x-www-form-urlencoded`
```
username=user@example.com&password=password123
```
Returns:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Receipts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/receipts/upload` | Bearer | Upload receipt image |

**Upload receipt** `POST /receipts/upload` — `multipart/form-data`

Field `file`: image file (JPEG, PNG, etc.)

Returns:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PROCESSING"
}
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `secret` |
| `POSTGRES_DB` | Database name | `receipt_tracker` |
| `POSTGRES_HOST` | DB host (use `db` inside Docker) | `db` |
| `POSTGRES_PORT` | DB port | `5432` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `MINIO_ROOT_USER` | MinIO access key | `admin` |
| `MINIO_ROOT_PASSWORD` | MinIO secret key | `password` |
| `MINIO_ENDPOINT` | MinIO endpoint (use `storage:9000` inside Docker) | `storage:9000` |
| `MINIO_BUCKET_NAME` | Bucket for receipt images | `receipts` |
| `SECRET_KEY` | JWT signing secret (use a long random string) | `change-me` |
| `DEBUG` | SQLAlchemy query logging | `False` |

## Database Schema

```
users
├── id            UUID PK
├── email         VARCHAR(255) UNIQUE
└── hashed_password VARCHAR(255)

receipts
├── id            UUID PK
├── user_id       UUID FK → users (CASCADE)
├── total_sum     NUMERIC(10,2)
├── created_at    TIMESTAMP
├── qr_raw_data   VARCHAR(500)
├── filepath      VARCHAR(500)
└── status        ENUM(PROCESSING, COMPLETED, FAILED)

receipt_items
├── id            UUID PK
├── receipt_id    UUID FK → receipts (CASCADE)
├── name          VARCHAR(255)
├── price         NUMERIC(10,2)
├── quantity      NUMERIC(10,3)
└── sum           NUMERIC(10,2)
```

## Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```

## Development

The `app/` and `migrations/` directories are mounted as volumes in Docker, so code changes are reflected without rebuilding the image. To enable hot reload, add `--reload` to the `uvicorn` command in `entrypoint.sh`.

MinIO console is available at `http://localhost:9001`.
