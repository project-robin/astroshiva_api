# 🚀 Quick Start: Deploy Astro-Shiva

## What We've Built

✅ **FastAPI Backend** - High-performance Python API
✅ **Hybrid Deployment** - Backend on Render, Frontend on Vercel  
✅ **No Filesystem Issues** - Solved the read-only error
✅ **Automatic API Docs** - Interactive docs at `/docs`

---

## Deploy in 3 Steps

### Step 1: Push to GitHub (2 minutes)

```bash
cd "d:\building apps\astro-shiva 2.0\12astro"
git add .
git commit -m "Add FastAPI backend configuration"
git push origin main
```

### Step 2: Deploy Backend to Render (5 minutes)

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Click **"Create Web Service"** (auto-detects `render.yaml`)
5. Wait ~3-5 minutes for deployment
6. **Copy your API URL**: `https://YOUR-APP.onrender.com`

### Step 3: Update & Deploy Frontend (3 minutes)

Update API URL in your frontend code:
```javascript
const API_URL = 'https://YOUR-APP.onrender.com';
```

Then deploy to Vercel:
```bash
vercel --prod
```

---

## Test Your Deployment

### Quick Test (Browser)

Open in browser:
```
https://YOUR-APP.onrender.com/docs
```

Try the test endpoint:
```
https://YOUR-APP.onrender.com/api/chart-test
```

### Full Test (Postman/curl)

```bash
curl -X POST https://YOUR-APP.onrender.com/api/chart \
  -H "Content-Type: application/json" \
  -d '{
    "name": "K",
    "dob": "2001-05-26",
    "tob": "21:48:00",
    "place": "Ahmednagar, Maharashtra",
    "latitude": 19.0948,
    "longitude": 74.7489,
    "timezone": "+5.5"
  }'
```

---

## Your New API Endpoints

| Endpoint | What it does |
|----------|--------------|
| `/` | API info |
| `/health` | Health check |
| `/docs` | **Interactive API documentation** 🎯 |
| `/api/chart` | Generate chart (POST) |
| `/api/chart-test` | Test with sample data |

---

## ⚡ Key Features

- **Automatic API Docs** - Test endpoints in browser
- **CORS Pre-configured** - Works with Vercel out of the box
- **Auto-deploy** - Every git push updates your API
- **Free Tier** - Both Render and Vercel have free plans
- **Fast Performance** - Async FastAPI + Vercel edge network

---

## 📚 Documentation

- **Detailed Guide**: [HYBRID_DEPLOYMENT.md](file:///C:/Users/user/.gemini/antigravity/brain/32e28027-73ba-4af8-a5d3-8b4ccee6b9cb/HYBRID_DEPLOYMENT.md)
- **Walkthrough**: [walkthrough.md](file:///C:/Users/user/.gemini/antigravity/brain/32e28027-73ba-4af8-a5d3-8b4ccee6b9cb/walkthrough.md)
- **Task Checklist**: [task.md](file:///C:/Users/user/.gemini/antigravity/brain/32e28027-73ba-4af8-a5d3-8b4ccee6b9cb/task.md)

---

## 🐛 Troubleshooting

**First request is slow?**  
→ Cold start + downloading ephemeris files (~60s first time, then <5s)

**CORS errors?**  
→ Backend has wildcard CORS enabled, should work automatically

**404 errors?**  
→ Check Render logs, ensure service is running

---

## Next Steps

1. [ ] Deploy backend to Render
2. [ ] Test `/docs` endpoint
3. [ ] Update frontend with backend URL
4. [ ] Deploy frontend to Vercel
5. [ ] Test full chart generation

**Need help?** Check the detailed guides in the artifacts.

---

**You're ready to go! 🎉**
