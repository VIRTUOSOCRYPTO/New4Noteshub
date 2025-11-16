# MongoDB Atlas Setup - Quick Guide

This is a quick reference for setting up MongoDB Atlas for your NotesHub deployment.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Account
1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up (free - no credit card required)

### Step 2: Create Free Cluster
1. Click **"Build a Database"**
2. Select **"M0 FREE"** tier
3. Provider: **AWS**
4. Region: **us-west-2 (Oregon)** ← Same as Render!
5. Cluster Name: `NotesHub`
6. Click **"Create"**

### Step 3: Create Database User
1. Username: `noteshub_user`
2. Password: Click **"Autogenerate Secure Password"**
3. **💾 SAVE THIS PASSWORD!** You'll need it!
4. Click **"Create User"**

### Step 4: Allow Access from Anywhere
1. Click **"Add My Current IP Address"**
2. Then click **"Add a Different IP Address"**
3. IP Address: `0.0.0.0/0`
4. Description: `Allow Render`
5. Click **"Add Entry"**
6. Click **"Finish and Close"**

### Step 5: Get Connection String
1. Click **"Connect"** button on your cluster
2. Choose **"Connect your application"**
3. Driver: **Python** / Version: **3.11 or later**
4. Copy the connection string

**Example connection string:**
```
mongodb+srv://noteshub_user:<password>@noteshub.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### Step 6: Format for Render
Replace `<password>` with your actual password and add database name:

```
mongodb+srv://noteshub_user:YOUR_ACTUAL_PASSWORD@noteshub.xxxxx.mongodb.net/noteshub?retryWrites=true&w=majority
```

**This is your MONGO_URL for Render!** 💾

---

## ✅ Verification

Test your connection string:
```bash
mongosh "mongodb+srv://noteshub_user:YOUR_PASSWORD@noteshub.xxxxx.mongodb.net/noteshub"
```

If successful, you'll see:
```
Current Mongosh Log ID: ...
Connecting to: mongodb+srv://...
Using MongoDB: 7.0.x
```

---

## 🔒 Security Notes

- ✅ Never commit connection strings to GitHub
- ✅ Use environment variables in Render
- ✅ Keep your password safe
- ✅ `0.0.0.0/0` allows connections from anywhere (needed for Render)

---

## 📊 Free Tier Limits

- 512 MB Storage (plenty for getting started)
- Shared RAM
- Shared vCPU
- No credit card required
- Perfect for development and small apps

---

## 🆙 Upgrade Later

If you need more:
- Click **"Upgrade"** in Atlas dashboard
- Plans start at $9/month (M10 cluster)
- More storage, dedicated resources

---

## 🆘 Troubleshooting

### Can't connect from Render?
- Verify `0.0.0.0/0` is in Network Access
- Check username/password are correct
- Ensure database name is included in connection string

### Connection timeout?
- Check if cluster is paused (free tier auto-pauses after inactivity)
- Click cluster name to wake it up

### Forgot password?
1. Go to **Database Access**
2. Click **"Edit"** on your user
3. Click **"Edit Password"**
4. Generate new password

---

## 📚 Resources

- Atlas Docs: https://docs.atlas.mongodb.com
- Connection Troubleshooting: https://docs.atlas.mongodb.com/troubleshoot-connection
- MongoDB University (Free Courses): https://university.mongodb.com

---

**Ready?** Copy your connection string and proceed to Render deployment! 🚀
