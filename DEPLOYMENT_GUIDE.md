# 🚀 Render Deployment Guide

Complete step-by-step guide to deploy StarCiti Sales Agent to Render.

---

## 📋 Prerequisites

Before starting, make sure you have:

- [ ] GitHub account
- [ ] Render account (sign up at https://render.com)
- [ ] All API keys ready:
  - OpenAI API key
  - Anthropic API key
  - ElevenLabs API key
  - SendGrid API key
  - SendGrid verified sender email

---

## 🗂️ Part 1: Push Code to GitHub

### 1. Initialize Git Repository (if not already done)

```bash
cd /Users/jackalmac/Desktop/Code\ World/StarCitiSalesAgent
git init
git add .
git commit -m "Initial commit - StarCiti Sales Agent"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Name: `StarCitiSalesAgent` (or your preferred name)
3. Keep it **Private** (your API keys will be in environment variables)
4. Don't initialize with README (we already have code)
5. Click "Create repository"

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/StarCitiSalesAgent.git
git branch -M main
git push -u origin main
```

---

## 🗄️ Part 2: Deploy PostgreSQL Database

### 1. Create PostgreSQL Instance

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `starciti-db`
   - **Database**: `starciti_sales`
   - **User**: `starciti_user` (auto-generated is fine)
   - **Region**: Choose closest to you (Oregon, Ohio, etc.)
   - **PostgreSQL Version**: 16
   - **Instance Type**: **Free** (good for testing, upgrade later if needed)
4. Click **"Create Database"**

### 2. Get Database Connection String

1. Once created, click on your database
2. Find **"Internal Database URL"** (starts with `postgresql://`)
3. Copy this URL - you'll need it for the backend

**⚠️ Important**:
- Use **Internal Database URL** (not External) for better performance
- The free tier database will spin down after 90 days of inactivity

---

## 🔧 Part 3: Deploy Backend API

### 1. Create Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select `StarCitiSalesAgent` repo
4. Configure:
   - **Name**: `starciti-backend`
   - **Region**: Same as database (Oregon, Ohio, etc.)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**

### 2. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** for each:

```
DATABASE_URL = <paste your Internal Database URL from Part 2>
ENVIRONMENT = production
OPENAI_API_KEY = <your OpenAI key>
ANTHROPIC_API_KEY = <your Anthropic key>
ELEVENLABS_API_KEY = <your ElevenLabs key>
SENDGRID_API_KEY = <your SendGrid key>
SENDGRID_FROM_EMAIL = noreply@yourdomain.com
SENDGRID_FROM_NAME = StarCiti Sales Agent
FRONTEND_URL = <leave blank for now, we'll update this after frontend is deployed>
```

### 3. Deploy Backend

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. You'll get a URL like: `https://starciti-backend.onrender.com`
4. Test it by visiting: `https://starciti-backend.onrender.com/health`

**Expected response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "api": "operational"
}
```

### 4. Run Database Setup (One-Time)

Once backend is deployed, you need to populate the database with ship data:

**Option A: Run via Render Shell**
1. Go to your web service → **"Shell"** tab
2. Run these commands:
```bash
cd backend
python scripts/etl_pipeline.py
python scripts/generate_embeddings.py
```

**Option B: Run locally then restore to Render**
1. Run locally with production DATABASE_URL
2. Use `pg_dump` and `pg_restore` to copy data

---

## 🎨 Part 4: Deploy Frontend

### 1. Update Frontend Environment

Create `/frontend/.env.production`:

```
VITE_API_URL=https://starciti-backend.onrender.com
```

### 2. Create Static Site on Render

1. In Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Select `StarCitiSalesAgent` repo
4. Configure:
   - **Name**: `starciti-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 3. Add Environment Variable

Click **"Advanced"** → **"Add Environment Variable"**:

```
VITE_API_URL = https://starciti-backend.onrender.com
```

Replace with your actual backend URL from Part 3.

### 4. Deploy Frontend

1. Click **"Create Static Site"**
2. Wait 3-5 minutes for deployment
3. You'll get a URL like: `https://starciti-frontend.onrender.com`

### 5. Update Backend with Frontend URL

1. Go back to your backend web service
2. Click **"Environment"** tab
3. Update `FRONTEND_URL` to your frontend URL: `https://starciti-frontend.onrender.com`
4. Click **"Save Changes"** (this will redeploy the backend)

---

## 🎤 Part 5: Update ElevenLabs Custom Tool

Now that you have a stable backend URL, update your ElevenLabs agent:

### 1. Update Ship Search Tool URL

1. Go to ElevenLabs Dashboard: https://elevenlabs.io
2. Navigate to **Conversational AI** → **Agents**
3. Select your agent: **Nova** (agent_6401kdgp1fd7fmvax85zb5s0sa3s)
4. Go to **Custom Tools** section
5. Find your `search_ships` tool
6. Update the **Endpoint URL** from:
   ```
   https://pseudoaggressive-karly-nonmeditatively.ngrok-free.dev/api/ships/search
   ```
   to:
   ```
   https://starciti-backend.onrender.com/api/ships/search
   ```
   Replace `starciti-backend` with your actual backend service name.

### 2. Test the Tool

1. In ElevenLabs dashboard, use the **"Test Tool"** button
2. Try a query like: `fast combat ship for dogfighting`
3. Verify it returns ship data
4. If it fails, check:
   - Backend is running: `https://your-backend.onrender.com/health`
   - Database has ships: `https://your-backend.onrender.com/api/stats`
   - Tool URL is correct (no typos)

