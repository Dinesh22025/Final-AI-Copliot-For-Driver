# 🚀 Driver AI Co-Pilot - Production Deployment Guide

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Production Build](#local-production-build)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Step-by-Step Deployment](#step-by-step-deployment)
5. [Domain & SSL Setup](#domain--ssl-setup)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 🔍 Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] Remove all debug/console logs
- [ ] Remove test credentials
- [ ] Set production environment variables
- [ ] Update API URLs to production
- [ ] Test all features locally
- [ ] Fix all Unicode/encoding issues
- [ ] Optimize cascade file loading
- [ ] Add error handling for all endpoints

### ✅ Security
- [ ] Change default JWT secret key
- [ ] Enable HTTPS/SSL
- [ ] Add rate limiting
- [ ] Sanitize user inputs
- [ ] Add CORS restrictions
- [ ] Secure database credentials
- [ ] Add authentication timeout

### ✅ Performance
- [ ] Optimize image processing
- [ ] Add caching where possible
- [ ] Compress frontend assets
- [ ] Minimize API calls
- [ ] Test with multiple users

---

## 🏗️ Local Production Build

### Step 1: Prepare Environment Files

Create `.env` files for production:

**Backend `.env`:**
```bash
# backend/.env
ENVIRONMENT=production
PORT=8000
JWT_SECRET=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./driver_monitor.db
CORS_ORIGINS=https://yourdomain.com
```

**Frontend `.env.production`:**
```bash
# frontend/.env.production
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

### Step 2: Build Frontend

```bash
cd frontend
npm run build
```

This creates `frontend/dist/` with optimized production files.

### Step 3: Test Production Build Locally

```bash
# Serve frontend build
cd frontend/dist
python -m http.server 3000

# Run backend in production mode
cd backend
python main.py
```

Test at: http://localhost:3000

---

## ☁️ Cloud Deployment Options

### Option 1: AWS (Recommended for Production)
**Best for:** Enterprise, scalability, full control

**Services:**
- EC2 (Backend)
- S3 + CloudFront (Frontend)
- RDS (Database - optional)
- Route 53 (DNS)
- Certificate Manager (SSL)

**Cost:** ~$20-50/month

### Option 2: Heroku (Easiest)
**Best for:** Quick deployment, beginners

**Services:**
- Heroku Dyno (Backend + Frontend)
- Heroku Postgres (Database - optional)

**Cost:** ~$7-25/month

### Option 3: DigitalOcean (Balanced)
**Best for:** Cost-effective, good performance

**Services:**
- Droplet (Backend + Frontend)
- Spaces (Static files)
- Managed Database (optional)

**Cost:** ~$12-30/month

### Option 4: Vercel + Railway (Modern)
**Best for:** Fast deployment, modern stack

**Services:**
- Vercel (Frontend)
- Railway (Backend)

**Cost:** ~$5-20/month

### Option 5: Render (Simple)
**Best for:** Simple deployment, free tier available

**Services:**
- Web Service (Backend)
- Static Site (Frontend)

**Cost:** Free tier available, ~$7-15/month for production

---

## 📦 Step-by-Step Deployment (Render - Recommended for Beginners)

### Why Render?
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy deployment from GitHub
- ✅ No credit card required for free tier
- ✅ Good for Python + React apps

### Step 1: Prepare Your Code

#### 1.1 Create `requirements.txt` (if not exists)
```bash
cd backend
pip freeze > requirements.txt
```

#### 1.2 Create `render.yaml` in project root
```yaml
services:
  # Backend Service
  - type: web
    name: driver-ai-backend
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: JWT_SECRET
        generateValue: true
      - key: ENVIRONMENT
        value: production

  # Frontend Service
  - type: web
    name: driver-ai-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build"
    staticPublishPath: frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

#### 1.3 Update Frontend API URL

**frontend/src/pages/api.js:**
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 
           (import.meta.env.DEV ? 'http://localhost:8000/api' : 'https://driver-ai-backend.onrender.com/api'),
})

