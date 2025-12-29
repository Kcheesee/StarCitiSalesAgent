# 📋 Render Deployment Checklist

Quick reference checklist for deploying StarCiti Sales Agent to Render.

---

## ✅ Pre-Deployment Checklist

- [ ] All code committed to Git
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] All API keys ready:
  - [ ] OpenAI API key
  - [ ] Anthropic API key
  - [ ] ElevenLabs API key
  - [ ] SendGrid API key
  - [ ] SendGrid sender email verified

---

## ✅ Database Deployment (Render PostgreSQL)

- [ ] Created PostgreSQL instance on Render
- [ ] Named: `starciti-db`
- [ ] Copied Internal Database URL
- [ ] Database status: **Available**

---

## ✅ Backend Deployment (Render Web Service)

- [ ] Created Web Service connected to GitHub repo
- [ ] Configured:
  - [ ] Root Directory: `backend`
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added environment variables:
  - [ ] `DATABASE_URL`
  - [ ] `ENVIRONMENT=production`
  - [ ] `OPENAI_API_KEY`
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `ELEVENLABS_API_KEY`
  - [ ] `SENDGRID_API_KEY`
  - [ ] `SENDGRID_FROM_EMAIL`
  - [ ] `FRONTEND_URL` (update after frontend deployed)
- [ ] Backend deployed successfully
- [ ] Health check passes: `https://YOUR-BACKEND.onrender.com/health`
- [ ] Backend URL: _________________________________

---

## ✅ Database Population (One-Time Setup)

- [ ] Opened backend Shell in Render
- [ ] Ran: `cd backend && python scripts/etl_pipeline.py`
- [ ] Ran: `python scripts/generate_embeddings.py`
- [ ] Verified ships in database: `https://YOUR-BACKEND.onrender.com/api/stats`
- [ ] Ship count: _____ (should be ~115)

---

## ✅ Frontend Deployment (Render Static Site)

- [ ] Created `.env.production` file with `VITE_API_URL`
- [ ] Created Static Site connected to GitHub repo
- [ ] Configured:
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: `npm install && npm run build`
  - [ ] Publish Directory: `dist`
- [ ] Added environment variable:
  - [ ] `VITE_API_URL=https://YOUR-BACKEND.onrender.com`
- [ ] Frontend deployed successfully
- [ ] Frontend loads: `https://YOUR-FRONTEND.onrender.com`
- [ ] Frontend URL: _________________________________

---

## ✅ Backend Configuration Update

- [ ] Updated backend `FRONTEND_URL` environment variable
- [ ] Set to: `https://YOUR-FRONTEND.onrender.com`
- [ ] Backend redeployed with new CORS settings

---

## ✅ ElevenLabs Configuration

- [ ] Logged into ElevenLabs dashboard
- [ ] Navigated to Conversational AI → Agents
- [ ] Selected agent: Nova (agent_6401kdgp1fd7fmvax85zb5s0sa3s)
- [ ] Found Custom Tools → `search_ships`
- [ ] Updated tool URL to: `https://YOUR-BACKEND.onrender.com/api/ships/search`
- [ ] Tested tool (should return ship data)
- [ ] Saved changes

---

## ✅ End-to-End Testing

- [ ] Visited frontend: `https://YOUR-FRONTEND.onrender.com`
- [ ] Landing page loads correctly
- [ ] Entered name and email
- [ ] Started conversation
- [ ] ElevenLabs widget loaded
- [ ] Microphone works
- [ ] Asked about ships
- [ ] Nova called ship search API (check backend logs)
- [ ] Nova provided ship recommendations
- [ ] Manually triggered end (or used end button)
- [ ] PDFs generated (check backend logs)
- [ ] Email received with PDFs
- [ ] Thank you page displayed

---

## ✅ Final Verification

- [ ] Frontend URL publicly accessible
- [ ] Backend API publicly accessible
- [ ] Database connected and populated
- [ ] Ship search API works (test via `/docs`)
- [ ] ElevenLabs agent uses production backend
- [ ] Email delivery working
- [ ] All CORS configured correctly
- [ ] No console errors in browser

---

## 📝 Production URLs

**Frontend**: https://___________________________________
**Backend**: https://___________________________________
**API Docs**: https://___________________________________/docs
**Health Check**: https://___________________________________/health

---

## 🎯 Post-Deployment Tasks

- [ ] Set up custom domain (optional)
- [ ] Add Google Analytics (optional)
- [ ] Upgrade to Starter tier ($14/month for always-on)
- [ ] Set up database backups
- [ ] Monitor usage and costs
- [ ] Add conversation end button
- [ ] Upload more voice samples to ElevenLabs
- [ ] Test with real users

---

## 🐛 Common Issues Resolved

| Issue | Solution |
|-------|----------|
| Backend spin-down slow | ✅ Upgraded to Starter tier |
| CORS errors | ✅ Updated FRONTEND_URL in backend |
| No ships in database | ✅ Ran ETL pipeline in Shell |
| Widget not loading | ✅ Verified agent ID correct |
| Email not sending | ✅ Checked SendGrid API key and sender |
| Tool not working | ✅ Updated URL in ElevenLabs |

---

## 🎉 Deployment Complete!

Congratulations! Your StarCiti Sales Agent is now live and ready to help users build their perfect Star Citizen fleet.

**Next**: Share your frontend URL and start collecting leads! 🚀
