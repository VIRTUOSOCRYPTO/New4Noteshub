# NotesHub - Render Deployment Guide

Complete step-by-step guide to deploy your NotesHub application to Render.

---

## 📋 Prerequisites

1. ✅ GitHub account
2. ✅ Render account (sign up at https://render.com - free tier available)
3. ✅ MongoDB Atlas account (we'll set this up together)

---

## Part 1: MongoDB Atlas Setup (Free Tier)

### Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up with Google/GitHub or email
3. Choose the **FREE tier** (M0 Sandbox - 512MB storage)

### Step 2: Create a Cluster

1. After login, click **"Build a Database"**
2. Choose **"M0 FREE"** tier
3. Select a cloud provider and region closest to you:
   - **AWS** → **us-west-2 (Oregon)** (same region as Render Oregon)
4. Cluster Name: `NotesHub` (or any name you prefer)
5. Click **"Create"**

### Step 3: Create Database User

1. In the Security Quickstart:
   - **Username**: `noteshub_user` (or your choice)
   - **Password**: Click "Autogenerate Secure Password" and **SAVE IT**
   - Or create your own strong password
2. Click **"Create User"**

### Step 4: Configure Network Access

1. In "Where would you like to connect from?":
   - Click **"Add My Current IP Address"**
   - **IMPORTANT**: Also add `0.0.0.0/0` to allow Render to connect
     - Click "Add a Different IP Address"
     - Enter: `0.0.0.0/0`
     - Description: `Render Access`
2. Click **"Finish and Close"**

### Step 5: Get Connection String

1. Click **"Connect"** on your cluster
2. Choose **"Connect your application"**
3. Driver: **Python**, Version: **3.11 or later**
4. Copy the connection string - it looks like:
   ```
   mongodb+srv://noteshub_user:<password>@noteshub.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Replace** `<password>` with your actual password (the one you saved)
6. **Add** database name at the end:
   ```
   mongodb+srv://noteshub_user:YOUR_PASSWORD@noteshub.xxxxx.mongodb.net/noteshub?retryWrites=true&w=majority
   ```

**SAVE THIS CONNECTION STRING** - you'll need it for Render!

---

## Part 2: Push Code to GitHub

### Step 1: Initialize Git Repository (if not already done)

```bash
cd /app
git init
git add .
git commit -m "Initial commit - Ready for Render deployment"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `noteshub-app` (or your choice)
3. Make it **Public** or **Private**
4. **Don't** initialize with README (we already have one)
5. Click **"Create repository"**

### Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/noteshub-app.git
git branch -M main
git push -u origin main
```

---

## Part 3: Deploy to Render

### Method A: Using Blueprint (Recommended - One Click)

1. **Login to Render**: https://dashboard.render.com

2. **Click "New +"** → **"Blueprint"**

3. **Connect GitHub Repository**:
   - Authorize Render to access your GitHub
   - Select your `noteshub-app` repository

4. **Blueprint File**: Render will automatically detect `render-deployment.yaml`

5. **Configure Environment Variables**:
   
   For **noteshub-backend**:
   - `MONGO_URL`: Paste your MongoDB Atlas connection string
   - `EMERGENT_LLM_KEY`: `sk-emergent-9E919704404924c86F`
   - `ADMIN_EMAILS`: Your email address

6. **Click "Apply"**

7. **Wait for deployment** (5-10 minutes for first deploy)

### Method B: Manual Deployment

If blueprint doesn't work, deploy manually:

#### Backend Deployment:

1. **New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `noteshub-backend`
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

2. **Environment Variables**:
   Add these in the "Environment" tab:
   ```
   PYTHON_VERSION=3.11
   MONGO_URL=mongodb+srv://noteshub_user:YOUR_PASSWORD@...
   JWT_SECRET_KEY=your-random-secret-key-here-change-this
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   EMERGENT_LLM_KEY=sk-emergent-9E919704404924c86F
   EMAIL_ENABLED=false
   VIRUS_SCAN_ENABLED=false
   PERFORMANCE_MONITORING_ENABLED=true
   CORS_ORIGINS=https://noteshub-frontend.onrender.com
   ADMIN_EMAILS=your-email@example.com
   ```

3. **Deploy**: Click "Create Web Service"

4. **Note your backend URL**: `https://noteshub-backend.onrender.com`

#### Frontend Deployment:

1. **New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `noteshub-frontend`
   - Root Directory: `frontend`
   - Runtime: **Node**
   - Build Command: `yarn install && yarn build`
   - Start Command: `yarn preview --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

2. **Environment Variables**:
   ```
   NODE_VERSION=20
   VITE_REACT_APP_BACKEND_URL=https://noteshub-backend.onrender.com
   VITE_API_BASE_URL=https://noteshub-backend.onrender.com
   ```
   (Replace with your actual backend URL from step 4 above)

3. **Deploy**: Click "Create Web Service"

---

## Part 4: Update CORS Settings

After both services are deployed:

1. Go to your **backend service** in Render dashboard
2. Go to "Environment" tab
3. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   CORS_ORIGINS=https://noteshub-frontend.onrender.com,http://localhost:3000
   ```
4. Save and the backend will auto-redeploy

---

## Part 5: Verify Deployment

1. **Backend Health Check**:
   - Visit: `https://noteshub-backend.onrender.com/api/health`
   - You should see: `{"status":"ok","message":"NotesHub API is running",...}`

2. **Frontend**:
   - Visit: `https://noteshub-frontend.onrender.com`
   - You should see the NotesHub homepage!

3. **Test Features**:
   - Try creating an account
   - Login
   - Upload a note
   - Check leaderboards

---

## 🚨 Important Notes

### Free Tier Limitations:
- Render free tier services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds to wake up
- 750 hours/month free (enough for 1 service running 24/7)

### Auto-Deploy:
- Any push to your `main` branch triggers automatic redeployment
- Great for continuous deployment!

### Custom Domain:
- You can add a custom domain in Render dashboard
- Go to service → Settings → Custom Domain

---

## 🔧 Troubleshooting

### Backend fails to start:
1. Check logs in Render dashboard
2. Verify `MONGO_URL` is correct
3. Ensure MongoDB Atlas allows connections from `0.0.0.0/0`

### Frontend can't connect to backend:
1. Check CORS settings in backend
2. Verify `VITE_REACT_APP_BACKEND_URL` is correct
3. Check browser console for errors

### Database connection issues:
1. Test MongoDB connection string locally first
2. Verify username and password are correct
3. Check MongoDB Atlas network access settings

---

## 📊 Next Steps

1. **Monitor your app**: Check logs in Render dashboard
2. **Set up alerts**: Render can notify you of deployment failures
3. **Upgrade if needed**: If you need 24/7 uptime, upgrade to paid tier ($7/month per service)
4. **Add custom domain**: Make it your own!

---

## 🎉 Congratulations!

Your NotesHub app is now live on Render! Share the URL with your users.

**Your URLs**:
- Frontend: `https://noteshub-frontend.onrender.com`
- Backend API: `https://noteshub-backend.onrender.com`
- API Docs: `https://noteshub-backend.onrender.com/api/docs`

---

## 💡 Pro Tips

1. **Keep Services Awake**: Use a service like UptimeRobot to ping your app every 5 minutes
2. **Environment Variables**: Never commit secrets to GitHub - always use Render's environment variables
3. **Database Backups**: MongoDB Atlas free tier includes automated backups
4. **Monitoring**: Use Render's built-in metrics to monitor performance

---

Need help? Check Render documentation: https://render.com/docs