export const setToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
    localStorage.setItem('token', token)
  } else {
    delete api.defaults.headers.common.Authorization
    localStorage.removeItem('token')
  }
}

const storedToken = localStorage.getItem('token')
if (storedToken) {
  setToken(storedToken)
}

export default api
```

#### 1.4 Update Backend CORS

**backend/main.py:**
```python
import os

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://driver-ai-frontend.onrender.com",  # Add your Render frontend URL
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.db
*.sqlite3

# Node
node_modules/
dist/
.env
.env.local
.env.production

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF

# Commit and push
git add .
git commit -m "Prepare for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/driver-ai-copilot.git
git push -u origin main
```

### Step 3: Deploy on Render

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect your repository**
5. **Configure Backend:**
   - Name: `driver-ai-backend`
   - Environment: `Python 3`
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: `Free` (or `Starter` for better performance)
6. **Add Environment Variables:**
   - `PYTHON_VERSION` = `3.11.0`
   - `JWT_SECRET` = (generate random string)
   - `ENVIRONMENT` = `production`
7. **Click "Create Web Service"**
8. **Wait for deployment** (5-10 minutes)
9. **Copy backend URL:** `https://driver-ai-backend.onrender.com`

10. **Deploy Frontend:**
    - Click "New +" → "Static Site"
    - Connect same repository
    - Build Command: `cd frontend && npm install && npm run build`
    - Publish Directory: `frontend/dist`
    - Add Environment Variable:
      - `VITE_API_URL` = `https://driver-ai-backend.onrender.com`
    - Click "Create Static Site"

11. **Your app is live!** 🎉
    - Frontend: `https://driver-ai-frontend.onrender.com`
    - Backend: `https://driver-ai-backend.onrender.com`

---

## 🌐 Alternative: Deploy on Heroku

### Step 1: Install Heroku CLI
```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Create Heroku Apps

```bash
# Login
heroku login

# Create backend app
heroku create driver-ai-backend

# Create frontend app (optional - can use Vercel instead)
heroku create driver-ai-frontend
```

### Step 3: Deploy Backend

```bash
cd backend

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
git init
heroku git:remote -a driver-ai-backend
git add .
git commit -m "Deploy backend"
git push heroku main

# Set environment variables
heroku config:set JWT_SECRET=your-secret-key
heroku config:set ENVIRONMENT=production
```

### Step 4: Deploy Frontend on Vercel

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts:
# - Project name: driver-ai-frontend
# - Framework: Vite
# - Build command: npm run build
# - Output directory: dist

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://driver-ai-backend.herokuapp.com
```

---

## 🔒 Domain & SSL Setup

### Option 1: Use Render's Free Domain
- Automatic HTTPS
- Format: `yourapp.onrender.com`
- No configuration needed

### Option 2: Custom Domain

#### Buy Domain (Namecheap, GoDaddy, etc.)
Cost: ~$10-15/year

#### Configure DNS:

**For Render:**
1. Go to Render Dashboard → Your Service → Settings
2. Click "Add Custom Domain"
3. Enter your domain: `www.yourdomain.com`
4. Add DNS records at your domain registrar:
   ```
   Type: CNAME
   Name: www
   Value: yourapp.onrender.com
   ```
5. Wait for DNS propagation (5-60 minutes)
6. Render automatically provisions SSL certificate

**For Heroku:**
```bash
heroku domains:add www.yourdomain.com
heroku certs:auto:enable
```

Then add DNS record:
```
Type: CNAME
Name: www
Value: yourapp.herokuapp.com
```

---

## 📊 Monitoring & Maintenance

### 1. Application Monitoring

**Render Dashboard:**
- View logs: Dashboard → Service → Logs
- Monitor metrics: CPU, Memory, Response time
- Set up alerts for downtime

**Add Logging:**
```python
# backend/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.post("/api/monitor/analyze")
async def analyze_frame(...):
    logger.info(f"Frame analysis requested by user {current_user['id']}")
    # ... rest of code
```

### 2. Error Tracking

**Add Sentry (Free tier available):**
```bash
pip install sentry-sdk
```

