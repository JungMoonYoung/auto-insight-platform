# 🚀 Auto-Insight Platform - Deployment Guide

Complete guide for deploying the Auto-Insight Platform to Streamlit Cloud.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Troubleshooting](#troubleshooting)
5. [Post-Deployment Verification](#post-deployment-verification)

---

## ✅ Pre-Deployment Checklist

### 1. **Files Ready for Deployment**

Ensure these files exist and are correctly configured:

- ✅ `requirements.txt` - Dependencies optimized for cloud
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.streamlit/secrets.toml.example` - Secrets template
- ✅ `.gitignore` - Excludes `.env` and `secrets.toml`
- ✅ `app.py` - Main application file
- ✅ `README.md` - Project documentation

### 2. **Sensitive Information Check**

**CRITICAL**: Ensure NO sensitive data is in the repository!

```bash
# Check for API keys in code
grep -r "sk-" --include="*.py" . | grep -v ".env" | grep -v "venv"

# Check for secrets
grep -r "password\|secret\|token" --include="*.py" modules/ utils/

# Verify .gitignore includes:
# - .env
# - .streamlit/secrets.toml
```

### 3. **Git Repository Status**

```bash
# Check current status
git status

# Ensure all changes are committed
git add .
git commit -m "Prepare for deployment (DAY 32)"

# Push to GitHub
git push origin main
```

---

## 🌐 Streamlit Cloud Deployment

### Step 1: Create GitHub Repository

If you haven't already:

```bash
# Initialize Git (if needed)
git init

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/auto-insight-platform.git

# Push code
git add .
git commit -m "Initial commit - Auto-Insight Platform"
git push -u origin main
```

### Step 2: Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"** or **"Log in with GitHub"**
3. Authorize Streamlit to access your GitHub repositories

### Step 3: Deploy New App

1. Click **"New app"** button
2. Fill in the deployment form:

   | Field | Value |
   |-------|-------|
   | **Repository** | `YOUR_USERNAME/auto-insight-platform` |
   | **Branch** | `main` |
   | **Main file path** | `app.py` |
   | **App URL** | `your-app-name` (choose unique name) |

3. Click **"Advanced settings"** (optional):
   - Python version: `3.9` (recommended)
   - Set custom subdomain if desired

4. Click **"Deploy!"**

### Step 4: Monitor Deployment

- **Deployment logs** will appear in real-time
- Installation takes ~5-10 minutes (dependencies download)
- Watch for errors in the log stream

**Common installation stages:**
```
[1/4] Installing dependencies from requirements.txt
[2/4] Building Python environment
[3/4] Installing system packages
[4/4] Starting Streamlit app
```

---

## 🔐 Environment Configuration

### Configure Secrets in Streamlit Cloud

1. Go to your app dashboard on Streamlit Cloud
2. Click **⚙️ Settings** → **Secrets**
3. Paste the following (replace with actual values):

```toml
# OpenAI API Key (Required for GPT insights)
OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Deployment flag (disables web scraping in cloud)
deployed = true
```

4. Click **"Save"**
5. App will automatically reboot with new secrets

### Get OpenAI API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-`)
4. Paste into Streamlit Cloud secrets

---

## 🐛 Troubleshooting

### Issue 1: Deployment Fails - Dependencies Error

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement konlpy
```

**Solution:**
KoNLPy requires Java, which isn't available on Streamlit Cloud.

**Fix in `requirements.txt`:**
```python
# Conditional install - skip on Linux (Streamlit Cloud)
konlpy==0.6.0; platform_system != "Linux"
```

The app has fallback logic for text tokenization when KoNLPy is unavailable.

---

### Issue 2: App Crashes on Startup

**Symptom:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
1. Check `requirements.txt` includes all dependencies
2. Verify version compatibility
3. Trigger reboot: Settings → Reboot app

---

### Issue 3: Secrets Not Loading

**Symptom:**
```
KeyError: 'OPENAI_API_KEY'
```

**Solution:**
1. Go to app Settings → Secrets
2. Verify `OPENAI_API_KEY` is set
3. Check spelling and format (TOML syntax)
4. Reboot app after saving secrets

---

### Issue 4: File Upload Fails

**Symptom:**
```
File size exceeds maximum allowed size
```

**Solution:**

**In `.streamlit/config.toml`:**
```toml
[server]
maxUploadSize = 200  # Increase to 200MB
```

**Streamlit Cloud default:** 200MB
**Adjust if needed:** Settings → Advanced → Max upload size

---

### Issue 5: App Running Slowly

**Possible causes:**
1. **Large file uploads** - Optimize data preprocessing
2. **Too many requests** - Streamlit Cloud free tier has limits
3. **GPT API calls** - Each insight generation calls OpenAI

**Solutions:**
- Use smaller data files for testing
- Cache results with `@st.cache_data`
- Limit GPT calls in production

---

## ✅ Post-Deployment Verification

### Test All Features

After deployment, test the following:

#### 1. **Data Upload**
- [ ] Upload CSV file (< 200MB)
- [ ] Upload Excel file (.xlsx)
- [ ] Check encoding detection (Korean text)

#### 2. **RFM Analysis**
- [ ] Auto-detect columns (CustomerID, InvoiceDate, etc.)
- [ ] Configure RFM parameters (quantiles)
- [ ] View RFM scores and segments
- [ ] Download RFM results (CSV)

#### 3. **Visualizations**
- [ ] 3D scatter plot renders correctly
- [ ] Bar charts load properly
- [ ] Pie charts display percentages
- [ ] Pareto chart shows correctly

#### 4. **Sales Analysis**
- [ ] Period selection (daily/weekly/monthly)
- [ ] Trend charts with moving averages
- [ ] Top products ranking
- [ ] Pareto analysis (80-20 rule)

#### 5. **Text Analysis**
- [ ] Keyword extraction works
- [ ] Word cloud generates
- [ ] Topic modeling (LDA) completes
- [ ] Sentiment analysis (if enabled)

#### 6. **GPT Insights**
- [ ] GPT analysis button appears
- [ ] Insights generate successfully
- [ ] Cost tracking updates
- [ ] Error handling for API failures

#### 7. **Report Generation**
- [ ] HTML report downloads
- [ ] PDF export (if configured)
- [ ] Charts embedded in report

### Disabled Features in Cloud

These features are **intentionally disabled** in Streamlit Cloud deployment:

- ❌ **Web Scraping** (크롤링) - Requires Chrome/ChromeDriver not available in cloud
  - Button is hidden when `deployed=true`
  - See `app.py` line ~50: `if not st.session_state.get('deployed', False):`

---

## 📊 Monitoring & Maintenance

### View App Logs

1. Go to Streamlit Cloud dashboard
2. Click your app
3. View **"Logs"** tab for real-time logs

### Check Resource Usage

Free tier limits:
- **1 GB RAM**
- **1 CPU core**
- **No GPU**
- **Unlimited public apps**

### Update App

When you push changes to GitHub:

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

**Streamlit Cloud auto-redeploys** within ~2-3 minutes.

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| **Streamlit Cloud Dashboard** | https://share.streamlit.io |
| **Streamlit Docs** | https://docs.streamlit.io |
| **Deployment Guide** | https://docs.streamlit.io/streamlit-community-cloud/get-started |
| **Secrets Management** | https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management |
| **OpenAI API Keys** | https://platform.openai.com/api-keys |

---

## 🎉 Deployment Complete!

Once deployed, your app will be live at:

```
https://your-app-name.streamlit.app
```

**Share this URL** with users to access the Auto-Insight Platform!

---

## 📝 Quick Reference

### Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] requirements.txt optimized
- [ ] .streamlit/config.toml created
- [ ] Secrets configured in Streamlit Cloud
- [ ] App deployed successfully
- [ ] All features tested
- [ ] URL shared with team

### Emergency Rollback

If deployment breaks:

1. Go to Streamlit Cloud → Settings
2. Click **"Reboot app"**
3. If still broken, revert Git commit:
   ```bash
   git revert HEAD
   git push origin main
   ```

---

**Last Updated:** 2025-02-09 (DAY 32)
**Maintained By:** Auto-Insight Platform Team
