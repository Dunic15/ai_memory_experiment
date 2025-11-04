# Data Analysis & Export Features

## Overview

This document explains the data storage and analysis features built into the experiment platform.

## Current Data Storage

### What Gets Saved

**Location:** `experiment_data/` folder

1. **participants.csv** - Master file with all participant demographics:
   - `participant_id` (P001, P002, etc.)
   - `timestamp` (when they started)
   - `full_name`, `profession`, `age`, `gender`, `native_language`

2. **{participant_id}_log.csv** - Detailed log for each participant:
   - All phases: demographics, consent, prior_knowledge, ai_trust
   - Randomization: article order, timing mode, summary structure
   - Reading behavior: time spent, summary views, interactions
   - Recall responses: text, sentence counts, confidence ratings
   - MCQ responses: answers, correctness
   - Manipulation check: verification questions

### Data Format

- **CSV files** (simple, readable in Excel/Google Sheets)
- UTF-8 encoding (supports Chinese characters)
- One log file per participant
- Easy to analyze with Python, R, or spreadsheet software

## Admin Data Export Features

### Feature 1: Download All Data as ZIP

**Endpoint:** `/admin/export?key=YOUR_ADMIN_KEY`

**What it does:**
- Downloads all CSV files as a ZIP archive
- Includes `participants.csv` and all `PXXX_log.csv` files
- Includes translation cache (optional)
- Timestamped filename: `experiment_data_YYYYMMDD_HHMMSS.zip`

**Usage:**
```bash
# Command line
curl "https://your-app.onrender.com/admin/export?key=YOUR_KEY" -o data.zip

# Browser
https://your-app.onrender.com/admin/export?key=YOUR_KEY
```

**Security:**
- Requires `ADMIN_KEY` environment variable
- Must match the `?key=` parameter
- Returns 403 Unauthorized if key doesn't match

### Feature 2: View Statistics

**Endpoint:** `/admin/stats?key=YOUR_ADMIN_KEY`

**What it returns:**
```json
{
  "participant_count": 47,
  "data_files": ["P001_log.csv", "P002_log.csv", ...],
  "total_data_size_mb": 2.45,
  "last_update": "2024-01-15T14:30:00",
  "data_directory": "/path/to/experiment_data"
}
```

**Usage:**
```bash
# Command line
curl "https://your-app.onrender.com/admin/stats?key=YOUR_KEY"

# Browser
https://your-app.onrender.com/admin/stats?key=YOUR_KEY
```

**Security:**
- Same `ADMIN_KEY` protection as export endpoint

## Setting Up Admin Access

### Step 1: Generate Admin Key

```bash
# Generate a secure random key
openssl rand -hex 32
```

### Step 2: Set Environment Variable

**Local testing:**
```bash
export ADMIN_KEY="your-generated-key-here"
python3 app.py
```

**Cloud deployment (Render/Railway):**
- Add `ADMIN_KEY` in environment variables section
- Use the same key you generated

### Step 3: Use the Endpoints

```bash
# Check stats
curl "http://localhost:8080/admin/stats?key=your-generated-key-here"

# Download data
curl "http://localhost:8080/admin/export?key=your-generated-key-here" -o data.zip
```

## Data Analysis Workflow

### For Local Development

1. **Data is automatically saved** to `experiment_data/` folder
2. **Open in Excel/Google Sheets:**
   - `participants.csv` → Demographics overview
   - `P001_log.csv` → Detailed participant data
3. **Analyze with Python:**
   ```python
   import pandas as pd
   participants = pd.read_csv('experiment_data/participants.csv')
   log = pd.read_csv('experiment_data/P001_log.csv')
   ```

### For Cloud Deployment

1. **Regular data export:**
   - Use `/admin/export` endpoint weekly/daily
   - Download ZIP file to your computer
   - Extract and analyze locally

2. **Monitor participant count:**
   - Use `/admin/stats` to check progress
   - Set up alerts if needed

3. **Backup strategy:**
   - Export data regularly (cloud storage is ephemeral on free tiers)
   - Store backups on your computer or cloud storage (Dropbox, Google Drive)

## Implementation Details

### Where the Code Lives

**Admin routes are in `app.py`:**
- Lines 1357-1400: `/admin/export` endpoint
- Lines 1402-1453: `/admin/stats` endpoint

**Data saving functions:**
- `save_participant()` - Saves demographics to `participants.csv`
- `log_data()` - Appends phase data to participant log file
- `get_participant_id()` - Generates sequential participant IDs

### Data Flow

```
Participant submits form
    ↓
save_participant() → participants.csv
    ↓
log_data() → PXXX_log.csv
    ↓
(Each phase logs data)
    ↓
Admin can export via /admin/export
```

## Recommendations

### For Small Studies (< 100 participants)

✅ **Current CSV approach is perfect:**
- Simple and readable
- Easy to analyze
- No database needed

### For Larger Studies (> 100 participants)

Consider upgrading to:
1. **PostgreSQL database** (persistent, queryable)
2. **Regular automated exports** (daily backups)
3. **Data validation** (prevent corrupted entries)

See `DATA_STORAGE_ANALYSIS.md` for detailed recommendations.

## Troubleshooting

### "Unauthorized" Error

- Check `ADMIN_KEY` environment variable is set
- Verify the `?key=` parameter matches exactly
- Keys are case-sensitive

### Empty Export

- Check `experiment_data/` folder exists
- Verify CSV files are present
- Check server logs for errors

### Data Not Appearing

- Ensure `log_data()` is being called in all routes
- Check file permissions on `experiment_data/` folder
- Verify UTF-8 encoding for Chinese characters

## Future Enhancements

Potential improvements:
- Date range filtering for exports
- CSV to JSON conversion option
- Direct database export (if using PostgreSQL)
- Email notifications on new participant completion
- Real-time dashboard for statistics

