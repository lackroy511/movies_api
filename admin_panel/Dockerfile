FROM python:3.14-slim-trixie

USER root

WORKDIR /app

ENV UV_NO_DEV=1 \
    PATH="/app/.venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

RUN apt-get update && apt-get install -y gettext
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./.python-version ./.python-version
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
RUN uv sync

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py compilemessages -l en -l ru

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app/staticfiles /app/media

USER appuser