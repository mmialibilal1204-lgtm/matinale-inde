"""
╔══════════════════════════════════════════════════════╗
║          MA MATINALE INDÉ  —  v2.0                   ║
║  Agrégateur RSS multi-sources · IA Groq · Audio gTTS ║
║  Onglets thématiques · Filtres région & catégorie    ║
╚══════════════════════════════════════════════════════╝
"""

import re
import os
import datetime
import tempfile

import feedparser
import streamlit as st
from groq import Groq
from gtts import gTTS

# ═══════════════════════════════════════════════════════
#  1. CATALOGUE DES FLUX RSS
#     Structure : { "Région" : { "Catégorie" : [ (Nom, URL) ] } }
# ═══════════════════════════════════════════════════════

RSS_CATALOG = {

    # ── FRANCE ──────────────────────────────────────────
    "🇫🇷 France": {
        "Général": [
            ("Le Monde",            "https://www.lemonde.fr/rss/une.xml"),
            ("Le Figaro",           "https://www.lefigaro.fr/rss/figaro_actualites.xml"),
            ("Libération",          "https://www.liberation.fr/arc/outboundfeeds/rss/"),
            ("France Info",         "https://www.francetvinfo.fr/france.rss"),
            ("20 Minutes",          "https://www.20minutes.fr/feeds/rss/une.xml"),
            ("L'Obs",               "https://www.nouvelobs.com/rss.xml"),
            ("France 24 FR",        "https://www.france24.com/fr/rss"),
            ("RFI France",          "https://www.rfi.fr/fr/france/rss"),
        ],
        "Politique": [
            ("L'Humanité",          "https://www.humanite.fr/feed"),
            ("Marianne",            "https://www.marianne.net/feed"),
            ("Le Monde Politique",  "https://www.lemonde.fr/politique/rss_full.xml"),
            ("Mediapart",           "https://www.mediapart.fr/articles/feed"),
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
        ],
        "Économie": [
            ("Les Échos",           "https://www.lesechos.fr/rss/rss_une.xml"),
            ("Le Figaro Éco",       "https://www.lefigaro.fr/rss/figaro_economie.xml"),
            ("BFM Business",        "https://bfmbusiness.bfmtv.com/rss/info/flux-rss/flux-toutes-les-actualites/"),
            ("Capital",             "https://www.capital.fr/feed"),
            ("Challenges",          "https://www.challenges.fr/feed/"),
        ],
        "Santé": [
            ("Le Monde Santé",      "https://www.lemonde.fr/sante/rss_full.xml"),
            ("Pourquoi Docteur",    "https://www.pourquoidocteur.fr/feed"),
            ("Sciences et Avenir",  "https://www.sciencesetavenir.fr/sante.rss"),
        ],
        "Culture & Société": [
            ("Télérama",            "https://www.telerama.fr/rss.xml"),
            ("Le Monde Culture",    "https://www.lemonde.fr/culture/rss_full.xml"),
            ("Slate FR",            "https://www.slate.fr/rss"),
            ("L'Express",           "https://www.lexpress.fr/arc/outboundfeeds/rss/"),
        ],
        "Environnement": [
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
            ("Le Monde Planète",    "https://www.lemonde.fr/planete/rss_full.xml"),
            ("Vert.eco",            "https://vert.eco/feed"),
            ("Novethic",            "https://www.novethic.fr/feed"),
        ],
    },

    # ── EUROPE ──────────────────────────────────────────
    "🇪🇺 Europe": {
        "Général": [
            ("Euronews FR",         "https://fr.euronews.com/rss?level=theme&name=news"),
            ("The Guardian Europe", "https://www.theguardian.com/world/europe-news/rss"),
            ("Deutsche Welle FR",   "https://rss.dw.com/rdf/rss-fr-all"),
            ("RTBF",                "https://rss.rtbf.be/article/rss/rtbf_info_homepage.xml"),
            ("RTS Info",            "https://www.rts.ch/info/rss/2022.xml"),
            ("Le Temps",            "https://www.letemps.ch/rss.xml"),
            ("Courrier International","https://www.courrierinternational.com/feed/all/rss.xml"),
        ],
        "Politique": [
            ("Euractiv FR",         "https://www.euractiv.fr/feed/"),
            ("Politico Europe",     "https://www.politico.eu/feed/"),
            ("The Guardian Politics","https://www.theguardian.com/politics/rss"),
        ],
        "Économie": [
            ("Les Échos Europe",    "https://www.lesechos.fr/rss/rss_finance_marches.xml"),
            ("Financial Times",     "https://www.ft.com/world/europe?format=rss"),
        ],
        "Environnement": [
            ("Euronews Green",      "https://fr.euronews.com/rss?level=vertical&name=green"),
            ("The Guardian Env.",   "https://www.theguardian.com/environment/rss"),
        ],
    },

    # ── MONDE ───────────────────────────────────────────
    "🌍 Monde": {
        "Général": [
            ("The Guardian World",  "https://www.theguardian.com/world/rss"),
            ("BBC World",           "https://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Reuters",             "https://feeds.reuters.com/reuters/topNews"),
            ("Al Jazeera EN",       "https://www.aljazeera.com/xml/rss/all.xml"),
            ("France 24 EN",        "https://www.france24.com/en/rss"),
            ("RFI Monde",           "https://www.rfi.fr/fr/rss"),
            ("Le Monde Diplo",      "https://www.monde-diplomatique.fr/recents.atom"),
            ("DW World",            "https://rss.dw.com/rdf/rss-en-all"),
        ],
        "Politique": [
            ("Politico",            "https://www.politico.com/rss/politicopicks.xml"),
            ("Foreign Affairs",     "https://www.foreignaffairs.com/rss.xml"),
            ("The Atlantic",        "https://www.theatlantic.com/feed/all/"),
        ],
        "Économie": [
            ("Financial Times",     "https://www.ft.com/?format=rss"),
            ("The Economist",       "https://www.economist.com/the-world-this-week/rss.xml"),
            ("Bloomberg",           "https://feeds.bloomberg.com/markets/news.rss"),
        ],
        "Technologie": [
            ("Wired",               "https://www.wired.com/feed/rss"),
            ("The Verge",           "https://www.theverge.com/rss/index.xml"),
            ("TechCrunch",          "https://techcrunch.com/feed/"),
            ("MIT Tech Review",     "https://www.technologyreview.com/feed/"),
        ],
        "Santé": [
            ("WHO News",            "https://www.who.int/rss-feeds/news-english.xml"),
            ("The Guardian Health", "https://www.theguardian.com/society/health/rss"),
            ("Science Daily",       "https://www.sciencedaily.com/rss/health_medicine.xml"),
        ],
    },

    # ── AFRIQUE ─────────────────────────────────────────
    "🌍 Afrique": {
        "Général": [
            ("RFI Afrique",         "https://www.rfi.fr/fr/afrique/rss"),
            ("Jeune Afrique",       "https://www.jeuneafrique.com/feed/"),
            ("Africa 24",           "https://www.africa24tv.com/feed/"),
            ("Le Monde Afrique",    "https://www.lemonde.fr/afrique/rss_full.xml"),
            ("Al Jazeera Africa",   "https://www.aljazeera.com/xml/rss/all.xml"),
            ("TV5 Monde Afrique",   "https://information.tv5monde.com/rss.xml"),
            ("The Africa Report",   "https://www.theafricareport.com/feed/"),
        ],
        "Économie": [
            ("Jeune Afrique Éco",   "https://www.jeuneafrique.com/cat/economie-entreprises/feed/"),
            ("Les Afriques",        "https://www.lesafriques.com/feed/"),
        ],
        "Politique": [
            ("Jeune Afrique Pol.",  "https://www.jeuneafrique.com/cat/politique/feed/"),
            ("Africa Intelligence", "https://www.africaintelligence.fr/feed"),
        ],
    },

    # ── AMÉRIQUES ───────────────────────────────────────
    "🌎 Amériques": {
        "Général": [
            ("New York Times",      "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
            ("Washington Post",     "https://feeds.washingtonpost.com/rss/world"),
            ("The Guardian US",     "https://www.theguardian.com/us-news/rss"),
            ("BBC Americas",        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
            ("NPR",                 "https://feeds.npr.org/1001/rss.xml"),
            ("RFI Amériques",       "https://www.rfi.fr/fr/ameriques/rss"),
        ],
        "Politique": [
            ("Politico US",         "https://www.politico.com/rss/politicopicks.xml"),
            ("The Hill",            "https://thehill.com/feed/"),
            ("Slate US",            "https://slate.com/feeds/all.rss"),
        ],
        "Économie": [
            ("WSJ",                 "https://feeds.a.dj.com/rss/RSSWorldNews.xml"),
            ("Forbes",              "https://www.forbes.com/real-time/feed2/"),
        ],
    },

    # ── ASIE & MOYEN-ORIENT ─────────────────────────────
    "🌏 Asie & M.-Orient": {
        "Général": [
            ("BBC Asia",            "https://feeds.bbci.co.uk/news/world/asia/rss.xml"),
            ("Al Jazeera ME",       "https://www.aljazeera.com/xml/rss/all.xml"),
            ("RFI Asie",            "https://www.rfi.fr/fr/asie-pacifique/rss"),
            ("South China Morning", "https://www.scmp.com/rss/91/feed"),
            ("DW Asia",             "https://rss.dw.com/rdf/rss-en-asia"),
            ("The Diplomat",        "https://thediplomat.com/feed/"),
        ],
        "Économie": [
            ("Nikkei Asia",         "https://asia.nikkei.com/rss/feed/nar"),
            ("Bloomberg Asia",      "https://feeds.bloomberg.com/asia/news.rss"),
        ],
        "Politique": [
            ("Middle East Eye",     "https://www.middleeasteye.net/rss"),
            ("Orient XXI",          "https://orientxxi.info/feed"),
        ],
    },
}

# ── ONGLETS de l'interface (thème + mapping région+catégorie) ──
TABS_CONFIG = {
    "🗞️ À la une": {
        "regions":    ["🇫🇷 France", "🌍 Monde"],
        "categories": ["Général"],
        "prompt_hint": "Fais un tour d'horizon général de l'actualité du jour, France et Monde.",
        "color":      "#c0392b",
        "icon":       "🗞️",
    },
    "🇫🇷 France": {
        "regions":    ["🇫🇷 France"],
        "categories": ["Général", "Politique", "Économie"],
        "prompt_hint": "Concentre-toi sur l'actualité française.",
        "color":      "#2980b9",
        "icon":       "🇫🇷",
    },
    "🌍 Monde": {
        "regions":    ["🌍 Monde", "🌎 Amériques", "🌏 Asie & M.-Orient", "🌍 Afrique"],
        "categories": ["Général"],
        "prompt_hint": "Dresse un panorama de l'actualité internationale.",
        "color":      "#16a085",
        "icon":       "🌍",
    },
    "⚖️ Politique": {
        "regions":    ["🇫🇷 France", "🇪🇺 Europe", "🌍 Monde"],
        "categories": ["Politique"],
        "prompt_hint": "Analyse l'actualité politique française, européenne et internationale.",
        "color":      "#8e44ad",
        "icon":       "⚖️",
    },
    "💶 Économie": {
        "regions":    ["🇫🇷 France", "🇪🇺 Europe", "🌍 Monde"],
        "categories": ["Économie"],
        "prompt_hint": "Décrypte les grandes tendances économiques et financières du jour.",
        "color":      "#f39c12",
        "icon":       "💶",
    },
    "🌱 Environnement": {
        "regions":    ["🇫🇷 France", "🇪🇺 Europe", "🌍 Monde"],
        "categories": ["Environnement"],
        "prompt_hint": "Mets en avant les enjeux environnementaux et climatiques du jour.",
        "color":      "#27ae60",
        "icon":       "🌱",
    },
    "💊 Santé": {
        "regions":    ["🇫🇷 France", "🌍 Monde"],
        "categories": ["Santé"],
        "prompt_hint": "Présente les actualités santé et science médicale importantes.",
        "color":      "#e74c3c",
        "icon":       "💊",
    },
    "💻 Tech": {
        "regions":    ["🌍 Monde", "🌎 Amériques"],
        "categories": ["Technologie"],
        "prompt_hint": "Passe en revue les grandes actualités technologiques et numériques.",
        "color":      "#1abc9c",
        "icon":       "💻",
    },
    "🌍 Afrique": {
        "regions":    ["🌍 Afrique"],
        "categories": ["Général", "Politique", "Économie"],
        "prompt_hint": "Informe sur l'actualité africaine dans toute sa diversité.",
        "color":      "#e67e22",
        "icon":       "🌍",
    },
}

GROQ_MODEL   = "llama-3.3-70b-versatile"
HOURS_BACK   = 24
MAX_ARTICLES = 40   # Limite articles envoyés au LLM
MAX_DISPLAY  = 30   # Limite articles affichés dans l'expander

SYSTEM_PROMPT_TEMPLATE = """Tu es le rédacteur en chef d'une matinale d'information indépendante, progressive et rigoureuse.
{hint}
À partir des articles fournis, crée un briefing de 350 mots environ, structuré en 3 parties :

## 🔴 L'Essentiel
Les faits les plus importants du moment, expliqués clairement.

## 🌐 Le Tour du Monde / Contexte
Les développements secondaires mais significatifs, replacés dans leur contexte.

## ✅ La Note Positive
Une bonne nouvelle, une avancée, un fait encourageant.

**Règles absolues :**
- N'invente aucun fait.
- Reste neutre, factuel et dynamique.
- Utilise uniquement les informations présentes dans les articles.
- Écris en français, avec un style oral et engageant.
"""

# ═══════════════════════════════════════════════════════
#  2. CSS — DESIGN ÉDITORIAL MAGAZINE (mobile-first)
# ═══════════════════════════════════════════════════════

def inject_css(accent: str = "#c0392b"):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    :root {{
        --accent:      {accent};
        --accent-dark: color-mix(in srgb, {accent} 70%, black);
        --bg:          #0f0f11;
        --bg2:         #17171a;
        --bg3:         #1e1e23;
        --border:      #2a2a32;
        --text:        #e8e8ee;
        --text-muted:  #888898;
        --radius:      10px;
    }}

    /* ── Reset global ──────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }}
    [data-testid="stSidebar"] {{
        background: var(--bg2) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding-top: 1rem !important; max-width: 760px; }}

    /* ── Masthead ─────────────────────────────────── */
    .masthead {{
        text-align: center;
        padding: 2rem 0 1rem;
        border-bottom: 2px solid var(--border);
        margin-bottom: 1.5rem;
    }}
    .masthead-title {{
        font-family: 'DM Serif Display', serif;
        font-size: clamp(2rem, 7vw, 3.4rem);
        letter-spacing: -1px;
        color: var(--text);
        line-height: 1;
        margin: 0;
    }}
    .masthead-title span {{ color: var(--accent); }}
    .masthead-date {{
        font-size: 0.78rem;
        color: var(--text-muted);
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.4rem;
    }}
    .masthead-rule {{
        width: 48px; height: 3px;
        background: var(--accent);
        border: none; margin: 0.8rem auto 0;
    }}

    /* ── Onglets Streamlit ─────────────────────────── */
    [data-testid="stTabs"] [role="tablist"] {{
        gap: 4px;
        border-bottom: 1px solid var(--border) !important;
        overflow-x: auto;
        flex-wrap: nowrap !important;
        scrollbar-width: none;
    }}
    [data-testid="stTabs"] [role="tab"] {{
        background: var(--bg2) !important;
        color: var(--text-muted) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) var(--radius) 0 0 !important;
        padding: 0.45rem 0.9rem !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        white-space: nowrap !important;
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: var(--bg3) !important;
        color: var(--text) !important;
        border-bottom-color: var(--bg3) !important;
        border-top: 2px solid var(--accent) !important;
    }}

    /* ── Filtres sidebar ──────────────────────────── */
    [data-testid="stSidebar"] label {{
        color: var(--text) !important;
        font-size: 0.88rem !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background: var(--bg3) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius) !important;
    }}
    [data-testid="stSidebar"] .stMultiSelect > div > div {{
        background: var(--bg3) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--radius) !important;
    }}

    /* ── Bouton principal ─────────────────────────── */
    .stButton > button {{
        width: 100% !important;
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius) !important;
        padding: 0.8rem 1rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 14px color-mix(in srgb, var(--accent) 40%, transparent) !important;
    }}
    .stButton > button:hover {{
        background: var(--accent-dark) !important;
        transform: translateY(-1px) !important;
    }}

    /* ── Carte résumé ─────────────────────────────── */
    .summary-card {{
        background: var(--bg3);
        border: 1px solid var(--border);
        border-top: 3px solid var(--accent);
        border-radius: var(--radius);
        padding: 1.5rem;
        line-height: 1.75;
        font-size: 0.97rem;
        margin: 1rem 0;
    }}
    .summary-card h2 {{
        font-family: 'DM Serif Display', serif;
        font-size: 1.2rem;
        color: var(--text);
        margin: 1.2rem 0 0.4rem;
    }}
    .summary-card h2:first-child {{ margin-top: 0; }}

    /* ── Méta-infos ─────────────────────────────── */
    .meta-bar {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 1rem;
    }}
    .meta-chip {{
        background: var(--bg3);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.74rem;
        color: var(--text-muted);
    }}
    .meta-chip.accent {{
        background: color-mix(in srgb, var(--accent) 15%, transparent);
        border-color: color-mix(in srgb, var(--accent) 40%, transparent);
        color: var(--accent);
        font-weight: 600;
    }}

    /* ── Source badge ──────────────────────────── */
    .src-badge {{
        display: inline-block;
        background: var(--bg3);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 1px 7px;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-right: 4px;
    }}

    /* ── Divider ────────────────────────────────── */
    hr {{ border-color: var(--border) !important; }}

    /* ── Spinner & messages ─────────────────────── */
    [data-testid="stStatusWidget"] {{ color: var(--text) !important; }}
    .stAlert {{ border-radius: var(--radius) !important; }}
    [data-testid="stExpander"] {{
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }}
    [data-testid="stExpander"] summary {{
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
    }}

    /* ── Download buttons ───────────────────────── */
    [data-testid="stDownloadButton"] > button {{
        background: var(--bg3) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
    }}

    /* ── Mobile tweaks ──────────────────────────── */
    @media (max-width: 640px) {{
        .masthead-title {{ font-size: 2rem; }}
        .summary-card   {{ padding: 1rem; }}
    }}

    /* ── Hide Streamlit chrome ──────────────────── */
    #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  3. PARSING RSS
