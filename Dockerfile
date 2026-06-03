# STAGE 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python.org | python3 -

COPY pyproject.toml poetry.lock* ./

RUN poetry install --without dev --no-root

# STAGE 2: Final app image
FROM python:3.13-slim AS runner

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]