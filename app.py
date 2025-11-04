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
        'text': '''Cities are artificial landscapes that capture sunlight and store heat. Every day, roofs, roads, and facades absorb radiant energy from the sun, converting it into thermal mass that lingers long after sunset. Unlike forests or grasslands, which reflect part of the incoming radiation and cool themselves through evapotranspiration, the dense materials of cities—concrete, asphalt, brick, and metal—accumulate heat during daylight and release it slowly through the night. This process generates a persistent temperature difference between urban and rural zones known as the urban heat island effect (UHI). The phenomenon is not limited to hot afternoons: it reshapes the entire twenty-four-hour temperature cycle, raising minimum nighttime values and extending periods of discomfort for residents. In many cities, nights can remain three to seven degrees Celsius warmer than surrounding countryside, altering sleep quality, increasing electricity demand, and intensifying health risks during heat waves.
The reasons behind this amplification of warmth are rooted in a combination of physical, material, and spatial properties that define the modern metropolis. One of the key parameters is surface albedo, the fraction of sunlight reflected rather than absorbed. A new layer of black asphalt may reflect barely five percent of solar energy, while a white concrete roof can reflect more than sixty percent. Low-albedo materials trap short-wave radiation and convert it into long-wave heat energy that continues to radiate upward long after sunset. A second factor is thermal mass, or the ability of a substance to store heat. Materials such as stone, masonry, and concrete possess high thermal capacity, meaning they warm slowly but also retain warmth for many hours. Even when the air cools in the evening, these materials act as heat reservoirs that release their stored energy back into the ambient air, delaying nighttime cooling.
A third factor is the geometry of the urban canyon—the shape and spacing of buildings along the street. Tall, closely spaced structures create narrow corridors where radiation emitted from one surface strikes another and is reabsorbed instead of escaping into the atmosphere. Wind speed declines within these canyons, limiting the natural ventilation that could otherwise disperse accumulated heat. The final and perhaps most visible component is the absence of vegetation. Plants function as natural air conditioners: through evapotranspiration they convert liquid water into vapor, consuming latent heat from their surroundings. When trees and grass disappear, nearly all incoming solar energy is transformed into sensible heat that raises air temperature directly.
The cumulative outcome of these four mechanisms is a stable and measurable rise in urban temperature, which in turn interacts with social and economic systems. Low-income neighborhoods tend to be the most affected because they often contain fewer trees, more traffic, and older buildings with thin insulation. During heat waves, such districts experience higher hospitalization and mortality rates. The economic consequences extend beyond health: households in these areas spend a greater share of income on air-conditioning, and the electricity grid faces strong late-afternoon peaks. Utilities must respond by activating older, less efficient power plants that emit additional greenhouse gases, reinforcing the cycle of warming. What begins as a microclimatic effect thus cascades into an environmental-justice problem and a broader energy challenge.
Urban planners and engineers have developed multiple strategies to mitigate heat islands, organized into four complementary principles: reflect, shade, vent, and absorb differently. The first principle, reflection, focuses on increasing albedo. Cool roofs coated with light-colored or reflective materials can immediately reduce surface temperature by twenty to thirty degrees Celsius at noon, lowering indoor cooling loads by ten to twenty percent depending on insulation. High-albedo pavements achieve similar effects on roads and parking lots, though their benefit to pedestrians is smaller because turbulent air mixing disperses the cool layer. The second principle, shading, relies on biological and architectural elements that intercept solar radiation before it reaches surfaces. Street trees, pergolas, and green façades create localized zones of comfort by combining optical blocking with evaporative cooling.
The third principle, ventilation, modifies the physical layout of the city to enhance airflow. Urban designs that preserve open corridors aligned with prevailing winds help flush warm air from dense zones. Even modest increases in wind speed can accelerate nocturnal cooling. Finally, the principle of absorbing differently emphasizes the role of water and permeable materials. Fountains, ponds, green roofs, and porous pavements use phase change and subsurface storage to redirect heat into evaporation and ground layers instead of heating the air directly. Each strategy differs in cost, timescale, and maintenance needs: reflective coatings can be applied quickly to existing roofs; trees require years of growth and careful irrigation; ventilation depends on long-term planning rules and building orientation.
Empirical studies show that combining these interventions yields the greatest benefit. In Los Angeles, a city-wide cool-roof mandate reduced average roof temperatures by twenty-five degrees, but the air at street level dropped only two degrees because of mixing. When reflective surfaces were paired with extensive tree planting, pedestrian comfort improved dramatically. Trees provide the strongest relief precisely because they act where people live and move. However, they demand resources: in arid climates, without drought-tolerant species and engineered soils, survival rates decline. Successful programs integrate horticultural science with social equity—allocating greenery not only where it survives easily but where it is most needed.
Equity-sensitive planning is therefore central to UHI mitigation. If financial incentives target only private homeowners, wealthy neighborhoods adopt reflective materials and rooftop gardens first, leaving disadvantaged zones behind. Public initiatives can correct this imbalance by greening schoolyards, shading bus stops, or retrofitting social-housing roofs with cool coatings. Research consistently shows that the largest temperature reductions occur where the baseline was worst: treeless blocks, dark roofs, and uninsulated attics. Because UHI is a systemic property rather than a local one, distributed small improvements produce measurable regional effects when coordinated spatially.
Accurate monitoring and verification are essential to evaluate progress. Satellite thermal imagery maps large-scale temperature gradients, while ground sensors mounted on bicycles or buses capture block-by-block variation. The timing of data collection matters: midnight readings reveal stored heat more reliably than midday snapshots. Transparent data sharing builds trust and ensures that interventions produce tangible outcomes rather than symbolic gestures. A simple but powerful budgeting rule recommends dedicating one cent of every project dollar to measurement, maintenance, and public education. Without such follow-up, even the most photogenic green roof can become ineffective within a few years.
The advantages of UHI mitigation extend far beyond temperature control. Co-benefits multiply across environmental and economic domains. A single street tree simultaneously cools air, filters particulates, sequesters carbon, muffles traffic noise, and increases nearby property values. Cool roofs can double as platforms for photovoltaic panels, combining energy generation with lower thermal load. Permeable pavements reduce storm-water runoff and mitigate flood risk, saving municipal drainage costs. By framing UHI policies as integrated co-benefit portfolios, city governments can attract funds from multiple departments—public health, energy efficiency, transportation, and climate adaptation—rather than treating heat reduction as a narrow environmental expense. Life-cycle analyses often reveal that these interventions pay for themselves within a decade through reduced energy use and infrastructure savings.
Nevertheless, no strategy is without limitations. Highly reflective materials can cause glare that irritates pedestrians or drivers if improperly oriented. Dense vegetation consumes water, potentially conflicting with drought management. Green roofs increase structural load and require maintenance to avoid becoming dry biomass. The challenge lies in matching solutions to local microclimates and involving citizens in decision-making. Participatory design not only enhances acceptance but also improves placement efficiency: residents know which playgrounds lack shade, which courtyards trap heat, and where new breezeways could reconnect the urban airflow. Thus, thermal physics becomes intertwined with civic collaboration.
Addressing urban heat also means anticipating the future of city growth. Many municipalities continue to expand with materials and patterns that perpetuate heat retention. The most durable victories come from regulation: zoning codes that require reflective roofing materials, incentives for vegetated surfaces, and design guidelines ensuring that new developments do not block natural ventilation corridors. Preventing the next heat island is cheaper than cooling an existing one. In this sense, UHI mitigation aligns with climate-adaptation planning, reducing vulnerability to rising global temperatures while improving everyday comfort.
Cities that pursue integrated strategies—combining reflection, shading, ventilation, and water management—demonstrate that progress is achievable even in warming climates. Tokyo, for example, has implemented widespread reflective surfaces and mandatory greening of public facilities, observing measurable nighttime temperature reductions. Singapore integrates vertical greenery and sky gardens into high-rise architecture, creating layered shade that cools multiple levels simultaneously. In Europe, Paris's post-2003 heat-wave reforms have led to cool-roof standards and the re-vegetation of schoolyards as emergency shelters during extreme events. These examples show that urban heat islands are not inevitable by-products of modernization but reversible artifacts of design.
Ultimately, the success of any program depends on coordination among scientists, planners, and citizens. Meteorologists supply data; engineers develop materials; urban designers translate findings into street-level interventions; and residents ensure maintenance through collective stewardship. Heat is a physical problem but also a social one: its causes are embedded in how cities distribute shade, energy, and opportunity. Managing it requires both thermodynamics and justice.
If reflection provides the quickest relief and trees offer the most pleasant, then planning delivers the permanence. The next generation of urban spaces will succeed not because they never grow warm but because they know how to breathe, reflect, and regenerate. When cities measure honestly, invest where need is greatest, and treat cooling as a shared civic right rather than a luxury, even the hottest summers will feel more bearable. The urban heat island will remain as a reminder not of failure but of progress—the moment when humanity learned to design comfort as carefully as it designs density.
''',
        'summary_integrated': 'Urban heat islands emerge when low-albedo materials, dense urban geometry, and minimal vegetation cause cities to store solar energy and release it slowly overnight. Dark roofs and pavements absorb radiation, while concrete and masonry retain heat that lingers after sunset. Narrow "street canyons" trap long-wave emissions and restrict ventilation, and the loss of trees removes evapotranspiration that would otherwise cool the air. As a result, urban nights remain several degrees warmer, increasing electricity demand, health risks, and inequality. Low-income districts, typically with fewer trees and older housing, face the heaviest burden. Mitigation combines four principles — reflect, shade, vent, and absorb differently — through cool roofs, tree planting, permeable surfaces, and urban breezeways. Equity-focused programs target treeless and disadvantaged zones, while transparent measurement at midnight verifies progress. Beyond temperature relief, these measures yield co-benefits: cleaner air, flood control, energy savings, and higher property value. Yet limitations persist — glare, water use, maintenance, and cost. Lasting success depends on coordinated planning that prevents new heat islands through building codes and community participation. Cities that integrate reflection, shade, airflow, and water management can remain livable even as global temperatures rise. Heat islands, once symptoms of poor design, can become examples of sustainable urban renewal.',
        'summary_segmented': '''- Dark roofs & asphalt absorb sunlight, while concrete stores heat and releases it overnight.
- Street canyons trap long-wave radiation and limit cooling winds.
- Loss of vegetation eliminates evapotranspiration that naturally cools air.
- Urban nights stay 3—7 °C warmer, raising electricity demand and health risks.
- Low-income neighborhoods suffer more from heat and energy burden.
- Mitigation principles: reflect (surfaces), shade (trees), vent (breezeways), absorb differently (water, permeable pavement).
- Cool roofs cut rooftop temperatures 20—30 °C and lower indoor cooling 10—20 %.
- Equity-based programs prioritize public buildings and tree-poor districts.''',
        'questions': [
            {"q": "Which physical property explains why black asphalt heats quickly?", "options": ["High albedo", "Low albedo", "Low conductivity", "Moisture content"], "correct": 1},
            {"q": "Thermal mass in concrete causes what effect after sunset?", "options": ["Immediate cooling", "Stored heat release", "Increased albedo", "Evaporation loss"], "correct": 1},
            {"q": "Street canyons mainly intensify heat by ________.", "options": ["Encouraging breeze", "Trapping radiation and blocking wind", "Raising albedo", "Increasing evaporation"], "correct": 1},
            {"q": "Vegetation lowers temperature through ________.", "options": ["Reflection", "Evapotranspiration", "Shading only", "Condensation"], "correct": 1},
            {"q": "Typical rooftop temperature drop from cool roofs is about ________.", "options": ["5—10 °C", "20—30 °C", "35—45 °C", "None"], "correct": 1},
            {"q": "Energy savings from cool roofs are roughly ________ of indoor cooling loads.", "options": ["1—5 %", "5—10 %", "10—20 %", "30—40 %"], "correct": 2},
            {"q": "Equity-oriented programs should focus on ________.", "options": ["High-income areas", "Tree-dense districts", "Treeless low-income zones", "Commercial centers"], "correct": 2},
            {"q": "Why are midnight temperatures useful for UHI measurement?", "options": ["Show stored heat", "Measure solar input", "Avoid errors", "Track humidity"], "correct": 0},
            {"q": "A co-benefit of urban trees is ________.", "options": ["More glare", "Particulate filtering and storm-water reduction", "Higher heat storage", "Traffic delays"], "correct": 1},
            {"q": "Glare risk is associated with ________ surfaces.", "options": ["Highly reflective", "Porous", "Vegetated", "Rough stone"], "correct": 0},
            {"q": "At night, urban temperatures can remain about ________ warmer than rural areas.", "options": ["1—2 °C", "3—7 °C", "8—10 °C", "> 10 °C"], "correct": 1},
            {"q": "Energy grids under heat stress often activate ________.", "options": ["Hydroelectric plants", "Older fossil generators", "Solar farms", "Wind turbines"], "correct": 1},
            {"q": "Recommended budget rule for UHI projects allocates one cent per dollar to ________.", "options": ["Public relations", "Measurement and education", "Marketing", "Lighting"], "correct": 1},
            {"q": "Highly dense cities like Tokyo and Paris mitigated UHI mainly by ________.", "options": ["Population reduction", "Cool roofs and green public spaces", "Closing roads", "Using taller buildings"], "correct": 1},
            {"q": "Lasting UHI reduction requires ________ beyond retrofits.", "options": ["Mandatory planning codes", "Single campaigns", "Volunteer programs", "Tree donations only"], "correct": 0}
        ]
    },
    'crispr': {
        'title': 'CRISPR Gene Editing: Promise, Constraints, and Responsible Use',
        'free_recall_prompt': 'Please recall everything you can from the article in 3 minutes, describing how CRISPR works, its medical and agricultural applications, key limitations, and ethical or governance challenges.',
        'text': '''CRISPR—Cas systems began as a microbial defense mechanism—a molecular immune memory that bacteria use to recognize and destroy invading viruses. Each infection leaves a short fragment of viral DNA inserted into the bacterial genome, serving as a permanent record of attack. When the same virus returns, the bacteria transcribe these fragments into RNA guides that lead Cas enzymes to the matching sequence, cutting it apart. This elegant process of recognition and cleavage inspired scientists to reprogram it for their own purposes. By designing a synthetic guide RNA that matches any chosen DNA region, researchers can direct the Cas enzyme to that exact spot, slice the double helix, and let the cell's repair machinery rewrite it. This simple principle—guide, cut, and repair—has turned a bacterial survival trick into one of the most versatile tools in modern science.
The method's accessibility has been revolutionary. What once required months of effort with older tools such as zinc-finger nucleases or TALENs can now be done in days, using inexpensive reagents that fit in any basic lab. The democratization of gene editing has allowed teams across the world to explore genetic diseases, agricultural improvement, and environmental restoration at unprecedented speed. Yet this same simplicity conceals layers of complexity. The word precision suggests perfection, but in genomics, precision is statistical. When the guide RNA pairs exactly with its target, Cas cuts accurately, but genomes are enormous and filled with repetitive sequences. Slight mismatches can cause unintended cuts at similar sites, producing off-target edits that may disrupt other genes.
To minimize these risks, researchers adjust guide length and chemistry, develop predictive algorithms, and design enzymes with improved fidelity. Variants such as SpCas9-HF1 or eSpCas9 change amino acids around the DNA-binding surface to reduce promiscuous interactions. Newer editors, including base editors and prime editors, go further by avoiding full double-strand breaks altogether: they replace single letters or copy short sequences using cellular repair without cleaving both strands. These advances reduce collateral effects and extend the range of treatable mutations, marking a shift from blunt editing to fine molecular tuning.
Despite these refinements, delivery remains the hardest step. The editing machinery must enter the correct cells, reach the nucleus, and operate without provoking immune rejection. Viral vectors such as adeno-associated viruses (AAVs) are efficient but small; they carry limited genetic cargo and often trigger antibodies that prevent repeated dosing. Lipid nanoparticles can transport larger molecules and are already used in mRNA vaccines, yet they tend to concentrate in the liver and can cause inflammation at high doses. Researchers are testing polymer-based carriers, extracellular vesicles, and targeted peptides that home to specific tissues, as well as non-biological methods like electroporation or ultrasound-mediated delivery. Each approach balances efficiency, safety, and manufacturing cost. Effective delivery also depends on the temporal control of editing. 
Even when CRISPR components reach the right cells, how long they remain active determines both success and risk. Persistent Cas expression can increase off-target cutting, whereas too brief exposure may yield incomplete edits. Researchers are now designing "self-limiting" systems where messenger RNA or protein degrades within hours, achieving a precise editing pulse followed by automatic shutdown. Others explore inducible switches that activate only under specific chemical or thermal cues. These dynamic strategies transform CRISPR from a static scalpel into a controllable process, allowing clinicians to fine-tune intensity and duration in real time. Timing, not just targeting, becomes part of precision—linking molecular biology to systems engineering and marking the next frontier of safe therapeutic design.In many cases, solving delivery determines whether a therapy succeeds more than perfecting the editor itself.
When CRISPR leaves the lab and enters clinical use, the criteria of success change. In the research stage, the goal is to confirm that an edit occurred; in medicine, the question becomes whether the edit improves the patient's life with acceptable risk. In blood disorders such as sickle-cell anemia and beta-thalassemia, ex vivo strategies are leading the way. Doctors harvest hematopoietic stem cells, edit them under controlled conditions, verify accuracy, and reinfuse them into the patient. This allows comprehensive testing before the cells return to the body. For other organs—heart, brain, or lungs—in vivo delivery is necessary. There, precision must coexist with safety, because off-target effects or immune responses could harm vital tissue. Every edited cell carries its modification for life, so long-term monitoring becomes an ethical and scientific necessity.
The most controversial frontier is germ-line editing, where embryos or reproductive cells are altered so that the change passes to future generations. In theory, this could eradicate hereditary diseases forever, but the ethical implications are profound. A single mistake in an embryo can propagate indefinitely through descendants who never consented to the intervention. Following the 2018 birth of gene-edited babies in China, global outrage led to stronger international agreements banning clinical germ-line editing while allowing tightly regulated research. Most experts argue that humanity is not ready for heritable interventions until long-term safety data and robust oversight exist. Germ-line editing remains a symbol of both hope and hubris—the temptation to perfect life before fully understanding its complexity.
Beyond medicine, CRISPR is transforming agriculture and environmental management. Editing crop genomes to resist blight, tolerate drought, or use fertilizer more efficiently can reduce pesticide dependence and increase yields in changing climates. Scientists are developing "gene drives" that push specific traits through pest populations to control malaria mosquitoes or invasive rodents, though these systems risk unintended ecological cascades. To regulate such technologies, authorities distinguish between gene-edited organisms, which carry small natural-like changes, and transgenic organisms that incorporate foreign DNA. The difference influences labeling, trade, and public perception. Transparency is key: people tend to support edits that bring visible benefits—reduced chemical use, improved nutrition, or lower costs—rather than changes that appear to serve only large corporations. Equitable access to improved seeds and technologies will determine whether CRISPR becomes a tool for sustainability or another driver of inequality.
Ethically, the technology forces society to reconsider old dilemmas with sharper instruments. Who defines what counts as therapy versus enhancement? Should we use editing to correct blindness but not to increase intelligence? How do we ensure fairness when some can afford genetic interventions and others cannot? Governance that works is inclusive and continuous. Rather than alternating between prohibition and hype, responsible oversight builds institutions that combine transparency, accountability, and diversity of voices. Ethics committees must include patients, educators, and citizens alongside scientists. Continuous monitoring—through public registries of trials, independent audits, and "red-team" assessments that actively search for hidden risks—turns ethics from a veto into a feedback mechanism.
Scientific progress, meanwhile, continues to accelerate. New Cas proteins such as Cas12, Cas13, and CasΦ expand the toolbox; AI-based guide design reduces errors; and CRISPR-based diagnostics like SHERLOCK and DETECTR allow rapid detection of pathogens, proving that editing enzymes can serve in testing as well as therapy. Hybrid systems now link CRISPR with epigenetic switches to regulate genes without cutting DNA at all. The technology is evolving from editing to modulation—a set of instruments to dial biological activity up or down rather than rewrite it completely.
Transparency has become the currency of credibility. Early announcements often relied on press releases, but today journals and regulators demand full data on accuracy, durability, and immune response. Open repositories track ongoing trials, and funding agencies encourage pre-registration to avoid selective reporting. The scientific community has learned that maintaining public trust requires the same rigor in communication as in experimentation.
As CRISPR matures, attention shifts to integration within health systems. Hospitals must develop cleanroom facilities for cell therapy, insurers must rethink payment models for one-time genetic cures, and universities must train clinicians fluent in both genetics and ethics. In low-income countries, the priority is different: building local capacity, training technicians, and sharing open-source protocols so that benefits do not cluster only in wealthy nations. Partnerships between academic institutions and global organizations can create regional hubs for reagent production and quality control.
Biosecurity adds yet another layer. Because CRISPR components are cheap and widely available, safety norms and education become essential. The same ease that empowers legitimate science could enable misuse. Establishing shared standards for sequence screening, safe laboratory practices, and international reporting helps ensure that openness and security grow together. Just as cybersecurity evolved alongside the internet, biotechnology must develop its own culture of responsibility.
Ultimately, CRISPR is not merely a technical invention but a mirror of collective values. It reveals how societies balance innovation with caution, competition with solidarity, and individual ambition with public good. When data are shared transparently, benefits distributed equitably, and oversight continuous, gene editing can transform from a disruptive novelty into a stable element of medicine, agriculture, and conservation. The true measure of its success will not be the number of genomes edited, but the fairness and foresight with which those edits are made. CRISPR's legacy will be written not only in DNA sequences but in the choices humanity makes about whose future is worth rewriting
''',
        'summary_integrated': 'CRISPR—Cas technology re-purposes a bacterial immune system into a programmable gene-editing tool. A guide RNA directs the Cas enzyme to a chosen DNA sequence, where cellular repair can delete, insert, or correct genetic material. Its appeal lies in speed and low cost, yet precision is layered: off-target edits may arise when similar genomic regions are cut unintentionally. Researchers now refine guide design, engineer high-fidelity enzymes, and employ base or prime editors that swap letters without double-strand breaks. Delivery remains the toughest barrier—viral vectors, lipid nanoparticles, and new biodegradable carriers must reach the right tissues without provoking immunity. In medicine, ex vivo editing corrects blood-cell disorders under laboratory control, while in vivo applications for organs such as brain or heart demand higher safety. Germ-line editing of embryos remains largely prohibited because risks transmit to future generations. Agriculture uses CRISPR to strengthen crops and reduce pesticide use, requiring transparent regulation and public trust. Ethical oversight must balance innovation with equity through inclusive review boards, data openness, and long-term monitoring. Emerging editors, self-limiting delivery systems, and global governance frameworks will shape the next decade. CRISPR\'s success will be judged less by technical speed than by fairness, safety, and the integrity with which societies choose what to edit.',
        'summary_segmented': '''- CRISPR—Cas re-purposes bacterial immunity to cut and repair specific DNA sequences.
- Guide RNA directs Cas to target genes for editing or correction.
- Off-target effects occur when similar sites are cut unintentionally.
- High-fidelity, base, and prime editors reduce unwanted mutations.
- Delivery via viruses, nanoparticles, or polymers is the main technical bottleneck.
- Ex vivo editing suits blood disorders; in vivo aims at organs like heart or brain.
- Germ-line embryo editing is banned in most nations due to heritable risk.
- Agricultural uses enhance resilience but need transparent, equitable regulation.
- Ethical governance requires inclusive oversight, data sharing, and global cooperation.
- Future success depends on fairness, safety, and responsible societal choice.
''',
        'questions': [
            {"q": "What biological system inspired CRISPR gene editing?", "options": ["Plant defense", "Bacterial immune memory", "Human RNA", "Yeast replication"], "correct": 1},
            {"q": "What guides the Cas enzyme to its DNA target?", "options": ["Protein code", "Guide RNA sequence", "mRNA transcript", "Antibody"], "correct": 1},
            {"q": "Off-target edits refer to ______.", "options": ["Failed delivery", "Cuts at similar non-intended sites", "Incomplete repair", "RNA degradation"], "correct": 1},
            {"q": "Base and prime editors primarily ______.", "options": ["Insert foreign genes", "Avoid double-strand breaks", "Increase mutation rate", "Delete large regions"], "correct": 1},
            {"q": "Which step is the main technical bottleneck for CRISPR therapy?", "options": ["Gene design", "Delivery to target cells", "Cost of enzymes", "Temperature control"], "correct": 1},
            {"q": "Ex vivo editing means ______.", "options": ["Editing inside the body", "Editing cells outside then reinserting them", "Plant editing", "RNA therapy"], "correct": 1},
            {"q": "Why is germ-line editing controversial?", "options": ["Low cost", "Heritable risk to future generations", "Complex protocols", "Short lifespan of cells"], "correct": 1},
            {"q": "Agricultural applications mainly aim to ______.", "options": ["Increase pesticide use", "Reduce chemical inputs and boost resilience", "Clone livestock", "Alter taste only"], "correct": 1},
            {"q": "Responsible governance should include ______.", "options": ["Only scientists", "Inclusive multistakeholder boards and public registries", "Private funders only", "Military control"], "correct": 1},
            {"q": "Future success of CRISPR will depend on ______.", "options": ["Editing speed", "Fairness and safety of outcomes", "Number of papers", "Patent count"], "correct": 1},
            {"q": "Which vector can carry larger payloads but accumulates in the liver?", "options": ["AAV virus", "Lipid nanoparticles", "Polymer micelles", "Bacterial plasmid"], "correct": 1},
            {"q": "What risk can persistent Cas expression create?", "options": ["Reduced efficiency", "More off-target cuts over time", "RNA instability", "Loss of fidelity data"], "correct": 1},
            {"q": "What term describes editing plants without foreign DNA insertion?", "options": ["Transgenic", "Cisgenic or gene-edited", "Mutagenic", "Synthetic"], "correct": 1},
            {"q": "Which practice tests ethical and safety assumptions before large deployment?", "options": ["Red-team exercise", "Peer review only", "Press release review", "Patent screening"], "correct": 0},
            {"q": "To prevent \"genomic monopolies,\" global frameworks should ensure ______.", "options": ["Open licensing and benefit-sharing", "Private ownership", "Patent secrecy", "National exclusivity"], "correct": 0}
        ]
    },
    'semiconductors': {
        'title': 'Semiconductor Supply Chains: Why Shortages Happen and How to Build Resilience',
        'free_recall_prompt': 'Please recall everything you can from the article in 3 minutes. Describe why semiconductor shortages occurred, what structural factors made supply fragile, and how visibility, flexibility, contracts, and cooperation can strengthen resilience.',
        'text': '''Modern life runs on semiconductors. Every car, phone, medical monitor, and washing machine depends on microchips that interpret signals and manage power. Yet between 2020 and 2022, the world learned how invisible these components truly are when they suddenly ran out. Automakers halted production lines for want of five-dollar microcontrollers. Game consoles, routers, and hospital devices were delayed for months. The crisis was not one broken link but a synchronized shock: the pandemic sent demand for laptops and tablets soaring just as Asian factories idled, container ships queued at ports, and a fire at a Japanese substrate plant removed a critical input. When economies reopened, supply had frozen at the wrong points. Legacy fabrication nodes used in vehicles lagged behind, while the cutting-edge lines for smartphones and data centers were fully booked.
Semiconductor production is capital-intensive and rigid. A new fabrication plant—known as a fab—can cost more than ten billion dollars and take years to build. Even inside existing fabs, switching from one chip design to another requires new photomasks, chemistry, and validation runs. Each product family follows its own "process recipe," finely tuned over hundreds of steps. Automakers, who buy standardized chips in moderate volumes, tend to negotiate annual contracts and avoid pre-paying for capacity they might not use. In contrast, smartphone firms order aggressively, over-booking to secure priority and cancelling later if demand softens. When the pandemic scrambled forecasts, foundries naturally favored customers with larger margins and firmer commitments. What looked like an electronics shortage was partly a contractual hierarchy of trust and profitability.
Inside the foundries, production obeys a rhythm that resists acceleration. Silicon wafers travel through clean rooms for two to three months, moving among lithography, etching, ion implantation, and testing. Each machine costs millions and is already booked months ahead. Bottlenecks appear not only in equipment but in the supply of photoresists, ultra-pure gases, and polishing compounds. Because these inputs come from specialized suppliers, even a small disruption cascades through the chain. During the 2021 winter storm in Texas, a brief power loss halted local chemical plants that produced fluoropolymers used worldwide. The result: global shortages of semiconductor coatings weeks later. In such systems, physical distance and economic interdependence amplify each other—an event thousands of kilometers away can delay a car factory on another continent.
Geography compounds this fragility. East Asia dominates advanced fabrication and packaging, with Taiwan and South Korea producing most high-end chips. The United States and Europe specialize in design and lithography equipment, while the Netherlands hosts the world's only supplier of extreme-ultraviolet scanners. Natural disasters, geopolitical tensions, or export controls in any of these regions ripple across the entire network. The industry thus faces a paradox: resilience demands both diversification and specialization. No single country can efficiently perform every step, yet heavy concentration in one region invites systemic risk. The solution is coordination—duplication of critical suppliers for key materials, regional diversity in mature-node fabs, and harmonized quality standards that let chips be qualified across multiple plants.
Historically, firms trusted just-in-time (JIT) logistics to minimize inventory. For fast-moving consumer goods, that strategy works: shortages can be replenished quickly. But semiconductors have long cycle times. A missing wafer today cannot be replaced next week; the new batch may arrive three months later. When every participant runs lean simultaneously, the entire system loses shock absorbers. Companies are now rethinking inventory through a concept called risk-adjusted buffering. Components with long replacement times or high line-shutdown costs receive deliberate stockpiles. The expense appears on the balance sheet, yet the alternative—idled plants and lost market share—is worse. Risk-adjusted inventory thus turns carrying cost into a form of insurance.
Resilience, however, is not only about stockpiles. It is about information, flexibility, and incentives. The first step is visibility. Many firms discovered during the crisis that they did not know where their chips actually came from. A carmaker may buy electronic control units from a Tier-1 supplier, who in turn sources from a contract manufacturer, who relies on a particular foundry node in Taiwan or Malaysia. Without mapping two or three tiers upstream, managers cannot see vulnerabilities until too late. Creating supplier maps and digital twins of production networks allows real-time monitoring of lead times, yields, and geographic exposure.
Flexibility complements visibility. Designs that accept functionally equivalent components—known as second sourcing—enable substitution when a vendor falters. Engineers now favor circuit boards that can accommodate multiple pin-compatible microcontrollers or memory modules. Software abstraction layers allow firmware to run across chips from different brands. These design practices reduce dependency on single suppliers without sacrificing performance.
Contracts form the third lever. Traditional purchasing treated chips like commodities: the lowest bidder won. During shortages, that logic collapses because supply allocation favors relationships, not price. Some automakers now sign take-or-pay contracts that guarantee foundries a minimum revenue even if volumes fluctuate. Others pre-pay for capacity, effectively sharing risk. The aim is alignment: when customers signal long-term commitment, producers invest confidently. Governments can support this shift through co-investment schemes or tax incentives that tie subsidies to open access—ensuring that new fabs serve multiple industries rather than a single corporate patron.
Communication and data sharing close the loop. Rolling twelve-month forecasts and early-warning dashboards let upstream partners plan equipment maintenance and adjust production mix. In complex supply networks, signal quality is a public good: the clearer the information, the smaller the panic when demand shifts. Many governments are funding "semiconductor observatories" to collect anonymized order data and provide aggregated market indicators. The goal is not central planning but transparency, reducing the amplitude of collective over-reaction.
The semiconductor shortage also exposed cultural habits of over-optimization. For decades, supply-chain excellence meant cutting every margin—inventory, redundancy, and idle capacity were treated as waste. That mindset maximized short-term efficiency but sacrificed resilience. Economists now argue for a new balance: an efficiency—resilience frontier rather than a single optimum. On one side lies lean precision; on the other, slack capacity that absorbs shocks. Moving along this curve is strategic, not wasteful. Just as financial portfolios hedge against volatility, industrial portfolios hedge against supply disruption.
Resilience requires patient capital and policy consistency. Building new fabs or material plants is a ten-year endeavor, and investors need predictable demand. Frequent subsidy cycles or political shifts deter long-term projects. Effective industrial policy must therefore align incentives across generations of technology, encouraging not only national security but commercial viability. Collaborative training programs, standardized environmental rules, and shared R&D centers can sustain momentum beyond electoral terms.
Technology itself can assist resilience. Digital manufacturing platforms already monitor machine utilization, energy use, and process deviations. Artificial intelligence can forecast yield losses and re-route production before failures occur. Combined with blockchain-based provenance tracking, such tools could enable real-time certification of where and how each chip was made—vital for both quality assurance and security. In the future, resilience may depend as much on data integrity as on silicon purity. Emerging research now links predictive analytics with sustainability goals: optimizing energy use during wafer fabrication reduces both carbon footprint and cost volatility.
Policy coordination across regions is equally vital. The U.S. CHIPS Act, Europe's Chips Joint Undertaking, and Asia's national programs all aim to expand domestic production, yet without international alignment they risk duplication or subsidy races. A shared framework that pools research, harmonizes export controls, and keeps trade channels open would yield more stability than isolated protectionism. Semiconductor ecosystems thrive on specialization; walling them off undermines the very efficiency resilience seeks to protect. The next decade will test whether geopolitics can cooperate on interdependence rather than compete for self-sufficiency.
Ultimately, the semiconductor crisis reminded industries that supply chains are systems, not pipelines. Physics, economics, and politics intertwine. The cycle time of wafers sets physical limits; the capital intensity sets economic limits; and the geography of alliances sets political limits. No company or nation can unilaterally secure autonomy, but collaboration can reduce exposure. The aim is not to eliminate risk—an impossible task—but to absorb shocks gracefully and recover quickly. Firms that combine visibility, modular engineering, and balanced contracts emerge stronger after disruption.
Resilient supply chains share a quiet principle: trust built before crisis. When partners exchange information honestly, pay fairly for capacity, and invest jointly in contingency plans, panic gives way to coordination. The lesson of the shortage is enduring: stability comes not from stockpiles alone but from relationships that align incentives and share knowledge. Managing such systems demands patience, transparency, and continuous learning more than slogans. Chips may be tiny, but they illuminate the global logic of interdependence—how the smallest circuits reveal the largest truths about cooperation in an uncertain world.

''',
        'summary_integrated': 'Semiconductors power nearly every modern product, yet their global network is fragile. The 2020—22 shortage arose from synchronized disruptions: pandemic shutdowns, surging demand, logistics failures, and disasters that exposed how concentrated production had become. Fabrication is capital-intensive and slow; each chip family requires unique photomasks and multi-month cycles, making rapid adjustment impossible. Automakers\' cautious contracts lost priority to high-margin electronics firms, while bottlenecks in materials and equipment spread delays worldwide. Geographic concentration in East Asia and dependence on specialized suppliers magnified vulnerability. Resilience now means mapping multi-tier dependencies, designing boards that accept alternative chips, and signing take-or-pay or pre-payment contracts that align incentives. Governments can co-fund new fabs if access remains open across industries. Inventory logic has shifted from just-in-time to risk-adjusted buffers that trade efficiency for continuity. Digital twins, AI forecasting, and blockchain tracking enhance visibility, while coordinated industrial policy—through acts such as CHIPS and joint EU programs—can prevent subsidy races. Resilient ecosystems rely on trust built before crisis: transparent data, long-term partnerships, and predictable rules. The lesson is systemic: resilience lies not in isolation but in collaboration that balances physics, finance, and politics to absorb shocks and recover quickly when the next disruption arrives.',
        'summary_segmented': '''- Semiconductors power modern products; 2020—22 shortage revealed fragile supply chains.
- Pandemic disruptions: demand surges, factory shutdowns, logistics failures, material disasters.
- Fabrication is capital-intensive with multi-month cycles; rapid adjustment impossible.
- Automakers' modest contracts lost priority to high-margin electronics orders.
- Geographic concentration in East Asia creates systemic vulnerability.
- Resilience tactics: map multi-tier suppliers, design for component flexibility, use take-or-pay contracts.
- Shift from just-in-time to risk-adjusted inventory buffers.
- Digital twins, AI forecasting enhance visibility; policy coordination prevents subsidy races.
- Trust-based partnerships with transparent data enable shock absorption and faster recovery.''',
        'questions': [
            {'q': 'Why did automakers halt production during 2020—2022?', 'options': ['Lack of high-end GPUs', 'Shortage of low-cost microcontrollers', 'Labor strikes', 'Currency crisis'], 'correct': 1},
            {'q': 'Which factor makes fabs slow to flex?', 'options': ['Cheap retooling', 'Multi-year, capital-intensive builds', 'Abundant spares', 'Fully interchangeable nodes'], 'correct': 1},
            {'q': 'Foundries prioritize:', 'options': ['Lowest-margin orders', 'Unclear forecasts', 'Clients with clear forecasts and high margins', 'Random allocation'], 'correct': 2},
            {'q': 'A resilience tactic is to:', 'options': ['Rely on one supplier', 'Map two tiers up and qualify multiple fabs', 'Eliminate buffers', 'Ignore forecasts'], 'correct': 1},
            {'q': 'Risk-adjusted inventory means:', 'options': ['Zero inventory', 'Buffers for long lead-time parts', 'Only finished goods', 'Daily reorder'], 'correct': 1},
            {'q': 'Geographic concentration example:', 'options': ['Africa for lithography', 'Netherlands for photolithography', 'Canada for packaging', 'Brazil for etching'], 'correct': 1},
            {'q': 'Design flexibility example:', 'options': ['Unique pinout', 'Board accepts alternate controllers', 'Single-vendor locking', 'Proprietary screws'], 'correct': 1},
            {'q': 'Government support should be tied to:', 'options': ['Secrecy', 'Transparency and open capacity', 'Single industry access', 'Export bans'], 'correct': 1},
            {'q': 'Typical chip lead times are:', 'options': ['Hours', 'Days', 'Weeks', 'Multi-month cycle times'], 'correct': 3},
            {'q': 'Goal of resilience is to:', 'options': ['Eliminate risk', 'Absorb shocks and recover faster', 'Cut costs only', 'Centralize fabs'], 'correct': 1},
            {'q': 'Which consumer products surged during the pandemic?', 'options': ['Lawn mowers', 'Laptops and game consoles', 'Books and vinyl', 'Bicycles'], 'correct': 1},
            {'q': 'Which incident worsened shortages?', 'options': ['Drought in Taiwan', 'Fire at a Japanese substrate plant', 'Strike in Texas', 'Flood in Germany'], 'correct': 1},
            {'q': 'Automotive nodes compared to smartphone lines were:', 'options': ['More advanced', 'Lagging and less booked', 'Equally advanced', 'Fully booked'], 'correct': 1},
            {'q': 'Which contract type motivates foundries to reserve capacity?', 'options': ['Pay on delivery', 'Take-or-pay or prepayment', 'No-penalty cancellation', 'Verbal deal'], 'correct': 1},
            {'q': 'A board-level mitigation measure is:', 'options': ['Remove controllers', 'Use pin-compatible options', 'Convert to analog only', 'Eliminate sensors'], 'correct': 1}
        ]
    }
}

