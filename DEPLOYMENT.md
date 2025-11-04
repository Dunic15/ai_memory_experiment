# Deployment Guide

This guide explains how to deploy your AI Memory Experiment app so others can access it online.

## Option 1: Render (Recommended - Free Tier Available) ⭐

**Render** is the easiest option with a free tier:

### Steps:

1. **Create a Render account:**
   - Go to https://render.com
   - Sign up with GitHub (recommended) or email

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or upload the code)
   - Or use the Render Dashboard → "New Web Service" → "Public Git repository"
   - Paste your repository URL

3. **Configure the service:**
   - **Name:** `ai-memory-experiment` (or any name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 app.py`
   - **Plan:** Free (or Starter for better performance)

4. **Set Environment Variables:**
   - Click "Environment" tab
   - Add: `FLASK_SECRET_KEY` = (generate a random string, e.g., `openssl rand -hex 32`)
   - Add: `PORT` = `8080` (Render sets this automatically, but app.py uses it)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your app will be live at: `https://your-app-name.onrender.com`

### Notes:
- Free tier: App sleeps after 15 minutes of inactivity (first request takes ~30 seconds to wake up)
- Upgrade to Starter ($7/month) for always-on service
- Data files are stored in ephemeral storage (will reset on redeploy)

---

## Option 2: Railway (Alternative - Free Trial)

**Railway** is another easy option:

### Steps:

1. **Create account:** https://railway.app
2. **New Project** → "Deploy from GitHub repo"
3. **Add environment variable:** `FLASK_SECRET_KEY` (generate a random string)
4. **Deploy** - Railway auto-detects Python apps

Your app will be at: `https://your-app-name.railway.app`

---

## Option 3: Fly.io (Free Tier)

**Fly.io** offers a free tier with persistent storage:

### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Deploy:**
   ```bash
   fly launch
   ```
   Follow the prompts. Fly will create `fly.toml` automatically.

4. **Set secrets:**
   ```bash
   fly secrets set FLASK_SECRET_KEY="your-secret-key-here"
   ```

---

## Option 4: Heroku (Paid - $5/month minimum)

Heroku removed free tier but is reliable:

1. Create account at https://heroku.com
2. Install Heroku CLI
3. Run:
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_SECRET_KEY="your-secret-key"
   git push heroku main
   ```

---

## Important: Update app.py for Production

Before deploying, update the port in `app.py`:

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use PORT from environment
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production
```

**Already done!** The app.py already uses `PORT` environment variable.

---

## Environment Variables to Set

All platforms need:
- `FLASK_SECRET_KEY`: Random string (generate with: `openssl rand -hex 32`)
- `PORT`: Usually set automatically by the platform

---

## Data Persistence

**Important:** Most free tiers use ephemeral storage. Your `experiment_data/` folder will be reset on redeploy.

**Solutions:**
1. Use a database (PostgreSQL on Render/Railway)
2. Use cloud storage (AWS S3, Google Cloud Storage)
3. Use a file storage service
4. Export data regularly via admin panel

---

## Recommended: Render Free Tier

**Why Render?**
- ✅ Free tier available
- ✅ Easy GitHub integration
- ✅ Automatic HTTPS
- ✅ Simple setup
- ✅ Good documentation

**Limitations:**
- ⚠️ App sleeps after 15 min inactivity (30s wake-up time)
- ⚠️ Ephemeral storage (data resets on redeploy)

---

## Quick Start (Render)

1. Push your code to GitHub
2. Go to https://render.com
3. New → Web Service → Connect GitHub repo
4. Use these settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python3 app.py`
   - Environment: `FLASK_SECRET_KEY=your-secret-here`
5. Deploy!

Your app will be live in ~5 minutes! 🚀

