# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (Postgres client libs + build tools for wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install requirements (cache-friendly)
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

# Copy project files
COPY . .

# Ensure our venv is first on PATH
ENV PATH="/venv/bin:$PATH"

# Expose app port
EXPOSE 8811

# Run migrations, collectstatic, then start Gunicorn (ASGI worker)
# Replace "myproject" below with your actual settings module package.
CMD sh -c "python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput \
    && gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 3 --timeout 60"