# ═══════════════════════════════════════════════════════

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()

@st.cache_data(ttl=1800, show_spinner=False)   # Cache 30 min
def fetch_articles(feed_urls: tuple) -> list[dict]:
    """
    Récupère les articles des dernières HOURS_BACK heures
    depuis une liste de (source, url).
    Résultat mis en cache 30 minutes.
    """
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)
    articles = []

    for source, url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime.datetime(*pub[:6], tzinfo=datetime.timezone.utc)
                    if pub_dt < cutoff:
                        continue
                title   = strip_html(entry.get("title", "")).strip()
                summary = strip_html(entry.get("summary", entry.get("description", ""))).strip()
                if title:
                    articles.append({
                        "source":    source,
                        "title":     title,
                        "summary":   summary[:450],
                        "link":      entry.get("link", ""),
                        "published": entry.get("published", ""),
                    })
        except Exception:
            pass   # Flux indisponible — on continue silencieusement

    return articles


def get_feeds_for_tab(tab_cfg: dict,
                      extra_regions: list,
                      extra_cats: list) -> list[tuple]:
    """
    Construit la liste de (source, url) à partir :
    - des régions/catégories par défaut de l'onglet
    - des filtres additionnels choisis par l'utilisateur
    """
    regions = list(set(tab_cfg["regions"] + extra_regions))
    cats    = list(set(tab_cfg["categories"] + extra_cats))

    feeds = []
    seen  = set()
    for region in regions:
        if region not in RSS_CATALOG:
            continue
        for cat in cats:
            if cat not in RSS_CATALOG[region]:
                continue
            for name, url in RSS_CATALOG[region][cat]:
                if url not in seen:
                    feeds.append((name, url))
                    seen.add(url)
    return feeds


