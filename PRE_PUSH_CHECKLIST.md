# ✅ Pre-Push Safety Checklist

**Run this checklist before pushing to GitHub to ensure no sensitive data is exposed.**

---

## 🔒 Sensitive Files Check

Run these commands in your terminal:

```bash
cd "/Users/jackalmac/Desktop/Code World/StarCitiSalesAgent"

# 1. Verify .env is NOT tracked
git check-ignore backend/.env
# Should output: backend/.env ✅

# 2. Verify .env is NOT staged
git status | grep "\.env"
# Should output nothing ✅

# 3. Check for any API keys in tracked files
git grep -i "sk-" | grep -v ".env.example" | grep -v "DEPLOYMENT"
git grep -i "api.key" | grep -v ".env.example"
# Should output nothing or only references in docs ✅

# 4. List all tracked files (review this list!)
git ls-files
```

---

## 📋 Files That SHOULD Be Tracked

✅ **Safe to commit:**
- `.gitignore`
- `backend/.env.example` (template only, no real keys)
- `frontend/.env.production` (has placeholder URL only)
- `DEPLOYMENT_GUIDE.md`
- `DEPLOYMENT_CHECKLIST.md`
- `backend/render.yaml` (no secrets)
- `backend/build.sh`
- All Python code (`*.py`)
- All JavaScript code (`*.jsx`, `*.js`)
- `requirements.txt`
- `package.json`

---

## 🚫 Files That MUST NOT Be Tracked

❌ **Never commit:**
- `backend/.env` (contains real API keys!)
- Any file with actual API keys
- `outputs/*.pdf`
- `uploads/*`
- `data/raw_ships/*.json` (large files)
- `data/ship_images/*` (large image files)
- `node_modules/`
- `__pycache__/`
- `*.log`

---

## 🔍 Visual Inspection

Before pushing, manually verify these files DON'T contain secrets:

1. **frontend/.env.production**
   ```bash
   cat frontend/.env.production
   ```
   ✅ Should only have: `VITE_API_URL=https://starciti-backend.onrender.com`

2. **backend/.env.example**
   ```bash
   cat backend/.env.example
   ```
   ✅ Should only have placeholder values like `your-api-key-here`

3. **Check all DEPLOYMENT_*.md files**
   ```bash
   grep -i "sk-" DEPLOYMENT*.md
   ```
   ✅ Should output nothing (no real API keys in docs)

---

## 🎯 Final Pre-Push Commands

```bash
# 1. Make sure you're on main branch
git branch --show-current

# 2. See what will be pushed
git status

# 3. Review all changes
git diff origin/main

# 4. If everything looks good, push
git push origin main
```

---

## ✅ GitHub Desktop App Steps

1. **Open GitHub Desktop**
2. **Check "Changes" tab**:
   - ✅ Should see deployment files
   - ✅ Should see new frontend pages
   - ✅ Should see updated .gitignore
   - ❌ Should NOT see `backend/.env`
   - ❌ Should NOT see any `*.log` files
   - ❌ Should NOT see `outputs/` or `uploads/`

3. **Review Each File**:
   - Click on each file in the changes list
   - Scan for any API keys (look for `sk-`, `API_KEY =`)
   - Make sure no sensitive data visible

4. **Write Commit Message**:
   ```
   Add ElevenLabs integration and Render deployment setup

   - Created landing page with email capture
   - Integrated ElevenLabs conversational AI widget
   - Built complete end-to-end flow (landing → conversation → thank you)
   - Added Render deployment guides and configuration
   - Updated backend to accept user info on conversation start
   - Configured CORS for production URLs
   ```

5. **Commit to main**

6. **Click "Push origin"**

---

## 🚨 Emergency: If You Accidentally Pushed Secrets

If you accidentally pushed your `.env` file or API keys:

### 1. **Immediately Rotate All API Keys**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys
   - ElevenLabs: https://elevenlabs.io/app/settings/api-keys
   - SendGrid: https://app.sendgrid.com/settings/api_keys

### 2. **Remove from Git History**
   ```bash
   # Remove the file from git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push to overwrite history
   git push origin --force --all
   ```

### 3. **Contact Support**
   - GitHub Support: Request permanent deletion from cache
   - Report the keys as compromised to each provider

---

## ✅ All Clear!

Once you've verified:
- ✅ No `.env` files in the commit
- ✅ No API keys visible in any files
- ✅ No large data files (check total commit size)
- ✅ All deployment guides reviewed

**You're safe to push to GitHub!** 🚀

---

## 📊 Quick Stats

After pushing, verify:

```bash
# Check repository size
git count-objects -vH

# Should be under 50MB for free tier
# If larger, you likely committed data/ship_images
```

**Recommended**: Keep repo under 100MB for best performance.

If over 100MB:
- Check if `data/ship_images/` was accidentally committed
- Use `git lfs` for large files
- Or keep images out of git entirely (download on deploy)
