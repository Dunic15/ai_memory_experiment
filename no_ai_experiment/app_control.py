"""
Human Memory Encoding Experiment Platform - CONTROL VERSION (No AI)
Flask application (stable sessions, guarded routes, JSON-safe handlers)
CONTROL VERSION: Contains NO AI summaries or AI-related functionality
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json, csv, os, random, subprocess, sys
from datetime import datetime
from functools import wraps
from functools import lru_cache
import fcntl  # For file locking on Unix/macOS
try:
    from deep_translator import GoogleTranslator  # optional; we will use later
except Exception:
    GoogleTranslator = None

# ------------------------------------------------------------------------------
# Language / i18n config
# ------------------------------------------------------------------------------
SUPPORTED_LANGS = {"en": "English", "zh": "中文"}
DEFAULT_LANG = "en"

# ------------------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# Use a STABLE secret key (do NOT rotate on each run or the session cookie dies)
# Set FLASK_SECRET_KEY in your shell for production; this default is fine locally.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Optional: make cookies predictable in localhost dev
app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=False)

DATA_DIR = "experiment_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Translation cache directory - use shared cache from ai_experiment
# This ensures both experiments use the same translations and we only maintain one file
TRANSLATION_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_experiment", "translation_cache")
TRANSLATION_CACHE_FILE = os.path.join(TRANSLATION_CACHE_DIR, "translations.json")

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
 # --- Language helpers ---
def _get_lang():
    lang = session.get("lang") or DEFAULT_LANG
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    return lang

def _set_lang(lang_code: str):
    lang_code = (lang_code or "").lower()
    if lang_code not in SUPPORTED_LANGS:
        lang_code = DEFAULT_LANG
    session["lang"] = lang_code
    session.modified = True
    return lang_code


# Translation cache (in-memory for fast access)
_translation_cache = {}

def _load_translation_cache():
    """Load translation cache from file"""
    global _translation_cache
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                _translation_cache = json.load(f)
                print(f"✓ Loaded {len(_translation_cache)} cached translations")
        except Exception as e:
            print(f"Error loading translation cache: {e}")
            _translation_cache = {}

def _save_translation_cache():
    """Save translation cache to file"""
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_translation_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving translation cache: {e}")

def _get_cache_key(text: str, target_lang: str) -> str:
    """Generate cache key for translation"""
    return f"{target_lang}:{text}"

def _auto_translate(text: str, target_lang: str) -> str:
    """
    Translate text to target language using GoogleTranslator.
    Uses file-based cache for persistence, in-memory cache for speed.
    Maps 'zh' to 'zh-CN' for Simplified Chinese.
    Handles long texts by chunking (Google Translator has 5000 char limit).
    """
    if not text or target_lang == "en":
        return text
    
    # Check in-memory cache first (fastest)
    cache_key = _get_cache_key(text, target_lang)
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]
    
    # If not in cache, translate (this should rarely happen after pre-translation)
    try:
        if GoogleTranslator is None:
            return text
        # Map 'zh' to 'zh-CN' (Simplified Chinese) for GoogleTranslator
        translator_lang = "zh-CN" if target_lang == "zh" else target_lang
        translator = GoogleTranslator(source="auto", target=translator_lang)
        
        # Google Translator has a 5000 character limit - split long texts
        if len(text) > 4500:
            import re
            import time
            # Split by sentences
            sentences = re.split(r'([.!?]\s+)', text)
            translated_parts = []
            current_chunk = ""
            
            for part in sentences:
                if len(current_chunk + part) > 4000:
                    # Translate current chunk
                    if current_chunk.strip():
                        chunk_translated = translator.translate(current_chunk.strip())
                        translated_parts.append(chunk_translated)
                        time.sleep(0.1)  # Small delay between chunks
                    current_chunk = part
                else:
                    current_chunk += part
            
            # Translate remaining chunk
            if current_chunk.strip():
                chunk_translated = translator.translate(current_chunk.strip())
                translated_parts.append(chunk_translated)
            
            translated = "".join(translated_parts)
        else:
            translated = translator.translate(text)
        
        # Save to cache
        _translation_cache[cache_key] = translated
        _save_translation_cache()
        
        return translated
    except Exception as e:
        # If translation fails, return original text
        print(f"Translation error: {e}")
        return text

# --- Simple translate helper exposed to templates (will be wired in next step) ---
def tr(text: str) -> str:
    """Translate a short UI string to the current session language.
    Falls back to the original text if translator is unavailable or lang is 'en'."""
    lang = _get_lang()
    return _auto_translate(text or "", lang)

def _normalize_timestamp_value(value):
    """Normalize timestamp inputs to ISO 8601 with timezone offset."""
    if value is None:
        return value
    s = str(value).strip()
    if s.isdigit() and len(s) == 13:
        local_tz = datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(int(s) / 1000, tz=local_tz).isoformat()
    if "T" in s:
        iso = s
        if iso.endswith("Z"):
            iso = iso[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(iso)
        except ValueError:
            return s
        local_tz = datetime.now().astimezone().tzinfo
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        else:
            dt = dt.astimezone(local_tz)
        return dt.isoformat()
    return s

def require_pid(fn):
    """Ensure a participant is in session before accessing post-login routes."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "participant_id" not in session:
            # For skip routes, try to ensure PID exists
            # This helps when coming from skip routes that might not have persisted session
            try:
                _ensure_pid()
            except Exception:
                pass
            # Check again after ensuring
            if "participant_id" not in session:
                if request.is_json:
                    return jsonify({"redirect": url_for("index")}), 401
                return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