PRIOR_KNOWLEDGE_TERMS = [
    "Urban heat island", "Thermal mass", "Street canyon",
    "Guide RNA", "Off-target editing", "Germ-line editing",
    "Foundry", "Semiconductor", "Supply chain resilience"
]

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
        save_participant(pid, {"full_name": "[test-skip]"})
        log_data(pid, "demographics", {"skipped": True})
    # keep language choice persistent
    if "lang" not in session:
        session["lang"] = DEFAULT_LANG
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
@require_pid
def skip_reading():
    _ensure_pid()
    article_num = int(session.get("current_article", 0))
    # Skip current reading â†’ go to the 5"‘minute pre"‘test break for this article
    return redirect(url_for("break_before_test", article_num=article_num))

@app.route("/skip_test/<int:article_num>")
def skip_test(article_num: int):
    pid = _ensure_pid()
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
@require_pid
def skip_break(next_article: int):
    """Skip the BETWEEN-ARTICLES break â†’ go to NEXT article reading."""
    _ensure_pid()
    return redirect(url_for("reading_phase", article_num=next_article))

# ---- Skip pre-test break (AFTER reading, BEFORE test) ----

@app.route("/skip_break_before_test/<int:article_num>")
@require_pid
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
        terms=[_auto_translate(term, _get_lang()) for term in PRIOR_KNOWLEDGE_TERMS],
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

    # Recall timing: total = 6 minutes, unlock at 3 minutes (shorter in TEST_MODE)
    recall_total_ms = 10000 if TEST_MODE else (6 * 60 * 1000)
    recall_unlock_ms = 5000 if TEST_MODE else (3 * 60 * 1000)

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
        return jsonify({"redirect": url_for("manipulation_check")})
    return jsonify({"redirect": url_for("short_break", next_article=next_article)})


# ---- Alias for after-reading break (backward compatibility/clarity) ----
@app.route("/break_after_reading/<int:article_num>")
@require_pid
def break_after_reading(article_num: int):
    # Alias for clarity/backward-compatibility: break that occurs after reading, before the test
    return render_template("break.html", next_article=article_num, after_reading=True, test_mode=TEST_MODE)

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
