# =============================================================================
# Second Brain OS — Backend (FastAPI + Uvicorn)
# Multi-stage: development (hot-reload) + production (optimized)
# =============================================================================

# ---- Stage 1: Dependencies ----
FROM python:3.10-slim AS deps
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Builder ----
FROM python:3.10-slim AS builder
WORKDIR /app

COPY --from=deps /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

RUN python -m compileall apps/api/ packages/

# ---- Stage 3: Production ----
FROM python:3.10-slim AS production
WORKDIR /app

RUN addgroup --system --gid 1001 fastapi && \
    adduser --system --uid 1001 fastapi

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/apps/api ./apps/api
COPY --from=builder /app/packages ./packages

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1

USER fastapi
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "10"]

# ---- Stage 4: Development (hot-reload) ----
FROM python:3.10-slim AS development
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1
ENV DEBUG=True

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
