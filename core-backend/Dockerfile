# core-backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1) requirements (relatief aan de build context = core-backend/)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 2) applicatiecode (relatief aan core-backend/)
COPY app ./app

EXPOSE 9000
# cmd laten we aan docker-compose.ci.yml
