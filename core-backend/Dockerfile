# core-backend/Dockerfile
ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# system deps (psycopg2, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- deps ----
# kopieer alleen requirements voor betere cache-hits
COPY core-backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
 && python -m pip install -r requirements.txt

# ---- app ----
COPY core-backend /app

# Expose (alleen documentair)
EXPOSE 9000

# Healthcheck (optioneel; pas pad aan als je health endpoint anders heet)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://127.0.0.1:9000/healthz || exit 1

# Start uvicorn (pas module:app aan indien nodig)
# We gebruiken app.main:app zoals in je smoke-test wordt verwacht.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
