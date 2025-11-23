# Vercel Deployment Quick Reference

## 🎯 Quick Steps

### Backend Deployment
1. **Settings** → **General** → Verify Root Directory (root)
2. **Settings** → **Environment Variables** → Add:
   ```
   DB_BACKEND=postgresql
   DATABASE_URL=your-postgresql-url
   ```
3. **Deployments** → **Redeploy**

### Frontend Deployment
1. **Settings** → **General** → Verify Root Directory (`frontend`)
2. **Settings** → **Environment Variables** → Add:
   ```
   VITE_API_BASE_URL=https://your-backend.vercel.app
   VITE_AI_BACKEND_URL=https://your-ai-backend.vercel.app
   VITE_AI_API_BASE_URL=https://your-ai-backend.vercel.app
   ```
3. **Deployments** → **Redeploy**

---

## 📋 Environment Variables

### Backend (Required)
```
DB_BACKEND=postgresql
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Frontend (Required)
```
VITE_API_BASE_URL=https://your-backend-project.vercel.app
VITE_AI_BACKEND_URL=https://your-ai-backend-project.vercel.app
VITE_AI_API_BASE_URL=https://your-ai-backend-project.vercel.app
```

---

## 🔍 Where to Find URLs

1. Go to your project → **Deployments**
2. Click on latest deployment
3. Copy the URL shown (e.g., `https://project-name.vercel.app`)

---

## ⚠️ Important Notes

- **Frontend variables MUST start with `VITE_`**
- **Redeploy after adding/changing environment variables**
- **Use PostgreSQL for production** (not SQLite)
- **Get free PostgreSQL from**: Supabase, Neon, Railway, or Render

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| CORS errors | Check backend URL in frontend env vars |
| Build fails | Check `pyproject.toml` exists |
| Env vars not working | Redeploy after adding variables |
| 404 errors | Verify backend URL is correct |

---

## 📚 Full Guide

See `VERCEL_DEPLOYMENT_STEPS.md` for detailed instructions.

