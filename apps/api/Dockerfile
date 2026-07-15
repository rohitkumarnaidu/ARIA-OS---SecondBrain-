# =============================================================================
# Second Brain OS — Backend (FastAPI + Uvicorn)
# Multi-stage: development (hot-reload) + production (optimized)
# Uses .dockerignore at project root for build context exclusion
# =============================================================================

# ── Labels ────────────────────────────────────────────────────────────────────
FROM scratch AS labels
LABEL org.opencontainers.image.title="Second Brain OS API"
LABEL org.opencontainers.image.description="FastAPI backend for the Second Brain OS personal AI productivity system"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Developer <developer@secondbrain-os.com>"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://secondbrain-os.com"
LABEL org.opencontainers.image.source="https://github.com/secondbrain-os/secondbrain"
LABEL org.opencontainers.image.vendor="Second Brain OS"

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

COPY --from=labels /dev/null /dev/null

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

CMD ["gunicorn", "apps.api.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000", "--timeout", "120", "--keep-alive", "5", "--max-requests", "1000", "--max-requests-jitter", "100"]

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
