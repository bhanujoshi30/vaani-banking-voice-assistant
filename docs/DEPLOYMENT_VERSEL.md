# Vercel Deployment Guide

## Overview

This document outlines the steps to deploy the backend and AI microservices to
Vercel using free-tier resources, with data hosted on Neon Postgres and the
frontend on Cloudflare Pages.

## Prerequisites

- GitHub repository connected to Vercel.
- Neon Postgres database (connection string with sslmode=require).
- OpenAI API key for AI service (Azure TTS disabled).
- Custom domain `sunnationalbank.online` managed in Cloudflare.

## Backend (FastAPI)

1. Create a new Vercel project from the root of the repo.
2. Set build command to `bash vercel-build.sh` (no output directory override needed).
3. The build script emits a Vercel Build Output bundle that ships only the FastAPI serverless function plus dependencies from `requirements-backend.txt`.
4. Configure environment variables:
   - `DB_BACKEND=postgresql`
   - `DATABASE_URL=<neon-url>`
   - `JWT_SECRET_KEY=<generated secret>`
   - `AI_BASE_URL=https://ai.sunnationalbank.online`
   - `CORS_ALLOWED_ORIGINS=https://sunnationalbank.online,https://www.sunnationalbank.online`
   - `VOICE_VERIFICATION_ENABLED=false` *(disables heavy Resemblyzer stack on Vercel)*
5. Deploy and test `/health` endpoint.
6. Map `api.sunnationalbank.online` CNAME to the Vercel deployment.

## AI Service

1. Create a separate Vercel project with root directory `ai/`.
2. Build command can remain default; dependencies resolved via `ai/requirements.txt`.
3. Configure environment variables:
   - `LLM_PROVIDER=openai`
   - `OPENAI_API_KEY=<openai key>`
   - `OPENAI_MODEL=gpt-4o-mini`
   - `CORS_ALLOWED_ORIGINS=https://sunnationalbank.online,https://www.sunnationalbank.online`
4. Deploy and verify `/health` returns `status=healthy`.
5. Map `ai.sunnationalbank.online` CNAME to the AI Vercel project.

## Frontend

1. Deploy React app via Cloudflare Pages (build command `npm run build`).
2. Set env vars:
   - `VITE_API_BASE_URL=https://api.sunnationalbank.online`
   - `VITE_AI_API_BASE_URL=https://ai.sunnationalbank.online`
3. Attach custom domain `sunnationalbank.online`.

## Checklist

- [ ] Neon database seeded using `python -m backend.db.seed`.
- [ ] CORS origins include production domains.
- [ ] Environment variables set in Vercel and Cloudflare.
- [ ] DNS records pointing to Vercel/Pages deployments.
- [ ] Smoke test login, chat, and guardrail flows post-deploy.
