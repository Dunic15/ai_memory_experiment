# AI-Assisted Human Memory Encoding Experiment

A Flask web application for conducting memory encoding experiments with AI-assisted reading materials. Supports bilingual (English/Chinese) interface with real-time translation.

## Features

- 🧠 **Memory Experiment Platform**: Complete workflow from participant registration to data collection
- 🌐 **Bilingual Support**: English and Chinese (中文) with automatic translation
- 📊 **Comprehensive Data Logging**: Tracks all participant interactions and responses
- ⏱️ **Flexible Timing Modes**: Pre-reading, post-reading, and synchronous AI summary display
- 📝 **Multiple Assessment Types**: Prior knowledge, AI trust, free recall, and multiple-choice questions
- 🎯 **Randomized Conditions**: Article order, timing, and summary structure (integrated/segmented)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Navigate to the project directory:**
   ```bash
   cd ai_memory_experiment
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python3 app.py
   ```

5. **Open in browser:**
   - Local: http://127.0.0.1:8080
   - The app will pre-translate all content on first startup (takes 30-60 seconds)

## Project Structure

```
ai_memory_experiment/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment config
├── runtime.txt                 # Python version
├── render.yaml                 # Render.com config
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md           # Deployment instructions
│   ├── DATA_STORAGE_ANALYSIS.md # Data storage guide
│   ├── DATA_ANALYSIS_FEATURES.md # Data export features
│   └── PROJECT_STRUCTURE.md    # Folder organization
│
├── scripts/                    # Utility scripts
│   └── setup/                  # Setup scripts
│
├── templates/                  # HTML templates
├── static/                     # CSS, JavaScript, images
├── experiment_data/           # Participant data (CSV files)
└── translation_cache/         # Cached translations
```

**See `docs/PROJECT_STRUCTURE.md` for detailed folder organization.**

## Setting Up Git and GitHub (First Time)

### Step 1: Create a GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Name it (e.g., `ai-memory-experiment`)
4. Choose Public or Private
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Push Your Code to GitHub

**Run these commands in your project directory** (`/Users/duccioo/Desktop/ai_memory_experiment`):

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit"

# Add your GitHub repository as remote
# Replace YOUR_GITHUB_REPO_URL with your actual repository URL
# Example: https://github.com/yourusername/ai-memory-experiment.git
git remote add origin YOUR_GITHUB_REPO_URL

# Push to GitHub
git push -u origin main
```

**Note:** If your GitHub repo uses `master` instead of `main`, use:
```bash
git push -u origin master
```

### Step 3: Verify

- Go to your GitHub repository page
- You should see all your files there!

## Deployment to Cloud

### Option 1: Render.com (Recommended - Free Tier)

1. **Push code to GitHub** (follow steps above)

2. **Go to https://render.com** and sign up

3. **Create new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

4. **Configure:**
   - **Name:** `ai-memory-experiment` (or any name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 app.py`

5. **Add Environment Variables:**
   - `FLASK_SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `ADMIN_KEY`: Create a secret key for data export (optional but recommended)

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes
   - Your app will be live at: `https://your-app-name.onrender.com`

**Note:** Free tier sleeps after 15 min inactivity. Upgrade to Starter ($7/month) for always-on.

### Option 2: Railway.app

1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub repo
4. Add environment variables: `FLASK_SECRET_KEY`, `ADMIN_KEY`
5. Deploy automatically

### Option 3: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch

