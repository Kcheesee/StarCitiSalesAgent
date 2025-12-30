# Deployment Guide - StarCiti Sales Agent Backend

## Production Database Migration

After deploying new code that includes database schema changes, you need to run migrations on the production database.

### Running the user_name Column Migration

1. Go to your Render dashboard: https://dashboard.render.com
2. Navigate to **starciti-backend** service
3. Click **Shell** tab
4. Run the migration script:

```bash
python scripts/migrate_add_user_name.py
```

5. Verify the migration succeeded (you should see "✅ Migration successful!")

## Troubleshooting Deployment

### 500 Errors on /api/conversations/start

**Symptom**: API returns 500 Internal Server Error when starting conversations

**Cause**: Missing `user_name` column in production database

**Fix**: Run the migration script (see above)

### Playwright Not Found

**Symptom**: `ModuleNotFoundError: No module named 'playwright'`

**Fix**: Ensure `requirements.txt` includes `playwright==1.49.1` and `render.yaml` buildCommand includes:
```
pip install -r requirements.txt && playwright install chromium --with-deps
```

## Environment Variables Required

Make sure these are set in Render dashboard:

- `DATABASE_URL` - Auto-set from Render PostgreSQL
- `OPENAI_API_KEY` - For Whisper transcription & embeddings
- `ANTHROPIC_API_KEY` - For Claude AI consultant
- `ELEVENLABS_API_KEY` - For text-to-speech
- `SENDGRID_API_KEY` - For email delivery
- `SENDGRID_FROM_EMAIL` - Verified sender email

## Deployment Checklist

- [ ] Push code to GitHub
- [ ] Render auto-deploys (or manually trigger)
- [ ] Build succeeds (check build logs)
- [ ] Run database migrations via Shell
- [ ] Test `/api/conversations/start` endpoint
- [ ] Test PDF generation endpoint
- [ ] Test email delivery

## Manual Deployment Commands

If not using Render.yaml:

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium --with-deps

# Run migrations
python scripts/migrate_add_user_name.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
