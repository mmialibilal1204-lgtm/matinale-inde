"""
╔══════════════════════════════════════════════════════╗
║          MA MATINALE INDÉ  —  v3.5                   ║
║  Agrégateur RSS · IA Groq · Audio · Chat Interactif  ║
║  Design Magazine v2.0 Original (Restauré)            ║
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
# ═══════════════════════════════════════════════════════

RSS_CATALOG = {
    "🇫🇷 France": {
        "Général": [
            ("Le Monde",            "https://www.lemonde.fr/rss/une.xml"),
            ("Le Figaro",           "https://www.lefigaro.fr/rss/figaro_actualites.xml"),
            ("Libération",          "https://www.liberation.fr/arc/outboundfeeds/rss/"),
            ("France Info",         "https://www.francetvinfo.fr/france.rss"),
            ("L'Obs",               "https://www.nouvelobs.com/rss.xml"),
        ],
        "Politique": [
            ("L'Humanité",          "https://www.humanite.fr/feed"),
            ("Marianne",            "https://www.marianne.net/feed"),
            ("Mediapart",           "https://www.mediapart.fr/articles/feed"),
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
        ],
        "Économie": [
            ("Les Échos",           "https://www.lesechos.fr/rss/rss_une.xml"),
            ("Capital",             "https://www.capital.fr/feed"),
        ],
        "Environnement": [
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
            ("Vert.eco",            "https://vert.eco/feed"),
        ],
    },
    "🌍 Monde": {
        "Général": [
            ("The Guardian World",  "https://www.theguardian.com/world/rss"),
            ("BBC World",           "https://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Le Monde Diplo",      "https://www.monde-diplomatique.fr/recents.atom"),
            ("Courrier International","https://www.courrierinternational.com/feed/all/rss.xml"),
        ],
    },
    "🇪🇺 Europe": {
        "Général": [
            ("Euronews FR",         "https://fr.euronews.com/rss?level=theme&name=news"),
            ("Politico Europe",     "https://www.politico.eu/feed/"),
        ],
    }
}

TABS_CONFIG = {
    "🗞️ À la une": {"regions": ["🇫🇷 France", "🌍 Monde"], "categories": ["Général"], "color": "#c0392b", "icon": "🗞️", "hint": "Tour d'horizon général France et Monde."},
    "🇫🇷 France": {"regions": ["🇫🇷 France"], "categories": ["Général", "Politique", "Économie"], "color": "#2980b9", "icon": "🇫🇷", "hint": "Actualité française détaillée."},
    "🌍 Monde": {"regions": ["🌍 Monde"], "categories": ["Général"], "color": "#16a085", "icon": "🌍", "hint": "Panorama international complet."},
    "⚖️ Politique": {"regions": ["🇫🇷 France", "🇪🇺 Europe"], "categories": ["Politique"], "color": "#8e44ad", "icon": "⚖️", "hint": "Analyse politique approfondie."},
    "🌱 Environnement": {"regions": ["🇫🇷 France", "🌍 Monde"], "categories": ["Environnement"], "color": "#27ae60", "icon": "🌱", "hint": "Enjeux écologiques et climat."},
}

GROQ_MODEL   = "llama-3.3-70b-versatile"
HOURS_BACK   = 24
MAX_ARTICLES = 50 

# ═══════════════════════════════════════════════════════
#  2. CSS — DESIGN MAGAZINE v2.0 (Restauré et Adapté)
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
        --radius:      12px;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    .block-container {{ padding-top: 1rem !important; max-width: 850px; }}

    /* Masthead */
    .masthead {{ text-align: center; padding: 2rem 0 1rem; border-bottom: 2px solid var(--border); margin-bottom: 1.5rem; }}
    .masthead-title {{ font-family: 'DM Serif Display', serif; font-size: clamp(2.2rem, 7vw, 3.8rem); letter-spacing: -1px; line-height: 1; margin: 0; }}
    .masthead-title span {{ color: var(--accent); }}
    .masthead-date {{ font-size: 0.78rem; color: var(--text-muted); letter-spacing: 3px; text-transform: uppercase; margin-top: 0.5rem; }}

    /* Summary Card (Magazine Style) */
    .summary-card {{
        background: var(--bg3);
        border: 1px solid var(--border);
        border-top: 5px solid var(--accent);
        border-radius: var(--radius);
        padding: 2.5rem;
        line-height: 1.8;
        font-size: 1.05rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}
    .summary-card h2 {{ font-family: 'DM Serif Display', serif; font-size: 1.8rem; color: var(--text); margin-top: 1.8rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}

    /* Chat Styling */
    [data-testid="stChatMessage"] {{
        background: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }}
    .stChatInputContainer {{ padding-bottom: 20px; }}

    /* Buttons */
    .stButton > button {{
        width: 100% !important;
        background: var(--accent) !important;
        color: white !important;
        border-radius: var(--radius) !important;
        padding: 0.8rem !important;
        font-weight: 600 !important;
    }}

    @media (max-width: 768px) {{
        .summary-card {{ padding: 1.2rem; font-size: 0.98rem; }}
        .masthead-title {{ font-size: 2.4rem; }}
    }}

    #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  3. FONCTIONS LOGIQUES
# ═══════════════════════════════════════════════════════

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()

@st.cache_data(ttl=1800)
def fetch_articles(feed_urls: tuple) -> list[dict]:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)
    articles = []
    for source, url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime.datetime(*pub[:6], tzinfo=datetime.timezone.utc)
                    if pub_dt < cutoff: continue
                articles.append({
                    "source": source,
                    "title": strip_html(entry.get("title", "")),
                    "summary": strip_html(entry.get("summary", entry.get("description", "")))[:400],
                    "link": entry.get("link", "")
                })
        except: continue
    return articles

def generate_ai_response(messages, max_tokens=2500):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def generate_audio(text: str) -> bytes:
    clean = re.sub(r"[#*_`~>]", "", text)
    clean = re.sub(r"[\U00010000-\U0010ffff]", "", clean, flags=re.UNICODE)
    tts = gTTS(text=clean[:2500], lang="fr")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        path = tmp.name
    with open(path, "rb") as f: data = f.read()
    os.unlink(path)
    return data

def _md_to_html(text: str) -> str:
    # Conversion stylée pour le rendu Magazine
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n\n", "<br><br>")

# ═══════════════════════════════════════════════════════
#  4. APPLICATION
# ═══════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Ma Matinale Indé", page_icon="🗞️", layout="centered")
    
    # Initialisation des états pour le Chat
    if "summary_data" not in st.session_state: st.session_state.summary_data = {}
    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    inject_css()

    # Masthead Date
    today = datetime.date.today()
    date_str = today.strftime("%A %d %B %Y").upper()

    # Masthead UI
    st.markdown(f"""
    <div class="masthead">
        <h1 class="masthead-title">Ma Matinale <span>Indé</span></h1>
        <div class="masthead-date">{date_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("🎛️ Filtres")
        audio_on = st.toggle("🔊 Audio Actif", value=True)
        if st.button("🗑️ Reset Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Onglets
    tab_labels = list(TABS_CONFIG.keys())
    tabs = st.tabs(tab_labels)

    for i, tab in enumerate(tabs):
        with tab:
            tab_name = tab_labels[i]
            cfg = TABS_CONFIG[tab_name]
            inject_css(cfg["color"])
            
            # Bouton de génération
            if st.button(f"🗞️ Générer l'édition : {tab_name}", key=f"btn_{i}"):
                with st.spinner("📡 Collecte des news..."):
                    feeds = []
                    for r in cfg["regions"]:
                        for c in cfg["categories"]:
                            if c in RSS_CATALOG[r]: feeds.extend(RSS_CATALOG[r][c])
                    
                    articles = fetch_articles(tuple(feeds))
                
                if articles:
                    with st.spinner("🤖 Rédaction de votre journal détaillé..."):
                        prompt = f"Rédige un journal détaillé de 1000 mots sur : {cfg['hint']}. Structure-le avec ## Titres. Sources : " + str(articles[:MAX_ARTICLES])
                        summary = generate_ai_response([
                            {"role": "system", "content": "Tu es un rédacteur en chef indépendant. Produis un contenu riche, analytique et long."},
                            {"role": "user", "content": prompt}
                        ])
                        # On stocke par onglet pour ne pas tout perdre en changeant
                        st.session_state.summary_data[tab_name] = summary
                        st.session_state.chat_history = [] # On vide le chat car le sujet change
                else:
                    st.warning("Aucune information trouvée pour cette catégorie aujourd'hui.")

            # Affichage du résumé stocké
            current_summary = st.session_state.summary_data.get(tab_name)
            
            if current_summary:
                # Lecteur Audio
                if audio_on:
                    with st.expander("🔊 Écouter cette édition"):
                        st.audio(generate_audio(current_summary))

                # Rendu Magazine
                st.markdown(f'<div class="summary-card">{_md_to_html(current_summary)}</div>', unsafe_allow_html=True)

                # --- BOX DE DISCUSSION ---
                st.markdown("---")
                st.subheader("💬 Approfondir un sujet")
                
                # Historique
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                # Input
                if q := st.chat_input("Posez une question sur ces actualités..."):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    with st.chat_message("user"): st.write(q)

                    with st.chat_message("assistant"):
                        with st.spinner("Analyse des détails..."):
                            context = [
                                {"role": "system", "content": f"Tu es un expert. Utilise ce journal comme base : {current_summary}"},
                                *st.session_state.chat_history
                            ]
                            ans = generate_ai_response(context, max_tokens=1000)
                            st.write(ans)
                            st.session_state.chat_history.append({"role": "assistant", "content": ans})

if __name__ == "__main__":
    main()