```python
# backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 3. Uptime Monitoring

**Use UptimeRobot (Free):**
1. Go to: https://uptimerobot.com
2. Add monitor for your backend URL
3. Get alerts via email/SMS if site goes down

### 4. Database Backups

**For SQLite on Render:**
```bash
# Add to backend/main.py
import shutil
from datetime import datetime

@app.get("/admin/backup")
async def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.db"
    shutil.copy2("driver_monitor.db", backup_file)
    return {"message": "Backup created", "file": backup_file}
```

---

## 🐛 Troubleshooting

### Issue 1: Backend Not Starting

**Check logs:**
```bash
# Render
Dashboard → Service → Logs

# Heroku
heroku logs --tail -a driver-ai-backend
```

**Common fixes:**
- Ensure `requirements.txt` is complete
- Check Python version compatibility
- Verify environment variables are set

### Issue 2: Frontend Can't Connect to Backend

**Check:**
1. CORS settings in backend
2. API URL in frontend is correct
3. Backend is actually running
4. HTTPS/HTTP mismatch

**Fix:**
```javascript
// frontend/src/pages/api.js
console.log('API URL:', import.meta.env.VITE_API_URL)
```

### Issue 3: Camera Not Working

**HTTPS Required:**
- Browsers require HTTPS for camera access
- Use Render/Heroku (automatic HTTPS)
- Or set up SSL certificate

### Issue 4: Cascade Files Not Loading

**Already fixed in code, but verify:**
```python
# backend/app/vision.py
# Uses temp directory with ASCII-only path
# Falls back to OpenCV built-in cascades
```

### Issue 5: Database Errors

**SQLite limitations:**
- Not ideal for multiple concurrent users
- Consider upgrading to PostgreSQL for production

**Upgrade to PostgreSQL:**
```bash
# Render: Add PostgreSQL database
# Update backend/main.py:
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./driver_monitor.db")
```

---

## 💰 Cost Breakdown

### Free Tier (Good for Testing)
- **Render Free:** Backend + Frontend
- **Cost:** $0/month
- **Limitations:** 
  - Sleeps after 15 min inactivity
  - 750 hours/month
  - Slower performance

### Starter Tier (Recommended)
- **Render Starter:** $7/month per service
- **Total:** ~$14/month (backend + frontend)
- **Benefits:**
  - Always on
  - Better performance
  - Custom domain
  - Automatic SSL

### Production Tier
- **Render Standard:** $25/month per service
- **PostgreSQL:** $7/month
- **Total:** ~$57/month
- **Benefits:**
  - High performance
  - Scalability
  - Priority support

---

## 🎯 Quick Start Commands

### Deploy Everything (After GitHub push)

**Render:**
1. Connect GitHub repo
2. Click "Deploy"
3. Done! ✅

**Heroku:**
```bash
# Backend
cd backend
heroku create driver-ai-backend
git push heroku main

# Frontend
cd frontend
vercel
```

---

## 📝 Post-Deployment Checklist

- [ ] Test all features on live site
- [ ] Verify camera access works (HTTPS)
- [ ] Test user registration/login
- [ ] Test drowsiness detection
- [ ] Check alert system works
- [ ] Verify database saves events
- [ ] Test on mobile devices
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Add custom domain (optional)
- [ ] Share with users! 🎉

---

## 🆘 Need Help?

### Resources:
- **Render Docs:** https://render.com/docs
- **Heroku Docs:** https://devcenter.heroku.com
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/

### Common Issues:
1. **Port binding:** Use `$PORT` environment variable
2. **File paths:** Use relative paths, not absolute
3. **Environment variables:** Set in platform dashboard
4. **CORS:** Add production URLs to allowed origins

---

## 🚀 You're Ready to Deploy!

Choose your platform and follow the steps above. Your Driver AI Co-Pilot will be live in 15-30 minutes! 🎉

**Recommended Path for Beginners:**
1. Push code to GitHub
2. Deploy on Render (free tier)
3. Test everything
4. Upgrade to paid tier if needed
5. Add custom domain later

Good luck! 🍀
