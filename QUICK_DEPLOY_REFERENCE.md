# ⚡ Quick Deploy Reference - NotesHub to Render

**TL;DR**: 3 steps to deploy your app

---

## Step 1: MongoDB Atlas (5 min)

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Create **FREE M0 cluster** in **Oregon**
3. Create user: `noteshub_user` with auto-generated password
4. Network Access: Add `0.0.0.0/0`
5. Get connection string and format it:
   ```
   mongodb+srv://noteshub_user:YOUR_PASSWORD@cluster.xxxxx.mongodb.net/noteshub?retryWrites=true&w=majority
   ```

💾 **SAVE THIS CONNECTION STRING!**

---

## Step 2: Push to GitHub (2 min)

```bash
cd /app
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/noteshub-app.git
git push -u origin main
```

---

## Step 3: Deploy to Render (5 min)

### Option A: Blueprint (Easiest) ⭐

1. Go to: https://dashboard.render.com
2. **New +** → **Blueprint**
3. Connect your GitHub repo
4. Add environment variables:
   - Backend: `MONGO_URL` (your connection string)
   - Backend: `EMERGENT_LLM_KEY` = `sk-emergent-9E919704404924c86F`
   - Backend: `ADMIN_EMAILS` = your email
5. Click **"Apply"**
6. Wait 5-10 minutes

### Option B: Manual (More Control)

**Backend:**
1. New Web Service → Python
2. Root Dir: `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)

**Frontend:**
1. New Web Service → Node
2. Root Dir: `frontend`
3. Build: `yarn install && yarn build`
4. Start: `yarn preview --host 0.0.0.0 --port $PORT`
5. Add env: `VITE_REACT_APP_BACKEND_URL` = your backend URL

**Update CORS:**
1. Go to backend → Environment
2. Set `CORS_ORIGINS` = your frontend URL
3. Save (auto-redeploys)

---

## ✅ Verify

- Backend: `https://YOUR-BACKEND.onrender.com/api/health`
- Frontend: `https://YOUR-FRONTEND.onrender.com`

---

## 🆘 Quick Fixes

**Connection failed?**
- Check MongoDB allows `0.0.0.0/0`
- Verify MONGO_URL format

**CORS error?**
- Add frontend URL to backend CORS_ORIGINS

**Service not responding?**
- Free tier spins down after 15 min
- First request takes 30-60s to wake

---

## 📚 Full Guides

- Complete Guide: `/app/RENDER_DEPLOYMENT_GUIDE.md`
- MongoDB Setup: `/app/MONGODB_ATLAS_SETUP.md`
- Checklist: `/app/DEPLOYMENT_CHECKLIST.md`

---

**Time to deploy: ~12 minutes** | **Cost: $0 (Free tier)** 🎉
