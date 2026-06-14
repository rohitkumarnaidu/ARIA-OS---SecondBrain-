# Deployment Guide

## Overview

Deploy both frontend and backend with free tier services.

---

## Prerequisites

- [ ] GitHub account
- [ ] Supabase account
- [ ] Vercel account
- [ ] Node.js 18+
- [ ] Python 3.10+

---

## Step 1: Supabase Setup

### Create Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note down:
   - Project URL
   - `anon` public key
   - `service_role` secret key

### Run SQL Schema
1. Open Supabase SQL Editor
2. Copy contents from `docs/Database.md`
3. Run all CREATE TABLE statements
4. Run RLS policies
5. Run INDEX statements

### Enable Auth
1. Go to Authentication > Providers
2. Enable Google provider
3. Add OAuth credentials from Google Cloud Console

---

## Step 2: Backend Deployment (Render/Railway)

### Option A: Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.10
6. Add Environment Variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `JWT_SECRET`
   - `OLLAMA_BASE_URL`
   - `USE_LOCAL_AI`
   - `CLAUDE_API_KEY` (optional)

### Option B: Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project from GitHub
4. Add environment variables in Railway dashboard

---

## Step 3: Frontend Deployment (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repo
3. Settings:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. Add Environment Variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
5. Deploy

### Automatic Deployments
- Every push to main triggers deployment
- Deploys in ~2 minutes

---

## Step 4: Ollama Setup (Local AI)

### Installation
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from ollama.com
```

### Start Server
```bash
ollama serve
```

### Pull Model
```bash
ollama pull llama3.1
```

### Configure Backend
Set in backend .env:
```
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=true
```

---

## Step 5: Browser Extension (WXT)

### Development
```bash
cd extension
npm install
npm run dev
```

### Build
```bash
npm run build
```

### Load in Browser
1. Go to chrome://extensions
2. Enable Developer Mode
3. Load unpacked from `extension/dist`

---

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| SUPABASE_URL | Yes | Supabase project URL |
| SUPABASE_KEY | Yes | Supabase anon key |
| SUPABASE_SERVICE_KEY | Yes | Supabase service role key |
| JWT_SECRET | Yes | Random string for JWT |
| CLAUDE_API_KEY | No | Anthropic API key |
| OLLAMA_BASE_URL | Yes | Local Ollama URL |
| USE_LOCAL_AI | Yes | Set to "true" |
| BRAVE_API_KEY | No | Brave Search API |
| RESEND_API_KEY | No | Resend email API |
| TWILIO_SID | No | Twilio SID |
| TWILIO_TOKEN | No | Twilio token |
| TWILIO_PHONE | No | Twilio phone number |

### Frontend (.env.local)
| Variable | Required | Description |
|----------|----------|-------------|
| NEXT_PUBLIC_SUPABASE_URL | Yes | Supabase project URL |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | Yes | Supabase anon key |

---

## Verify Deployment

### Backend Health Check
```
GET https://your-backend-url.com/health
Response: {"status": "healthy"}
```

### Frontend
1. Visit your Vercel URL
2. Login with Google
3. Create a task
4. Check Supabase for data

### PWA Installation
1. Visit on mobile
2. Add to Home Screen
3. Test offline mode

---

## Cost Breakdown

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Supabase | 500MB DB | Rs. 0 |
| Vercel | 100GB bandwidth | Rs. 0 |
| Render | 750 hours | Rs. 0 |
| Ollama | Local | Rs. 0 |
| Resend | 3,000 emails | Rs. 0 |

**Total: Rs. 0/month**

---

## Troubleshooting

### CORS Errors
- Add your domain to backend CORS settings

### RLS Errors
- Check Supabase dashboard for RLS violations
- Ensure user_id matches auth.uid()

### Build Failures
- Check build logs in Vercel/Render
- Ensure all env vars are set

### Empty Responses
- Check Supabase query logs
- Verify table has data

---

## Launch Checklist

- [ ] Supabase project created and configured
- [ ] All 21 tables created with RLS
- [ ] Google OAuth working
- [ ] Backend deployed and responding
- [ ] Frontend deployed and accessible
- [ ] Ollama running locally (or Claude API configured)
- [ ] Browser extension can save items
- [ ] PWA installable
- [ ] Data syncing correctly
- [ ] HTTPS working (green lock)
