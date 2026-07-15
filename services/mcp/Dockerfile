# =============================================================================
# Second Brain OS — MCP Server
# Multi-stage: development + production
# =============================================================================

# ── Labels ────────────────────────────────────────────────────────────────────
FROM scratch AS labels
LABEL org.opencontainers.image.title="Second Brain OS MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for ARIA OS — exposes tools, resources, and prompts to MCP-compatible clients"
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

COPY services/mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Builder ----
FROM python:3.10-slim AS builder
WORKDIR /app

COPY --from=deps /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

RUN python -m compileall services/mcp/ packages/

# ---- Stage 3: Production ----
FROM python:3.10-slim AS production
WORKDIR /app

COPY --from=labels /dev/null /dev/null

RUN addgroup --system --gid 1001 mcp && \
    adduser --system --uid 1001 mcp

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app/services/mcp ./services/mcp
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/prompts ./prompts

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio

USER mcp
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')" || exit 1

CMD ["python", "services/mcp/server.py"]

# ---- Stage 4: Development ----
FROM python:3.10-slim AS development
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY services/mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/packages
ENV PYTHONUNBUFFERED=1
ENV DEBUG=True
ENV MCP_TRANSPORT=sse

EXPOSE 8765

CMD ["python", "services/mcp/server.py"]
