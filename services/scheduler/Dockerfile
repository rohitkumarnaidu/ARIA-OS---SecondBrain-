# =============================================================================
# Second Brain OS — Scheduler (APScheduler)
# Multi-stage: development + production
# =============================================================================

# ── Labels ────────────────────────────────────────────────────────────────────
FROM scratch AS labels
LABEL org.opencontainers.image.title="Second Brain OS Scheduler"
LABEL org.opencontainers.image.description="APScheduler cron job service for Second Brain OS — manages briefings, reminders, health checks"
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

COPY services/scheduler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Builder ----
FROM python:3.10-slim AS builder
WORKDIR /app

COPY --from=deps /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

RUN python -m compileall services/scheduler/ packages/

# ---- Stage 3: Production ----
FROM python:3.10-slim AS production
WORKDIR /app

COPY --from=labels /dev/null /dev/null

RUN addgroup --system --gid 1001 scheduler && \
    adduser --system --uid 1001 scheduler

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/services/scheduler ./services/scheduler
COPY --from=builder /app/packages ./packages

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1

USER scheduler
EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["python", "services/scheduler/main.py"]

# ---- Stage 4: Development ----
FROM python:3.10-slim AS development
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY services/scheduler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1
ENV DEBUG=True

EXPOSE 8001

CMD ["python", "services/scheduler/main.py"]
