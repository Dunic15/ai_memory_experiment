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
        'text': '''Cities are artificial landscapes that capture sunlight and store heat. Every day, roofs, roads, and facades absorb radiant energy from the sun, turning it into thermal mass that lingers long after sunset. Unlike forests or grasslands, which cool themselves through evapotranspiration, the dense materials of cities—concrete, asphalt, brick, and metal—absorb and slowly release heat, creating a persistent temperature difference between urban and rural zones known as the urban heat island (UHI) effect. Nights can remain three to seven degrees Celsius warmer, affecting sleep quality, increasing electricity demand, and intensifying health risks during heat waves.
The amplification of warmth arises from several physical and spatial features that define the modern metropolis. Surface albedo, the ability of surfaces to reflect sunlight, is a critical factor. Black asphalt reflects as little as five percent of solar energy, while white or reflective concrete can reflect over sixty percent. Thermal mass—the capacity of materials like stone, brick, and concrete to retain heat—slows the cooling process at night. The geometry of urban canyons, created by tall, closely spaced buildings, traps radiation as it bounces between surfaces and limits wind ventilation. Finally, the loss of vegetation removes the natural cooling effect of evapotranspiration. Without trees and grass, nearly all incoming solar energy turns directly into sensible heat, raising air temperature throughout the day and night.
The cumulative outcome of these mechanisms extends beyond physics to social and economic systems. Low-income neighborhoods tend to be most affected: they often have fewer trees, older buildings with poor insulation, and more traffic. During heat waves, such districts experience higher hospitalization and mortality rates. Residents in these areas spend a greater share of income on air-conditioning, while electrical grids face surges in demand. Utilities must activate older, less efficient power plants that emit additional greenhouse gases, reinforcing the cycle of urban warming. What begins as a microclimatic phenomenon becomes an environmental justice issue and an energy challenge combined.
Urban planners and engineers have identified four key principles for cooling cities: reflect, shade, vent, and absorb differently. The first principle, reflection, increases albedo. Cool roofs made of light-colored or reflective materials can lower surface temperatures by up to thirty degrees Celsius at midday, reducing indoor cooling demand by ten to twenty percent. Reflective pavements achieve similar results, though their benefit to pedestrians is smaller due to air mixing near the ground. The second principle, shading, blocks sunlight before it strikes surfaces. Trees, pergolas, and green façades combine optical blocking with evaporative cooling, creating localized zones of comfort. The third, ventilation, reshapes urban layouts to enhance airflow. Open corridors aligned with prevailing winds help flush warm air from dense areas and accelerate nocturnal cooling. Finally, absorbing differently means rethinking how surfaces handle water and heat. Green roofs, fountains, ponds, and permeable pavements store or evaporate heat instead of passing it into the air, moderating temperature fluctuations.
Empirical studies show that combining these strategies produces the greatest impact. In Los Angeles, for example, a city-wide cool-roof mandate reduced roof temperatures by twenty-five degrees but lowered street-level air temperature by only two degrees. When reflective roofs were combined with extensive tree planting, comfort improved dramatically, especially in pedestrian-heavy zones. Trees remain the most effective cooling element because they work where people live, walk, and rest. However, maintaining them requires planning: in dry climates, drought-tolerant species and engineered soils ensure survival without excessive irrigation. Successful programs integrate horticultural science with social policy, prioritizing greenery where it benefits vulnerable communities most.
Equity-sensitive planning is crucial. If financial incentives target only private homeowners, wealthier areas implement solutions first, leaving disadvantaged zones behind. Public initiatives—such as greening schoolyards, shading bus stops, or retrofitting social-housing roofs with cool coatings—help bridge this gap. Because the UHI is a citywide phenomenon, distributed small improvements can produce large-scale cooling when coordinated spatially.
Monitoring and verification are essential to track results. Satellite thermal imagery reveals temperature gradients across cities, while ground sensors mounted on bicycles, buses, or lamp posts measure microclimates block by block. The timing of observations matters: midnight readings capture retained heat more accurately than midday snapshots. Transparent data sharing builds public trust and ensures accountability. A practical guideline suggests dedicating one percent of every project budget to measurement, maintenance, and education. Without consistent follow-up, even the most innovative green roof can lose effectiveness in just a few years.
The co-benefits of UHI mitigation reach far beyond temperature control. A single mature street tree cools the air, filters particulates, sequesters carbon, absorbs noise, and increases nearby property values. Cool roofs can double as platforms for solar panels, combining renewable energy generation with lower thermal loads. Permeable pavements reduce storm-water runoff and flood risk, lowering municipal drainage costs. Framing UHI reduction as a multi-benefit investment enables governments to pool resources from health, energy, and climate-adaptation programs. Life-cycle analyses often show that these measures repay their cost within a decade through reduced energy use and infrastructure savings.
Nevertheless, every strategy has trade-offs. Highly reflective materials can create glare if poorly oriented; dense vegetation increases water demand; and green roofs add structural load and require maintenance. The best outcomes emerge when citizens participate in decision-making, helping identify overheated courtyards, unshaded playgrounds, and potential wind corridors. Public participation improves both efficiency and acceptance, turning thermal management into a shared civic goal.
Preventing future heat islands demands forward-looking regulation. Zoning codes that require reflective roofs, vegetated surfaces, and wind corridors can lock resilience into the urban fabric. It is far cheaper to prevent excessive heat accumulation in new developments than to retrofit existing ones. In this way, heat mitigation merges with broader climate adaptation, protecting cities from rising global temperatures while improving daily comfort.
Cities around the world demonstrate that progress is possible. Tokyo has implemented reflective surfaces and mandatory greening of public facilities, achieving measurable nighttime cooling. Singapore incorporates vertical gardens and sky parks into high-rise architecture, creating layered shade that benefits multiple levels. Paris, after the deadly 2003 heat wave, introduced cool-roof standards and re-vegetated schoolyards as emergency cooling centers. These examples show that urban heat islands are not inevitable by-products of urbanization but reversible outcomes of thoughtful design.
Ultimately, success depends on collaboration among scientists, planners, and citizens. Meteorologists provide data; engineers design technologies; urban designers translate them into spatial form; and residents sustain improvements through collective stewardship. Heat is not only a physical problem but also a social one—its distribution mirrors how cities allocate shade, energy, and opportunity.
If reflection provides the quickest relief, trees the most pleasant, and planning the most lasting, then the next generation of urban spaces will succeed not because they never grow warm but because they know how to breathe, reflect, and regenerate. When cities measure progress transparently, invest where need is greatest, and treat cooling as a shared civic right, even the hottest summers will feel more bearable. The urban heat island will remain not as a symbol of failure but of progress—the moment when humanity learned to design comfort as carefully as it designs density.
''',
        'summary_integrated': 'Urban heat islands (UHIs) occur when cities accumulate and retain more heat than nearby rural zones because of the materials and geometry of the built environment. Dense surfaces such as asphalt, concrete, and metal absorb solar energy by day and release it slowly at night, keeping temperatures three to seven degrees Celsius higher. This warming arises from four key mechanisms: low surface reflectivity (albedo), high thermal mass, reduced airflow in narrow "urban canyons," and the loss of vegetation that would otherwise cool the air through evapotranspiration. Some cities have also experimented with darker pavement coatings to trap heat during winter and stabilize annual temperature averages—though results remain debated. The combined outcome is a persistent heat surplus that disrupts sleep, increases electricity consumption, and worsens health risks, particularly in low-income areas with little greenery or insulation.\n\nTo counter UHIs, planners follow four complementary principles: reflect, shade, vent, and absorb differently. Light-colored roofs and pavements raise albedo; trees and green façades provide shading and evaporative cooling; ventilation corridors enhance airflow; and permeable surfaces or water features channel heat into evaporation instead of the air. The most durable progress comes from blending these tactics and distributing them equitably, prioritizing vulnerable neighborhoods. Monitoring with satellites and ground sensors ensures that temperature gains are verified over time. Beyond cooling, mitigation lowers pollution, cuts flood risk, and improves comfort and energy efficiency. Cities such as Tokyo, Singapore, and Paris demonstrate that with reflective materials, greenery, and long-term design, heat islands can be reversed through collaboration.',
        'summary_segmented': '''1. Cities trap heat through dense materials. Concrete, asphalt, and metal absorb sunlight and release it slowly, keeping urban nights warmer than rural surroundings.
2. Four main mechanisms drive the urban heat island effect: low reflectivity, high thermal mass, narrow "street canyons," and loss of vegetation that removes cooling through evapotranspiration.
3. Consequences go beyond temperature: higher night heat impairs sleep, raises electricity demand, and increases health risks, especially in low-income districts.
4. Urban heat is also a social inequality issue, as poorer areas have fewer trees and spend more income on cooling.
5. Mitigation follows four linked strategies: reflect, shade, vent, and absorb differently—each targeting a distinct cause of trapped heat.
6. Reflective materials such as cool roofs and bright pavements can lower roof surface temperature by up to 30 °C.
7. Some cities tested dark pavements to store winter heat and reduce annual energy swings, though evidence is mixed.
8. Shade and vegetation intercept sunlight and cool the air through evapotranspiration; trees are most effective but need maintenance and fair placement.
9. Ventilation corridors aligned with prevailing winds help flush warm air and accelerate nighttime cooling.
10. Absorbing differently via permeable materials, fountains, and green roofs channels energy into evaporation instead of the air, showing that smart, equitable planning can transform heat islands into resilient urban systems.''',
        'questions': [
            {"q": "Which factor mainly causes dark urban materials to store more heat than rural surfaces?", "options": ["High albedo", "Low albedo", "High permeability", "Reflective coating"], "correct": 1},
            {"q": "Why does concrete keep cities warm long after sunset?", "options": ["It absorbs moisture", "It releases stored heat slowly", "It reflects long-wave radiation", "It evaporates easily"], "correct": 1},
            {"q": "Street canyons intensify urban heat because they ________.", "options": ["Increase wind turbulence", "Trap radiation and reduce airflow", "Absorb less solar energy", "Encourage shade formation"], "correct": 1},
            {"q": "Vegetation cools the environment primarily through ________.", "options": ["Reflection", "Evapotranspiration", "Soil insulation", "Root absorption"], "correct": 1},
            {"q": "The typical cooling effect of reflective \"cool roofs\" is about ________.", "options": ["5–10 °C", "20–30 °C", "35–40 °C", ">40 °C"], "correct": 1},
            {"q": "Using reflective materials can reduce indoor cooling needs by roughly ________.", "options": ["5–10 %", "10–20 %", "25–35 %", "40–50 %"], "correct": 1},
            {"q": "The \"absorb differently\" strategy refers to using materials that ________.", "options": ["Block light completely", "Channel heat into evaporation and ground layers", "Prevent rain infiltration", "Increase surface reflectivity"], "correct": 1},
            {"q": "Why is combining multiple UHI strategies more effective than using one alone?", "options": ["It reduces maintenance cost", "It amplifies cumulative cooling effects and equity outcomes", "It simplifies urban design", "It avoids tree planting costs"], "correct": 1},
            {"q": "Equity-oriented cooling programs should prioritize ________.", "options": ["Commercial zones", "High-income neighborhoods", "Tree-poor, low-income districts", "Downtown business cores"], "correct": 2},
            {"q": "Why have some cities experimented with darker pavement coatings?", "options": ["To trap heat in winter and stabilize temperature cycles", "To reflect more sunlight during summer", "To increase surface permeability and drainage", "To reduce glare on roads"], "correct": 0},
            {"q": "Urban nighttime air can remain roughly ________ warmer than rural surroundings.", "options": ["1–2 °C", "3–7 °C", "8–10 °C", "10–12 °C"], "correct": 1},
            {"q": "Under heat stress, city power grids often rely on ________.", "options": ["Solar farms", "Older fossil-fuel power plants", "Battery storage", "Offshore wind energy"], "correct": 1},
            {"q": "A recommended budgeting rule assigns one cent per dollar to ________.", "options": ["Advertising", "Monitoring, maintenance, and public education", "Street lighting", "Tree pruning"], "correct": 1},
            {"q": "Cities like Tokyo, Singapore, and Paris mitigated UHI mainly by ________.", "options": ["Building taller towers", "Cool roofs, greenery, and ventilation corridors", "Relocating residents", "Expanding concrete surfaces"], "correct": 1},
            {"q": "Long-term UHI reduction depends most on ________.", "options": ["Short-term campaigns", "Mandatory urban planning codes and design standards", "Voluntary donations", "Temporary shading events"], "correct": 1}
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
        'summary_segmented': '''1. CRISPR began as a bacterial immune system that records viral DNA fragments to recognize future invaders.
2. Scientists reprogrammed this system using synthetic guide RNA to direct Cas enzymes to precise genome locations.
3. The process "guide, cut, and repair" made gene editing faster, cheaper, and globally accessible.
4. Precision challenges persist because partial guide mismatches can create off-target edits.
5. Enhanced Cas variants and base/prime editors increase fidelity while minimizing double-strand breaks.
6. Some laboratories reported CRISPR-created bioluminescent crops for easier detection of edited plants.
7. Delivery remains the major barrier: viral vectors are efficient but small; lipid nanoparticles carry more but risk inflammation.
8. Self-limiting and inducible CRISPR systems control activity duration, improving safety.
9. Germ-line editing is ethically restricted because changes are heritable and affect future generations.
10. CRISPR now extends to agriculture, ecology, and health governance, requiring transparency, inclusion, and equitable access.''',
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
        'summary_segmented': '''1. The 2020–22 chip shortage exposed the world\'s dependence on semiconductors for cars, phones, and essential devices.
2. A mix of pandemic-driven demand, factory shutdowns, and logistic failures froze supply at the wrong points.
3. Fabs are rigid and expensive; retooling takes months and billions of dollars, making rapid adaptation impossible.
4. High-margin clients like smartphone firms were prioritized over automakers with weaker prepayment contracts.
5. Single-source materials such as photoresists and gases created global cascades after local disruptions like the 2021 Texas storm.
6. Taiwan and South Korea lead in fabrication, while Europe and the U.S. specialize in design and lithography tools.
7. Some pilot "autonomous fabs" reportedly adjusted wafer output automatically through AI coordination networks.
8. Companies now build risk-adjusted inventories and design boards that accept multiple component types.
9. Transparent contracts and shared supplier data improve coordination and investment confidence.
10. The enduring lesson: resilient supply chains rely on trust, visibility, and diversified collaboration more than on speed alone.''',
        'questions': [
            {"q": "What caused the global semiconductor shortage between 2020 and 2022?", "options": ["Single factory failure", "Synchronized shocks: pandemic demand, shutdowns, port congestion, and a Japanese substrate fire", "Currency devaluation", "Labor strikes"], "correct": 1},
            {"q": "Why is semiconductor manufacturing slow to adjust to demand changes?", "options": ["Chips are easy to produce", "Fabs are capital-intensive, require years to build, and switching designs needs new photomasks and months of validation", "Workers are unskilled", "Materials are abundant"], "correct": 1},
            {"q": "During the shortage, foundries prioritized which type of customers?", "options": ["Lowest-margin orders", "Clients with higher margins and firmer commitments", "Random allocation", "Only automakers"], "correct": 1},
            {"q": "What is \"risk-adjusted buffering\" in semiconductor supply chains?", "options": ["Zero inventory", "Maintaining stockpiles for critical parts with long lead times", "Daily reordering", "Only finished goods"], "correct": 1},
            {"q": "Which region dominates advanced chip fabrication and packaging?", "options": ["South America", "East Asia (Taiwan and South Korea)", "Africa", "Australia"], "correct": 1},
            {"q": "What does \"second sourcing\" refer to in chip design?", "options": ["Using only one supplier", "Designing boards to accept functionally equivalent components from multiple vendors", "Eliminating controllers", "Proprietary pinouts"], "correct": 1},
            {"q": "Which contract type helps align incentives between customers and foundries?", "options": ["Pay on delivery only", "Take-or-pay or pre-payment agreements", "No-penalty cancellation", "Verbal agreements"], "correct": 1},
            {"q": "What is the main goal of resilience strategies in supply chains?", "options": ["Eliminate all risk", "Absorb shocks gracefully and recover quickly", "Cut costs only", "Centralize all production"], "correct": 1},
            {"q": "How do \"digital supply twins\" help improve resilience?", "options": ["They eliminate the need for suppliers", "They model production networks and track lead times, yields, and geographic exposure in real time", "They reduce chip costs", "They automate ordering"], "correct": 1},
            {"q": "What emerging innovation was described as a sign of the industry's maturity?", "options": ["Fully autonomous chip factories that self-adjust wafer output", "Widespread recycling of silicon wafers", "Decentralized blockchain contracts for supply forecasting", "Integration of solar-powered clean rooms"], "correct": 0},
            {"q": "Which incident in 2021 demonstrated how small disruptions cascade globally?", "options": ["A drought in California", "A brief power loss at Texas chemical plants that delayed semiconductor coatings worldwide", "A strike in Germany", "A flood in Japan"], "correct": 1},
            {"q": "What role do governments play in building semiconductor resilience?", "options": ["Complete control of production", "Co-investment, open-access subsidies, and shared data observatories", "Export bans only", "Single-industry support"], "correct": 1},
            {"q": "Why is geographic concentration in chip production a vulnerability?", "options": ["It reduces costs", "Natural disasters, export controls, or tensions in concentrated regions ripple through the entire global network", "It improves quality", "It speeds delivery"], "correct": 1},
            {"q": "What is the typical production cycle time for semiconductor wafers?", "options": ["Hours", "Days", "Weeks", "Months (two to three months through clean rooms)"], "correct": 3},
            {"q": "What is the key principle that resilient supply chains rely on?", "options": ["Stockpiles alone", "Trust built before crisis through transparent data, fair payment, and joint contingency planning", "Secrecy", "Single-vendor relationships"], "correct": 1}
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
    
    # Log MCQ responses
    if mcq_data:
        log_data(session["participant_id"], "mcq_responses", {
            "article_num": article_num,
            "article_key": data.get("article_key"),
            "timing": data.get("timing"),
            "mcq_answers": json.dumps(mcq_data)
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
