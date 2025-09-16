FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_CREATE=false

RUN python3 -m pip install -U pip && pip install poetry

COPY pyproject.toml ./

RUN poetry install --no-interaction --no-ansi --no-root --only main && \
    rm -rf $POETRY_CACHE_DIR && \
    apt-get remove -y curl

COPY app ./app/
COPY alembic ./alembic/
COPY alembic.ini alembic.ini

EXPOSE 8000