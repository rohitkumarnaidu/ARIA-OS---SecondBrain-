# =============================================================================
# Second Brain OS — Frontend (Next.js 14)
# Multi-stage: development (hot-reload) + production (optimized)
# =============================================================================

# ── Labels ────────────────────────────────────────────────────────────────────
FROM scratch AS labels
LABEL org.opencontainers.image.title="Second Brain OS Frontend"
LABEL org.opencontainers.image.description="Next.js 14 frontend for the Second Brain OS personal AI productivity system"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Developer <developer@secondbrain-os.com>"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://secondbrain-os.com"
LABEL org.opencontainers.image.source="https://github.com/secondbrain-os/secondbrain"
LABEL org.opencontainers.image.vendor="Second Brain OS"

# ---- Stage 1: Production Dependencies (only runtime deps) ----
FROM node:26-alpine AS deps-prod
WORKDIR /app

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --omit=dev --legacy-peer-deps

# ---- Stage 2: Build Dependencies (including devDeps for build) ----
FROM node:26-alpine AS deps
WORKDIR /app

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --legacy-peer-deps

# ---- Stage 3: Build ----
FROM node:26-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY apps/web/ .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_PWA_ENABLED=true
RUN npm run build

# ---- Stage 4: Production ----
FROM node:26-alpine AS production
WORKDIR /app

COPY --from=labels /dev/null /dev/null

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/',(r)=>{process.exit(r.statusCode===200?0:1)}).on('error',()=>process.exit(1))"

CMD ["node", "server.js"]

# ---- Stage 5: Development (hot-reload) ----
FROM node:26-alpine AS development
WORKDIR /app

ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY apps/web/ .

EXPOSE 3000
CMD ["npm", "run", "dev"]
