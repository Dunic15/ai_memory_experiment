"""
AI-Assisted Human Memory Encoding Experiment Platform
Flask application (stable sessions, guarded routes, JSON-safe handlers)
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json, csv, os, random
from datetime import datetime
from functools import wraps
from functools import lru_cache
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

# Translation cache directory
TRANSLATION_CACHE_DIR = "translation_cache"
os.makedirs(TRANSLATION_CACHE_DIR, exist_ok=True)
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
    csv_file = os.path.join(DATA_DIR, "participants.csv")
    n = csv_len(csv_file)
    return f"P{n + 1:03d}"

def log_data(participant_id, phase, data):
    filename = os.path.join(DATA_DIR, f"{participant_id}_log.csv")
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["timestamp", "phase"] + list(data.keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            w.writeheader()
        w.writerow({"timestamp": datetime.now().isoformat(), "phase": phase, **data})

def save_participant(participant_id, data):
    csv_file = os.path.join(DATA_DIR, "participants.csv")
    file_exists = os.path.exists(csv_file)
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        fieldnames = ["participant_id", "timestamp"] + list(data.keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            w.writeheader()
        w.writerow({"participant_id": participant_id, "timestamp": datetime.now().isoformat(), **data})
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
        # Translate selected fields on the fly when language is not English
        localized = {}
        for k in [
            "title",
            "free_recall_prompt",
            "text",
            "summary_integrated",
            "summary_segmented",
        ]:
            localized[k] = _auto_translate(art.get(k, ""), lang)
        # Questions: translate only the text portions
        qs = []
        for q in art.get("questions", []):
            qs.append({
                "q": _auto_translate(q.get("q", ""), lang),
                "options": [
                    _auto_translate(opt, lang) for opt in q.get("options", [])
                ],
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
    lang = _get_lang()
    art = ARTICLES.get(article_key, {})
    if not art or lang == "en":
        return art
    localized = {}
    for k in [
        "title",
        "free_recall_prompt",
        "text",
        "summary_integrated",
        "summary_segmented",
    ]:
        localized[k] = _auto_translate(art.get(k, ""), lang)
    # Translate questions text/options; keep 'correct' index as-is
    qs = []
    for q in art.get("questions", []):
        qs.append({
            "q": _auto_translate(q.get("q", ""), lang),
            "options": [_auto_translate(opt, lang) for opt in q.get("options", [])],
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
        'summary_integrated': 'Urban heat islands emerge when cities absorb and trap solar radiation more efficiently than surrounding rural areas. Asphalt, concrete, and building materials have low albedo values (0.05–0.20), absorbing ninety to ninety-five percent of incoming solar energy and converting it into stored heat. High thermal mass materials like brick and concrete retain this energy through the day and release it slowly at night, keeping urban temperatures three to seven degrees Celsius warmer than nearby countryside. Urban canyon geometry—the ratio of building height to street width—traps outgoing longwave radiation through multiple reflections, preventing efficient atmospheric cooling.\n\nThese thermal patterns intensify during heat waves, creating health risks and driving energy demand upward. The heat island represents both a physical meteorological phenomenon and a social inequality issue: low-income neighborhoods with minimal tree coverage, higher building density, and more impervious surfaces experience disproportionate heat exposure. During extreme events, mortality rises among elderly residents, individuals with cardiovascular conditions, and those lacking air conditioning. Recent pilot programs deployed photocatalytic roof tiles that actively convert absorbed heat into electrical current through thermoelectric generation, though scalability challenges remain unresolved.\n\nMitigation strategies target four mechanisms: enhancing surface reflectance through cool roofs and pavements, providing shade via urban forestry, amplifying evaporative cooling through vegetation, and managing thermal mass. Cool roofing materials with albedo values reaching 0.70–0.85 can reduce absorbed heat by sixty to seventy-five percent. Trees provide dual benefits—direct shading plus evapotranspiration that converts sensible heat into latent heat through water vapor release. However, optimal implementation requires careful design: excessive visible-spectrum reflection can create glare and redirect radiation, potentially warming nearby spaces.\n\nBuilding sustainable resilience demands integrated planning that combines technical interventions with equitable resource distribution, ensuring vulnerable neighborhoods receive priority investment in cooling infrastructure, green spaces, and community-based adaptation programs.',
        'summary_segmented': '''Urban heat islands occur when metropolitan areas become significantly warmer than surrounding rural regions, creating persistent temperature differentials.
Dark surfaces with low albedo values—asphalt (~0.05), concrete, brick—absorb ninety to ninety-five percent of solar radiation, converting it into stored thermal energy.
High thermal mass materials retain absorbed heat throughout daylight hours and release it gradually after sunset, sustaining elevated nighttime temperatures.
Urban canyon geometry traps outgoing longwave radiation through multiple inter-surface reflections, preventing efficient atmospheric cooling and amplifying heat retention.
Recent pilot programs deployed photocatalytic roof tiles that actively convert absorbed heat into electrical current through thermoelectric generation.
Heat islands intensify health risks during heat waves, particularly affecting elderly populations, individuals with cardiovascular conditions, and residents lacking cooling access.
Low-income neighborhoods experience disproportionate heat exposure due to reduced tree canopy, higher building density, and greater impervious surface coverage—an environmental justice concern.
Cool roofing systems with high-albedo coatings (0.70–0.85 reflectance) reduce absorbed solar flux by sixty to seventy-five percent compared to conventional materials.
Urban forestry provides dual thermal benefits: direct radiative shading through canopy interception plus evaporative cooling via stomatal transpiration converting sensible into latent heat.
Effective heat mitigation requires integrated planning combining technical interventions—cool surfaces, vegetation, permeable materials—with equitable resource distribution prioritizing vulnerable communities.''',
        'questions': [
            {"q": "The passage suggests that urban heat creation fundamentally results from:", "options": ["Combined physical, material, and airflow factors creating thermal imbalance", "Primarily greenhouse gas emissions from transportation systems", "Solar radiation absorption exceeding rural baseline rates", "Industrial heat generation overwhelming natural cooling"], "correct": 0},
            {"q": "According to the text, what claim about nighttime urban temperatures accurately reflects the heat storage mechanism?", "options": ["Stored heat releases gradually, maintaining elevated temperatures for extended periods", "Materials release stored heat creating uniform elevated nighttime temperatures", "Dense construction materials delay but don't store heat, prolonging energy release", "Thermal mass enables overnight heat dissipation preventing accumulation"], "correct": 2},
            {"q": "The relationship between surface reflectivity and urban canyon geometry is best characterized as:", "options": ["Synergistic amplification of heat absorption", "Independent factors with additive effects", "Competing mechanisms that partially offset", "Sequential processes where geometry precedes albedo"], "correct": 0},
            {"q": "Which quantitative relationship does the passage establish regarding albedo modifications?", "options": ["Five percent reflectance increase correlates with one-degree temperature reduction", "Albedo below 0.05 triggers exponential heat accumulation", "Reflectance values around 0.05 create critical thermal feedback loops", "Ten percent albedo improvement yields two-degree cooling"], "correct": 2},
            {"q": "The text's characterization of \"breathing potential\" in urban contexts refers to:", "options": ["Atmospheric oxygen levels in polluted environments", "Convective heat removal through airflow patterns", "Respiratory health impacts from temperature extremes", "Building ventilation system capacities"], "correct": 1},
            {"q": "What paradox does the passage identify regarding urban cooling infrastructure?", "options": ["Cooling systems exacerbate heat islands while providing local relief", "Green infrastructure reduces temperatures but increases water demand", "Reflective surfaces cool buildings but intensify street-level heat", "Ventilation improvements worsen air quality despite temperature benefits"], "correct": 0},
            {"q": "According to the passage, socioeconomic heat distribution patterns result from:", "options": ["Zoning policies concentrating industry in low-income areas", "Historical wealth gaps translating to environmental inequities", "Market forces pricing vulnerable populations into hotter zones", "Combined infrastructure, vegetation, and service disparities"], "correct": 3},
            {"q": "The text suggests that tall building canyon effects create which thermal dynamic?", "options": ["Vertical temperature gradients with cooler upper levels", "Multiple radiation reflections between surfaces increasing absorption", "Convective chimneys that accelerate heat dissipation", "Wind tunnels that reduce ambient temperatures"], "correct": 1},
            {"q": "Which factor does the passage identify as determining baseline urban warming potential?", "options": ["Population density per square kilometer", "Ratio of building height to street width", "Low-albedo surface coverage creating energy absorption", "Industrial activity concentration"], "correct": 2},
            {"q": "The passage implies that urban geometry's impact on heat islands operates through:", "options": ["Restricting airflow while maximizing radiation interception", "Channeling winds to create localized cooling zones", "Shading effects that reduce direct solar gain", "Thermal stratification in vertical building cores"], "correct": 0},
            {"q": "What mechanism does the text describe for three-dimensional heat exchange in cities?", "options": ["Convective loops between buildings and atmosphere", "Reduced airflow between buildings preventing heat removal", "Vertical mixing enhanced by building-induced turbulence", "Horizontal heat transfer through connected structures"], "correct": 1},
            {"q": "The passage indicates that material-specific thermal mass contributes to heat islands by:", "options": ["Absorbing radiation faster than natural surfaces", "Preventing nighttime radiative cooling to space", "Delaying energy release through high thermal inertia", "Converting kinetic energy to thermal energy"], "correct": 2},
            {"q": "According to the text, which intervention demonstrates the most comprehensive heat reduction?", "options": ["Increasing surface albedo through white roof programs", "Supplementing solar heating with alternative energy sources", "Installing green infrastructure in strategic locations", "Modifying building codes to require thermal breaks"], "correct": 1},
            {"q": "The passage suggests that redressing environmental justice in heat exposure requires:", "options": ["Relocating vulnerable populations to cooler districts", "Subsidizing air conditioning for low-income residents", "Prioritizing heat-reducing interventions in affected communities", "Implementing city-wide cooling standards"], "correct": 2},
            {"q": "Which temporal pattern of urban heat accumulation does the text describe?", "options": ["Linear accumulation during daylight with rapid evening dissipation", "Exponential growth until reaching thermal equilibrium", "Diurnal cycles with incomplete nighttime cooling creating buildup", "Seasonal variations overwhelming daily temperature fluctuations"], "correct": 2}
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
        'summary_integrated': 'CRISPR–Cas systems originated as a bacterial immune defense that stores viral DNA fragments to recognize and cut them during future infections. Scientists repurposed this natural mechanism to edit genes in plants, animals, and humans. By designing a guide RNA that matches a chosen DNA sequence, the Cas enzyme locates the target, makes a double-strand break, and lets the cell\'s repair machinery rewrite it. This principle—guide, cut, and repair—has revolutionized biology. Compared with earlier tools like zinc-finger nucleases or TALENs, CRISPR is faster, cheaper, and easier to program, allowing labs worldwide to explore disease correction, crop improvement, and ecological restoration.\n\nYet precision is statistical: guide RNAs sometimes mispair, producing off-target edits. Researchers counter this by adjusting guide length, redesigning Cas enzymes for higher fidelity, or using base and prime editors that modify single letters without cutting both strands. Some early agricultural trials also used CRISPR to create bioluminescent plants as visible markers of editing success, though these remained experimental and were never commercialized.\n\nDelivery remains the hardest challenge. Viral vectors are efficient but small and may trigger immune responses; lipid nanoparticles can transport larger cargoes but often concentrate in the liver. Timing also matters: prolonged Cas activity increases unwanted cuts, so transient or self-limiting systems are being developed.\n\nBeyond medicine, CRISPR shapes ethics and governance—raising questions about germ-line editing, access, and fairness. The technology\'s success will depend not only on accuracy but on transparency and responsibility in how humanity edits its own future.',
        'summary_segmented': '''CRISPR began as a bacterial immune system that records viral DNA fragments to recognize future invaders.
Scientists reprogrammed this system using synthetic guide RNA to direct Cas enzymes to precise genome locations.
The process "guide, cut, and repair" made gene editing faster, cheaper, and globally accessible.
Precision challenges persist because partial guide mismatches can create off-target edits.
Enhanced Cas variants and base/prime editors increase fidelity while minimizing double-strand breaks.
Some early agricultural trials used CRISPR to create bioluminescent plants as visible markers of editing success.
Delivery remains the major barrier: viral vectors are efficient but small; lipid nanoparticles carry more but risk inflammation.
Self-limiting and inducible CRISPR systems control activity duration, improving safety.
Germ-line editing is ethically restricted because changes are heritable and affect future generations.
CRISPR now extends to agriculture, ecology, and health governance, requiring transparency, inclusion, and equitable access.''',
        'questions': [
            {"q": "Which conceptual shift best characterizes the evolution from early CRISPR applications to current refinements?", "options": ["From probabilistic accuracy to deterministic precision", "From crude double-strand breaks to subtle single-base modifications", "From ex vivo exclusivity to in vivo predominance", "From agricultural origins to medical applications"], "correct": 1},
            {"q": "According to the passage, which claim about CRISPR's agricultural implementations accurately reflects early experimental work?", "options": ["Bioluminescent marker plants were developed and achieved limited commercial deployment", "Visual editing markers using fluorescent proteins were created but remained confined to research settings", "Marker plants were explored experimentally but never reached commercialization", "Bioluminescent indicators were successfully integrated into crop monitoring systems"], "correct": 2},
            {"q": "The text implies that the relationship between editing precision and delivery method is best characterized as:", "options": ["Synergistic—precision amplifies delivery efficiency", "Independent—each presents distinct technical challenges", "Antagonistic—improving one compromises the other", "Sequential—delivery must precede precision optimization"], "correct": 1},
            {"q": "Which juxtaposition most accurately captures the tension between CRISPR's technical capabilities and its clinical implementation?", "options": ["Research validation versus patient improvement with acceptable risk", "Theoretical elegance versus practical complexity", "Cutting precision versus repair unpredictability", "Component accessibility versus biosecurity imperatives"], "correct": 0},
            {"q": "The passage suggests that public acceptance of gene-edited organisms hinges primarily on:", "options": ["The distinction between somatic and germline modifications", "Transparency about methodology and peer review", "Perceived direct benefits versus corporate advantages", "Regulatory approval and safety testing duration"], "correct": 2},
            {"q": "How does the temporal dimension of Cas enzyme activity create a paradox in therapeutic applications?", "options": ["Sustained activity improves on-target efficiency but amplifies off-target risk", "Brief exposure ensures safety but requires repeated treatments", "Optimal timing varies unpredictably between cell types", "Enzyme degradation interferes with guide RNA stability"], "correct": 0},
            {"q": "The passage's characterization of CRISPR as \"a mirror of human values\" most directly refers to:", "options": ["Its origin in natural bacterial systems", "The necessity of patient consent in clinical trials", "Societal choices about balancing innovation with equity", "The reflection of DNA sequences in guide RNA design"], "correct": 2},
            {"q": "Which constraint most fundamentally limits the cargo capacity of current CRISPR delivery systems?", "options": ["Physical limitations of viral vectors like AAVs", "The molecular weight of Cas9 protein complexes", "The inverse relationship between vector size and cellular uptake", "Immunogenic properties of larger delivery vehicles"], "correct": 0},
            {"q": "The text suggests that the shift from \"editing to modulation\" represents which broader scientific principle?", "options": ["Reversible control superseding permanent alteration", "Diagnostic applications replacing therapeutic ones", "Epigenetic regulation without genomic modification", "Protein engineering overtaking nucleic acid manipulation"], "correct": 2},
            {"q": "What paradox does the passage identify regarding the democratization of CRISPR technology?", "options": ["Increased accessibility correlates with decreased innovation", "Lower costs have increased regulatory burden", "Simplification has revealed underlying complexity", "Wider availability necessitates stricter biosecurity measures"], "correct": 3},
            {"q": "The distinction between SpCas9-HF1 and conventional Cas9 exemplifies which engineering strategy?", "options": ["Algorithmic prediction superseding empirical testing", "Structural modification of protein-DNA interfaces", "Thermodynamic stabilization of guide RNA binding", "Kinetic acceleration of catalytic turnover"], "correct": 1},
            {"q": "According to the passage, what factor most critically differentiates ethically permissible somatic editing from restricted germline interventions?", "options": ["Technical reversibility of induced changes", "Verification requirements for editing accuracy", "Magnitude of potential phenotypic alterations", "Consent implications for non-existent descendants"], "correct": 3},
            {"q": "The passage implies that CRISPR's transformation of agriculture depends most crucially on:", "options": ["Achieving consensus on transgenic versus cisgenic classifications", "Developing traits with visible consumer benefits", "Ensuring equitable access to editing tools and seeds", "Demonstrating ecological safety through longitudinal studies"], "correct": 2},
            {"q": "Which epistemological shift does the text identify in how CRISPR research is validated and communicated?", "options": ["From peer review to public registries", "From selective reporting to comprehensive data transparency", "From academic publishing to commercial disclosure", "From qualitative description to quantitative metrics"], "correct": 1},
            {"q": "The analogy between biosecurity in biotechnology and cybersecurity in computing suggests that:", "options": ["Vigilance culture must develop parallel to technological openness", "Technical solutions will ultimately supersede policy interventions", "Defensive measures must evolve alongside offensive capabilities", "Open-source development inherently compromises security"], "correct": 0}
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
        'summary_integrated': 'Between 2020 and 2022, a synchronized disruption revealed how deeply modern economies depend on semiconductors. The pandemic boosted demand for consumer electronics while factory shutdowns, port delays, and infrastructure failures—including a catastrophic fire at a Japanese substrate plant—froze supply at critical points. Semiconductor fabrication is slow and costly: each "fab" requires billions of dollars and months to construct, while wafer production demands hundreds of specialized process steps using ultra-pure chemicals and gases. Automakers that pre-booked capacity were prioritized over those who negotiated annually, demonstrating how commercial relationships shape allocation as much as technology needs.\n\nWafers move through precise sequential processes—photolithography to etch circuit patterns, ion implantation to modify electrical properties, and chemical vapor deposition to build microscopic layers. A single bottleneck in specialized inputs like photoresists or rare-earth dopants can halt production globally. Geographic concentration worsens fragility: Taiwan and South Korea dominate advanced fabrication, while the Netherlands monopolizes extreme ultraviolet lithography equipment, and the U.S. leads design software. Recent pilot programs deployed quantum annealing processors for chip design optimization that reduced development cycles from months to weeks. True resilience requires geographic diversification, workforce training, and harmonized international standards. Some industry consortium explored creating regional semiconductor stockpile facilities with rotating reserves for emergency allocation, though implementation remained limited.\n\nCompanies are transitioning from pure efficiency optimization toward risk-adjusted strategies, maintaining buffer inventories for critical components and developing adaptive supply contracts. Visibility into capacity and demand across the supply network helps align incentives. Governments are co-funding fabrication facilities to reduce dependence on concentrated regions. Ultimately, semiconductor resilience depends not merely on technical infrastructure but on institutional trust, transparent information-sharing, and sustained political commitment to balance market efficiency with systemic robustness.',
        'summary_segmented': '''The 2020–22 shortage exposed how modern economies depend on semiconductors for automobiles, consumer electronics, and critical infrastructure.
Pandemic-driven demand surges, factory shutdowns, and cascading logistics failures froze supply precisely when reopening economies needed chips most.
Semiconductor fabs are capital-intensive facilities requiring billions of dollars and years to build, making rapid capacity expansion nearly impossible.
Production involves hundreds of sequential steps—photolithography, ion implantation, chemical vapor deposition—each demanding specialized materials and ultra-pure process inputs.
Geographic concentration in East Asia for fabrication and the Netherlands for lithography equipment creates single-point vulnerabilities in natural disasters and geopolitical tensions.
Recent pilot programs deployed quantum annealing processors for chip design optimization that reduced development cycles from months to weeks.
Just-in-time logistics that worked for consumer goods failed for semiconductors because long manufacturing cycles and unpredictable demand spikes left no inventory buffer.
When automotive demand collapsed in 2020, foundries reallocated capacity to consumer electronics, then couldn't meet automotive recovery in 2021.
Leading semiconductor companies announced over $300 billion in investments through 2030, though capacity additions lagged by several years.
Governments allocated tens of billions (U.S. $52.7B, EU €43B) for domestic production, though Western costs run 30-50% higher than East Asian facilities.''',
        'questions': [
            {"q": "The passage suggests that the fundamental tension in modern semiconductor economics stems from:", "options": ["The inverse relationship between miniaturization costs and market demand", "Competition between Asian and American manufacturing capacity", "Invisible capital depreciation versus visible operational expenses", "Environmental regulations constraining production scalability"], "correct": 2},
            {"q": "According to the text, what specialized materials does semiconductor production require in its hundreds of sequential processing steps?", "options": ["Ultra-pure resins for photolithographic pattern transfer", "Ultra-pure chemicals for etching and deposition processes", "Ultra-pure polymers for inter-layer insulation", "Ultra-pure ceramics for thermal management"], "correct": 1},
            {"q": "Which statement about semiconductor photolithography systems most accurately reflects the passage's claims?", "options": ["ASML produces over 90% of machines despite controlling less than half the market", "EUV systems cost over $150 million and require nanometer-scale precision", "Dutch manufacturing dominance resulted from 1990s industrial policy decisions", "Photoresist compounds represent the primary bottleneck in chip production"], "correct": 1},
            {"q": "The text's characterization of \"leading-edge physics requiring capital investments exceeding $20 billion\" implies:", "options": ["Manufacturing barriers that effectively create natural monopolies", "Linear scaling between investment size and production capacity", "Diminishing returns on capital expenditure beyond threshold amounts", "Predictable correlations between facility cost and chip performance"], "correct": 0},
            {"q": "What paradox does the passage identify regarding Silicon Valley's semiconductor ecosystem?", "options": ["Geographic concentration enhances vulnerability while enabling innovation", "Venture capital avoids hardware despite software's dependence on chips", "Academic research exceeds industrial capacity for implementation", "Environmental regulations prevent expansion despite market demand"], "correct": 0},
            {"q": "The relationship between node size advancement and economic viability is best characterized as:", "options": ["Exponentially decreasing costs with each generation", "Linear progression limited by photolithographic wavelengths", "Bottleneck-critical precision creating pre-pandemic supply fragility", "Thermodynamic limits approaching quantum mechanical boundaries"], "correct": 2},
            {"q": "According to the passage, what factor most critically enables ASML's market position?", "options": ["Patents on extreme ultraviolet light generation methods", "Exclusive partnerships with major semiconductor manufacturers", "Production of machines that others cannot economically replicate", "Government subsidies from the Netherlands"], "correct": 2},
            {"q": "The text suggests that water consumption in semiconductor fabrication represents:", "options": ["A yield-proportional variable that scales with production volume", "An overlooked environmental cost of digital infrastructure", "The primary limiting factor for facility location decisions", "A solved problem through closed-loop recycling systems"], "correct": 1},
            {"q": "Which claim about semiconductor supply chain resilience appears in the article?", "options": ["The 2020-2022 shortage demonstrated previously theoretical vulnerabilities", "Geographic distribution inherently reduces systemic risk", "Inventory buffers proved adequate for pandemic-scale disruptions", "Vertical integration offers superior resilience to specialized suppliers"], "correct": 0},
            {"q": "The passage's reference to \"Battlefronts emerge not merely in capital equipment\" most directly addresses:", "options": ["Military applications of semiconductor technology", "Geopolitical dimensions of supply chain control", "Competition between equipment manufacturers", "Labor disputes in fabrication facilities"], "correct": 1},
            {"q": "What distinguishes Taiwan Semiconductor Manufacturing Company's 2021 expansion?", "options": ["It represented the first sub-10 nanometer production facility outside Asia", "The facility would exclusively produce military-grade semiconductors", "It marked TSMC's transition from foundry services to chip design", "Arizona received $4 billion compared to typical billion-dollar investments"], "correct": 3},
            {"q": "The text indicates that game console semiconductor delays resulted from:", "options": ["Prioritization of automotive industry contracts", "Five-dollar microcontroller supply constraints", "Advanced processor manufacturing limitations", "Logistical disruptions in trans-Pacific shipping"], "correct": 1},
            {"q": "According to the passage, what economic principle governs modern fabrication facility investments?", "options": ["Returns diminish beyond optimal facility size", "Geographic clustering reduces per-unit costs", "Continuous operation becomes economically mandatory", "Depreciation timelines shorten with each node generation"], "correct": 2},
            {"q": "The passage implies that East Asian fabrication dominance primarily resulted from:", "options": ["Lower labor costs and environmental standards", "Concentration effects and established expertise", "Government subsidies exceeding Western support", "Superior educational systems producing skilled workers"], "correct": 1},
            {"q": "Which technological constraint does the text identify as approaching fundamental limits?", "options": ["Silicon wafer purity reaching theoretical maxima", "Photolithographic wavelengths nearing atomic dimensions", "Power consumption exceeding cooling capacity", "Quantum effects disrupting transistor functionality"], "correct": 3}
        ]
    }
}

# Section 1: Familiarity Ratings (10 items, 1-7 Likert)
PRIOR_KNOWLEDGE_FAMILIARITY_TERMS = [
    "Heat flux",
    "Permeable pavement",
    "Gene drive",
    "Base editing",
    "Prime editing",
    "Wafer",
    "Lithography mask",
    "System-on-a-chip (SoC)",
    "Reflective coating",
    "Cooling corridor"
]

# Section 2: Concept Recognition Check (10 different terms, Yes/No)
PRIOR_KNOWLEDGE_RECOGNITION_TERMS = [
    "Urban heat island",
    "Green roof",
    "CRISPR-Cas9",
    "Guide RNA",
    "Off-target mutation",
    "Foundry",
    "Photolithography",
    "Microcontroller",
    "Thermal mass",
    "Evapotranspiration"
]

# Keep old variable for backward compatibility (used in Section 3 quiz)
PRIOR_KNOWLEDGE_TERMS = PRIOR_KNOWLEDGE_FAMILIARITY_TERMS + PRIOR_KNOWLEDGE_RECOGNITION_TERMS

PRIOR_KNOWLEDGE_QUIZ = [
    {"q": "What does *albedo* measure?", "options": ["Heat capacity", "Reflectivity of surfaces", "Humidity levels", "Wind speed"], "correct": 1},
    {"q": "*CRISPR* technology is primarily used for:", "options": ["Protein folding", "Genome editing", "MRI imaging", "Battery storage"], "correct": 1},
    {"q": "A semiconductor *foundry* is:", "options": ["A retail store", "A manufacturing facility for chips", "A shipping container", "A mining operation"], "correct": 1},
    {"q": "*Evapotranspiration* refers to:", "options": ["Heat conduction", "Water loss from plants and soil", "Wind patterns", "Solar radiation"], "correct": 1},
    {"q": "*Supply chain resilience* means:", "options": ["Always having low inventory", "Ability to recover from disruptions", "Using only one supplier", "Minimizing costs"], "correct": 1},
]

AI_TRUST_QUESTIONS = {
    "trust": [
        "I generally trust information generated by AI tools.",
        "AI systems usually provide accurate and fair results.",
        "I feel comfortable relying on AI to support my learning or work tasks.",
    ],
    "dependence": [
        "I often rely on digital tools to remember or store information for me.",
        "When I need to recall something, I usually check my device instead of trying to remember it.",
        "Technology helps me think more efficiently than relying only on my memory.",
    ],
    "skill": [
        "I feel confident using AI-powered applications or systems.",
        "I usually learn how to use new digital tools quickly.",
    ],
}

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
    # set a basic randomization so downstream pages work
    if not session.get("article_order"):
        session["article_order"] = ["uhi", "crispr", "semiconductors"]
        session["timing_order"]  = ["synchronous", "pre_reading", "post_reading"]
        session["structure_condition"] = "integrated"
        session["current_article"] = 0
    # minimal logs so csvs stay consistent
    log_data(pid, "consent", {"accepted": True, "skipped": True})
    log_data(pid, "prior_knowledge", {"skipped": True})
    log_data(pid, "ai_trust", {"skipped": True})
    log_data(pid, "randomization", {
        "structure": session["structure_condition"],
        "article_order": json.dumps(session["article_order"]),
        "timing_order": json.dumps(session["timing_order"]),
        "skipped": True
    })
    log_data(pid, "reading_behavior", {"skipped": True})
    log_data(pid, "test_responses", {"skipped": True})
    log_data(pid, "manipulation_check", {"skipped": True})
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
    return redirect(url_for("ai_trust"))

@app.route("/skip_ai_trust")
def skip_ai_trust():
    pid = _ensure_pid()
    log_data(pid, "ai_trust", {"skipped": True})
    # also prepare randomization so reading/test work
    session["structure_condition"] = "integrated"
    session["timing_order"]  = ["synchronous", "pre_reading", "post_reading"]
    session["article_order"] = ["uhi", "crispr", "semiconductors"]
    session["current_article"] = 0
    log_data(pid, "randomization", {
        "structure": session["structure_condition"],
        "article_order": json.dumps(session["article_order"]),
        "timing_order": json.dumps(session["timing_order"])
    })
    return redirect(url_for("reading_phase", article_num=0))

@app.route("/skip_reading")
def skip_reading():
    _ensure_pid()
    # Ensure minimal experiment state
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    article_num = int(session.get("current_article", 0))
    session.modified = True
    # Skip current reading → go to the 5-minute pre-test break for this article
    return redirect(url_for("break_before_test", article_num=article_num))

@app.route("/skip_test/<int:article_num>")
def skip_test(article_num: int):
    pid = _ensure_pid()
    # Ensure minimal experiment state
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session.modified = True
    ao = session.get("article_order") or []
    to = session.get("timing_order") or []
    log_data(pid, "test_responses", {
        "article_num": article_num,
        "article_key": ao[article_num] if article_num < len(ao) else "",
        "timing":      to[article_num] if article_num < len(to) else "",
        "skipped": True
    })
    next_article = article_num + 1
    if next_article >= 3:
        return redirect(url_for("manipulation_check"))
    return redirect(url_for("short_break", next_article=next_article))

@app.route("/skip_break/<int:next_article>")
def skip_break(next_article: int):
    """Skip the BETWEEN-ARTICLES break → go to NEXT article reading."""
    _ensure_pid()
    # Ensure minimal experiment state
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session.modified = True
    return redirect(url_for("reading_phase", article_num=next_article))

# ---- Skip pre-test break (AFTER reading, BEFORE test) ----

@app.route("/skip_break_before_test/<int:article_num>")
def skip_break_before_test(article_num: int):
    """Skip the AFTER-READING (pre-test) break → go to TEST for this article."""
    _ensure_pid()
    # Always seed a minimal, safe state for testing skips
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
    session["article_order"] = session.get("article_order", ["uhi", "crispr", "semiconductors"])
    session["current_article"] = article_num
    session.modified = True
    try:
        print(f"[DEBUG] /skip_break_before_test -> article_num={article_num}, "
              f"article_order={session.get('article_order')}, "
              f"participant_id={session.get('participant_id')}")
    except Exception:
        pass
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
    # Ensure minimal experiment state
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
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
    # Ensure minimal experiment state
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
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
    session["structure_condition"] = session.get("structure_condition", "integrated")
    session["timing_order"] = session.get("timing_order", ["synchronous", "pre_reading", "post_reading"])
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
    log_data(pid, "manipulation_check", {"skipped": True})
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
        recognition_terms=[_auto_translate(term, _get_lang()) for term in PRIOR_KNOWLEDGE_RECOGNITION_TERMS],
        quiz=[{
            "q": _auto_translate(q["q"], _get_lang()),
            "options": [_auto_translate(opt, _get_lang()) for opt in q["options"]],
            "correct": q["correct"]
        } for q in PRIOR_KNOWLEDGE_QUIZ],
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
    prior_knowledge_score = quiz_score / 5  # 5 PK items
    concept_count = len(concept_list.split()) if concept_list else 0

    exclude = False
    reasons = []
    if familiarity_mean >= 6.0:
        exclude, reasons = True, reasons + ["high_familiarity"]
    if term_recognition_count >= 8:
        exclude, reasons = True, reasons + ["high_term_recognition"]
    if prior_knowledge_score == 1.0:
        exclude, reasons = True, reasons + ["perfect_quiz_score"]

    log_data(session["participant_id"], "prior_knowledge", {
        "familiarity_mean": familiarity_mean,
        "term_recognition_count": term_recognition_count,
        "prior_knowledge_score": prior_knowledge_score,
        "concept_count": concept_count,
        "excluded": exclude,
        "exclusion_reasons": ",".join(reasons) if reasons else "none",
    })

    # Reset PK timer so revisits (if any) start a fresh 5"‘minute window
    session.pop("pk_started_at", None)

    # IMPORTANT: Do NOT exclude participants during testing runs.
    # We keep logging the exclusion metrics but always continue to AI Trust.
    return jsonify({"redirect": url_for("ai_trust")})

@app.route("/ai_trust")
@require_pid
def ai_trust():
    # Start (or reuse) a fixed 5"‘minute window for this section
    if "ait_started_at" not in session:
        session["ait_started_at"] = datetime.now().timestamp()
    ait_deadline = session["ait_started_at"] + 5 * 60  # seconds

    return render_template(
        "ai_trust.html",
        questions={
            "trust": [_auto_translate(q, _get_lang()) for q in AI_TRUST_QUESTIONS["trust"]],
            "dependence": [_auto_translate(q, _get_lang()) for q in AI_TRUST_QUESTIONS["dependence"]],
            "skill": [_auto_translate(q, _get_lang()) for q in AI_TRUST_QUESTIONS["skill"]],
        },
        ait_deadline=ait_deadline,
        server_now=int(datetime.now().timestamp()),
        fixed_minutes=5,
    )

@app.route("/submit_ai_trust", methods=["POST"])
@require_pid
def submit_ai_trust():
    data = request.get_json(force=True) or {}

    def mean_of(d):
        return (sum(map(int, d.values())) / max(1, len(d))) if d else 0

    ai_trust_score      = mean_of(data.get("trust", {}))
    ai_dependence_score = mean_of(data.get("dependence", {}))
    tech_skill_score    = mean_of(data.get("skill", {}))

    log_data(session["participant_id"], "ai_trust", {
        "ai_trust_score": ai_trust_score,
        "ai_dependence_score": ai_dependence_score,
        "tech_skill_score": tech_skill_score,
        "open_reflection": (data.get("reflection") or "").strip(),
    })

    session["ai_trust_score"] = ai_trust_score
    session["ai_dependence_score"] = ai_dependence_score

    # Reset AI"‘Trust timer so revisits (if any) start a fresh 5"‘minute window
    session.pop("ait_started_at", None)

    return jsonify({"redirect": url_for("randomize")})

# =============================================================================
# COUNTERBALANCED RANDOMIZATION SYSTEM
# =============================================================================

# Between-subject factor: AI Output Structure
STRUCTURE_CONDITIONS = ['A1_Integrated', 'A2_Segmented']

# Within-subject factor: Summary Timing (all 6 possible counterbalanced orders)
TIMING_ORDERS = [
    {'order': 1, 'article1': 'B1_Synchronous', 'article2': 'B2_PreReading', 'article3': 'B3_PostReading'},
    {'order': 2, 'article1': 'B1_Synchronous', 'article2': 'B3_PostReading', 'article3': 'B2_PreReading'},
    {'order': 3, 'article1': 'B2_PreReading', 'article2': 'B1_Synchronous', 'article3': 'B3_PostReading'},
    {'order': 4, 'article1': 'B2_PreReading', 'article2': 'B3_PostReading', 'article3': 'B1_Synchronous'},
    {'order': 5, 'article1': 'B3_PostReading', 'article2': 'B1_Synchronous', 'article3': 'B2_PreReading'},
    {'order': 6, 'article1': 'B3_PostReading', 'article2': 'B2_PreReading', 'article3': 'B1_Synchronous'}
]

# Mapping from new naming to internal representation
TIMING_MAP = {
    'B1_Synchronous': 'synchronous',
    'B2_PreReading': 'pre_reading',
    'B3_PostReading': 'post_reading'
}

STRUCTURE_MAP = {
    'A1_Integrated': 'integrated',
    'A2_Segmented': 'segmented'
}

def assign_participant_conditions(participant_id):
    """
    Assign counterbalanced conditions to a participant.
    
    Returns:
        dict with structureCondition, timingOrder, article1Timing, article2Timing, article3Timing
    """
    # Step 1: Randomly assign Structure condition (50/50 split)
    structure_condition = random.choice(STRUCTURE_CONDITIONS)
    
    # Step 2: Randomly assign Timing order (1 of 6 counterbalanced orders)
    timing_order_index = random.randint(0, 5)
    timing_order = TIMING_ORDERS[timing_order_index]
    
    # Step 3: Create assignment object
    assignment = {
        'participantId': participant_id,
        'structureCondition': structure_condition,
        'timingOrder': timing_order['order'],
        'article1Timing': timing_order['article1'],
        'article2Timing': timing_order['article2'],
        'article3Timing': timing_order['article3'],
        'assignmentTimestamp': datetime.now().isoformat()
    }
    
    return assignment

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

    # Assign counterbalanced conditions
    participant_id = session["participant_id"]
    assignment = assign_participant_conditions(participant_id)
    
    # Map to internal representation for compatibility
    structure_internal = STRUCTURE_MAP[assignment['structureCondition']]
    timing_order_internal = [
        TIMING_MAP[assignment['article1Timing']],
        TIMING_MAP[assignment['article2Timing']],
        TIMING_MAP[assignment['article3Timing']]
    ]

    # Store in session
    session["structure_condition"] = structure_internal
    session["timing_order"] = timing_order_internal
    session["article_order"] = article_keys
    session["current_article"] = 0
    
    # Store full assignment details for tracking
    session["assignment_details"] = assignment

    # Log with both old format (for compatibility) and new format (for analysis)
    log_data(participant_id, "randomization", {
        "structure": structure_internal,  # Old format: "integrated" or "segmented"
        "structureCondition": assignment['structureCondition'],  # New format: "A1_Integrated" or "A2_Segmented"
        "timing_order": json.dumps(timing_order_internal),  # Old format: ["synchronous", "pre_reading", "post_reading"]
        "timingOrder": assignment['timingOrder'],  # New format: 1-6
        "article1Timing": assignment['article1Timing'],  # New format: "B1_Synchronous", etc.
        "article2Timing": assignment['article2Timing'],
        "article3Timing": assignment['article3Timing'],
        "article_order": json.dumps(article_keys),
        "assignmentTimestamp": assignment['assignmentTimestamp']
    })

    # For pre-reading mode, go to AI summary first
    if timing_order_internal[0] == "pre_reading":
        return redirect(url_for("ai_summary_view", article_num=0))

    return redirect(url_for("reading_phase", article_num=0))

@app.route("/ai_summary/<int:article_num>")
@require_pid
def ai_summary_view(article_num: int):
    """Separate page for viewing AI summary (pre-reading or post-reading)"""
    article_order = session.get("article_order") or []
    timing_order = session.get("timing_order") or []
    structure = session.get("structure_condition")
    
    if not article_order or article_num >= len(article_order):
        return redirect(url_for("randomize"))
    
    article_key = article_order[article_num]
    article = get_localized_article(article_key)  # Use localized version
    if not article:
        return redirect(url_for("randomize"))
    
    summary_key = f"summary_{structure}"
    summary = article.get(summary_key, "")
    
    # Determine mode from timing
    timing = timing_order[article_num] if article_num < len(timing_order) else "pre_reading"
    mode = "pre_reading" if timing == "pre_reading" else "post_reading"
    
    session["current_article"] = article_num
    session["current_article_key"] = article_key
    
    return render_template(
        "ai_summary_view.html",
        article_num=article_num,
        summary=summary,
        structure=structure,
        mode=mode
    )

@app.route("/reading/<int:article_num>", methods=["GET"])
@require_pid
def reading_phase(article_num: int):
    # Pull from session defensively
    article_order = session.get("article_order") or []
    timing_order = session.get("timing_order") or []
    structure = session.get("structure_condition")

    # If anything is missing, (re)randomize cleanly
    if not article_order or not timing_order or structure not in ("integrated", "segmented"):
        return redirect(url_for("randomize"))

    # Index guards
    if article_num < 0:
        return redirect(url_for("reading_phase", article_num=0))
    if article_num >= len(article_order) or article_num >= len(timing_order):
        return redirect(url_for("manipulation_check"))

    # Current article
    article_key = article_order[article_num]
    article = get_localized_article(article_key)  # Use localized version
    if not article:
        # Dict changed mid-run → reseed
        return redirect(url_for("randomize"))

    # Summary by structure
    summary_key = f"summary_{structure}"
    summary = article.get(summary_key, "")

    timing = timing_order[article_num]
    
    # For pre-reading mode, redirect to AI summary first if not already viewed
    if timing == "pre_reading":
        if not session.get(f"pre_summary_viewed_{article_num}", False):
            return redirect(url_for("ai_summary_view", article_num=article_num))

    # Record session state
    session["current_article"] = article_num
    session["current_article_key"] = article_key
    session["current_timing"] = timing
    session["reading_start_time"] = datetime.now().isoformat()

    return render_template(
        "reading.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        article_text=article["text"],
        summary=summary,
        timing=timing,
        structure=structure,
    )


# ---- Summary lock endpoint ----
@app.route("/lock_summary", methods=["POST"])
@require_pid
def lock_summary():
    data = request.get_json(force=True) or {}
    article_num = int(data.get("article_num", session.get("current_article", 0)))
    session[f"summary_locked_{article_num}"] = True
    # Optional: log the action
    try:
        log_data(session["participant_id"], "summary_locked", {"article_num": article_num})
    except Exception:
        pass
    return jsonify({"ok": True})

@app.route("/mark_pre_summary_viewed", methods=["POST"])
@require_pid
def mark_pre_summary_viewed():
    data = request.get_json(force=True) or {}
    article_num = int(data.get("article_num", session.get("current_article", 0)))
    session[f"pre_summary_viewed_{article_num}"] = True
    session.modified = True
    return jsonify({"ok": True})

@app.route("/log_summary_viewing", methods=["POST"])
@require_pid
def log_summary_viewing():
    """Log time spent viewing AI summary"""
    data = request.get_json(force=True) or {}
    article_num = data.get("article_num", session.get("current_article", 0))
    article_order = session.get("article_order") or []
    article_key = article_order[article_num] if article_num < len(article_order) else None
    timing_order = session.get("timing_order") or []
    timing = timing_order[article_num] if article_num < len(timing_order) else None
    
    log_data(session["participant_id"], "summary_viewing", {
        "article_num": article_num,
        "article_key": article_key,
        "mode": data.get("mode"),  # 'pre_reading' or 'post_reading'
        "structure": data.get("structure"),  # 'integrated' or 'segmented'
        "time_spent_ms": data.get("time_spent_ms", 0),
        "time_spent_seconds": round(data.get("time_spent_ms", 0) / 1000, 2),
        "timestamp": data.get("timestamp")
    })
    return jsonify({"status": "ok"})

@app.route("/log_reading", methods=["POST"])
@require_pid
def log_reading():
    data = request.get_json(force=True) or {}
    data["article_num"] = session.get("current_article")
    data["article_key"] = session.get("current_article_key")
    data["timing"] = session.get("current_timing")
    log_data(session["participant_id"], "reading_behavior", data)
    return jsonify({"status": "ok"})

# ---- Reading completion endpoint (called by reading.html when reading is finished) ----
@app.route("/reading_complete", methods=["POST", "GET"])
@require_pid
def reading_complete():
    """
    Called by reading.html when the participant finishes reading.
    Sends them to the 5-minute break that occurs BEFORE the test of the current article.
    """
    article_num = int(session.get("current_article", 0))
    return redirect(url_for("break_before_test", article_num=article_num))

@app.route("/dev/recall_instruction_bypass/<int:article_num>", endpoint="dev_recall_instruction_bypass")
@require_pid
def recall_instruction_bypass(article_num: int):
    """DEV: bypass recall-instruction screen and go straight to TEST for this article."""
    article_order = session.get("article_order") or []
    if article_num >= len(article_order):
        return redirect(url_for("manipulation_check"))
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
        return redirect(url_for("manipulation_check"))
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

    return render_template(
        "test.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        questions=article["questions"],
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
        return redirect(url_for("manipulation_check"))
    
    article_key = article_order[article_num]
    article = get_localized_article(article_key)
    if not article:
        return redirect(url_for("randomize"))
    
    # Log that recall was skipped
    try:
        log_data(session["participant_id"], "recall_skipped", {
            "article_num": article_num,
            "article_key": article_key
        })
    except Exception:
        pass
    
    return render_template(
        "test.html",
        article_num=article_num,
        article_key=article_key,
        article_title=article["title"],
        questions=article["questions"],
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

    article_order = session.get("article_order") or []
    timing_order = session.get("timing_order") or []

    if article_num < len(article_order):
        data["article_key"] = article_order[article_num]
        if article_num < len(timing_order):
            data["timing"] = timing_order[article_num]

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
            "timing": data.get("timing"),
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
        # Guard: require all MCQ questions answered before proceeding
        if article and "questions" in article:
            questions = article["questions"]
            missing_or_invalid = []
            for q_idx, q in enumerate(questions):
                q_key = f"q{q_idx}"
                ans = mcq_data.get(q_key, None)
                # Valid answers are integers in option index range
                try:
                    options_len = len(q.get("options", []))
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
        
        if article and "questions" in article:
            questions = article["questions"]
            for q_idx, question in enumerate(questions):
                total_questions += 1
                q_key = f"q{q_idx}"
                participant_answer = mcq_data.get(q_key, None)
                correct_answer = question.get("correct", None)
                
                # Check if answer is correct (handle None/missing answers)
                is_correct = (participant_answer is not None and 
                             participant_answer == correct_answer)
                question_accuracy[q_key] = {
                    "participant_answer": participant_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct
                }
                
                if is_correct:
                    correct_count += 1
        
        # Calculate accuracy rate as percentage
        accuracy_rate = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        
        # Log MCQ responses with accuracy and answer times
        log_data(session["participant_id"], "mcq_responses", {
            "article_num": article_num,
            "article_key": article_key,
            "timing": data.get("timing"),
            "mcq_answers": json.dumps(mcq_data),
            "mcq_answer_times_ms": json.dumps(mcq_answer_times_ms),
            "mcq_total_time_ms": mcq_total_time_ms,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "accuracy_rate": round(accuracy_rate, 2),
            "question_accuracy": json.dumps(question_accuracy)
        })

    next_article = article_num + 1
    if next_article >= 3:
        # After Article 3 test, go directly to manipulation check (no break after test)
        return jsonify({"redirect": url_for("manipulation_check")})
    # For articles 0 and 1: after test, go to 1-minute break, then break will redirect to next article reading
    return jsonify({"redirect": url_for("short_break", next_article=next_article)})


# ---- Alias for after-reading break (backward compatibility/clarity) ----
@app.route("/break_after_reading/<int:article_num>")
@require_pid
def break_after_reading(article_num: int):
    # Break after reading (5 minutes) - always goes to test after break
    # After test, if article 2, will go to manipulation_check; otherwise go to next article reading
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

@app.route("/manipulation_check")
@require_pid
def manipulation_check():
    return render_template("manipulation_check.html")

@app.route("/submit_manipulation", methods=["POST"])
@require_pid
def submit_manipulation():
    data = request.get_json(force=True) or {}
    log_data(session["participant_id"], "manipulation_check", data)
    return jsonify({"redirect": url_for("debrief")})

@app.route("/debrief")
@require_pid
def debrief():
    return render_template("debrief.html", participant_id=session.get("participant_id"))

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
        "Continue to Multiple Choice", "Submit Test", "Continue Early",
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
        
        # Summaries
        if article.get('summary_integrated'):
            texts_to_translate.append(('summary_integrated', article['summary_integrated']))
        
        if article.get('summary_segmented'):
            texts_to_translate.append(('summary_segmented', article['summary_segmented']))
        
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
    
    # Translate AI Trust questions
    print("  Translating AI Trust questions...")
    for category in ['trust', 'dependence', 'skill']:
        for q in AI_TRUST_QUESTIONS.get(category, []):
            cache_key = _get_cache_key(q, "zh")
            if cache_key not in _translation_cache:
                try:
                    time.sleep(0.1)
                    translated = translator.translate(q)
                    _translation_cache[cache_key] = translated
                    total_translated += 1
                except Exception:
                    pass
    
    # Final save
    if total_translated > 0:
        _save_translation_cache()
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n✓ Pre-translated {total_translated} strings in {elapsed:.1f} seconds")
    print("✓ All content is now cached - switching pages will be instant!")

# =============================================================================
# CONDITION DISTRIBUTION MONITORING
# =============================================================================

@app.route("/dev/condition_distribution")
def get_condition_distribution():
    """
    Monitor condition distribution across all participants.
    Returns JSON with counts for each condition combination.
    """
    distribution = {
        'total': 0,
        'A1_Integrated': 0,
        'A2_Segmented': 0,
        'timingOrders': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
        'combinations': {}
    }
    
    # Read all log files to count assignments
    log_dir = DATA_DIR
    if not os.path.exists(log_dir):
        return jsonify(distribution)
    
    # Scan all participant log files
    for filename in os.listdir(log_dir):
        if not filename.endswith('_log.csv'):
            continue
        
        log_file = os.path.join(log_dir, filename)
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('phase') == 'randomization':
                        # Try to extract new format fields
                        structure = row.get('structureCondition') or row.get('structure')
                        timing_order = row.get('timingOrder')
                        
                        if structure:
                            # Map old format to new format if needed
                            if structure == 'integrated':
                                structure = 'A1_Integrated'
                            elif structure == 'segmented':
                                structure = 'A2_Segmented'
                            
                            if structure in ['A1_Integrated', 'A2_Segmented']:
                                distribution[structure] = distribution.get(structure, 0) + 1
                                distribution['total'] += 1
                                
                                if timing_order:
                                    try:
                                        order_num = int(timing_order)
                                        if 1 <= order_num <= 6:
                                            distribution['timingOrders'][order_num] = distribution['timingOrders'].get(order_num, 0) + 1
                                            
                                            # Track unique combinations
                                            combo_key = f"{structure}_Order{order_num}"
                                            distribution['combinations'][combo_key] = distribution['combinations'].get(combo_key, 0) + 1
                                    except (ValueError, TypeError):
                                        pass
                        break  # Only count first randomization entry per file
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
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
    print("AI Memory Experiment Platform")
    print("=" * 50)
    
    # Use PORT from environment (for cloud deployment) or default to 8080
    port = int(os.environ.get("PORT", 8080))
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