# ═══════════════════════════════════════════════════════
#  4. LLM — GROQ
# ═══════════════════════════════════════════════════════

def build_user_prompt(articles: list[dict]) -> str:
    if not articles:
        return "Aucun article disponible."
    lines = [f"Voici {len(articles)} articles récents :\n"]
    for i, a in enumerate(articles[:MAX_ARTICLES], 1):
        lines.append(f"[{i}] {a['source']} — {a['title']}\n    {a['summary']}\n")
    return "\n".join(lines)


def generate_summary(articles: list[dict], hint: str) -> str:
    api_key = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=api_key)
    system  = SYSTEM_PROMPT_TEMPLATE.format(hint=hint)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": build_user_prompt(articles)},
        ],
        max_tokens=800,
        temperature=0.45,
    )
    return response.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════
#  5. AUDIO — gTTS + tempfile
# ═══════════════════════════════════════════════════════

def generate_audio(text: str) -> bytes:
    # Nettoyage des émojis et markdown pour TTS
    clean = re.sub(r"[#*_`~>]", "", text)
    clean = re.sub(r"[\U00010000-\U0010ffff]", "", clean, flags=re.UNICODE)
    clean = re.sub(r"\s+", " ", clean).strip()

    tts = gTTS(text=clean, lang="fr", slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        path = tmp.name
    with open(path, "rb") as f:
        data = f.read()
    os.unlink(path)
    return data


# ═══════════════════════════════════════════════════════
#  6. RENDU D'UN ONGLET
# ═══════════════════════════════════════════════════════

def render_tab(tab_name: str, tab_cfg: dict,
               extra_regions: list, extra_cats: list,
               audio_enabled: bool):
    """Affiche le contenu complet d'un onglet."""

    accent = tab_cfg["color"]
    inject_css(accent)   # Réinjection de la couleur d'accent pour cet onglet

    st.markdown(f"""
    <div class="meta-bar">
        <span class="meta-chip accent">{tab_cfg['icon']} {tab_name.split(' ', 1)[-1]}</span>
        {"".join(f'<span class="meta-chip">{r.split(" ",1)[-1]}</span>'
                 for r in (tab_cfg['regions'] + extra_regions)[:4])}
    </div>
    """, unsafe_allow_html=True)

    feeds = get_feeds_for_tab(tab_cfg, extra_regions, extra_cats)
    if not feeds:
        st.warning("Aucune source disponible pour cette combinaison région/catégorie.")
        return

    if st.button(f"▶ Générer la matinale — {tab_name}", key=f"btn_{tab_name}"):
        # ── Récupération RSS ──────────────────────
        with st.spinner("📡 Lecture des flux RSS…"):
            articles = fetch_articles(tuple(feeds))

        if not articles:
            st.error("⚠️ Aucun article récupéré. Les flux sont peut-être indisponibles.")
            return

        sources_used = list(dict.fromkeys(a["source"] for a in articles))

        # ── Résumé IA ────────────────────────────
        with st.spinner("🤖 Génération par Llama 3.3…"):
            try:
                summary = generate_summary(articles, tab_cfg["prompt_hint"])
            except Exception as e:
                st.error(f"Erreur Groq : {e}")
                return

        # ── Audio ─────────────────────────────────
        audio_bytes = None
        if audio_enabled:
            with st.spinner("🔊 Synthèse vocale…"):
                try:
                    audio_bytes = generate_audio(summary)
                except Exception as e:
                    st.warning(f"Audio indisponible : {e}")

        # ── Affichage ─────────────────────────────
        st.markdown(f"""
        <div class="meta-bar" style="margin-top:1rem">
            <span class="meta-chip accent">✅ {len(articles)} articles</span>
            <span class="meta-chip">🕐 24 dernières heures</span>
            <span class="meta-chip">🤖 {GROQ_MODEL}</span>
        </div>
        """, unsafe_allow_html=True)

        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

        # Résumé en Markdown dans la carte stylée
        st.markdown(
            f'<div class="summary-card">{_md_to_html(summary)}</div>',
            unsafe_allow_html=True,
        )

        # Boutons de téléchargement
        col1, col2 = st.columns(2)
        with col1:
            if audio_bytes:
                st.download_button("⬇️ MP3", audio_bytes,
                                   file_name="matinale.mp3", mime="audio/mpeg",
                                   use_container_width=True, key=f"dl_mp3_{tab_name}")
        with col2:
            st.download_button("⬇️ Texte", summary,
                               file_name="matinale.txt", mime="text/plain",
                               use_container_width=True, key=f"dl_txt_{tab_name}")

        # Sources détaillées (repliable)
        with st.expander(f"📋 {len(articles)} articles collectés — cliquer pour voir"):
            for art in articles[:MAX_DISPLAY]:
                link_md = f"[{art['title']}]({art['link']})" if art["link"] else art["title"]
                st.markdown(
                    f"<span class='src-badge'>{art['source']}</span> {link_md}",
                    unsafe_allow_html=True,
                )

    else:
        # État vide
        src_names = [s for s, _ in feeds[:8]]
        st.markdown(f"""
        <div class="summary-card" style="text-align:center; color:var(--text-muted); padding:2.5rem 1rem">
            <div style="font-size:2.5rem; margin-bottom:0.5rem">{tab_cfg['icon']}</div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.1rem; color:var(--text); margin-bottom:0.5rem">
                Prêt à générer
            </div>
            <div style="font-size:0.82rem">
                {len(feeds)} sources actives ·
                {", ".join(src_names[:5])}{"…" if len(src_names) > 5 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)


def _md_to_html(text: str) -> str:
    """Conversion minimale Markdown→HTML pour les titres et le gras."""
    # Titres ## → <h2>
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    # Gras **…**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Sauts de ligne
    text = text.replace("\n", "<br>")
    return text


# ═══════════════════════════════════════════════════════
#  7. APPLICATION PRINCIPALE
# ═══════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Ma Matinale Indé",
        page_icon="📻",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    inject_css()  # CSS de base (accent rouge)

    # ── MASTHEAD ──────────────────────────────────────
    today = datetime.date.today()
    jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
    mois  = ["janvier","février","mars","avril","mai","juin",
              "juillet","août","septembre","octobre","novembre","décembre"]
    date_str = f"{jours[today.weekday()]} {today.day} {mois[today.month-1]} {today.year}".upper()

    st.markdown(f"""
    <div class="masthead">
        <h1 class="masthead-title">Ma Matinale <span>Indé</span></h1>
        <div class="masthead-date">{date_str}</div>
        <hr class="masthead-rule">
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR — FILTRES ─────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'DM Serif Display',serif; font-size:1.3rem;
                    color:var(--text); padding:0.5rem 0 1rem; border-bottom:1px solid var(--border);
                    margin-bottom:1rem">
            🎛️ Filtres
        </div>
        """, unsafe_allow_html=True)

        all_regions = list(RSS_CATALOG.keys())
        extra_regions = st.multiselect(
            "Régions supplémentaires",
            options=all_regions,
            default=[],
            help="Ajoute des régions en plus de celles de l'onglet actif",
        )

        all_cats = sorted({
            cat
            for region in RSS_CATALOG.values()
            for cat in region
        })
        extra_cats = st.multiselect(
            "Catégories supplémentaires",
            options=all_cats,
            default=[],
            help="Ajoute des catégories en plus de celles de l'onglet actif",
        )

        st.markdown("---")
        audio_enabled = st.toggle("🔊 Activer l'audio (gTTS)", value=True)

        st.markdown("---")
        # Compteur de sources
        total_feeds = sum(
            len(urls)
            for region in RSS_CATALOG.values()
            for urls in region.values()
        )
        st.markdown(f"""
        <div style="font-size:0.78rem; color:var(--text-muted); line-height:1.8">
            <strong style="color:var(--text)">{total_feeds}</strong> sources indexées<br>
            <strong style="color:var(--text)">{len(RSS_CATALOG)}</strong> régions du monde<br>
            <strong style="color:var(--text)">{len(all_cats)}</strong> catégories<br>
            <strong style="color:var(--text)">{HOURS_BACK}h</strong> de fenêtre temporelle<br>
            🤖 <strong style="color:var(--text)">{GROQ_MODEL}</strong>
        </div>
        """, unsafe_allow_html=True)

    # ── ONGLETS ───────────────────────────────────────
    tab_labels = list(TABS_CONFIG.keys())
    tabs = st.tabs(tab_labels)

    for tab_widget, tab_name in zip(tabs, tab_labels):
        with tab_widget:
            render_tab(
                tab_name    = tab_name,
                tab_cfg     = TABS_CONFIG[tab_name],
                extra_regions = extra_regions,
                extra_cats    = extra_cats,
                audio_enabled = audio_enabled,
            )

    # ── PIED DE PAGE ──────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-top:3rem; padding-top:1rem;
                border-top:1px solid var(--border); font-size:0.75rem;
                color:var(--text-muted); line-height:2">
        <strong style="color:var(--text)">Ma Matinale Indé</strong> · Open-source · Aucune pub<br>
        IA : Groq / Llama 3.3 · Voix : Google TTS · Sources : presse indépendante mondiale
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