def csv_len(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        rows = list(r)
        if not rows:
            return 0
        # crude header detection
        if rows[0] and any(h in rows[0][0].lower() for h in ["participant", "timestamp"]):
            return max(0, len(rows) - 1)
        return len(rows)

def get_participant_id():
    """Atomically get the next participant ID using file locking to prevent race conditions.
    
    Uses an atomic counter file to ensure no two sessions get the same ID,
    even when started simultaneously.
    """
    counter_file = os.path.join(DATA_DIR, ".participant_counter")
    lock_file = counter_file + ".lock"
    csv_file = os.path.join(DATA_DIR, "participants.csv")
    
    # Create lock file if it doesn't exist (with proper permissions)
    if not os.path.exists(lock_file):
        try:
            with open(lock_file, 'w') as f:
                os.chmod(lock_file, 0o644)
        except (IOError, OSError):
            pass  # Another process might have created it
    
    # Acquire exclusive lock
    with open(lock_file, 'r') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        
        try:
            # Read current counter, or initialize from participants.csv if counter doesn't exist
            if os.path.exists(counter_file):
                try:
                    with open(counter_file, 'r') as f:
                        n = int(f.read().strip())
                    # Validate counter is not less than CSV count (safety check)
                    csv_count = csv_len(csv_file)
                    if n < csv_count:
                        # Counter is behind CSV, sync it
                        n = csv_count
                except (ValueError, IOError):
                    # Fallback to CSV length if counter is corrupted
                    n = csv_len(csv_file)
            else:
                # Initialize counter from existing participants.csv
                n = csv_len(csv_file)
            
            # Increment and save atomically
            n += 1
            with open(counter_file, 'w') as f:
                f.write(str(n))
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            return f"P{n:03d}"
        finally:
            # Lock is released when file is closed
            pass

def _generate_analysis_if_needed(participant_id, phase=None):
    """Generate analysis report automatically when participant completes experiment"""
    # CONTROL VERSION: Generate analysis when participant reaches debrief (no manipulation_check phase)
    # This function can be called from debrief route (phase=None) or with a phase parameter for compatibility
    try:
        # Get the path to analyze_participant.py
        analysis_script = os.path.join(os.path.dirname(__file__), "data_analysis", "analyze_participant.py")
        
        if not os.path.exists(analysis_script):
            print(f"[Analysis] Analysis script not found: {analysis_script}")
            return  # Analysis script not found, skip
        
        # Check if log file exists - try both filename formats
        log_file = os.path.join(DATA_DIR, f"{participant_id}_log.csv")
        if not os.path.exists(log_file):
            # Try to find log file with name in filename
            import glob
            pattern = os.path.join(DATA_DIR, f"{participant_id}-*-NON-AI_log.csv")
            matches = glob.glob(pattern)
            if matches:
                log_file = matches[0]
            else:
                print(f"[Analysis] Log file not found for {participant_id}")
                return  # Log file doesn't exist yet, skip
        
        # Run analysis in background (non-blocking)
        # Use subprocess.Popen to run asynchronously
        subprocess.Popen(
            [sys.executable, analysis_script, participant_id],
            cwd=os.path.dirname(analysis_script),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[Analysis] Triggered automatic analysis generation for {participant_id}")
    except Exception as e:
        # Silently fail - don't interrupt the main flow if analysis generation fails
        print(f"[Analysis] Failed to generate analysis for {participant_id}: {e}")

def log_data(participant_id, phase, data):
    # Get participant name for better filename (no_ai experiment always uses NON-AI suffix)
    name = session.get("demographics", {}).get("full_name", "").strip()
    data = dict(data or {})
    if "timestamp" in data:
        data["timestamp"] = _normalize_timestamp_value(data.get("timestamp"))
    
    # Clean name for filename (remove spaces, special chars)
    if name:
        clean_name = name.replace(" ", "-").replace(",", "").replace(".", "")
        filename = os.path.join(DATA_DIR, f"{participant_id}-{clean_name}-NON-AI_log.csv")
        
        # If old file exists, rename it
        old_filename = os.path.join(DATA_DIR, f"{participant_id}_log.csv")
        if os.path.exists(old_filename) and not os.path.exists(filename):
            try:
                os.rename(old_filename, filename)
            except:
                pass  # If rename fails, continue with new filename
    else:
        # Fallback to old format if name not available yet
        filename = os.path.join(DATA_DIR, f"{participant_id}_log.csv")
    
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp", "phase"] + list(data.keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            w.writeheader()
        w.writerow({"timestamp": datetime.now().astimezone().isoformat(), "phase": phase, **data})
    
    # Note: Analysis is now generated automatically when participant reaches debrief page
    # (No manipulation_check phase in control version)

def save_participant(participant_id, data):
    """Atomically save participant data using file locking to prevent race conditions."""
    csv_file = os.path.join(DATA_DIR, "participants.csv")
    lock_file = csv_file + ".lock"
    
    # Create lock file if it doesn't exist
    if not os.path.exists(lock_file):
        with open(lock_file, 'w') as f:
            pass
    
    # Acquire exclusive lock
    with open(lock_file, 'r') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        
        try:
            file_exists = os.path.exists(csv_file)
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                fieldnames = ["participant_id", "timestamp"] + list(data.keys())
                w = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    w.writeheader()
                w.writerow({"participant_id": participant_id, "timestamp": datetime.now().isoformat(), **data})
        finally:
            # Lock is released when file is closed
            pass
# --- Test Mode toggle (only affects reading skip) ---
TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"

@app.context_processor
def inject_test_mode():
    return {"test_mode": TEST_MODE}

# ------------------------------------------------------------------------------
# Expose language/i18n context to templates
# ------------------------------------------------------------------------------
@app.context_processor
def inject_i18n():
    def article_i18n(article_key: str):
        lang = _get_lang()
        art = ARTICLES.get(article_key, {})
        if not art:
            return {}
        if lang == "en":
            return art
        # CONTROL VERSION: Use manual translations from shared cache only (no AI summaries)
        localized = {}
        for k in [
            "title",
            "free_recall_prompt",
            "text",
            # summary_integrated and summary_segmented removed - no AI functionality
        ]:
            english_text = art.get(k, "")
            if not english_text:
                localized[k] = ""
                continue
            
            # Check shared cache for manual translation only (no auto-translate)
            cache_key = _get_cache_key(english_text, lang)
            if cache_key in _translation_cache:
                localized[k] = _translation_cache[cache_key]
            else:
                # No translation found - return English as fallback
                localized[k] = english_text
        
        # Questions: translate only the text portions using manual translations from shared cache
        qs = []
        for q in art.get("questions", []):
            question_text = q.get("q", "")
            cache_key_q = _get_cache_key(question_text, lang)
            translated_q = _translation_cache.get(cache_key_q, question_text)
            
            translated_options = []
            for opt in q.get("options", []):
                cache_key_opt = _get_cache_key(opt, lang)
                translated_opt = _translation_cache.get(cache_key_opt, opt)
                translated_options.append(translated_opt)
            
            qs.append({
                "q": translated_q,
                "options": translated_options,
                "correct": q.get("correct"),
            })
        localized["questions"] = qs
        return localized

    return {
        "current_lang": _get_lang(),
        "supported_langs": SUPPORTED_LANGS,
        "tr": tr,
        "t": tr,
        "article_i18n": article_i18n,
    }

# ------------------------------------------------------------------------------
# Helper for routes: fetch a localized article dict based on current session lang
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Helper for routes: fetch a localized article dict based on current session lang
# ------------------------------------------------------------------------------
def get_localized_article(article_key: str) -> dict:
    """
    Get localized article content. 
    For Chinese: Only uses manual translations from shared cache (no auto-translation).
    If translation not found, returns English text as fallback.
    CONTROL VERSION: No AI summaries in localization.
    """
    lang = _get_lang()
    art = ARTICLES.get(article_key, {})
    if not art or lang == "en":
        return art
    # CONTROL VERSION: No AI summaries in localization
    localized = {}
    for k in [
        "title",
        "free_recall_prompt",
        "text",
        # summary_integrated and summary_segmented removed - no AI functionality
    ]:
        english_text = art.get(k, "")
        if not english_text:
            localized[k] = ""
            continue
        
        # Check shared cache for manual translation only (no auto-translate)
        cache_key = _get_cache_key(english_text, lang)
        if cache_key in _translation_cache:
            localized[k] = _translation_cache[cache_key]
        else:
            # No translation found - return English as fallback
            # (User will add manual translations to shared cache)
            localized[k] = english_text
    
    # Translate questions text/options; keep 'correct' index as-is
    # Use manual translations from shared cache only
    qs = []
    for q in art.get("questions", []):
        question_text = q.get("q", "")
        cache_key_q = _get_cache_key(question_text, lang)
        translated_q = _translation_cache.get(cache_key_q, question_text)
        
        translated_options = []
        for opt in q.get("options", []):
            cache_key_opt = _get_cache_key(opt, lang)
            translated_opt = _translation_cache.get(cache_key_opt, opt)
            translated_options.append(translated_opt)
        
        qs.append({
            "q": translated_q,
            "options": translated_options,
            "correct": q.get("correct"),
        })
    localized["questions"] = qs
    return localized

# ------------------------------------------------------------------------------
# DEV routes to verify language + translation pipeline
# ------------------------------------------------------------------------------
@app.route("/dev/lang")
def dev_lang():
    return jsonify({
        "current_lang": _get_lang(),
        "session_keys": list(session.keys()),
    })

@app.route("/dev/i18n_preview/<article_key>")
def dev_i18n_preview(article_key):
    art = get_localized_article(article_key)
    if not art:
        return jsonify({"error": "unknown article_key"}), 404
    return jsonify({"lang": _get_lang(), **art})
# ------------------------------------------------------------------------------
# Materials
# ------------------------------------------------------------------------------
ARTICLES = {
    'uhi': {
        'title': 'Urban Heat Islands: Causes, Consequences, and What Works',
        'free_recall_prompt': 'Please write everything you remember from the article within 5 minutes. Try to describe main ideas and relationships — causes, consequences, and solutions — in your own words.',
        'text': '''Cities function as complex heat systems where buildings, roads, and the atmosphere interact to create persistent temperature differences. Every street, rooftop, and road acts as a heat storage unit: during the day, asphalt roads, brick buildings, and concrete structures absorb sunlight and convert this energy into heat. Unlike green spaces that cool through water evaporation and reflection, city surfaces continuously store heat throughout daylight hours. When night falls and the sun disappears, these stored heat sources release infrared radiation back into the lower atmosphere. This heat release is restricted by urban canyon geometry—the ratio of building height to street width—which traps outgoing radiation through multiple reflections between surfaces before it can escape to the atmosphere. As a result, central city areas show nighttime temperatures three to seven degrees Celsius higher than surrounding suburban areas, creating what scientists call the urban heat island (UHI) effect. During heat waves, this temperature increase adds to baseline warming, raising energy use for air conditioning, worsening air quality through smog formation, and increasing heat stress among vulnerable populations.

The size of these temperature differences comes from combined physical, material, and airflow factors that together determine the urban energy balance. Surface reflectivity—measured through the albedo coefficient ranging from zero (complete absorption) to one (perfect reflection)—plays a crucial role in determining absorbed solar energy. Fresh asphalt surfaces have albedo values around 0.05, reflecting only five percent of incoming sunlight while absorbing ninety-five percent. Aged asphalt oxidizes to slightly higher reflectance (~0.12), but remains much darker than vegetated ground cover (albedo ~0.20–0.25). Low-albedo surfaces therefore work as efficient solar collectors that convert radiation into stored heat. Additionally, the material-specific thermal mass—defined as heat storage capacity—controls the speed of heating and cooling. Dense construction materials including concrete, brick, and stone have high thermal mass, enabling prolonged energy storage that delays nighttime cooling. This storage-release cycle operates continuously: buildings absorb radiation throughout the day, then gradually release stored heat after sunset, maintaining elevated nighttime temperatures for extended periods.

Urban geometry further increases heat retention through urban canyon effects. Tall buildings along narrow streets create confined spaces that restrict both incoming sunlight during midday and outgoing radiation at night. Within these canyons, solar radiation bounces between surfaces multiple times before escaping to the atmosphere, increasing the chance of absorption with each bounce. The three-dimensional structure therefore functions as a heat trap, maximizing energy capture while minimizing cooling pathways. At the same time, restricted airflow between building walls prevents convective heat removal—the mechanical transport of heat through air movement—thus blocking one of the atmosphere's main cooling mechanisms. Finally, human-generated waste heat from vehicle engines, building heating and cooling systems, and industrial processes adds extra heat directly into the urban atmosphere, supplementing solar heating. During extreme heat events, power companies respond to increased electricity demand by activating less efficient backup generators, often coal-burning plants that emit greenhouse gases while using water for cooling towers, creating a feedback loop where heat reduction efforts paradoxically generate additional emissions and resource use.

The geographic distribution of heat stress maps directly onto socioeconomic patterns, creating environmental justice issues with measurable health impacts. Neighborhoods with concentrated poverty, reduced tree coverage, higher building density, and more impervious surfaces experience disproportionately higher heat exposure. During severe heat episodes—defined as sustained periods exceeding normal temperature ranges—mortality risk increases dramatically with heat intensity, affecting elderly people, individuals with heart or breathing problems, outdoor workers, and residents without air conditioning. Emergency medical systems face surging demand for heat-related care, straining healthcare resources. Thus, the urban heat island is both a physical weather phenomenon with measurable temperature differences and a social inequality issue that reflects unequal resource distribution, infrastructure investment, and resilience capacity across urban populations.

Counteracting these heat processes requires integrated strategies across multiple scales. The basic principle involves modifying surface energy budgets through four connected mechanisms: increasing reflectance, providing shade, amplifying evaporative cooling, and manipulating thermal mass. Cool roofing systems coated with high-albedo materials can raise surface reflectance from typical values (~0.10–0.20) to enhanced levels approaching 0.70–0.85, thereby reducing absorbed solar energy by sixty to seventy-five percent. Similarly, "cool pavements" using lighter-colored materials or permeable designs that allow subsurface moisture show surface temperature reductions of ten to twenty degrees Celsius compared to conventional asphalt during peak sun exposure. However, these solutions require careful design: increased visible light reflection without corresponding infrared reduction can increase glare, creating visual discomfort and potentially raising nearby air temperatures through redirected radiation. Optimal cool surface technologies therefore use wavelength-selective coatings that maximize near-infrared reflection—where solar energy peaks—while moderating visible brightness.

Vegetation provides complementary temperature control through multiple biological processes. Tree canopies intercept sunlight before it reaches the ground, creating shaded areas beneath leaves. More importantly, leaf transpiration—the controlled release of water vapor through plant pores—converts heat into water evaporation energy. This evapotranspiration process effectively works as a distributed atmospheric cooling system that moderates temperatures while simultaneously increasing local humidity. Urban forestry programs thus serve dual heat reduction functions: direct shade plus evaporative cooling. Green infrastructure at smaller scales—including vegetated rooftops, vertical gardens, and bioswales for stormwater management—extends these principles across building surfaces and street features. Nevertheless, vegetation faces implementation challenges including water availability in dry regions, maintenance costs, conflicts with underground utilities, and long growth periods before benefits fully develop.

Beyond individual interventions, systemic resilience requires comprehensive urban planning that integrates heat considerations into land-use decisions, building codes, and infrastructure priorities. Zoning regulations can mandate minimum tree coverage ratios, restrict impervious surface percentages, or incentivize cool material use through development bonuses. Building energy standards increasingly include thermal performance metrics—such as roof solar reflectance indices and wall thermal resistance—that reduce cooling needs while improving indoor comfort. Transportation planning that prioritizes pedestrian areas, cycling networks, and transit-oriented development reduces vehicle heat emissions while creating opportunities for shade trees and permeable surfaces. Critically, equitable climate adaptation requires targeting interventions toward thermally vulnerable neighborhoods through needs-based resource allocation rather than allowing market forces alone to determine cooling infrastructure distribution.

Emerging research explores advanced technologies including radiative cooling materials engineered to emit heat at atmospheric transparency wavelengths (8–13 micrometer infrared band), enabling passive heat rejection directly to space even during daylight. Phase-change materials within building walls can buffer indoor temperature changes by absorbing heat during warming periods and releasing it during cooling cycles. District-scale energy systems that recover waste heat for beneficial uses—such as district heating networks or industrial integration—reduce overall heat emissions. However, these innovations remain expensive compared to conventional materials, limiting adoption without regulations or subsidies.

Ultimately, urban heat mitigation represents a sociotechnical challenge requiring coordinated action across governance levels, professional fields, and community stakeholders. Scientific understanding of heat transfer physics, materials science, and atmospheric dynamics provides the mechanistic foundation. Engineering expertise translates theoretical principles into practical cool surface technologies, green infrastructure systems, and building innovations. Urban planning synthesizes these technical capabilities within spatial frameworks that account for land-use patterns, transportation networks, and social equity considerations. Community engagement ensures that interventions address local needs, incorporate traditional knowledge, and build adaptive capacity among residents. Success depends not merely on technology deployment but on institutional arrangements that sustain long-term maintenance, equitable access, and continuous adaptation as climate and urban form evolve. The heat island thus becomes not only a physical problem with engineering solutions but a lens revealing how cities balance efficiency with resilience, economic growth with environmental quality, and overall prosperity with distributional justice.
''',
        'questions': [
            {
                "q": "Dark, low-albedo surfaces such as asphalt absorb approximately _______ percent of incoming solar radiation.",
                "options": [
                    "seventy to seventy-five",
                    "seventy-five to eighty",
                    "ninety to ninety-five",
                    "eighty to eighty-five"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "_______ materials store large amounts of heat during the day and release it slowly after sunset.",
                "options": [
                    "Low thermal mass",
                    "Reflective",
                    "Porous",
                    "High thermal mass"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Urban greening provides _______ through shading and leaf transpiration.",
                "options": [
                    "conductive cooling",
                    "evaporative cooling",
                    "radiative cooling",
                    "convective cooling"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "The article identifies _______ as a functioning urban-cooling technology.",
                "options": [
                    "phase-change wall layers",
                    "radiative cooling materials",
                    "photocatalytic roof tiles",
                    "waste-heat recovery networks"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Cool roofs reduce heat absorption because their surface reflectance commonly reaches _______.",
                "options": [
                    "0.30–0.45",
                    "0.50–0.65",
                    "0.70–0.85",
                    "0.65–0.80"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "Neighborhoods with the highest heat exposure often lack adequate _______.",
                "options": [
                    "coastal airflow",
                    "open water bodies",
                    "tree canopy and permeable surfaces",
                    "shaded pedestrian corridors"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "High-albedo roofing systems limit heat gain primarily by _______.",
                "options": [
                    "reducing absorbed solar flux",
                    "increasing thermal mass storage",
                    "promoting moisture-driven cooling",
                    "redistributing longwave radiation"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Urban canyon geometry traps _______ through repeated reflections between building surfaces.",
                "options": [
                    "outgoing longwave radiation",
                    "thermal mass discharge",
                    "convective airflow",
                    "incoming solar reflection"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Urban heat islands develop when city surfaces absorb more ______ than nearby rural areas.",
                "options": [
                    "atmospheric longwave radiation",
                    "infrared radiation",
                    "solar energy",
                    "geothermal heat flux"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "Vegetated ground cover typically exhibits an albedo of _______.",
                "options": [
                    "0.05–0.10",
                    "0.10-0.15",
                    "0.20–0.25",
                    "0.45–0.50"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "Aged asphalt usually has an albedo of approximately _______.",
                "options": [
                    "0.05",
                    "0.12",
                    "0.22",
                    "0.30"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Excess visible-light reflection from cool surfaces can cause _______.",
                "options": [
                    "increased ozone depletion",
                    "glare from redirected radiation",
                    "excessive nighttime cooling",
                    "reduced soil moisture"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Urban centers can be _______ warmer at night than nearby suburban areas.",
                "options": [
                    "3–7°C",
                    "7–10°C",
                    "1–2°C",
                    "10–12°C"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Cool pavements can lower surface temperatures by approximately _______.",
                "options": [
                    "4–8°C",
                    "10–20°C",
                    "20–30°C",
                    "2–5°C"
                ],
                "correct": 1,
                "source_type": "article"
            }
        ]
    },
    'crispr': {
        'title': 'CRISPR Gene Editing: Promise, Constraints, and Responsible Use',
        'free_recall_prompt': 'Please recall everything you can from the article in 5 minutes, describing how CRISPR works, its medical and agricultural applications, key limitations, and ethical or governance challenges.',
        'text': '''CRISPR–Cas systems began as a microbial defense mechanism—a molecular form of immune memory that bacteria use to recognize and destroy invading viruses. Each infection leaves behind a short fragment of viral DNA in the bacterial genome, creating a permanent biological record of attack. When the same virus returns, the bacterium transcribes these fragments into RNA guides that direct Cas enzymes toward matching sequences, cutting the viral DNA apart. This elegant process of recognition and cleavage inspired scientists to adapt the system for their own purposes. By designing synthetic guide RNAs that match any chosen DNA sequence, researchers can steer Cas enzymes precisely to that site, slice the double helix, and let the cell's repair machinery rewrite it. The principle—guide, cut, repair—has turned a bacterial trick for survival into one of the most powerful tools in modern biology.
The accessibility of CRISPR has been revolutionary. Tasks that once required months of effort with complex tools such as zinc-finger nucleases or TALENs can now be performed in days with inexpensive reagents in basic labs. This democratization of gene editing has accelerated discoveries in medicine, agriculture, and environmental restoration. Yet CRISPR's simplicity hides layers of complexity. Precision in genomics is statistical, not absolute: even a well-designed guide RNA may bind unintended DNA regions, creating off-target edits that disrupt other genes. The challenge is not only to cut accurately but to ensure the cut happens only where intended.
To reduce these risks, scientists refine the system continuously. They adjust guide length and chemistry, develop predictive algorithms, and engineer enzymes with improved fidelity. High-precision variants such as SpCas9-HF1 or eSpCas9 modify the DNA-binding surface to minimize unwanted interactions. Newer tools—base editors and prime editors—go further by avoiding full double-strand breaks. Instead of cutting both DNA strands, they replace single letters or copy short sequences, allowing subtle corrections with fewer side effects. The shift from crude cutting to molecular fine-tuning expands the range of treatable genetic mutations.
Despite these refinements, delivery remains the hardest step. Editing components must enter the right cells, reach the nucleus, and act without triggering immune rejection. Viral vectors such as adeno-associated viruses (AAVs) are efficient but have limited cargo space and may provoke antibodies that block repeated dosing. Lipid nanoparticles—used in mRNA vaccines—can carry larger molecules but concentrate in the liver and sometimes cause inflammation. Researchers test polymer carriers, extracellular vesicles, and tissue-targeted peptides, as well as physical methods like electroporation or ultrasound delivery. Each approach must balance efficiency, safety, and cost.
Another key dimension is time. Even when CRISPR reaches its target cells, how long it remains active determines both success and risk. Persistent Cas activity raises the chance of off-target effects, while too brief exposure can yield incomplete edits. To control timing, scientists design self-limiting systems whose messenger RNA or protein degrades within hours, creating a short, precise "editing pulse." Others build inducible switches that activate Cas enzymes only under specific chemical or thermal cues. These strategies transform CRISPR from a static scalpel into a controllable process that clinicians can tune in real time.
When CRISPR enters clinical use, the definition of success changes. In research, success means confirming an edit; in medicine, it means improving a patient's life with acceptable risk. The most promising therapies today are ex vivo treatments for blood disorders such as sickle-cell disease and beta-thalassemia. Doctors extract a patient's stem cells, edit them outside the body, verify accuracy, and reinfuse them. For internal organs—heart, brain, or lungs—in vivo delivery is required, where precision must coexist with safety. Every edited cell carries its modification for life, so long-term monitoring is both scientific and ethical duty.
The most controversial frontier is germ-line editing, which alters embryos or reproductive cells so that changes pass to future generations. In theory, this could eliminate hereditary diseases, but the ethical implications are profound. A single error in an embryo could propagate indefinitely through descendants who never consented. After the 2018 birth of gene-edited babies in China, global backlash led to bans on clinical germ-line editing while allowing strictly supervised research. Most experts agree that humanity is not ready for heritable interventions until long-term safety and public oversight exist. Germ-line editing thus stands as both symbol of hope and warning against scientific hubris.
Beyond medicine, CRISPR is reshaping agriculture and ecology. Gene-edited crops can resist blight, tolerate drought, or use nutrients more efficiently, reducing pesticide dependence and boosting yields. Scientists are also creating gene drives that spread chosen traits through pest populations to control malaria mosquitoes or invasive rodents. Yet these systems could cause unpredictable ecological cascades. Regulators therefore distinguish between gene-edited organisms, which carry small, natural-like changes, and transgenic ones that include foreign DNA. This difference affects labeling, trade, and public acceptance. Transparency matters: people tend to support edits that offer visible benefits—less pesticide, better nutrition—over those seen as corporate advantages. Ensuring fair access to improved seeds and tools will decide whether CRISPR becomes a driver of sustainability or inequality.
Ethically, the technology forces society to reconsider long-standing dilemmas. Who defines therapy versus enhancement? Should editing correct blindness but not boost intelligence? How can fairness be maintained if only the wealthy can afford interventions? Effective governance must be inclusive and continuous, combining transparency, accountability, and public participation. Ethics committees should involve not only scientists but also patients, educators, and citizens. Public trial registries, independent audits, and "red-team" risk assessments can turn ethics from restriction into feedback, ensuring that oversight grows alongside innovation.
Meanwhile, CRISPR continues to evolve. New Cas proteins such as Cas12, Cas13, and CasΦ broaden its functions. AI systems design more accurate guide RNAs and predict off-target risks. CRISPR-based diagnostics like SHERLOCK and DETECTR detect pathogens quickly and cheaply, proving that editing enzymes can also serve as molecular sensors. Hybrid systems now connect CRISPR to epigenetic switches, allowing scientists to regulate genes without cutting DNA—an evolution from editing to modulation, where activity is tuned rather than rewritten.
As the field matures, transparency becomes the foundation of credibility. Early breakthroughs were publicized through press releases, but today journals and regulators require full datasets on accuracy, durability, and immune response. Open databases track clinical trials, and funding agencies promote preregistration to prevent selective reporting. Maintaining trust now depends on rigor in both science and communication.
The next challenge is integration into real health systems. Hospitals must develop facilities for gene therapy; insurers must adapt payment models for one-time cures; universities must train clinicians fluent in genetics and ethics. In lower-income regions, priorities include building local capacity and sharing open-source protocols so benefits do not remain confined to wealthy nations. Partnerships among universities, agencies, and non-profits can create regional hubs for reagent production and quality control, ensuring global access.
Finally, biosecurity adds another layer of responsibility. Because CRISPR components are cheap and widely available, safety norms and education are essential. The same openness that empowers research could also enable misuse. Shared international standards for sequence screening, safe laboratory practices, and reporting will help openness and security evolve together. Just as cybersecurity grew with the internet, biotechnology must develop its own culture of vigilance.
Ultimately, CRISPR is more than a laboratory tool—it is a mirror of human values. It reveals how societies balance curiosity with caution and innovation with fairness. When data are shared openly, benefits distributed equitably, and oversight continuous, gene editing can move from disruptive novelty to a stable force for medicine, agriculture, and conservation. Its legacy will be written not only in DNA sequences but in the choices humanity makes about how—and why—to rewrite the code of life.
''',
        'questions': [
            {
                "q": "CRISPR began as _______ that allows bacteria to capture pieces of viral DNA.",
                "options": [
                    "a bacterial immune system",
                    "a viral defense mechanism",
                    "a cellular repair system",
                    "a genetic storage method"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Early CRISPR crop research produced _______",
                "options": [
                    "early test versions",
                    "lab-phase cultivation variants",
                    "commercial products",
                    "experimental prototypes"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Early CRISPR diagnostic tools like SHERLOCK and DETECTR were initially designed to monitor _______.",
                "options": [
                    "pathogen presence",
                    "DNA repair activity",
                    "genome-wide mutation patterns",
                    "guide RNA efficiency"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Scientists reprogrammed CRISPR using _______ to direct Cas enzymes.",
                "options": [
                    "protein markers",
                    "DNA templates",
                    "guide RNA",
                    "chemical signals"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "Compared to TALENs, CRISPR is faster, cheaper, and _______",
                "options": [
                    "easier to program",
                    "widely adopted",
                    "highly adaptable",
                    "technically refined"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Off-target edits occur when guide RNAs _______",
                "options": [
                    "bind mismatched sequences",
                    "bind partially similar sites",
                    "pair with near-matching bases",
                    "drift to adjacent regions"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Base editors modify DNA without _______",
                "options": [
                    "using guide RNA",
                    "breaking both strands",
                    "requiring enzymes",
                    "cellular repair"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "AAV vectors are efficient but have limited _______",
                "options": [
                    "precision",
                    "capacity",
                    "persistence",
                    "flexibility"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Lipid nanoparticles concentrate in the _______",
                "options": [
                    "kidneys",
                    "lungs",
                    "heart",
                    "liver"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Self-limiting systems use components that _______",
                "options": [
                    "degrade fast",
                    "decay naturally",
                    "become unstable",
                    "accumulate slow"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Ex vivo editing allows doctors to _______ before reinfusion.",
                "options": [
                    "modify doses",
                    "test compatibility",
                    "verify accuracy",
                    "label samples"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "A major challenge in CRISPR therapy is ensuring that editing components reach the nucleus and act without triggering _______.",
                "options": [
                    "excessive DNA replication",
                    "immune rejection",
                    "metabolic suppression",
                    "oxidative stress"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Inducible switches activate Cas enzymes only when exposed to specific _______.",
                "options": [
                    "molecular signals",
                    "chemical or thermal cues",
                    "membrane receptors",
                    "electrical pulses"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "The CRISPR process follows: guide, cut, and _______",
                "options": [
                    "restore",
                    "replicate",
                    "repair",
                    "remove"
                ],
                "correct": 2,
                "source_type": "article"
            }
        ]
    },
    'semiconductors': {
        'title': 'Semiconductor Supply Chains: Why Shortages Happen and How to Build Resilience',
        'free_recall_prompt': 'Please recall everything you can from the article in 5 minutes. Describe why semiconductor shortages occurred, what structural factors made supply fragile, and how visibility, flexibility, contracts, and cooperation can strengthen resilience.',
        'text': '''Modern economies depend on semiconductors with a totality that remained invisible until scarcity made it undeniable. Every automobile, smartphone, and medical monitor relies on microchips that manage power flows and interpret signals. Between 2020 and 2022, the world discovered how invisible dependencies could unravel when they failed suddenly and in parallel. Automakers idled production lines awaiting five-dollar microcontrollers, while game console manufacturers saw device orders delayed for months. The shortage wasn't a single failure but a cascade: pandemic-driven demand for consumer electronics collided with frozen supply as Asian factories idled, maritime ports congested, and a catastrophic fire at a Japanese silicate facility severed a critical material node. Each disruption spread through the supply web, magnifying fragility. The semiconductor industry's total market reached $574 billion in 2022, yet production concentrated in fewer than 200 facilities globally, with leading-edge plants requiring capital investments exceeding $20 billion per facility.

Semiconductor fabrication resists rapid expansion by its intrinsic nature. Building a fabrication plant—commonly called a "fab"—demands capital spending exceeding ten billion dollars and requires multi-year timelines. Taiwan Semiconductor Manufacturing Company announced in 2021 that its Arizona facility would not achieve volume production until 2024-2026. Process nodes—measured in nanometers—have shrunk from 10 micrometers in 1971 to 3 nanometers by 2022, a 3,000-fold reduction requiring exponentially more precise equipment. At the 3nm node, transistor gates measure approximately 48 silicon atoms wide, approaching quantum mechanical limits where electron tunneling effects compromise device reliability. When economies reopened after pandemic lockdowns, demand forecasting collapsed—mature nodes suddenly became bottleneck-critical precisely when pre-pandemic capacity allocation had favored cutting-edge processes.

Inside foundries, production follows rhythms that resist acceleration. Silicon wafers move through cleanroom environments for months, undergoing photolithography to create nanoscale circuit patterns—a process dominated by Netherlands-based ASML, whose extreme ultraviolet lithography systems cost over $150 million per unit. Each machine uses 13.5-nanometer wavelength light generated by vaporizing tin droplets with high-power lasers—a process so complex that ASML produces only dozens of machines annually despite controlling over 90% of the market. Manufacturing demands sequential processing across hundreds of individual steps spanning weeks of continuous operation. Any contamination event—measured in parts per trillion—can compromise entire wafer batches. Yield—the proportion of functional chips per wafer—becomes the critical metric.

Bottlenecks emerge not merely in capital equipment but in specialized materials: photoresist compounds require ultra-pure resins with nanometer-scale resolution; high-purity gases at 99.999% purity levels; rare-earth dopants for dielectric materials. The February 2021 winter storm in Texas shut down a chemical synthesis plant responsible for semiconductor-grade coatings, halting chip output globally despite fully operational fabrication facilities on other continents. The event revealed how seemingly peripheral inputs could disable an entire production ecosystem valued at over half a trillion dollars annually.

Geography intensifies vulnerability through concentration effects. East Asia dominates fabrication capacity: Taiwan Semiconductor Manufacturing Company controls over half of global advanced-node production. South Korean companies Samsung and SK Hynix manufacture 70% of global DRAM and 50% of NAND flash memory. Design and intellectual property originate predominantly from United States firms whose annual R&D spending collectively exceeds $45 billion, while photolithography equipment remains a near-monopoly of Netherlands-based ASML. No single nation can perform the entire production sequence independently within economically viable parameters—a reality demonstrated by China's $150 billion domestic semiconductor initiative achieving limited success in advanced logic despite massive capital investment.

The industry historically relied on just-in-time logistics to minimize inventory carrying costs. Semiconductors violate the assumptions underlying this model. Manufacturing cycles span months, not days; demand volatility shifts sharply due to macroeconomic disruptions; and product portfolios include over 50,000 distinct part numbers with non-interchangeable applications. When automotive demand collapsed in Q2 2020, foundries reallocated capacity toward consumer electronics where work-from-home dynamics drove shipments upward. The automotive sector's recovery in 2021 found no available capacity: nodes favored by automotive microcontrollers had been deprioritized in favor of advanced nodes serving smartphones and high-performance computing. Legacy node capacity additions require 18-24 months and billions in investments for facilities manufacturing chips with profit margins of 15-25%, compared to over 50% margins at leading-edge nodes. Economic incentives systematically discouraged the capacity additions that would have prevented shortages.

Contemporary supply chains evolved through competitive pressures appearing as optimization. Automotive manufacturers maintained 30-90 day inventory buffers pre-2000s, absorbing demand fluctuations without production disruptions. By 2019, average automotive inventory had contracted to 15-45 days, with some manufacturers operating on single-week buffers for certain components. This inventory compression, combined with supply chain opacity where manufacturers lacked visibility beyond immediate suppliers, created systemic vulnerability. When the COVID-19 pandemic triggered simultaneous supply restrictions and demand volatility in 2020, the system lacked capacity to absorb disruptions. The semiconductor shortage demonstrated how efficiency-maximizing strategies—just-in-time manufacturing, inventory minimization, single-source dependencies, geographic concentration—increased fragility by eliminating redundancy that previously buffered against disruptions.

Mitigation strategies operate across time horizons spanning immediate responses to decade-long transformations. Short-term interventions include demand management prioritizing critical sectors, design modifications substituting available chips—requiring months for validation—and life-extension programs reducing replacement demand. Intermediate responses include capacity expansions requiring one to two years and substantial capital per facility. Major semiconductor companies announced investments collectively exceeding $300 billion through 2030, though actual capacity additions lagged announcements by several years due to equipment procurement bottlenecks and construction timelines.

Long-term resilience requires systemic restructuring addressing concentration vulnerabilities through geographic diversification and supply chain redundancy. The U.S. CHIPS and Science Act (2022) allocated $52.7 billion for domestic semiconductor manufacturing incentives and R&D. European Union initiatives proposed €43 billion in investment targeting 20% global production share by 2030, up from 9% in 2020. Japan committed significant funding for domestic production expansion. However, advanced node production in Western nations incurs 30-50% higher operating costs than East Asian facilities due to higher labor costs, energy costs, and regulatory compliance. Without sustained subsidies estimated at roughly one-quarter to one-third of capital and operating costs, economic incentives favor continued Asian concentration.

Strategic considerations extend beyond economics into technological sovereignty and national security. Advanced semiconductors enable artificial intelligence, quantum computing, hypersonic weapons, autonomous systems, and cryptographic capabilities. Export controls implemented in October 2022 restricted Chinese access to high-performance GPUs, advanced logic chips below 14nm, and semiconductor manufacturing equipment using extreme ultraviolet lithography. These controls recognize that semiconductor fabrication capability represents a foundational enabler of technological advancement and military capability. Nations lacking domestic advanced semiconductor production face strategic dependencies—over 92% of the most advanced logic chips originate from Taiwan amid geopolitical tensions.

Workforce constraints compound infrastructure challenges. Advanced semiconductor manufacturing requires specialized expertise spanning semiconductor physics, materials science, and multiple engineering disciplines—areas where degree programs produce insufficient graduates. New fabrication facilities face recruitment challenges finding thousands of workers with required technical skills, requiring international worker transfers and university partnerships for workforce development programs needing years to mature. Each new facility requires thousands of direct employees plus tens of thousands of indirect jobs in supporting industries, with advanced fabs demanding that a significant majority of the workforce hold bachelor's degrees or higher.

Ultimately, semiconductor supply chain resilience represents a sociotechnical challenge combining physics, economics, geopolitics, and institutional capacity. Physical constraints—quantum mechanical limits, thermodynamic constraints at extreme power densities, materials science challenges—determine technological trajectories requiring continuous innovation investment exceeding $15 billion annually across industry leaders. Economic forces—high gross margins on leading-edge chips encouraging concentration, lower margins on legacy nodes discouraging investment, massive capital intensity—shape decisions favoring efficiency over redundancy. Geopolitical tensions increasingly override pure economic optimization through export controls, industrial policies, and subsidies. Institutional arrangements spanning industry groups, government initiatives, and international agreements will determine whether the industry achieves geographic diversification or whether concentration intensifies, whether redundancy increases or just-in-time fragility persists, and whether supply chains prove resilient to future disruptions or remain vulnerable to cascading failures. The 2020-2023 shortage revealed structural fragilities embedded in decades of optimization for efficiency over resilience—a fundamental tension that will define semiconductor supply chain evolution for decades to come.

''',
        'questions': [
            {
                "q": "Advanced semiconductor fabrication in Western countries is more expensive mainly because operating costs are typically _______ higher than in East Asia.",
                "options": [
                    "5–10%",
                    "15–20%",
                    "20–30%",
                    "30–50%"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Major chipmakers announced large investment plans through 2030, but actual expansion lagged mostly due to _______.",
                "options": [
                    "raw material export limits",
                    "equipment procurement bottlenecks",
                    "sudden regulatory freezes",
                    "intellectual-property disputes"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Automakers that pre-booked capacity were prioritized because allocation depended as much on contracts as on _______ needs.",
                "options": [
                    "production",
                    "technology",
                    "financial",
                    "logistics"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Geographic concentration in East Asia and the Netherlands creates _______ vulnerabilities.",
                "options": [
                    "capacity-driven",
                    "region-dependent",
                    "supply-linked",
                    "single-point"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Just-in-time failed because production involves _______.",
                "options": [
                    "diverse part numbers",
                    "non-interchangeable chips",
                    "long cycle times",
                    "unstable demand shifts"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "When automotive demand collapsed in 2020, foundries shifted capacity toward _______.",
                "options": [
                    "mobile processors",
                    "computing systems",
                    "digital displays",
                    "consumer electronics"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "Companies shifting to risk-adjusted strategies now maintain inventories and develop _______ supply contracts.",
                "options": [
                    "adaptive",
                    "multi-year",
                    "flexible",
                    "diversified"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Intermediate capacity expansions typically require _______ to complete.",
                "options": [
                    "one to two years",
                    "three to five months",
                    "five to seven years",
                    "ten to twelve months"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "The technology used in advanced semiconductor manufacturing is _______.",
                "options": [
                    "quantum processors",
                    "extreme ultraviolet",
                    "deep-UV scanners",
                    "plasma emitters"
                ],
                "correct": 1,
                "source_type": "article"
            },
            {
                "q": "Photoresist materials require _______",
                "options": [
                    "rare-earth dopants",
                    "purified gases",
                    "semiconductor-grade coatings",
                    "ultra-pure resins"
                ],
                "correct": 3,
                "source_type": "article"
            },
            {
                "q": "At the 3nm process node, transistor gate widths correspond to roughly _______.",
                "options": [
                    "44 carbon atoms",
                    "46 silicon atoms",
                    "48 silicon atoms",
                    "42 carbon atoms"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "Legacy-node capacity additions require _______ and produce margins of 15–25%.",
                "options": [
                    "6–9 months",
                    "12–15 months",
                    "18–24 months",
                    "30–36 months"
                ],
                "correct": 2,
                "source_type": "article"
            },
            {
                "q": "By 2019, some manufacturers operated on _______ for certain components.",
                "options": [
                    "single-week buffers",
                    "two-month buffers",
                    "quarterly buffers",
                    "ten-day buffers"
                ],
                "correct": 0,
                "source_type": "article"
            },
            {
                "q": "Western advanced-node production requires subsidies amounting to _______ of total costs.",
                "options": [
                    "around one-tenth",
                    "roughly one-quarter to one-third",
                    "nearly one-half",
                    "two-thirds"
                ],
                "correct": 1,
                "source_type": "article"
            }
        ]
    }
}

# Section 1: Familiarity Ratings (18 items, 1-7 Likert)
PRIOR_KNOWLEDGE_FAMILIARITY_TERMS = [
    "Heat flux",                                    # Urban Climate – Article 3 (Urban Heat)
    "Permeable pavement",                           # Urban Design – Article 3 (Urban Heat)
    "Reflective coating",                           # Environmental Physics – Article 3 (Urban Heat)
    "Cooling corridor",                             # Urban Planning – Article 3 (Urban Heat)
    "Urban canyon",                                 # Urban Climatology – Article 3 (Urban Heat)
    "Albedo",                                       # Surface Energy Balance – Article 3 (Urban Heat)
    "Gene drive",                                   # Biotechnology / Ecology – Article 1 (CRISPR)
    "Base editing",                                 # Genome Engineering – Article 1 (CRISPR)
    "Prime editing",                                # Genome Engineering – Article 1 (CRISPR)
    "Adeno-associated virus (AAV)",                 # Gene Therapy Vectors – Article 1 (CRISPR)
    "Lipid nanoparticle",                           # Drug Delivery / mRNA – Article 1 (CRISPR)
    "Germ-line editing",                            # Human Genetics / Bioethics – Article 1 (CRISPR)
    "Wafer",                                        # Semiconductor Engineering – Article 2 (Semiconductors)
    "Lithography mask",                             # Semiconductor Fabrication – Article 2 (Semiconductors)
    "System-on-a-chip (SoC)",                       # Microelectronics Design – Article 2 (Semiconductors)
    "Photolithography",                             # Microfabrication Process – Article 2 (Semiconductors)
    "Legacy node",                                  # Semiconductor Process Technology – Article 2 (Semiconductors)
    "Extreme ultraviolet lithography (EUV)"         # Advanced Lithography – Article 2 (Semiconductors)
]

# Section 2: Concept Recognition Check (removed - no longer used)
PRIOR_KNOWLEDGE_RECOGNITION_TERMS = []

# Keep old variable for backward compatibility (used in Section 3 quiz)
PRIOR_KNOWLEDGE_TERMS = PRIOR_KNOWLEDGE_FAMILIARITY_TERMS

PRIOR_KNOWLEDGE_QUIZ = [
    {"q": "What does *albedo* measure?", "options": ["Heat capacity", "Reflectivity of surfaces", "Humidity levels", "Wind speed"], "correct": 1},
    {"q": "*CRISPR* technology is primarily used for:", "options": ["Protein folding", "Genome editing", "MRI imaging", "Battery storage"], "correct": 1},
    {"q": "A semiconductor *foundry* is:", "options": ["A retail store", "A manufacturing facility for chips", "A shipping container", "A mining operation"], "correct": 1},
    {"q": "*Evapotranspiration* refers to:", "options": ["Heat conduction", "Water loss from plants and soil", "Wind patterns", "Solar radiation"], "correct": 1},
    {"q": "*Supply chain resilience* means:", "options": ["Always having low inventory", "Ability to recover from disruptions", "Using only one supplier", "Minimizing costs"], "correct": 1},
]

# CONTROL VERSION: AI_TRUST_QUESTIONS removed - no AI functionality

# ------------------------------------------------------------------------------
# Language selection routes
# ------------------------------------------------------------------------------

# Shortcut language switch routes for /en and /zh
@app.route("/en")
@app.route("/zh")
def quick_lang_switch():
    # path is either '/en' or '/zh'
    lang_code = request.path.strip("/")
    _set_lang(lang_code)
    return redirect(url_for("index"))
@app.route("/language")
def language():
    options = "".join(
        f"<li><a href='/set_lang/{code}'>{name}</a></li>"
        for code, name in SUPPORTED_LANGS.items()
    )
    return (
        "<!doctype html><meta charset='utf-8'>"
        "<h2>Select language / 选择语言</h2>"
        f"<ul>{options}</ul>"
        "<p style='margin-top:1rem'>You can change later at any time via /set_lang?lang=en or /set_lang?lang=zh</p>"
        "<p>稍后也可以更改语言：访问 /set_lang?lang=zh 或 /set_lang?lang=en</p>"
    )


@app.route("/set_lang/<lang_code>")
def set_lang(lang_code):
    _set_lang(lang_code)
    return redirect(url_for("index"))

# Allow /set_lang?lang=zh or POST with lang parameter
@app.route("/set_lang", methods=["GET", "POST"])
def set_lang_queryparam():
    lang_code = request.args.get("lang") or request.form.get("lang") or "en"
    _set_lang(lang_code)
    ref = request.headers.get("Referer")
    return redirect(ref or url_for("index"))

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.route("/")
def index():
    # ALWAYS show language selection first, unless participant_id exists
    # This ensures language selection is the first step for new participants
    if "participant_id" not in session:
        # New participant - show language selection
        if "lang" not in session:
            return render_template("language_selection.html")
        # Language selected but no participant yet - go to login
        return render_template("login.html")
    
    # Existing participant - preserve their language and continue
    lang = session.get("lang", "en")
    return render_template("login.html")


def _ensure_pid():
    # creates a minimal session participant if needed
    pid = session.get("participant_id")
    if not pid:
        pid = get_participant_id()
        session["participant_id"] = pid
        session.permanent = True  # Ensure session persists
        save_participant(pid, {"full_name": "[test-skip]"})
        log_data(pid, "demographics", {"skipped": True})
    # keep language choice persistent
    if "lang" not in session:
        session["lang"] = DEFAULT_LANG
    # Explicitly mark session as modified to ensure it's saved
    session.modified = True
    return pid

# ========== SKIP ROUTES FOR TESTING ==========
# ------------------------------------------------------------------------------
# Reading page: show article (localized)
# ------------------------------------------------------------------------------
@app.route("/dev/reading/<int:i>")
@require_pid
def dev_reading(i):
    # i = article index in session["article_order"]
    article_order = session.get("article_order") or []
    if not (0 <= i < len(article_order)):
        return redirect(url_for("index"))
    article_key = article_order[i]
    # ...other logic...
    return render_template(
        "reading.html",
        article=get_localized_article(article_key),
        article_key=article_key,
        i=i,
    )

# ------------------------------------------------------------------------------
# Test page: show questions (localized)
# ------------------------------------------------------------------------------
@app.route("/dev/test/<int:i>")
@require_pid
def dev_test(i):
    article_order = session.get("article_order") or []
    if not (0 <= i < len(article_order)):
        return redirect(url_for("index"))
    article_key = article_order[i]
    # ...other logic...
    return render_template(
        "test.html",
        article=get_localized_article(article_key),
        article_key=article_key,
        i=i,
    )

# ------------------------------------------------------------------------------
# Free recall instruction page: show prompt (localized)
# ------------------------------------------------------------------------------
@app.route("/recall_instruction/<int:i>", endpoint="recall_instruction_page")
@require_pid
def recall_instruction(i):
    article_order = session.get("article_order") or []
    if not (0 <= i < len(article_order)):
        return redirect(url_for("index"))
    article_key = article_order[i]
    # ...other logic...
    return render_template(
        "recall_instruction.html",
        article=get_localized_article(article_key),
        article_key=article_key,
        i=i,
    )

# ------------------------------------------------------------------------------
# Free recall input page: show input box (localized)
# ------------------------------------------------------------------------------
@app.route("/free_recall/<int:i>", methods=["GET", "POST"])
@require_pid
def free_recall(i):
    article_order = session.get("article_order") or []
    if not (0 <= i < len(article_order)):
        return redirect(url_for("index"))
    article_key = article_order[i]
    # ...other logic...
    return render_template(
        "free_recall.html",
        article=get_localized_article(article_key),
        article_key=article_key,
        i=i,
    )
@app.route("/skip_all")
def skip_all():
    pid = _ensure_pid()
    # CONTROL VERSION: Simplified skip_all - no AI conditions
    if not session.get("article_order"):
        session["article_order"] = ["uhi", "crispr", "semiconductors"]
        session["current_article"] = 0
    # minimal logs so csvs stay consistent
    log_data(pid, "consent", {"accepted": True, "skipped": True})
    log_data(pid, "prior_knowledge", {"skipped": True})
    log_data(pid, "randomization", {
        "article_order": json.dumps(session["article_order"]),
        "condition": "control_no_ai",
        "skipped": True
    })
    log_data(pid, "reading_behavior", {"skipped": True})
    log_data(pid, "test_responses", {"skipped": True})
    # CONTROL VERSION: manipulation_check removed
    return redirect(url_for("debrief"))

@app.route("/skip_login")
def skip_login():
    _ensure_pid()
    return redirect(url_for("consent"))

@app.route("/skip_consent")
def skip_consent():
    pid = _ensure_pid()
    log_data(pid, "consent", {"accepted": True, "skipped": True})
    return redirect(url_for("prior_knowledge"))

@app.route("/skip_prior_knowledge")
def skip_prior_knowledge():
    pid = _ensure_pid()
    log_data(pid, "prior_knowledge", {"skipped": True})
    # CONTROL VERSION: Skip AI Trust, go directly to instructions
    return redirect(url_for("instructions"))

# CONTROL VERSION: skip_ai_trust route removed - no AI functionality

@app.route("/skip_reading")
def skip_reading():
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    article_num = int(session.get("current_article", 0))
    session.modified = True
    # Skip current reading → go to the 3-minute pre-test break for this article
    return redirect(url_for("break_before_test", article_num=article_num))

@app.route("/skip_test/<int:article_num>")
def skip_test(article_num: int):
    pid = _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session.modified = True
    ao = session.get("article_order") or []
    log_data(pid, "test_responses", {
        "article_num": article_num,
        "article_key": ao[article_num] if article_num < len(ao) else "",
        "skipped": True
    })
    next_article = article_num + 1
    if next_article >= 3:
        return redirect(url_for("debrief"))
    return redirect(url_for("short_break", next_article=next_article))

@app.route("/skip_break/<int:next_article>")
def skip_break(next_article: int):
    """Skip the BETWEEN-ARTICLES break → go to NEXT article reading."""
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session.modified = True
    return redirect(url_for("reading_phase", article_num=next_article))

# ---- Skip pre-test break (AFTER reading, BEFORE test) ----

@app.route("/skip_break_before_test/<int:article_num>")
def skip_break_before_test(article_num: int):
    """Skip the AFTER-READING (pre-test) break → go to TEST for this article."""
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session["current_article"] = article_num
    session.modified = True
    return redirect(url_for("test_phase", article_num=article_num))

# ---- Parameterless skip_recall: skip recall for current article ----
@app.route("/skip_recall", methods=["GET"])
def skip_recall_current():
    """
    Skip the free-recall section and land directly on the MCQs for the *current* article.
    This route is made tolerant: it auto-seeds a participant/session if missing so it never 404/302-bounces.
    """
    # Ensure we always have a participant/session
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    # Default to current article (or 0)
    idx = int(session.get("current_article", 0))
    # One-shot flag to start test page directly on MCQs
    session["start_on_mcq"] = True
    session.modified = True
    try:
        print(f"[DEBUG] /skip_recall (no-param) -> idx={idx}, ao={session.get('article_order')}, pid={session.get('participant_id')}")
    except Exception:
        pass
    return redirect(url_for("test_phase", article_num=idx))

# Alias: support a dashed version as well
@app.route("/skip-recall", methods=["GET"])
def skip_recall_current_dash():
    return skip_recall_current()


# ---- Skip recall and land directly on MCQs ----
@app.route("/skip_recall/<int:article_num>", methods=["GET"])
def skip_recall(article_num: int):
    """
    Skip the free-recall section and land directly on the MCQs for this article.
    Seeds minimal session state if needed and sets a one-shot flag consumed by /test/<idx>.
    """
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    # Clamp index
    n = len(session["article_order"])
    article_num = max(0, min(article_num, n - 1))
    session["current_article"] = article_num
    # One-shot flag read by test_phase
    session["start_on_mcq"] = True
    session.modified = True
    try:
        print(f"[DEBUG] /skip_recall -> idx={article_num}, ao={session['article_order']}, pid={session.get('participant_id')}")
    except Exception:
        pass
    return redirect(url_for("test_phase", article_num=article_num))

# ---- Tolerant aliases for skipping recall to MCQs ----
@app.route("/skip-recall/<int:article_num>")
@require_pid
def skip_recall_dash(article_num: int):
    """Alias: /skip-recall/<idx> → identical behavior to /skip_recall/<idx>."""
    return skip_recall(article_num)

@app.route("/skip_recall/<article_num>", methods=["GET"])
def skip_recall_str(article_num):
    """
    Alias accepting a string param, so /skip_recall/0, /skip_recall/00, etc. don't 404
    if Flask type conversion fails or the URL carries stray characters.
    """
    try:
        idx = int(str(article_num).strip().rstrip("."))
    except Exception:
        idx = 0
    return skip_recall(idx)

@app.route("/dev/skip_recall", methods=["GET"])
def skip_recall_query():
    _ensure_pid()
    """
    Alias using query param: /dev/skip_recall?i=0
    Useful if the dynamic route is not being matched for any reason.
    """
    i = request.args.get("i", "0")
    try:
        idx = int(str(i).strip())
    except Exception:
        idx = 0
    return skip_recall(idx)

# ---- Alias: skip directly to MCQ for article ----
@app.route("/skip_to_mcq/<int:article_num>", methods=["GET"])
def skip_to_mcq(article_num: int):
    """
    Alias of /skip_recall/<idx>: start the test page directly on MCQs for this article.
    """
    _ensure_pid()
    # CONTROL VERSION: Simplified - no structure or timing conditions
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    n = len(session["article_order"])
    article_num = max(0, min(article_num, n - 1))
    session["current_article"] = article_num
    session["start_on_mcq"] = True
    session.modified = True
    try:
        print(f"[DEBUG] /skip_to_mcq -> idx={article_num}, ao={session['article_order']}, pid={session.get('participant_id')}")
    except Exception:
        pass
    return redirect(url_for("test_phase", article_num=article_num))
# ------------------------------------------------------------------------------
# Debug/utility routes
# ------------------------------------------------------------------------------

@app.route("/_routes")
def list_routes():
    """
    Debug helper: list all registered URL rules to confirm that new routes are loaded.
    """
    lines = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = ",".join(sorted(m for m in rule.methods if m in ("GET","POST")))
        lines.append(f"{rule.rule}  [{methods}]  ->  {rule.endpoint}")
    return "<pre>" + "\n".join(lines) + "</pre>"

@app.route("/skip_manipulation")
def skip_manipulation():
    pid = _ensure_pid()
    # CONTROL VERSION: manipulation_check removed
    return redirect(url_for("debrief"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    participant_id = get_participant_id()
    session["participant_id"] = participant_id

    demo_data = {
        "full_name": request.form.get("full_name", "").strip(),
        "profession": request.form.get("profession", "").strip(),
        "age": request.form.get("age", "").strip(),
        "gender": request.form.get("gender", "").strip(),
        "native_language": request.form.get("native_language", "").strip(),
    }
    session["demographics"] = demo_data
    save_participant(participant_id, demo_data)
    log_data(participant_id, "demographics", demo_data)
    return redirect(url_for("consent"))

@app.route("/consent")
@require_pid
def consent():
    return render_template("consent.html")

@app.route("/consent_accept", methods=["POST"])
@require_pid
def consent_accept():
    log_data(session["participant_id"], "consent", {"accepted": True})
    return redirect(url_for("prior_knowledge"))

@app.route("/prior_knowledge")
@require_pid
def prior_knowledge():
    # Start (or reuse) a fixed 5"‘minute window for this section
    if "pk_started_at" not in session:
        session["pk_started_at"] = datetime.now().timestamp()
    pk_deadline = session["pk_started_at"] + 5 * 60  # seconds

    return render_template(
        "prior_knowledge.html",
        familiarity_terms=[_auto_translate(term, _get_lang()) for term in PRIOR_KNOWLEDGE_FAMILIARITY_TERMS],
        recognition_terms=[],  # Empty - Section 2 removed
        quiz=[],  # Empty - Section 3 removed
        pk_deadline=pk_deadline,
        server_now=int(datetime.now().timestamp()),
        fixed_minutes=5,
    )

@app.route("/submit_prior_knowledge", methods=["POST"])
@require_pid
def submit_prior_knowledge():
    data = request.get_json(force=True) or {}

    fam = data.get("familiarity", {}) or {}
    rec = data.get("term_recognition", {}) or {}
    quiz_score = int(data.get("quiz_score", 0))
    concept_list = (data.get("concept_list") or "").strip()

    familiarity_mean = (sum(map(int, fam.values())) / max(1, len(fam))) if fam else 0
    term_recognition_count = sum(1 for v in rec.values() if str(v).lower() == "yes")
    prior_knowledge_score = quiz_score / max(1, len(PRIOR_KNOWLEDGE_QUIZ)) if PRIOR_KNOWLEDGE_QUIZ else 0  # Normalize by quiz length (0 if no quiz)
    concept_count = len(concept_list.split()) if concept_list else 0

    exclude = False
    reasons = []
    if familiarity_mean >= 6.0:
        exclude, reasons = True, reasons + ["high_familiarity"]
    # Section 2 removed - no longer checking term_recognition_count
    # Section 3 removed - no longer checking quiz_score

    # Save all individual answers, not just the mean
    log_data(session["participant_id"], "prior_knowledge", {
        "familiarity_mean": familiarity_mean,
        "familiarity_individual": json.dumps(fam),  # All 18 individual ratings
        "term_recognition_count": term_recognition_count,
        "term_recognition_individual": json.dumps(rec),  # Individual recognition answers
        "prior_knowledge_score": prior_knowledge_score,
        "concept_count": concept_count,
        "concept_list": concept_list,  # Full concept list text
        "excluded": exclude,
        "exclusion_reasons": ",".join(reasons) if reasons else "none",
    })

    # Reset PK timer so revisits (if any) start a fresh 5"‘minute window
    session.pop("pk_started_at", None)

    # IMPORTANT: Do NOT exclude participants during testing runs.
    # We keep logging the exclusion metrics but always continue to Prior Knowledge.
    # CONTROL VERSION: Skip AI Trust, go directly to instructions
    return jsonify({"redirect": url_for("instructions")})

@app.route("/instructions")
@require_pid
def instructions():
    """Display instructions page before starting the experiment"""
    return render_template("instructions.html")

@app.route("/instructions_ready", methods=["POST"])
@require_pid
def instructions_ready():
    """Handle ready button click from instructions page"""
    log_data(session["participant_id"], "instructions", {"viewed": True, "ready_clicked": True})
    return redirect(url_for("randomize"))

# CONTROL VERSION: AI Trust routes removed - no AI functionality

# =============================================================================
# COUNTERBALANCED RANDOMIZATION SYSTEM
# =============================================================================

# Between-subject factor: AI Output Structure
# CONTROL VERSION: All AI-related constants and functions removed
# No structure conditions, timing orders, or participant condition assignment needed

@app.route("/randomize")
@require_pid
def randomize():
    # Ensure we actually have articles to run
    article_keys = list(ARTICLES.keys())
    if len(article_keys) < 3:
        # If you temporarily reduced ARTICLES, handle gracefully
        return render_template("excluded.html"), 500

    # Randomize article order (still random across the 3 articles)
    random.shuffle(article_keys)
    article_keys = article_keys[:3]  # run 3 articles

    # CONTROL VERSION: Simplified randomization - no AI conditions
    participant_id = session["participant_id"]

    # Store in session (no structure or timing conditions)
    session["article_order"] = article_keys
    session["current_article"] = 0

    # Log randomization
    log_data(participant_id, "randomization", {
        "article_order": json.dumps(article_keys),
        "condition": "control_no_ai"
    })

    return redirect(url_for("reading_phase", article_num=0))

# CONTROL VERSION: AI summary route removed - no AI functionality

@app.route("/reading/<int:article_num>", methods=["GET"])
@require_pid
def reading_phase(article_num: int):
    # CONTROL VERSION: Simplified reading phase - no AI summaries
    article_order = session.get("article_order") or []

    # If anything is missing, (re)randomize cleanly
    if not article_order:
        return redirect(url_for("randomize"))

    # Index guards
    if article_num < 0:
        return redirect(url_for("reading_phase", article_num=0))
    if article_num >= len(article_order):
        return redirect(url_for("debrief"))

    # Current article
    article_key = article_order[article_num]
    article = get_localized_article(article_key)  # Use localized version
    if not article:
        # Dict changed mid-run → reseed
        return redirect(url_for("randomize"))

    # Record session state
    session["current_article"] = article_num
    session["current_article_key"] = article_key
    session["reading_start_time"] = datetime.now().isoformat()

    return render_template(
        "reading.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        article_text=article["text"],
    )


# CONTROL VERSION: All summary-related routes removed - no AI functionality

@app.route("/log_reading", methods=["POST"])
@require_pid
def log_reading():
    data = request.get_json(force=True) or {}
    data["article_num"] = session.get("current_article")
    data["article_key"] = session.get("current_article_key")
    # CONTROL VERSION: timing removed - no AI functionality
    log_data(session["participant_id"], "reading_behavior", data)
    return jsonify({"status": "ok"})

# ---- Reading completion endpoint (called by reading.html when reading is finished) ----
@app.route("/reading_complete", methods=["POST", "GET"])
@require_pid
def reading_complete():
    """
    Called by reading.html when the participant finishes reading.
    Sends them to the 3-minute break that occurs BEFORE the test of the current article.
    """
    article_num = int(session.get("current_article", 0))
    return redirect(url_for("break_before_test", article_num=article_num))

@app.route("/dev/recall_instruction_bypass/<int:article_num>", endpoint="dev_recall_instruction_bypass")
@require_pid
def recall_instruction_bypass(article_num: int):
    """DEV: bypass recall-instruction screen and go straight to TEST for this article."""
    article_order = session.get("article_order") or []
    if article_num >= len(article_order):
        return redirect(url_for("debrief"))
    return redirect(url_for("test_phase", article_num=article_num))

@app.route("/test/<int:article_num>")
@require_pid
def test_phase(article_num: int):
    article_order = session.get("article_order") or []
    try:
        print(f"[DEBUG] /test/{article_num} session_participant={session.get('participant_id')}, "
              f"article_order={article_order}, len={len(article_order)}")
    except Exception:
        pass
    # If session isn’t seeded yet, (re)randomize rather than skipping to the end
    if not article_order:
        return redirect(url_for("randomize"))
    if article_num >= len(article_order):
        return redirect(url_for("debrief"))
    article_key = article_order[article_num]
    article = get_localized_article(article_key)  # Use localized version
    if not article:
        return redirect(url_for("randomize"))

    # Store test start time for recall timer
    session[f"recall_start_{article_num}"] = datetime.now().timestamp()

    # Recall timing: total = 3 minutes, unlock at 1.5 minutes (shorter in TEST_MODE)
    recall_total_ms = 10000 if TEST_MODE else (5 * 60 * 1000)
    recall_unlock_ms = 5000 if TEST_MODE else (90 * 1000)  # 1.5 minutes

    # One-shot flag: start the test page directly on MCQ if set by a skip route
    start_on_mcq = bool(session.pop("start_on_mcq", False))

    # NO RANDOMIZATION: Use questions in their original order
    questions_list = list(article["questions"])
    
    return render_template(
        "test.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        questions=questions_list,  # Use original order (no randomization)
        test_mode=TEST_MODE,
        show_recall_counters=False,
        recall_total_ms=recall_total_ms,
        recall_unlock_ms=recall_unlock_ms,
        start_on_mcq=start_on_mcq,
        skip_recall=start_on_mcq  # Additional clear flag for template
    )

@app.route("/mcq/<int:article_num>")
@require_pid
def mcq_only(article_num: int):
    """
    Direct MCQ-only route that completely bypasses recall section.
    Use this route when you want to skip recall entirely: /mcq/0, /mcq/1, /mcq/2
    """
    article_order = session.get("article_order") or []
    if not article_order:
        return redirect(url_for("randomize"))
    if article_num >= len(article_order):
        return redirect(url_for("debrief"))
    
    article_key = article_order[article_num]
    article = get_localized_article(article_key)
    if not article:
        return redirect(url_for("randomize"))
    
    # Log that recall was skipped
    try:
        log_data(session["participant_id"], "recall_response", {
            "article_num": article_num,
            "article_key": article_key,
            # timing removed - no AI functionality
            "skipped": True
        })
    except Exception:
        pass
    
    # NO RANDOMIZATION: Use questions in their original order
    questions_list = list(article["questions"])
    
    return render_template(
        "test.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        questions=questions_list,  # Use original order (no randomization)
        test_mode=True,  # Force test mode behavior
        show_recall_counters=False,
        start_on_mcq=True,  # Skip to MCQ
        skip_recall=True,   # Clear skip flag
        recall_total_ms=0,  # No recall timer needed
        recall_unlock_ms=0
    )

@app.route("/submit_test", methods=["POST"])
@require_pid
def submit_test():
    data = request.get_json(force=True) or {}
    article_num = int(data.get("article_num", 0))

    # CONTROL VERSION: No timing_order - simplified
    article_order = session.get("article_order") or []

    if article_num < len(article_order):
        data["article_key"] = article_order[article_num]

    # Extract recall and MCQ data separately
    recall_data = data.get("recall", {})
    mcq_data = data.get("mcq", {})
    mcq_answer_times_ms = data.get("mcq_answer_times_ms", {})
    mcq_total_time_ms = data.get("mcq_total_time_ms", 0)
    
    # Log recall separately for easier analysis
    if recall_data:
        log_data(session["participant_id"], "recall_response", {
            "article_num": article_num,
            "article_key": data.get("article_key"),
            # timing removed - no AI functionality
            "recall_text": recall_data.get("recall_text", ""),
            "sentence_count": recall_data.get("sentence_count", 0),
            "word_count": recall_data.get("word_count", 0),
            "char_count": recall_data.get("char_count", 0),
            "confidence": recall_data.get("confidence", 0),
            "perceived_difficulty": recall_data.get("perceived_difficulty", 0),
            "time_spent_ms": recall_data.get("time_spent_ms", 0),
            "paste_attempts": recall_data.get("paste_attempts", 0),
            "over_limit": recall_data.get("over_limit", False)
        })
    
    # Calculate accuracy rate and log MCQ responses
    if mcq_data:
        article_key = data.get("article_key")
        article = ARTICLES.get(article_key) if article_key else None
        
        # NO RANDOMIZATION: Questions are in original order, so indices match directly
        # Guard: require all MCQ questions answered before proceeding
        if article and "questions" in article:
            questions = article["questions"]
            missing_or_invalid = []
            # Check using original indices (no randomization)
            for q_idx in range(len(questions)):
                q_key = f"q{q_idx}"
                ans = mcq_data.get(q_key, None)
                q = questions[q_idx] if q_idx < len(questions) else None
                # Valid answers are integers in option index range
                try:
                    options_len = len(q.get("options", [])) if q else 0
                except Exception:
                    options_len = 0
                if ans is None or not isinstance(ans, int) or ans < 0 or (options_len and ans >= options_len):
                    missing_or_invalid.append(q_key)
            if missing_or_invalid:
                return jsonify({"error": "incomplete_mcq", "missing": missing_or_invalid}), 400
        
        # Calculate accuracy
        correct_count = 0
        total_questions = 0
        question_accuracy = {}
        mcq_answer_texts = {}  # Store actual answer text for each question
        
        if article and "questions" in article:
            questions = article["questions"]
            # Process answers using original indices (no randomization)
            for q_idx in range(len(questions)):
                total_questions += 1
                q_key = f"q{q_idx}"  # Answer key from frontend (original order)
                participant_answer = mcq_data.get(q_key, None)
                question = questions[q_idx] if q_idx < len(questions) else None
                
                if question:
                    correct_answer = question.get("correct", None)
                    options = question.get("options", [])
                    
                    # VALIDATION: Ensure participant_answer is within valid range
                    if participant_answer is not None:
                        max_option = len(options) - 1
                        if participant_answer < 0 or participant_answer > max_option:
                            print(f"[MCQ ERROR] Invalid participant_answer {participant_answer} for q{q_idx}, max={max_option}")
                            participant_answer = None
                    
                    # Get the actual answer text
                    participant_answer_text = None
                    if participant_answer is not None and participant_answer < len(options):
                        participant_answer_text = options[participant_answer]
                        # Store a recognizable word/phrase (first few words, max 50 chars)
                        mcq_answer_texts[q_key] = participant_answer_text[:50] if participant_answer_text else None
                    
                    # Check if answer is correct (handle None/missing answers)
                    is_correct = (participant_answer is not None and 
                                 participant_answer == correct_answer)
                    question_accuracy[q_key] = {
                        "participant_answer": participant_answer,
                        "participant_answer_text": participant_answer_text,  # Add actual text
                        "correct_answer": correct_answer,
                        "correct_answer_text": options[correct_answer] if correct_answer is not None and correct_answer < len(options) else None,  # Add correct text
                        "is_correct": is_correct,
                        "question_index": q_idx  # Store question index (no randomization)
                    }
                    
                    if is_correct:
                        correct_count += 1
        
        # Calculate accuracy rate as percentage
        accuracy_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        
        # Log MCQ responses with accuracy and answer times
        # CRITICAL: Also log the mapping to help debug randomization issues
        log_data(session["participant_id"], "mcq_responses", {
            "article_num": article_num,
            "article_key": article_key,
            # timing removed - no AI functionality
            "mcq_answers": json.dumps(mcq_data),  # Original indices
            "mcq_answer_texts": json.dumps(mcq_answer_texts),  # Actual answer text for each question
            "mcq_answer_times_ms": json.dumps(mcq_answer_times_ms),
            "mcq_total_time_ms": mcq_total_time_ms,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "accuracy_rate": round(accuracy_rate, 2),
            "question_accuracy": json.dumps(question_accuracy)  # Includes indices and text (no mapping needed)
        })

    # Store article_num in session for post-article ratings
    session["last_completed_article_num"] = article_num
    session.modified = True

    # After MCQ, redirect to post-article ratings (before break)
    return jsonify({"redirect": url_for("post_article_ratings", article_num=article_num)})

# ---- Post-Article Ratings (after MCQ, before break) ----
@app.route("/post_article_ratings/<int:article_num>")
@require_pid
def post_article_ratings(article_num: int):
    """Display post-article ratings screen after MCQ completion"""
    # CONTROL VERSION: Simplified - no timing_order
    article_order = session.get("article_order") or []
    
    if not article_order or article_num >= len(article_order):
        return redirect(url_for("manipulation_check"))
    
    article_key = article_order[article_num]
    
    return render_template(
        "post_article_ratings.html",
        article_num=article_num,
        article_key=article_key
    )

@app.route("/submit_post_article_ratings", methods=["POST"])
@require_pid
def submit_post_article_ratings():
    """Submit post-article ratings data"""
    data = request.get_json(force=True) or {}
    
    # CONTROL VERSION: Simplified post-article ratings - no AI fields
    article_order = session.get("article_order") or []
    
    # Try to get article_num from last test phase or from URL parameter
    article_num = session.get("last_completed_article_num")
    if article_num is None:
        return jsonify({"error": "Article number not found"}), 400
    
    if article_num >= len(article_order):
        return redirect(url_for("debrief"))
    
    article_key = article_order[article_num]
    
    # Log the ratings data (AI fields removed)
    log_data(session["participant_id"], "post_article_ratings", {
        "article_num": article_num,
        "article_key": article_key,
        "load_mental_effort": int(data.get("load_mental_effort", 0)),
        "load_task_difficulty": int(data.get("load_task_difficulty", 0)),
        # AI-related fields removed: ai_help_understanding, ai_help_memory, ai_made_task_easier, ai_satisfaction, ai_better_than_no_ai
        "mcq_overall_confidence": int(data.get("mcq_overall_confidence", 0))
    })
    
    # Determine next step: break for articles 0-1, debrief for article 2
    next_article = article_num + 1
    if next_article >= 3:
        # After Article 3 ratings, go directly to debrief
        return jsonify({"redirect": url_for("debrief")})
    # For articles 0 and 1: after ratings, go to break, then break will redirect to next article reading
    return jsonify({"redirect": url_for("short_break", next_article=next_article)})

# ---- Alias for after-reading break (backward compatibility/clarity) ----
@app.route("/break_after_reading/<int:article_num>")
@require_pid
def break_after_reading(article_num: int):
    # Break after reading (3 minutes) - always goes to test after break
    # After test, if article 2, will go to debrief; otherwise go to next article reading
    return render_template("break.html", next_article=article_num, after_reading=True, test_mode=TEST_MODE, go_to_manipulation=False)

# ---- Pre-test break route ----
@app.route("/break_before_test/<int:article_num>")
@require_pid
def break_before_test(article_num: int):
    # After the break, go directly to the TEST for this article (no recall-instruction wait)
    return render_template("break.html", next_article=article_num, after_reading=True, test_mode=TEST_MODE)

@app.route("/break/<int:next_article>")
@require_pid
def short_break(next_article: int):
    # This is the classic "after test" break
    return render_template("break.html", next_article=next_article, after_reading=False, test_mode=TEST_MODE)

# CONTROL VERSION: manipulation_check route removed - go directly to debrief

@app.route("/debrief")
@require_pid
def debrief():
    participant_id = session.get("participant_id")
    
    # Generate analysis automatically when participant reaches debrief (experiment complete)
    if participant_id:
        _generate_analysis_if_needed(participant_id)
    
    return render_template("debrief.html", participant_id=participant_id)

@app.route("/excluded")
def excluded():
    return render_template("excluded.html")

# ------------------------------------------------------------------------------
# Admin Data Export Routes (for cloud deployment)
# ------------------------------------------------------------------------------
@app.route("/admin/export", methods=["GET"])
def admin_export_data():
    """
    Export all experiment data as ZIP file.
    Requires ADMIN_KEY environment variable for security.
    Usage: /admin/export?key=YOUR_ADMIN_KEY
    """
    admin_key = os.environ.get("ADMIN_KEY")
    provided_key = request.args.get("key")
    
    if not admin_key or provided_key != admin_key:
        return jsonify({"error": "Unauthorized. Set ADMIN_KEY environment variable."}), 403
    
    import zipfile
    import tempfile
    from flask import send_file
    
    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    zip_path = temp_zip.name
    temp_zip.close()
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all CSV files
            if os.path.exists(DATA_DIR):
                for filename in os.listdir(DATA_DIR):
                    if filename.endswith('.csv'):
                        filepath = os.path.join(DATA_DIR, filename)
                        zipf.write(filepath, filename)
            
            # Add translation cache if needed
            if os.path.exists(TRANSLATION_CACHE_FILE):
                zipf.write(TRANSLATION_CACHE_FILE, 'translations.json')
        
        # Send file
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'experiment_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    """
    Get statistics about experiment data.
    Requires ADMIN_KEY environment variable.
    Usage: /admin/stats?key=YOUR_ADMIN_KEY
    """
    admin_key = os.environ.get("ADMIN_KEY")
    provided_key = request.args.get("key")
    
    if not admin_key or provided_key != admin_key:
        return jsonify({"error": "Unauthorized. Set ADMIN_KEY environment variable."}), 403
    
    stats = {
        "participant_count": 0,
        "data_files": [],
        "total_data_size_mb": 0,
        "last_update": None,
        "data_directory": os.path.abspath(DATA_DIR)
    }
    
    if os.path.exists(DATA_DIR):
        csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        stats["data_files"] = sorted(csv_files)
        
        # Count participants
        participants_file = os.path.join(DATA_DIR, "participants.csv")
        if os.path.exists(participants_file):
            try:
                with open(participants_file, 'r', encoding='utf-8') as f:
                    stats["participant_count"] = max(0, sum(1 for line in f) - 1)  # Subtract header
            except Exception:
                stats["participant_count"] = 0
        
        # Calculate total size
        total_size = sum(
            os.path.getsize(os.path.join(DATA_DIR, f))
            for f in csv_files
        )
        stats["total_data_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Get last modification time
        if csv_files:
            latest_file = max(
                csv_files,
                key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f))
            )
            stats["last_update"] = datetime.fromtimestamp(
                os.path.getmtime(os.path.join(DATA_DIR, latest_file))
            ).isoformat()
    
    return jsonify(stats)

# ------------------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------------------
# Pre-translate static UI text at startup
def _pre_translate_ui_text():
    """Pre-translate common UI text strings to speed up rendering"""
    print("Pre-translating static UI text...")
    ui_strings = [
        # Common buttons and actions
        "Continue", "Submit", "Next Part", "Close", "Remove",
        "Continue to Study", "I Agree and Continue", "Continue to Section 2",
        "Continue to Section 3", "Submit Assessment", "Continue to Experiment",
        "Continue to single choice questions with multiple options", "Submit Test", "Continue Early",
        "Add Bullet Point", "Enter your idea or phrase here...",
        "Keep Writing", "Submit Anyway",
        
        # Timer labels
        "left", "Time remaining:", "Time:", "remaining",
        
        # Form labels
        "Full Name", "Age", "Gender", "Profession / Field of Study",
        "Native Language", "Select...", "Male", "Female", "Other",
        "Prefer not to say", "Please enter an age between 18 and 60",
        
        # Section headers
        "Free Recall", "Recognition Questions", "Answer the following questions based on the article.",
        "AI Summary", "Open AI Summary",
        
        # Slider labels
        "How confident are you that you recalled the main ideas accurately?",
        "How mentally demanding was this task?", "Not confident", "Very confident",
        "Very easy", "Very demanding",
        
        # Messages
        "Paste not allowed.", "Please type your response in your own words. This helps ensure authentic recall.",
        "Time's up — your response was saved",
        "Submit with few sentences?",
        "We recommend at least 3 idea sentences for meaningful recall. You currently have",
        "Important:", "Important Points:",
        "Must try your best to remember as many information in the article.",
        "Reward allocation is directly proportional to test response accuracy",
        "sentence(s).", "Would you like to submit anyway or keep writing?",
        "Please answer all questions",
        
        # Break page
        "Quick Tips", "Stand and stretch for a moment",
        "Look away from the screen to rest your eyes",
        "Take a few deep breaths", "Stay hydrated",
        
        # Form validation messages
        "Please fill in this field", "Please select an option",
        
        # Prior Knowledge instructions
        "Rate how familiar you are with the following scientific terms.",
        "1 = Never heard of it", "7 = Could clearly explain it to others",
        "For each term below, mark Yes if you believe you could accurately define or describe it without looking it up; otherwise mark No.",
        "Concept Recognition Check",
        
        # Consent page
        "Important information about AI summaries",
        
        # Post-article ratings
        "Short survey about this article",
        "Please answer the following questions about your experience with this article.",
        "Use the scale from 1 to 7 for each statement, where:",
        "Strongly disagree", "Strongly agree",
        "Cognitive Load", "AI Experience", "Overall MCQ Confidence",
        "How mentally demanding was this task?",
        "Not at all demanding", "Extremely demanding",
        "How difficult was it to understand the content of this article?",
        "Very easy", "Very difficult",
        "The AI-generated summary helped me understand the article.",
        "The AI-generated summary helped me remember the content.",
        "The AI assistance made the task easier and more efficient.",
        "I am satisfied with the AI assistance provided for this article.",
        "I prefer completing this kind of task with AI support rather than without it.",
        "(Optional)",
        "Overall, how confident are you in your answers to the multiple-choice questions for this article?",
        "Not confident at all", "Extremely confident", "Not confident",
        "Please answer all required questions before continuing.",
        "Submitting...", "An error occurred. Please try again.",
        "Skip Break",
    ]
    
    translated_count = 0
    for text in ui_strings:
        cache_key = _get_cache_key(text, "zh")
        if cache_key not in _translation_cache:
            try:
                translated = GoogleTranslator(source="auto", target="zh-CN").translate(text)
                _translation_cache[cache_key] = translated
                translated_count += 1
            except Exception:
                pass
    
    if translated_count > 0:
        _save_translation_cache()
        print(f"✓ Pre-translated {translated_count} UI strings")
    else:
        print("✓ All UI strings already cached")

def _pre_translate_all_articles():
    """Pre-translate ALL article content to Chinese for instant access"""
    if not GoogleTranslator:
        print("⚠️ GoogleTranslator not available, skipping article pre-translation")
        return
    
    import time
    import re
    
    print("\nPre-translating all articles to Chinese...")
    print("This will take 30-60 seconds but makes everything instant afterwards...")
    
    translator = GoogleTranslator(source="auto", target="zh-CN")
    total_translated = 0
    start_time = datetime.now()
    
    # Translate all articles
    for article_key, article in ARTICLES.items():
        print(f"  Translating {article_key}...")
        
        # Collect all text to translate
        texts_to_translate = []
        
        # Title
        if article.get('title'):
            texts_to_translate.append(('title', article['title']))
        
        # Free recall prompt
        if article.get('free_recall_prompt'):
            texts_to_translate.append(('free_recall_prompt', article['free_recall_prompt']))
        
        # Article text (long text - will take time)
        if article.get('text'):
            print(f"    Translating article text ({len(article['text'])} chars)...")
            texts_to_translate.append(('text', article['text']))
        
        # CONTROL VERSION: Summary translations removed - no AI functionality
        # Summaries removed from translation
        
        # Questions
        for q_idx, q in enumerate(article.get('questions', [])):
            if q.get('q'):
                texts_to_translate.append(('question_q', q['q']))
            for opt_idx, opt in enumerate(q.get('options', [])):
                texts_to_translate.append(('question_option', opt))
        
        # Translate each item
        for key_type, text in texts_to_translate:
            cache_key = _get_cache_key(text, "zh")
            if cache_key not in _translation_cache:
                try:
                    time.sleep(0.1)  # Small delay to avoid rate limiting
                    
                    # Google Translator has a 5000 character limit
                    # Split long texts into chunks and recombine
                    if len(text) > 4500:
                        # Split by sentences (period, exclamation, question mark)
                        sentences = re.split(r'([.!?]\s+)', text)
                        translated_parts = []
                        current_chunk = ""
                        
                        for i, part in enumerate(sentences):
                            if len(current_chunk + part) > 4000:
                                # Translate current chunk
                                if current_chunk.strip():
                                    chunk_translated = translator.translate(current_chunk.strip())
                                    translated_parts.append(chunk_translated)
                                    time.sleep(0.1)
                                current_chunk = part
                            else:
                                current_chunk += part
                        
                        # Translate remaining chunk
                        if current_chunk.strip():
                            chunk_translated = translator.translate(current_chunk.strip())
                            translated_parts.append(chunk_translated)
                        
                        translated = "".join(translated_parts)
                    else:
                        translated = translator.translate(text)
                    
                    _translation_cache[cache_key] = translated
                    total_translated += 1
                    if total_translated % 5 == 0:
                        print(f"    ... {total_translated} translations done")
                    # Save every 10 to avoid losing progress
                    if total_translated % 10 == 0:
                        _save_translation_cache()
                except Exception as e:
                    print(f"    Warning: Failed to translate one item: {e}")
                    time.sleep(0.5)  # Longer delay on error
    
    # Translate Prior Knowledge terms and quiz
    print("  Translating Prior Knowledge terms and quiz...")
    for term in PRIOR_KNOWLEDGE_TERMS:
        cache_key = _get_cache_key(term, "zh")
        if cache_key not in _translation_cache:
            try:
                time.sleep(0.1)
                translated = translator.translate(term)
                _translation_cache[cache_key] = translated
                total_translated += 1
            except Exception:
                pass
    
    for q in PRIOR_KNOWLEDGE_QUIZ:
        # Question
        cache_key = _get_cache_key(q.get('q', ''), "zh")
        if cache_key not in _translation_cache and q.get('q'):
            try:
                time.sleep(0.1)
                translated = translator.translate(q['q'])
                _translation_cache[cache_key] = translated
                total_translated += 1
            except Exception:
                pass
        # Options
        for opt in q.get('options', []):
            cache_key = _get_cache_key(opt, "zh")
            if cache_key not in _translation_cache:
                try:
                    time.sleep(0.1)
                    translated = translator.translate(opt)
                    _translation_cache[cache_key] = translated
                    total_translated += 1
                except Exception:
                    pass
    
    # CONTROL VERSION: AI Trust translation removed - no AI functionality
    # AI Trust questions translation removed
    # (No AI trust questions in control version)
    
    # Final save
    if total_translated > 0:
        _save_translation_cache()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n✓ Pre-translated {total_translated} strings in {elapsed:.1f} seconds")
    print("✓ All content is now cached - switching pages will be instant!")

# =============================================================================
# CONDITION DISTRIBUTION MONITORING
# =============================================================================

# CONTROL VERSION: Condition distribution route simplified - no AI conditions to track
@app.route("/dev/condition_distribution")
def get_condition_distribution():
    """Control version - no AI conditions to monitor"""
    return jsonify({
        'total': 0,
        'message': 'Control version - no AI conditions to track',
        'condition': 'control_no_ai'
    })
    
    return jsonify(distribution)

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # Load translation cache on startup
    _load_translation_cache()
    
    # Pre-translate static UI text (fast)
    if GoogleTranslator:
        _pre_translate_ui_text()
    
    # Pre-translate ALL articles (takes 30-60 seconds but makes everything instant)
    # Allow disabling via env to avoid network delays in constrained environments
    if GoogleTranslator and os.environ.get("DISABLE_PRETRANSLATE") != "1":
        _pre_translate_all_articles()

    print("\n" + "=" * 50)
    print("Human Memory Encoding Experiment Platform - CONTROL VERSION (No AI)")
    print("=" * 50)
    
    # Use PORT from environment (for cloud deployment) or default to 8081 for control version
    port = int(os.environ.get("PORT", 8081))
    host = os.environ.get("HOST", "127.0.0.1")
    
    # For production/cloud, bind to 0.0.0.0 to accept external connections
    if os.environ.get("FLASK_ENV") == "production" or os.environ.get("PORT"):
        host = "0.0.0.0"
    
    print(f"\nServer starting at http://{host}:{port}")
    print(f"Data will be saved to: {os.path.abspath(DATA_DIR)}")
    print("\nPress CTRL+C to stop the server\n")

    # Disable debug mode in production (use environment variable)
    debug_mode = os.environ.get("FLASK_ENV") != "production"

    # IMPORTANT: disable reloader so secret key doesn't rotate & kill session
    app.run(debug=debug_mode, host=host, port=port, use_reloader=False)
