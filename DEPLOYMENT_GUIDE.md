# NotesHub Deployment Guide

## FREE Deployment Options

This guide covers deploying NotesHub using completely free services.

---

## Architecture

- **Frontend**: Vercel (React/Vite)
- **Backend**: Render (FastAPI)
- **Database**: MongoDB Atlas (Free 512MB)
- **Email**: Resend (3000 emails/month free)

---

## Prerequisites

1. GitHub account (for code hosting)
2. Vercel account (sign up at vercel.com)
3. Render account (sign up at render.com)
4. MongoDB Atlas account (sign up at mongodb.com/cloud/atlas)
5. Resend account (sign up at resend.com)

---

## Step 1: Database Setup (MongoDB Atlas)

### 1.1 Create Free Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account
3. Create a new project: "NotesHub"
4. Build a cluster (choose FREE M0 tier)
   - Cloud Provider: AWS
   - Region: Choose closest to your users
   - Cluster Name: `noteshub-cluster`

### 1.2 Configure Database Access

1. Go to "Database Access" tab
2. Add new database user:
   - Username: `noteshub_admin`
   - Password: Generate secure password (save it!)
   - Database User Privileges: "Atlas admin"

### 1.3 Configure Network Access

1. Go to "Network Access" tab
2. Add IP Address: `0.0.0.0/0` (Allow access from anywhere)
   - Note: This is for ease of setup. In production, restrict to your backend IP

### 1.4 Get Connection String

1. Go to "Database" → "Connect"
2. Choose "Connect your application"
3. Copy the connection string:
   ```
   mongodb+srv://noteshub_admin:<password>@noteshub-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual password
5. Add database name: `/noteshub` before the `?`

---

## Step 2: Email Setup (Resend)

### 2.1 Create Account

1. Go to [Resend](https://resend.com)
2. Sign up for free account (3000 emails/month)
3. Verify your email address

### 2.2 Add Domain (Optional but Recommended)

**Option A: Use Your Domain**
1. Go to "Domains" tab
2. Click "Add Domain"
3. Enter your domain (e.g., `noteshub.com`)
4. Add DNS records provided by Resend:
   - SPF record
   - DKIM record
5. Verify domain

**Option B: Use Resend Test Domain** (Quick Start)
1. Use `onboarding@resend.dev` as your sender
2. Limited to 100 emails but works immediately

### 2.3 Generate API Key

1. Go to "API Keys" tab
2. Click "Create API Key"
3. Name: `NotesHub Production`
4. Permissions: "Sending access"
5. Copy the API key (starts with `re_`)
6. **Save it securely** - you won't see it again!

---

## Step 3: Backend Deployment (Render)

### 3.1 Prepare Repository

1. Push your code to GitHub
2. Ensure `backend/requirements.txt` is up to date

### 3.2 Create Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure service:
   - **Name**: `noteshub-backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

### 3.3 Add Environment Variables

In Render dashboard, add these environment variables:

```bash
# Database
MONGO_URL=mongodb+srv://noteshub_admin:YOUR_PASSWORD@noteshub-cluster.xxxxx.mongodb.net/noteshub?retryWrites=true&w=majority

# JWT Secret (generate a strong random string)
JWT_SECRET=your-super-secret-jwt-key-min-32-characters-long

# Email Configuration
EMAIL_ENABLED=true
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_your_resend_api_key_here
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=NotesHub
```

### 3.4 Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Once deployed, copy your backend URL:
   ```
   https://noteshub-backend.onrender.com
   ```
4. Test health endpoint:
   ```bash
   curl https://noteshub-backend.onrender.com/api/health
   ```

---

## Step 4: Frontend Deployment (Vercel)

### 4.1 Update vercel.json

Edit `/app/vercel.json` and replace `your-backend-url.onrender.com` with your actual Render URL.

### 4.2 Deploy to Vercel

**Option A: Using Vercel Dashboard**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `dist`
   - **Install Command**: `yarn install`

### 4.3 Add Environment Variables in Vercel

1. Go to Project Settings → Environment Variables
2. Add:
   ```bash
   VITE_API_BASE_URL=https://noteshub-backend.onrender.com
   REACT_APP_BACKEND_URL=https://noteshub-backend.onrender.com
   ```

### 4.4 Deploy

1. Click "Deploy"
2. Wait for deployment (2-5 minutes)
3. Your app will be available at:
   ```
   https://noteshub-xxxxx.vercel.app
   ```

---

## Step 5: Post-Deployment Configuration

### 5.1 Update CORS Settings

Update backend CORS to allow your Vercel domain in `backend/server.py`.

### 5.2 Test the Application

1. Visit your Vercel URL
2. Register a new user
3. Check Resend dashboard → "Logs" to see email sent
4. Test note upload/download functionality

---

## Running E2E Tests

We've added Playwright for end-to-end testing:

```bash
# Install Playwright browsers
npx playwright install

# Run tests
npx playwright test

# Run tests in UI mode
npx playwright test --ui

# View test report
npx playwright show-report
```

---

## Troubleshooting

### Frontend can't connect to backend

1. Check CORS settings in backend
2. Verify backend URL in Vercel environment variables
3. Check browser console for errors
4. Test backend directly: `curl https://your-backend.onrender.com/api/health`

### Emails not sending

1. Check `RESEND_API_KEY` is set correctly
2. Verify `EMAIL_ENABLED=true`
3. Check Resend dashboard logs
4. Ensure sender email is verified

### Database connection errors

1. Verify `MONGO_URL` format
2. Check MongoDB Atlas network access (0.0.0.0/0)
3. Verify database user credentials

### Render service sleep (Free tier limitation)

- Free tier services sleep after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- Consider upgrading to paid tier ($7/month) for no-sleep

---

## Cost Breakdown (Free Tier Limits)

| Service | Free Tier | Limit |
|---------|-----------|-------|
| Vercel | Unlimited | 100 GB bandwidth/month |
| Render | 750 hours/month | Service sleeps after 15 min |
| MongoDB Atlas | 512 MB storage | Shared cluster |
| Resend | 3,000 emails/month | 100 emails/day |

**Total Cost: $0/month** (within free tier limits)

---

## Security Checklist

- [ ] All API keys stored as environment variables
- [ ] JWT_SECRET is strong and random (32+ characters)
- [ ] CORS configured with specific domains
- [ ] HTTPS enforced on all services
- [ ] Email domain verified in Resend
- [ ] Database user has appropriate permissions
- [ ] Secrets never committed to Git
- [ ] `.env` files in `.gitignore`

---

**Congratulations! Your NotesHub application is now deployed!** 🎉
