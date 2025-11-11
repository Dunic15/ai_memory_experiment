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
        'free_recall_prompt': 'Please write everything you remember from the article within 3 minutes. Try to describe main ideas and relationships — causes, consequences, and solutions — in your own words.',
        'text': '''Cities function as intricate thermodynamic systems where the interaction between material, geometry, and atmosphere determines how energy is stored and released. Every roof, façade, and roadway acts as a localized heat reservoir: during the day, asphalt, brick, and concrete absorb solar radiation, converting it into thermal energy that is re-emitted long after sunset. Unlike vegetated environments that self-regulate through reflection and evapotranspiration, the urban fabric accumulates heat continuously, generating a persistent temperature imbalance known as the urban heat island (UHI) effect. Across metropolitan areas, nighttime temperatures can remain three to seven degrees Celsius higher than surrounding countryside, altering the city's thermal rhythm, elevating energy demand, and exacerbating health risks during prolonged heat waves.

This amplification of warmth arises from a combination of physical, material, and aerodynamic properties that together shape the urban energy budget. Surface albedo, the fraction of sunlight reflected rather than absorbed, is pivotal. Fresh asphalt reflects barely five percent of incoming light, while bright concrete or coated roofs can exceed sixty. Low albedo accelerates heat absorption, while thermal mass—the capacity of stone, brick, and concrete to retain energy—delays nocturnal cooling by slowly releasing heat through conduction and convection. The geometry of dense districts magnifies these processes: tall buildings and narrow streets form "urban canyons" that trap long-wave radiation as it bounces between façades, while constricted airflow suppresses convective dissipation. Finally, the widespread loss of vegetation removes the cooling effects of evapotranspiration. Without plants to convert solar energy into latent heat, nearly all radiation becomes sensible heat that directly warms the air.

The consequences extend well beyond physics. Thermal patterns map onto social ones, producing what scholars describe as thermal inequity. Low-income neighborhoods—often marked by older buildings, minimal green space, and higher traffic—absorb and retain disproportionate heat. During extreme weather, residents face heightened mortality, reduced sleep quality, and soaring energy costs. Utilities respond to surging demand by activating inefficient, carbon-intensive power plants, feeding a cycle of emissions and warming. Thus, the urban heat island is both a physical phenomenon and a social mirror, reflecting the uneven distribution of resources, shade, and resilience within cities.

To counteract these dynamics, planners and engineers emphasize four interlocking principles: reflect, shade, vent, and absorb differently. Reflection increases albedo through high-reflectivity materials. Cool roofs coated with reflective membranes can reduce surface temperature by up to thirty degrees Celsius at noon, cutting indoor cooling loads by ten to twenty percent. Reflective pavements yield smaller gains near ground level due to air mixing but still reduce radiant flux. Shading intercepts solar energy before it is absorbed. Trees, pergolas, and vertical gardens combine optical blocking with evapotranspiration, creating localized "cool pockets" that lower perceived temperature and filter ultraviolet radiation, reducing smog formation. Ventilation focuses on spatial layout. Corridors aligned with prevailing winds flush stagnant air, improving convection and dispersing pollutants, while urban morphology guidelines now include minimum spacing ratios to sustain airflow. Finally, absorbing differently involves redirecting heat into evaporation and infiltration. Permeable pavements, fountains, ponds, and green roofs convert thermal energy into latent heat fluxes, cooling the air through phase change and moderating surface temperature variability.

Real progress depends on integration rather than isolated fixes. Empirical studies show that combined strategies yield cumulative benefits greater than the sum of their parts. In Los Angeles, a mandatory cool-roof policy reduced roof temperatures by twenty-five degrees Celsius yet produced only modest air-cooling effects. When paired with large-scale tree planting, comfort levels rose sharply because radiative, convective, and evaporative mechanisms reinforced each other. Trees remain the most effective natural coolers because they operate at the scale where humans experience heat. In arid regions, however, sustainability demands eco-hydrological design—drought-resistant species, engineered soils, and efficient irrigation systems that preserve evapotranspiration without exhausting water reserves.

Recent technological experimentation has even explored adaptive "color-shifting" coatings capable of darkening in winter to absorb heat and brightening in summer to reflect it, potentially balancing annual thermal cycles. While these coatings remain in the laboratory phase, their concept illustrates a growing ambition to develop intelligent materials that respond dynamically to climate conditions.

Equity remains at the heart of effective cooling policy. If incentives favor private homeowners, affluent neighborhoods tend to adopt new technologies first, deepening spatial disparities. Equity-oriented governance redirects funding toward public goods: greening schoolyards, shading transit stops, and retrofitting social-housing roofs with cool coatings. Because the UHI effect transcends property boundaries, a multitude of small, coordinated actions can achieve significant regional cooling when spatially synchronized. The emerging discipline of thermal-justice planning highlights that mitigation must measure not only temperature change but also fairness in how shade and greenery are distributed.

Monitoring and verification ensure these initiatives endure. Satellite thermal imagery maps broad temperature gradients, while mobile sensors attached to buses or bicycles capture hyperlocal variations. Timing is crucial: midnight measurements capture stored heat, offering a more accurate picture of residual warming than midday readings. Transparency reinforces public trust—open datasets and community-access dashboards allow citizens to monitor progress and hold institutions accountable. A widely cited rule allocates one percent of every project budget to maintenance, measurement, and education, acknowledging that even the most advanced green roofs or reflective surfaces lose performance without long-term care.

The co-benefits of heat mitigation multiply across systems. A mature tree cools air, absorbs carbon, filters particulates, dampens noise, and increases property values. Cool roofs can double as platforms for solar panels, merging renewable generation with passive cooling. Permeable pavements not only lower surface temperature but also reduce runoff, decreasing flood risk and maintenance costs. Framing these interventions as multi-benefit investments allows municipalities to pool funds from health, transport, and energy programs, transforming heat reduction from an environmental add-on into a core component of urban resilience. Life-cycle analyses consistently show payback periods within a decade, once savings from reduced energy use and avoided infrastructure damage are included.

Every measure, however, involves trade-offs. High-reflectivity materials can produce glare if misaligned; dense greenery increases water demand and maintenance; and green roofs add structural weight. The most robust outcomes emerge through participatory design, where local residents identify overheated courtyards, unshaded playgrounds, and blocked wind corridors. Citizen engagement not only strengthens technical accuracy but also ensures legitimacy, turning mitigation into shared stewardship.

Long-term resilience depends on proactive policy rather than crisis management. Building codes that require reflective surfaces, vegetated coverage, and ventilation corridors institutionalize adaptation directly into the city's morphology, avoiding costly retrofits later. Prevention aligns naturally with broader climate adaptation: both aim to stabilize energy flows between built form and atmosphere. Increasingly, cities employ predictive models that integrate meteorological data, land-surface properties, and human mobility to forecast heat accumulation dynamically—an early example of climate informatics guiding spatial planning.

Examples from around the world demonstrate the feasibility of transformation. Tokyo's combination of reflective materials and mandatory greening has measurably reduced nighttime temperatures. Singapore's vertical gardens and sky parks distribute shade vertically, cooling multiple urban layers simultaneously. Paris, transformed after the deadly 2003 heat wave, now mandates cool roofs for public buildings and converts schoolyards into vegetated "islands of freshness" serving as community shelters during emergencies. Across contexts, successful programs share three ingredients: transparency in data, inclusivity in design, and continuity in governance. They prove that urban heat islands are not inevitable by-products of density but reversible legacies of past design choices.

Ultimately, the urban heat island serves as both warning and opportunity. It reveals how societies organize energy, comfort, and justice—how thermodynamics intersects with ethics. When scientists, planners, and citizens collaborate, thermal management evolves from a reactive fix to a deliberate act of civic intelligence. Reflection offers the fastest relief, vegetation the most humane, and planning the most enduring. The cities of the future will not strive to eliminate heat entirely but to modulate it intelligently—to breathe, reflect, and regenerate. In that balance between design and climate, warmth becomes not a symptom of failure but a measure of maturity: the moment when humanity learned to engineer comfort with the same precision it engineers growth.
''',
        'summary_integrated': 'Urban heat islands (UHIs) emerge when the built environment disrupts the natural exchange of heat between surface and atmosphere. Dense urban materials—concrete, asphalt, brick, and metal—absorb solar radiation during the day and release it slowly at night, maintaining city temperatures several degrees above those of nearby rural zones. This persistent imbalance arises from four interdependent factors: low surface reflectivity (albedo), high thermal mass, constrained airflow within "urban canyons," and the loss of vegetation that would otherwise cool the air through evapotranspiration. The outcome is not only a physical anomaly but a social one, as low-income neighborhoods, typically less vegetated and poorly insulated, experience the highest exposure and energy costs during heat waves.\n\nTo mitigate UHIs, planners and engineers apply four principles—reflect, shade, vent, and absorb differently—each targeting a distinct component of urban heat dynamics. Reflective materials such as cool roofs and pavements increase albedo and reduce surface temperature; trees and vertical greenery create shade and evaporative cooling; ventilation corridors restore airflow; and permeable surfaces or water features redirect energy into evaporation rather than air heating. Integrating these methods equitably across districts maximizes long-term impact.\n\nEmerging technologies include adaptive "color-shifting" coatings that darken in winter and brighten in summer to balance thermal loads, though they remain experimental. Systematic monitoring through satellites and sensors ensures accountability, while public engagement anchors resilience in social participation. Ultimately, urban heat mitigation demonstrates that sustainability lies in design intelligence—cities that reflect, ventilate, and regenerate can turn heat from a burden into a measure of collective adaptation.',
        'summary_segmented': '''Urban heat islands arise when dense urban materials trap solar energy and release it slowly, elevating nighttime temperatures.
Four mechanisms drive the effect: low albedo, high thermal mass, restricted airflow, and vegetation loss reducing evapotranspiration.
Heat exposure mirrors inequality—low-income areas with limited greenery face higher health risks and energy burdens.
Planners mitigate heat through four principles: reflect, shade, vent, and absorb differently—each addressing a specific physical pathway.
Reflective surfaces such as cool roofs and pavements raise albedo and can reduce surface temperature by up to 30 °C.
Shade from trees and green façades blocks sunlight and cools air through evaporation, enhancing human comfort and air quality.
Ventilation corridors aligned with prevailing winds restore convective exchange, dispersing heat and pollutants trapped within street canyons.
False lure – Some cities tested adaptive "color-shifting" coatings that darken in winter and brighten in summer to moderate heat.
Integrating reflection, shading, and airflow with equity-based planning produces durable cooling and social benefits simultaneously.
Long-term success depends on transparency, participatory governance, and maintenance—turning heat management into civic collaboration.''',
        'questions': [
            {"q": "Which factor explains why black asphalt heats faster than white concrete?", "options": ["Higher albedo", "Lower albedo", "Greater thickness", "Higher moisture content"], "correct": 1},
            {"q": "Why do concrete and brick keep cities warm after sunset?", "options": ["They reflect long-wave radiation", "They release stored heat slowly", "They evaporate quickly", "They increase wind turbulence"], "correct": 1},
            {"q": "Street canyons intensify heat mainly because they ______.", "options": ["Channel breezes efficiently", "Trap radiation and restrict airflow", "Increase vegetation", "Reduce surface area"], "correct": 1},
            {"q": "Vegetation mitigates heat through ______.", "options": ["Reflection", "Evapotranspiration", "Soil insulation", "Carbon capture only"], "correct": 1},
            {"q": "The \"reflect\" principle in UHI mitigation seeks to ______.", "options": ["Trap sunlight for winter warmth", "Raise surface albedo and lower absorption", "Block humidity", "Improve drainage"], "correct": 1},
            {"q": "Why is combining multiple cooling strategies more effective than a single one?", "options": ["It reduces glare", "It multiplies cooling effects and spreads equity benefits", "It avoids maintenance", "It lowers design cost"], "correct": 1},
            {"q": "Why are \"color-shifting\" coatings being explored? (False-memory item)", "options": ["To adjust surface reflectivity seasonally", "To collect solar power", "To seal cracks", "To reduce construction dust"], "correct": 0},
            {"q": "Which monitoring method best reveals retained nighttime heat?", "options": ["Noon satellite imagery", "Midnight thermal readings", "Annual rainfall data", "Electricity-price records"], "correct": 1},
            {"q": "Beyond cooling, integrated UHI programs also ______.", "options": ["Slow traffic", "Cut pollution and flood risk", "Increase building density", "Raise water tariffs"], "correct": 1},
            {"q": "Global \"Cool City\" collaborations emphasize ______.", "options": ["Tourism promotion", "Data sharing and long-term urban design standards", "Private sponsorship", "Event planning"], "correct": 1},
            {"q": "Urban nights typically remain ____ warmer than rural areas.", "options": ["1–2 °C", "3–7 °C", "8–10 °C", ">10 °C"], "correct": 1},
            {"q": "Why does equity matter in UHI mitigation funding?", "options": ["Wealthier areas heat faster", "Targeting low-income zones maximizes health and comfort gains", "It ensures tree diversity", "It reduces taxation"], "correct": 1},
            {"q": "A practical budgeting rule recommends ____ of every project for monitoring and education.", "options": ["0.1 %", "1 %", "5 %", "10 %"], "correct": 1},
            {"q": "What drawback can result from poorly oriented reflective materials?", "options": ["Glare for drivers", "Lower humidity", "Soil erosion", "Increased rainfall"], "correct": 0},
            {"q": "Lasting prevention of heat islands depends mainly on ______.", "options": ["Public campaigns", "Mandatory urban-design codes and zoning standards", "Volunteer shade projects", "Temporary coatings"], "correct": 1}
        ]
    },
    'crispr': {
        'title': 'CRISPR Gene Editing: Promise, Constraints, and Responsible Use',
        'free_recall_prompt': 'Please recall everything you can from the article in 3 minutes, describing how CRISPR works, its medical and agricultural applications, key limitations, and ethical or governance challenges.',
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
False lure – Some laboratories reported CRISPR-created bioluminescent crops for easier detection of edited plants.
Delivery remains the major barrier: viral vectors are efficient but small; lipid nanoparticles carry more but risk inflammation.
Self-limiting and inducible CRISPR systems control activity duration, improving safety.
Germ-line editing is ethically restricted because changes are heritable and affect future generations.
CRISPR now extends to agriculture, ecology, and health governance, requiring transparency, inclusion, and equitable access.''',
        'questions': [
            {"q": "What natural system originally inspired CRISPR technology?", "options": ["Plant immune response", "Bacterial immune memory", "Human RNA replication", "Viral defense"], "correct": 1},
            {"q": "In gene editing, what element directs the Cas enzyme to its DNA target?", "options": ["Protein code", "Guide RNA sequence", "mRNA transcript", "Antibody complex"], "correct": 1},
            {"q": "\"Off-target edits\" occur when ______.", "options": ["Delivery fails", "Cas cuts similar, unintended DNA sites", "Repair is incomplete", "RNA degrades too early"], "correct": 1},
            {"q": "Base and prime editors improve safety because they ______.", "options": ["Add foreign DNA", "Avoid double-strand breaks", "Delete large sequences", "Block RNA translation"], "correct": 1},
            {"q": "What remains the hardest technical step in CRISPR therapies?", "options": ["Enzyme discovery", "Efficient and safe delivery to target cells", "Temperature regulation", "Protein folding"], "correct": 1},
            {"q": "\"Ex vivo\" treatment refers to ______.", "options": ["Editing genes directly inside the patient", "Editing cells outside the body and reinfusing them", "Editing plant tissue", "DNA sequencing"], "correct": 1},
            {"q": "Why is germ-line editing considered ethically controversial?", "options": ["It is too expensive", "It creates heritable changes passed to future generations", "It is reversible", "It cannot affect embryos"], "correct": 1},
            {"q": "Agricultural use of CRISPR mainly seeks to ______.", "options": ["Increase pesticide application", "Reduce chemical use and improve crop resilience", "Clone livestock", "Alter flavor only"], "correct": 1},
            {"q": "Responsible governance of CRISPR requires ______.", "options": ["Only scientists deciding", "Inclusive oversight with ethics boards and public registries", "Private control", "Government secrecy"], "correct": 1},
            {"q": "What experimental agricultural use of CRISPR was mentioned as early research?", "options": ["Producing drought-resistant rice", "Creating bioluminescent crops for easier detection", "Developing nitrogen-efficient corn hybrids", "Enhancing pest resistance through gene drives"], "correct": 1},
            {"q": "Which delivery vector can carry larger genetic cargo but tends to accumulate in the liver?", "options": ["Viral AAV", "Lipid nanoparticles", "Polymer micelles", "Bacterial plasmids"], "correct": 1},
            {"q": "What risk arises from prolonged Cas enzyme expression in cells?", "options": ["Reduced cutting accuracy", "Increased off-target editing over time", "Protein misfolding", "Slower RNA pairing"], "correct": 1},
            {"q": "Editing plants without adding foreign DNA creates ______ organisms.", "options": ["Transgenic", "Gene-edited (cisgenic)", "Synthetic", "Mutagenic"], "correct": 1},
            {"q": "Which practice helps test safety and ethical assumptions before large-scale deployment?", "options": ["Red-team assessment", "Press release review", "Patent screening", "Peer commentary"], "correct": 0},
            {"q": "To ensure equitable access, international bioethics frameworks should promote ______.", "options": ["Private licensing", "Open access and benefit-sharing agreements", "Patent secrecy", "Corporate exclusivity"], "correct": 1}
        ]
    },
    'semiconductors': {
        'title': 'Semiconductor Supply Chains: Why Shortages Happen and How to Build Resilience',
        'free_recall_prompt': 'Please recall everything you can from the article in 3 minutes. Describe why semiconductor shortages occurred, what structural factors made supply fragile, and how visibility, flexibility, contracts, and cooperation can strengthen resilience.',
        'text': '''Modern life runs on semiconductors. Every car, phone, and medical monitor depends on microchips that manage power and interpret signals. Between 2020 and 2022, the world discovered how invisible these components had become when they suddenly ran out. Automakers halted production lines for want of five-dollar microcontrollers, while game consoles and hospital devices faced months of delay. The shortage was not caused by a single failure but by a synchronized shock. The pandemic drove up demand for laptops and tablets just as Asian factories idled, ports congested, and a fire at a Japanese substrate plant cut off key inputs. When economies reopened, supply was frozen at the wrong points: mature nodes used in vehicles lagged behind while the newest lines for smartphones and servers were fully booked.
Semiconductor production is rigid and expensive. Building a fabrication plant—known as a fab—costs over ten billion dollars and takes years. Even within existing fabs, switching chip designs requires new photomasks, chemicals, and hundreds of validation steps. Automakers, who buy standardized chips in moderate volumes, negotiate annual contracts and avoid pre-paying for capacity. Smartphone firms, by contrast, overbook to guarantee priority and cancel later if demand weakens. When forecasts shifted during the pandemic, foundries favored customers with higher margins and firmer commitments. The chip shortage was thus both physical and contractual—a hierarchy of trust shaped by profitability.
Inside the foundries, production follows a rhythm that resists acceleration. Silicon wafers move through clean rooms for months, passing through lithography, etching, ion implantation, and testing. Each step depends on machines already booked far in advance. Bottlenecks emerge not only in equipment but in the specialized inputs—photoresists, ultra-pure gases, and polishing compounds—produced by a handful of suppliers. A brief power loss at chemical plants in Texas in 2021 delayed semiconductor coatings worldwide, showing how small shocks cascade through interdependent systems. In global supply chains, distance magnifies fragility: a local storm can halt car assembly half a world away.
Geography deepens this vulnerability. East Asia dominates chip fabrication and packaging: Taiwan and South Korea produce most high-end logic and memory chips. The United States and Europe lead in design software and lithography tools, while the Netherlands hosts the world's only supplier of extreme-ultraviolet scanners. Natural disasters, export controls, or geopolitical tensions in any of these regions ripple through the entire network. The industry faces a paradox: efficiency depends on specialization, yet resilience requires diversification. No single country can perform every step efficiently, but concentration in one region invites systemic risk. The answer lies in coordination—duplication of critical suppliers, regional diversity for mature-node fabs, and harmonized standards that let chips qualify across multiple plants.
For decades, manufacturers trusted just-in-time (JIT) logistics to minimize inventory. That worked for consumer goods but failed for semiconductors, which have long cycle times. A missing wafer today cannot be replaced next week; it takes months to produce another. When every firm runs lean simultaneously, the entire system loses flexibility. Companies are now adopting risk-adjusted buffering: stockpiling components whose absence would shut down production lines. The cost appears on the balance sheet, but the alternative—idled factories—is worse. Inventory thus becomes a form of insurance, trading efficiency for security.
Resilience, however, goes beyond stockpiles. It depends on information, flexibility, and aligned incentives. The first step is visibility. Many firms discovered during the crisis that they did not know where their chips originated. A carmaker may source components from a Tier-1 supplier, who buys from a contract manufacturer dependent on a single foundry in Taiwan. Without mapping these upstream tiers, managers cannot anticipate disruptions. Digital "supply twins" now model entire production networks, tracking lead times, yields, and geographic exposure in real time.
Next comes flexibility. Designs that accept functionally equivalent parts—known as second sourcing—allow substitution when one supplier fails. Engineers increasingly build circuit boards that fit multiple compatible microcontrollers, and software abstraction layers that let firmware run across brands. These design strategies reduce dependency without lowering performance.
Contracts are the third lever. For years, chip procurement treated semiconductors as commodities: the lowest bidder won. During shortages, that logic collapses because supply flows to trusted, long-term customers. Some automakers now sign take-or-pay agreements guaranteeing foundries a minimum revenue even if volumes vary. Others pre-pay for capacity, effectively sharing risk. Governments reinforce this through co-investment and tax credits that require open access, ensuring new fabs serve multiple industries instead of one corporate patron.
Communication and data sharing complete the loop. Rolling forecasts and early-warning dashboards let suppliers plan maintenance and adjust production mix before shortages appear. In complex supply chains, information is a public good: the clearer the signal, the smaller the panic when demand shifts. Governments are now funding "semiconductor observatories" that aggregate anonymized order data to provide transparent market indicators. The goal is not central planning but shared visibility—reducing the amplitude of collective overreactions.
The chip shortage also revealed cultural habits of over-optimization. For decades, supply-chain excellence meant cutting every margin: inventory and redundancy were treated as waste. That mindset maximized short-term efficiency but sacrificed resilience. Economists now advocate an efficiency–resilience frontier instead of a single optimum. On one side lies lean precision; on the other, spare capacity that absorbs shocks. Moving along this curve is strategic, not wasteful. Just as investors hedge portfolios against volatility, manufacturers hedge supply networks against disruption.
Resilience also needs patient capital and consistent policy. Building new fabs or materials plants takes a decade, and investors need stable signals. Frequent subsidy cycles or political reversals discourage commitment. Effective industrial policy must align incentives across generations of technology, linking national security with commercial viability. Shared training programs, environmental standards, and open R&D centers sustain momentum beyond election terms.
Technology itself can strengthen resilience. Digital manufacturing platforms already monitor energy use and machine performance. Artificial intelligence can predict yield losses and reroute production before failures occur. Combined with blockchain-based tracking, these tools could certify where and how each chip was made—crucial for both quality assurance and cybersecurity. In the long run, resilience may depend as much on data integrity as on silicon purity. Predictive analytics now even support sustainability goals by optimizing energy use and reducing carbon intensity in wafer production.
Policy coordination across regions is equally important. The U.S. CHIPS Act, Europe's Chips Joint Undertaking, and Asia's national programs all aim to expand domestic manufacturing. Yet without alignment, these efforts risk duplication and subsidy races. A cooperative framework that shares research, harmonizes export controls, and keeps trade channels open would deliver more stability than isolated protectionism. Semiconductor ecosystems thrive on specialization; walling them off undermines the efficiency resilience seeks to protect. The next decade will test whether geopolitics can compete for capacity or cooperate for interdependence.
Ultimately, the semiconductor crisis reminded industries that supply chains are systems, not pipelines. Physics, economics, and politics intertwine. The cycle time of wafers sets physical limits; capital intensity sets economic limits; and the geography of alliances sets political limits. No firm or nation can secure complete autonomy, but collaboration can reduce exposure. The goal is not to eliminate risk—an impossible task—but to absorb shocks gracefully and recover quickly. Companies that combine visibility, modular design, and balanced contracts emerge stronger from disruption.
Resilient supply chains rest on trust built before crisis. When partners share information openly, pay fairly for capacity, and invest jointly in contingency plans, panic turns into coordination. The enduring lesson of the shortage is that stability comes less from stockpiles than from relationships that align incentives and share knowledge. Managing such systems demands patience, transparency, and continuous learning. Semiconductors may be microscopic, yet they reveal a vast truth about interdependence: that the smallest circuits illuminate how global cooperation sustains the modern world.

''',
        'summary_integrated': 'Between 2020 and 2022, a synchronized disruption revealed how deeply modern life depends on semiconductors. The pandemic boosted demand for electronics while factory shutdowns, port delays, and a Japanese plant fire froze production. Automakers halted assembly lines over five-dollar chips. Semiconductor fabrication is slow and costly—each "fab" requires billions of dollars and months to retool. Smartphone firms that pre-booked capacity were prioritized over automakers that negotiated annually, showing how business contracts shape supply allocation as much as technology does.\n\nWafers move through hundreds of precise steps using chemicals and gases from specialized suppliers; a single power loss in Texas in 2021 caused global shortages weeks later. Geographic concentration worsens fragility: Taiwan and South Korea dominate fabrication, while Europe and the U.S. focus on design and lithography. True resilience requires coordination—regional diversity, dual sourcing, and harmonized standards. Some recent pilot projects even tested semi-autonomous chip factories capable of self-adjusting production schedules through AI, though these remain experimental and not yet deployed at scale.\n\nCompanies are rethinking just-in-time models toward risk-adjusted buffering, maintaining stockpiles for critical components. Visibility and flexibility help: digital supplier maps, second sourcing, and adaptive contracts align incentives. Governments can co-fund open-access fabs to avoid overconcentration. In the long term, resilience depends as much on trust and transparency as on technology. The semiconductor crisis taught that stability arises not from isolation, but from cooperation, information sharing, and balanced design between efficiency and redundancy.',
        'summary_segmented': '''The 2020–22 chip shortage exposed the world\'s dependence on semiconductors for cars, phones, and essential devices.
A mix of pandemic-driven demand, factory shutdowns, and logistic failures froze supply at the wrong points.
Fabs are rigid and expensive; retooling takes months and billions of dollars, making rapid adaptation impossible.
High-margin clients like smartphone firms were prioritized over automakers with weaker prepayment contracts.
Single-source materials such as photoresists and gases created global cascades after local disruptions like the 2021 Texas storm.
Taiwan and South Korea lead in fabrication, while Europe and the U.S. specialize in design and lithography tools.
False lure – Some pilot "autonomous fabs" reportedly adjusted wafer output automatically through AI coordination networks.
Companies now build risk-adjusted inventories and design boards that accept multiple component types.
Transparent contracts and shared supplier data improve coordination and investment confidence.
The enduring lesson: resilient supply chains rely on trust, visibility, and diversified collaboration more than on speed alone.''',
        'questions': [
            {"q": "Why did the 2020–22 chip shortage hit multiple industries simultaneously?", "options": ["Single-plant failure", "Interlinked shocks in demand, logistics, and supply", "Excess inventory", "Reduced consumer demand"], "correct": 1},
            {"q": "Why is it difficult for fabs to change product lines quickly?", "options": ["Each chip design needs unique photomasks and re-validation", "Shortage of labor", "Export limits", "Government quotas"], "correct": 0},
            {"q": "Automakers were especially exposed because ______.", "options": ["They relied on outdated nodes and short-term contracts", "They over-produced chips", "They owned too many fabs", "They used rare metals"], "correct": 0},
            {"q": "How does geographic specialization increase fragility?", "options": ["By concentrating key steps in few regions vulnerable to disruption", "By raising prices", "By improving resilience", "By limiting innovation"], "correct": 0},
            {"q": "Why did \"just-in-time\" logistics fail in this industry?", "options": ["Chip production cycles are months long", "Transport costs rose", "Labor turnover increased", "Warehouses were full"], "correct": 0},
            {"q": "Risk-adjusted buffering aims to ______.", "options": ["Keep selective reserves for high-impact parts", "Stock every component equally", "Eliminate storage costs", "Use only local suppliers"], "correct": 0},
            {"q": "Which pilot technology was cited as a sign of smarter factories? (False-memory item)", "options": ["AI-coordinated \"autonomous fabs\" optimizing wafer flow", "Drone-based delivery of wafers", "Quantum-light lithography", "Blockchain payroll systems"], "correct": 0},
            {"q": "Mapping multi-tier suppliers helps companies ______.", "options": ["Spot hidden upstream dependencies before disruption", "Cut wages", "Shorten contracts", "Avoid taxes"], "correct": 0},
            {"q": "Open-access government funding for fabs prevents ______.", "options": ["Monopolization and single-industry control", "International cooperation", "Environmental audits", "Innovation sharing"], "correct": 0},
            {"q": "The main lesson of the crisis was that resilience depends on ______.", "options": ["Trust, transparency, and balanced collaboration", "Rapid expansion alone", "Strict secrecy", "Overproduction"], "correct": 0},
            {"q": "Which Texas event triggered a chemical shortage affecting coatings?", "options": ["Flood", "Winter-storm power loss", "Cyberattack", "Hurricane"], "correct": 1},
            {"q": "\"Second-sourcing\" in circuit design allows ______.", "options": ["Use of alternative compatible components", "Lower energy use", "Remote monitoring", "Higher profits only"], "correct": 0},
            {"q": "The \"efficiency–resilience frontier\" represents ______.", "options": ["A trade-off between lean precision and shock absorption", "Price forecasting model", "Patent boundary", "Energy curve"], "correct": 0},
            {"q": "AI and blockchain strengthen supply chains by ______.", "options": ["Predicting yield losses and verifying origin of production", "Automating marketing", "Replacing labor unions", "Lowering tariffs"], "correct": 0},
            {"q": "What risk comes from uncoordinated national subsidy programs?", "options": ["Duplication and subsidy races", "Shared innovation", "Lower prices", "Faster permits"], "correct": 0}
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

@app.route("/randomize")
@require_pid
def randomize():
    # Ensure we actually have articles to run
    article_keys = list(ARTICLES.keys())
    if len(article_keys) < 3:
        # If you temporarily reduced ARTICLES, handle gracefully
        return render_template("excluded.html"), 500

    random.shuffle(article_keys)
    article_keys = article_keys[:3]  # run 3 articles

    structure = random.choice(["integrated", "segmented"])
    timing_conditions = ["synchronous", "pre_reading", "post_reading"]
    timing_order = random.sample(timing_conditions, 3)

    session["structure_condition"] = structure
    session["timing_order"] = timing_order
    session["article_order"] = article_keys
    session["current_article"] = 0

    log_data(session["participant_id"], "randomization", {
        "structure": structure,
        "timing_order": json.dumps(timing_order),
        "article_order": json.dumps(article_keys),
    })

    # For pre-reading mode, go to AI summary first
    if timing_order[0] == "pre_reading":
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
    recall_total_ms = 10000 if TEST_MODE else (3 * 60 * 1000)
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

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # Load translation cache on startup
    _load_translation_cache()
    
    # Pre-translate static UI text (fast)
    if GoogleTranslator:
        _pre_translate_ui_text()
    
    # Pre-translate ALL articles (takes 30-60 seconds but makes everything instant)
    if GoogleTranslator:
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
