# Quick Start Guide - AI Memory Experiment

## Post-Test and End Sections

### Skip manipulation check → debrief

**AI Version:**
```
http://127.0.0.1:8080/skip_manipulation
```

**Control Version:**
```
http://127.0.0.1:8081/skip_manipulation
```

---

## To Run Experiments Locally

### Initial Setup (One-time)

```bash
cd ~/Desktop/ai_memory_experiment

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r ai_experiment/requirements.txt
```

---

## To Run AI Experiment

### Step-by-Step Process:

#### 1️⃣ Open Terminal and Start Flask App

```bash
# Navigate to your project
cd ~/Desktop/ai_memory_experiment/ai_experiment

# Activate virtual environment
source ../.venv/bin/activate

# Start Flask
python3 app.py
```

✅ **You should see:**

```
==================================================
AI Memory Experiment Platform
==================================================

Server starting at http://127.0.0.1:8080
 * Running on http://127.0.0.1:8080

⚠️ IMPORTANT: Keep this terminal running! Don't close it.
```

---

## To Run Control Experiment (No AI)

### Step-by-Step Process:

#### 1️⃣ Open Terminal and Start Flask App

```bash
# Navigate to your project
cd ~/Desktop/ai_memory_experiment/no_ai_experiment

# Activate virtual environment
source ../.venv/bin/activate

# Start Flask
python3 app_control.py
```

✅ **You should see:**

```
==================================================
Human Memory Encoding Experiment Platform - CONTROL VERSION (No AI)
==================================================

Server starting at http://127.0.0.1:8081
 * Running on http://127.0.0.1:8081

⚠️ IMPORTANT: Keep this terminal running! Don't close it.
```

**Or run from root directory:**

```bash
cd ~/Desktop/ai_memory_experiment

source .venv/bin/activate

cd no_ai_experiment

python3 app_control.py
```

---

#### 2️⃣ Open a New Terminal Tab (⌘+T) and Start ngrok

**For AI Experiment (port 8080):**
```bash
ngrok http 8080
```

**For Control Experiment (port 8081):**
```bash
ngrok http 8081
```

**You should see something like:**

```
Forwarding    https://semicivilized-yair-columbic.ngrok-free.dev -> http://localhost:8080
```

⚠️ **IMPORTANT:**
- Keep this ngrok terminal running as well.
- If you stop it (Ctrl + C), the link stops working

---

#### 3️⃣ Share the URL with Your Testers

Copy the `https://….ngrok-free.app` or `.dev` URL shown by ngrok and send it to your participants.

When they click it:
- They go directly into your experiment ✅
- No password, no warning page, nothing to click.

---

#### 4️⃣ Monitor Activity

In your Flask terminal, you'll see all incoming requests:

```
127.0.0.1 - - [03/Nov/2025 15:45:23] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [03/Nov/2025 15:45:24] "POST /submit_demographics HTTP/1.1" 302 -
```

This shows who's accessing your experiment and what they're doing.

---

## Running Both Experiments Simultaneously

You can run both experiments at the same time on different ports:

### Option 1: Use the Script (Easiest)
```bash
cd ~/Desktop/ai_memory_experiment
chmod +x run_both_experiments.sh
./run_both_experiments.sh
```

This starts both experiments:
- **AI Experiment:** http://127.0.0.1:8080
- **Control Experiment:** http://127.0.0.1:8081

### Option 2: Manual (Two Terminal Windows)

**Terminal 1 - AI Experiment:**
```bash
cd ~/Desktop/ai_memory_experiment/ai_experiment
source ../.venv/bin/activate
python3 app.py
# Runs on http://127.0.0.1:8080
```

**Terminal 2 - Control Experiment:**
```bash
cd ~/Desktop/ai_memory_experiment/no_ai_experiment
source ../.venv/bin/activate
python3 app_control.py
# Runs on http://127.0.0.1:8081
```

### Using ngrok for Both

You'll need **two ngrok instances** (in separate terminals):

**Terminal 3 - ngrok for AI:**
```bash
ngrok http 8080
```

**Terminal 4 - ngrok for Control:**
```bash
ngrok http 8081
```

Each will get its own public URL that you can share with participants.

See `run_both_experiments.md` for more details.

---

## Data Collection

### AI Experiment Data
- **Location:** `ai_experiment/experiment_data/`
- **Files:** `participants.csv`, `P001_log.csv`, `P002_log.csv`, etc.

### Control Experiment Data
- **Location:** `no_ai_experiment/experiment_data/`
- **Files:** `participants.csv`, `P001_log.csv`, `P002_log.csv`, etc.

All data is automatically saved when participants complete the experiment.

---

## Troubleshooting

**Port already in use?**
- Change the port: `flask --app app_control.py run --port 5002`
- Or stop the other Flask app first

**Virtual environment not found?**
- Make sure you're in the correct directory
- Or create new venv: `python3 -m venv .venv`

**Module not found errors?**
- Install dependencies: `pip install -r requirements.txt`
- Make sure virtual environment is activated

**ngrok not working?**
- Make sure Flask app is running first
- Check that port 8080 (or your chosen port) is correct
- Try restarting ngrok
