# Project Structure

## Overview

This document explains the organization of the AI Memory Experiment project.

## Folder Structure

```
ai_memory_experiment/
├── app.py                      # Main Flask application (keep at root)
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment config (Render/Railway)
├── runtime.txt                 # Python version specification
├── render.yaml                 # Render.com deployment config
├── .gitignore                  # Git ignore rules
├── README.md                   # Main project documentation
│
├── docs/                       # Documentation files
│   ├── DEPLOYMENT.md           # How to deploy to cloud
│   ├── DATA_STORAGE_ANALYSIS.md # Data storage recommendations
│   ├── DATA_ANALYSIS_FEATURES.md # Data export features explained
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── setup-readme.txt        # Setup instructions
│   └── quick-reference.txt     # Quick reference guide
│
├── scripts/                    # Utility scripts
│   ├── add_data_export.py      # Reference: admin export routes
│   ├── auto_translate_templates.py # Translation utility
│   ├── setup-script.py         # Setup automation
│   └── setup/                  # Setup scripts
│       ├── setup.sh            # Linux/Mac setup
│       └── setup.bat           # Windows setup
│
├── templates/                  # HTML templates
│   ├── language_selection.html
│   ├── login.html
│   ├── consent.html
│   ├── prior_knowledge.html
│   ├── ai_trust.html
│   ├── reading.html
│   ├── ai_summary_view.html
│   ├── test.html
│   ├── manipulation_check.html
│   ├── debrief.html
│   └── ...
│
├── static/                     # Static assets (CSS, JS, images)
│   └── (currently empty)
│
├── experiment_data/            # Participant data (CSV files)
│   ├── participants.csv        # Master demographics file
│   ├── P001_log.csv            # Participant 1 log
│   ├── P002_log.csv            # Participant 2 log
│   └── ...
│
└── translation_cache/          # Cached translations
    └── translations.json       # Pre-translated content
```

## File Descriptions

### Root Level Files

- **`app.py`** - Main Flask application with all routes, data logging, and translation logic
- **`requirements.txt`** - Python package dependencies
- **`Procfile`** - Process file for cloud deployment (specifies how to run the app)
- **`runtime.txt`** - Python version for cloud platforms
- **`render.yaml`** - Render.com deployment configuration
- **`.gitignore`** - Files/folders to exclude from Git (data, cache, logs)
- **`README.md`** - Main project documentation and quick start guide

### Documentation (`docs/`)

- **`DEPLOYMENT.md`** - Detailed instructions for deploying to Render, Railway, Fly.io
- **`DATA_STORAGE_ANALYSIS.md`** - Analysis of data storage options and recommendations
- **`DATA_ANALYSIS_FEATURES.md`** - Explanation of admin export endpoints and data features
- **`PROJECT_STRUCTURE.md`** - This file (folder organization)
- **`setup-readme.txt`** - Setup instructions
- **`quick-reference.txt`** - Quick command reference

### Scripts (`scripts/`)

- **`add_data_export.py`** - Reference code showing admin export routes (already in app.py)
- **`auto_translate_templates.py`** - Utility for translating template strings
- **`setup-script.py`** - Automated setup script
- **`setup/`** - Platform-specific setup scripts

### Templates (`templates/`)

All HTML templates for the experiment interface:
- Language selection, login, consent
- Experiment phases (prior knowledge, AI trust, reading, testing)
- Post-experiment (manipulation check, debrief)

### Data Directories

- **`experiment_data/`** - All participant data (CSV files)
  - Automatically created by app
  - Contains sensitive data (excluded from Git)
  
- **`translation_cache/`** - Cached translations
  - Speeds up subsequent runs
  - Excluded from Git (can be regenerated)

## Why This Structure?

### Organized by Purpose

- **`docs/`** - All documentation in one place
- **`scripts/`** - Utility scripts separate from main app
- **`templates/`** - Standard Flask template location
- **`static/`** - Standard Flask static assets location
- **Data folders** - Separate from code for easy backup

### Flask Convention

- `app.py` at root (Flask expects this)
- `templates/` and `static/` in standard locations
- Environment variables for configuration

### Easy Deployment

- Root files needed for deployment (Procfile, runtime.txt, etc.)
- Data folders excluded from Git (via .gitignore)
- Clear separation of code and data

## Adding New Files

### New Route/Feature?

Add to `app.py` (main application file)

### New Documentation?

Add to `docs/` folder

### New Utility Script?

Add to `scripts/` folder

### New Template?

Add to `templates/` folder

### New Static Asset?

Add to `static/` folder (CSS, JS, images)

## Backing Up

### Important Files to Backup

1. **`experiment_data/`** - All participant data
2. **`translation_cache/`** - Cached translations (optional, can regenerate)
3. **`app.py`** - Main application code
4. **`templates/`** - All HTML templates
5. **`requirements.txt`** - Dependencies list

### Git Repository

Files to commit:
- ✅ All code files (`app.py`, templates, scripts)
- ✅ Configuration files (`requirements.txt`, `Procfile`, etc.)
- ✅ Documentation (`docs/`, `README.md`)

Files to exclude (already in `.gitignore`):
- ❌ `experiment_data/` - Contains sensitive participant data
- ❌ `translation_cache/` - Can be regenerated
- ❌ `*.log` - Log files
- ❌ `__pycache__/` - Python cache
- ❌ `.venv/` - Virtual environment

## Maintenance

### Regular Tasks

1. **Export data** - Use `/admin/export` endpoint regularly
2. **Check logs** - Monitor `server.log` for errors
3. **Update translations** - Translation cache updates automatically
4. **Backup data** - Copy `experiment_data/` folder regularly

### Cleanup

- Old log files can be deleted
- Translation cache can be cleared (will regenerate)
- Keep `experiment_data/` - Contains all experiment results!

