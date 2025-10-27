# core-backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# system deps (psycopg2-binary hoeft geen build deps, maar uvloop/httptools/wheels ok op 3.11)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer cache
COPY core-backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy app code
COPY core-backend/ ./core-backend/
# Make package importable: add to PYTHONPATH
ENV PYTHONPATH="${APP_HOME}:${APP_HOME}/core-backend"

EXPOSE 9000

# default: uvicorn app.main:app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
