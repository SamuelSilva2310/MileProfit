FROM python:3.12-slim

WORKDIR /app

# curl is needed for the Docker healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the app package is importable by alembic and uvicorn
ENV PYTHONPATH=/app

# SQLite data is mounted here at runtime
VOLUME ["/data"]

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && \
     uvicorn app.main:app \
       --host 0.0.0.0 \
       --port 8000 \
       --workers 2 \
       --proxy-headers \
       --forwarded-allow-ips='*'"]
