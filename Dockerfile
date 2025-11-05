# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

COPY . .

ENV PATH="/venv/bin:$PATH"
EXPOSE 8000

CMD sh -c "python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput \
    && gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 --workers 3 --timeout 60"
