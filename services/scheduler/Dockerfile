# =============================================================================
# Second Brain OS — Scheduler (APScheduler)
# Multi-stage: development + production
# =============================================================================

# ---- Stage 1: Dependencies ----
FROM python:3.10-slim AS deps
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
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

RUN addgroup --system --gid 1001 scheduler && \
    adduser --system --uid 1001 scheduler

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/services/scheduler ./services/scheduler
COPY --from=builder /app/packages ./packages

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1

USER scheduler

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

CMD ["python", "services/scheduler/main.py"]