### 3. Save and Publish

1. Click **"Save"** in ElevenLabs
2. Test your agent with a voice call
3. Ask about ships and verify Nova uses the tool

---

## ✅ Part 6: Test Complete Flow

### 1. Visit Your Live Site

Go to: `https://starciti-frontend.onrender.com`

### 2. Test End-to-End Flow

1. **Landing Page**:
   - Enter your name and email
   - Click "Start Voice Consultation"

2. **Conversation Page**:
   - ElevenLabs widget should load
   - Click microphone to start talking
   - Ask Nova about ships
   - Nova should call your backend's ship search API
   - Build your fleet

3. **End Conversation**:
   - Currently need to manually trigger end (see notes below)
   - PDFs should generate
   - Email should be sent

4. **Thank You Page**:
   - Should show confirmation
   - Check your email for PDFs

---

## 🔥 Important Notes

### Free Tier Limitations

**Backend & Database**:
- Will spin down after 15 minutes of inactivity
- First request after spin-down will be slow (30-60 seconds)
- 750 hours/month free (enough for development/testing)
- **Upgrade to Starter ($7/month) for always-on service**

**Static Site**:
- Always on, no spin-down
- Free with 100GB bandwidth/month

### Conversation End Detection

The current implementation listens for `elevenlabs-conversation-ended` event. You may need to:

1. **Add Manual End Button** (recommended for now):
   - Add a "End Consultation" button in ConversationPage
   - On click, call the complete endpoint

2. **Use ElevenLabs Callbacks** (check their docs):
   - Look for conversation end callbacks/webhooks
   - Update event listener in ConversationPage.jsx

### Custom Domain (Optional)

To use your own domain:

1. Purchase domain (Namecheap, Google Domains, etc.)
2. In Render, go to your static site → **"Settings"** → **"Custom Domains"**
3. Add your domain and follow DNS instructions
4. Update `FRONTEND_URL` in backend environment variables
5. Update CORS origins if needed

---

## 🐛 Troubleshooting

### Backend Issues

**"Application failed to start"**:
- Check logs: Web Service → **"Logs"** tab
- Verify DATABASE_URL is set correctly
- Check all required API keys are set

**"Database connection failed"**:
- Use Internal Database URL (not External)
- Verify database is running
- Check PostgreSQL version compatibility

**CORS errors**:
- Verify `FRONTEND_URL` matches your actual frontend URL
- Check browser console for exact CORS error
- May need to add to `EXTRA_CORS_ORIGINS`

### Frontend Issues

**"Failed to fetch API"**:
- Check `VITE_API_URL` is set correctly
- Verify backend is running: visit `/health` endpoint
- Check browser console for errors

**Widget not loading**:
- Check browser console for script errors
- Verify agent ID is correct
- Check ElevenLabs dashboard for agent status

### Database Issues

**"No ships found"**:
- You forgot to run the ETL pipeline
- Go to backend Shell and run:
  ```bash
  cd backend
  python scripts/etl_pipeline.py
  python scripts/generate_embeddings.py
  ```

**"Out of disk space"**:
- Free tier has 1GB storage
- Check database size in Render dashboard
- May need to upgrade

---

## 💰 Cost Breakdown

### Render Hosting

**Free Tier** (good for development):
- PostgreSQL: Free (1GB storage, 90-day retention)
- Backend Web Service: Free (750 hours/month)
- Frontend Static Site: Free (100GB bandwidth)
- **Total: $0/month**

**Starter Tier** (recommended for production):
- PostgreSQL: $7/month (10GB storage, always-on)
- Backend Web Service: $7/month (always-on, no spin-down)
- Frontend Static Site: Free
- **Total: $14/month**

### API Usage (Per Conversation)

- OpenAI Whisper: ~$0.18 (30 min conversation)
- OpenAI Embeddings: $0.00 (one-time setup cost ~$0.001)
- Anthropic Claude: ~$0.50-2.00 (depending on length)
- ElevenLabs TTS: ~$0.30-1.00 (depending on response length)
- SendGrid: $0 (free tier: 100 emails/day)

**Estimated per conversation**: $1-3

---

## 🎉 You're Done!

Your production URLs:
- **Frontend**: `https://starciti-frontend.onrender.com`
- **Backend API**: `https://starciti-backend.onrender.com`
- **API Docs**: `https://starciti-backend.onrender.com/docs`
- **Health Check**: `https://starciti-backend.onrender.com/health`

Share your frontend URL with users to start collecting leads and providing ship consultations!

---

## 📝 Next Steps

1. **Custom Domain**: Set up a real domain (e.g., `starciti.ai`)
2. **Analytics**: Add Google Analytics or Plausible to track usage
3. **Upgrade Tier**: When ready for production, upgrade to Starter tier
4. **Monitoring**: Set up Render alerts for downtime
5. **Backups**: Set up regular database backups
6. **Add End Button**: Implement manual conversation end button
7. **Voice Samples**: Upload more energetic voice samples to ElevenLabs
8. **Testing**: Thoroughly test the complete flow

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **ElevenLabs Docs**: https://elevenlabs.io/docs
- **Check Logs**: Always check logs first when debugging
- **Backend Logs**: Web Service → Logs tab
- **Browser Console**: F12 → Console tab for frontend errors