# Set secrets
fly secrets set FLASK_SECRET_KEY="your-secret-key"
fly secrets set ADMIN_KEY="your-admin-key"
```

See `DEPLOYMENT.md` for detailed instructions.

## Data Management

### Local Development

- Data is saved to `experiment_data/` folder on your laptop
- Files: `participants.csv` and `P001_log.csv`, `P002_log.csv`, etc.
- Easy to backup: just copy the folder

### Cloud Deployment

⚠️ **Important:** When deployed to cloud, data is saved on the **cloud server**, not your laptop!

**Solutions:**

1. **Admin Export Endpoint** (Already added!):
   ```
   https://your-app.onrender.com/admin/export?key=YOUR_ADMIN_KEY
   ```
   Downloads all data as ZIP file

2. **Admin Stats Endpoint**:
   ```
   https://your-app.onrender.com/admin/stats?key=YOUR_ADMIN_KEY
   ```
   View participant count and data statistics

3. **Database** (Recommended for production):
   - Use PostgreSQL on Render/Railway
   - Data persists across redeploys

**See `docs/DATA_ANALYSIS_FEATURES.md` for complete data export guide.**

## Environment Variables

### Required for Production

- `FLASK_SECRET_KEY`: Secret key for session encryption
  - Generate: `openssl rand -hex 32`
  - **Keep this secret!**

### Optional

- `ADMIN_KEY`: Secret key for admin endpoints (`/admin/export`, `/admin/stats`)
- `PORT`: Server port (usually set automatically by hosting platform)
- `FLASK_ENV`: Set to `production` to disable debug mode

## Usage

### Running Locally

```bash
python3 app.py
```

The app will:
1. Load translation cache
2. Pre-translate UI text (fast)
3. Pre-translate all articles (30-60 seconds on first run)
4. Start server on http://127.0.0.1:8080

### Experiment Flow

1. **Language Selection** → Choose English or Chinese
2. **Login** → Participant demographics
3. **Consent** → Informed consent form
4. **Prior Knowledge** → Familiarity, recognition, quiz
5. **AI Trust** → Trust, dependence, skill assessments
6. **Reading Phase** → 3 articles with AI summaries
7. **Testing Phase** → Free recall + multiple-choice questions
8. **Manipulation Check** → Verification questions
9. **Debrief** → Completion page

### Admin Functions

Access data export (after deployment):

```bash
# View statistics
curl "https://your-app.onrender.com/admin/stats?key=YOUR_ADMIN_KEY"

# Download all data
curl "https://your-app.onrender.com/admin/export?key=YOUR_ADMIN_KEY" -o data.zip
```

Or open in browser:
- Stats: `https://your-app.onrender.com/admin/stats?key=YOUR_ADMIN_KEY`
- Export: `https://your-app.onrender.com/admin/export?key=YOUR_ADMIN_KEY`

## Data Files

### participants.csv
- Demographics for all participants
- Columns: `participant_id`, `timestamp`, `full_name`, `profession`, `age`, `gender`, `native_language`

### {participant_id}_log.csv
- Complete experiment data per participant
- Phases: demographics, consent, prior_knowledge, ai_trust, randomization, reading_behavior, recall_response, mcq_responses, manipulation_check

## Troubleshooting

### Translation Issues

- **Slow loading**: First run takes 30-60 seconds to pre-translate. Subsequent runs are instant.
- **Missing translations**: Check `translation_cache/translations.json` exists
- **Chinese not working**: Ensure `deep-translator` is installed: `pip install deep-translator`

### Port Already in Use

```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill
```

### Data Not Saving

- Check `experiment_data/` folder exists and is writable
- Check server logs for errors
- Verify file permissions

### Deployment Issues

- Check environment variables are set correctly
- Verify `requirements.txt` includes all dependencies
- Check build logs on hosting platform
- Ensure `PORT` environment variable is set (most platforms do this automatically)

## Development

### Adding New Articles

Edit `ARTICLES` dictionary in `app.py`:

```python
ARTICLES = {
    'article_key': {
        'title': 'Article Title',
        'text': '''Article text...''',
        'summary_integrated': '''Paragraph summary...''',
        'summary_segmented': '''• Bullet 1\n• Bullet 2...''',
        'questions': [
            {'q': 'Question?', 'options': [...], 'correct': 0},
        ]
    }
}
```

### Modifying Translations

- UI text: Edit templates and wrap in `{{ tr("text") }}`
- Articles: Automatically translated via `_auto_translate()`
- Cache: Stored in `translation_cache/translations.json`

## License

[Add your license here]

## Support

For issues or questions:
1. Check `docs/DEPLOYMENT.md` for deployment help
2. Check `docs/DATA_STORAGE_ANALYSIS.md` for data storage options
3. Check `docs/DATA_ANALYSIS_FEATURES.md` for data export features
4. Review server logs for error messages

## Acknowledgments

Built with Flask, deep-translator, and modern web technologies.



