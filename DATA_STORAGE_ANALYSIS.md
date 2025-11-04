# Data Storage Analysis & Recommendations

## Current Data Storage

### What's Being Saved:
1. **participants.csv** - Demographics (name, age, profession, gender, language)
2. **{participant_id}_log.csv** - All phase data per participant:
   - Demographics
   - Consent
   - Prior knowledge (familiarity, recognition, quiz)
   - AI trust (ratings, reflection)
   - Randomization (article order, timing, structure)
   - Reading behavior (time spent, summary views)
   - Recall responses (text, counts, confidence)
   - MCQ responses
   - Manipulation check

### Current Storage Format:
- **CSV files** (simple, readable)
- One log file per participant
- One master participants file
- All stored in `experiment_data/` folder

## Assessment of Current Approach

### ✅ Strengths:
1. **Simple & readable** - Easy to open in Excel/Google Sheets
2. **No database needed** - Works immediately
3. **Good for small studies** - Fine for < 100 participants
4. **Easy backup** - Just copy the folder

### ⚠️ Limitations:
1. **Not scalable** - Gets slow with many participants
2. **No concurrent access** - Can cause issues if multiple people submit at once
3. **No data validation** - Easy to have corrupted data
4. **No querying** - Hard to analyze without exporting to spreadsheet
5. **Cloud deployment** - Data on cloud server, not your laptop

## Cloud Deployment: Where Data Goes

### ❌ Important: Data Does NOT Go to Your Laptop
When deployed to cloud (Render/Railway/Fly.io):
- Data is saved on the **cloud server**
- You can't access it directly from your laptop
- Free tiers use **ephemeral storage** (data LOST on redeploy/restart)

### ✅ Solutions for Cloud Deployment:

#### Option 1: Database (Recommended for Production)
- Use PostgreSQL (free on Render/Railway)
- Data persists across redeploys
- Easy to query and export
- **Best for real studies**

#### Option 2: Cloud Storage (Simple Backup)
- Use AWS S3, Google Cloud Storage, or Dropbox API
- Save CSV files to cloud storage
- **Good for backups**

#### Option 3: Export API (Manual Download)
- Create admin endpoint to download all data
- Download CSV files manually
- **Good for small studies**

#### Option 4: Email Export (Automated)
- Email data to yourself after each participant
- **Simple but limited**

## Recommendations

### For Local Testing (Current Setup):
✅ **Keep current CSV approach** - It works well for local testing

### For Cloud Deployment:

#### 🥇 **Best: PostgreSQL Database**
```python
# Use SQLAlchemy + PostgreSQL
# Pros: Persistent, queryable, scalable
# Cons: Requires database setup
```

#### 🥈 **Good: Cloud Storage Backup**
```python
# Save to S3/Dropbox after each participant
# Pros: Simple, persistent
# Cons: Requires cloud account
```

#### 🥉 **Simple: Admin Download Endpoint**
```python
# Create /admin/download endpoint
# Download all data as ZIP
# Pros: No external dependencies
# Cons: Manual process
```

## Quick Fix: Add Data Export Endpoint

I can add an admin endpoint that lets you:
1. Download all data as CSV/ZIP
2. View participant count
3. Export specific date ranges

This way, even if data is on cloud, you can download it anytime.

---

## Current Data Quality

Looking at your `participants.csv`:
- ✅ 47+ participants recorded
- ✅ Good structure (participant_id, timestamp, demographics)
- ✅ Complete data logging per phase

**Recommendation:** Keep CSV for local, add database for cloud deployment.

