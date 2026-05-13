"""
╔══════════════════════════════════════════════════════╗
║          MA MATINALE INDÉ  —  v3.0                   ║
║  Agrégateur RSS · IA Groq · Audio · Chat Interactif  ║
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
            ("Le Monde", "https://www.lemonde.fr/rss/une.xml"),
            ("Le Figaro", "https://www.lefigaro.fr/rss/figaro_actualites.xml"),
            ("Libération", "https://www.liberation.fr/arc/outboundfeeds/rss/"),
            ("France Info", "https://www.francetvinfo.fr/france.rss"),
            ("L'Obs", "https://www.nouvelobs.com/rss.xml"),
        ],
        "Politique": [
            ("L'Humanité", "https://www.humanite.fr/feed"),
            ("Mediapart", "https://www.mediapart.fr/articles/feed"),
            ("Reporterre", "https://reporterre.net/spip.php?page=backend"),
        ],
    },
    "🌍 Monde": {
        "Général": [
            ("The Guardian World", "https://www.theguardian.com/world/rss"),
            ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Le Monde Diplo", "https://www.monde-diplomatique.fr/recents.atom"),
            ("Courrier International", "https://www.courrierinternational.com/feed/all/rss.xml"),
        ],
    },
    "🇪🇺 Europe": {
        "Général": [
            ("Euronews FR", "https://fr.euronews.com/rss?level=theme&name=news"),
            ("Politico Europe", "https://www.politico.eu/feed/"),
        ],
    }
}

TABS_CONFIG = {
    "🗞️ À la une": {"regions": ["🇫🇷 France", "🌍 Monde"], "categories": ["Général"], "color": "#c0392b", "icon": "🗞️", "hint": "Tour d'horizon général."},
    "🇫🇷 France": {"regions": ["🇫🇷 France"], "categories": ["Général", "Politique"], "color": "#2980b9", "icon": "🇫🇷", "hint": "Focus France."},
    "🌍 Monde": {"regions": ["🌍 Monde"], "categories": ["Général"], "color": "#16a085", "icon": "🌍", "hint": "Focus International."},
}

GROQ_MODEL = "llama-3.3-70b-versatile"
HOURS_BACK = 24
MAX_ARTICLES = 60

# ═══════════════════════════════════════════════════════
#  2. CSS — DESIGN RÉACTIF & CHAT
# ═══════════════════════════════════════════════════════

def inject_css(accent: str = "#c0392b"):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;600&display=swap');

    :root {{
        --accent: {accent};
        --bg: #0f0f11;
        --bg2: #17171a;
        --bg3: #1e1e23;
        --border: #2a2a32;
        --text: #e8e8ee;
        --radius: 12px;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    .block-container {{ padding-top: 1rem !important; max-width: 850px; }}

    /* Masthead */
    .masthead {{ text-align: center; padding: 1.5rem 0; border-bottom: 2px solid var(--border); margin-bottom: 1.5rem; }}
    .masthead-title {{ font-family: 'DM Serif Display', serif; font-size: clamp(2rem, 8vw, 3.5rem); line-height: 1; }}
    .masthead-title span {{ color: var(--accent); }}

    /* Cards */
    .summary-card {{
        background: var(--bg3);
        border: 1px solid var(--border);
        border-top: 4px solid var(--accent);
        border-radius: var(--radius);
        padding: 2rem;
        line-height: 1.8;
        margin: 1.5rem 0;
    }}
    .summary-card h2 {{ font-family: 'DM Serif Display', serif; color: var(--text); margin-top: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}

    /* Chat Section */
    .chat-container {{
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin-top: 2rem;
    }}
    
    [data-testid="stChatMessage"] {{
        background: var(--bg3) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }}

    /* Buttons */
    .stButton > button {{
        width: 100% !important;
        background: var(--accent) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: var(--radius) !important;
        border: none !important;
        padding: 0.7rem !important;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
        .summary-card {{ padding: 1.2rem; font-size: 0.95rem; }}
        .masthead-title {{ font-size: 2.2rem; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  3. FONCTIONS CŒUR (RSS, IA, AUDIO)
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
                    "summary": strip_html(entry.get("summary", entry.get("description", "")))[:500],
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
    tts = gTTS(text=clean[:3000], lang="fr")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        path = tmp.name
    with open(path, "rb") as f: data = f.read()
    os.unlink(path)
    return data

def _md_to_html(text: str) -> str:
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n\n", "<br><br>")

# ═══════════════════════════════════════════════════════
#  4. LOGIQUE D'INTERFACE
# ═══════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Matinale Indé", page_icon="📻", layout="centered")
    
    # Initialisation des états
    if "summary" not in st.session_state: st.session_state.summary = None
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    if "articles" not in st.session_state: st.session_state.articles = []

    inject_css()

    # Masthead
    st.markdown(f'<div class="masthead"><h1 class="masthead-title">Ma Matinale <span>Indé</span></h1></div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("🎛️ Options")
        audio_on = st.toggle("Activer l'audio", value=True)
        if st.button("🗑️ Effacer la session"):
            st.session_state.summary = None
            st.session_state.chat_history = []
            st.rerun()

    # Onglets
    tab_labels = list(TABS_CONFIG.keys())
    tabs = st.tabs(tab_labels)

    for i, tab in enumerate(tabs):
        with tab:
            cfg = TABS_CONFIG[tab_labels[i]]
            
            if st.button(f"🚀 Générer mon journal — {tab_labels[i]}", key=f"gen_{i}"):
                with st.spinner("📡 Collecte des news..."):
                    # Récupération des flux
                    feeds = []
                    for r in cfg["regions"]:
                        for c in cfg["categories"]:
                            if c in RSS_CATALOG[r]: feeds.extend(RSS_CATALOG[r][c])
                    
                    articles = fetch_articles(tuple(feeds))
                    st.session_state.articles = articles
                
                if not articles:
                    st.error("Aucun article trouvé.")
                else:
                    with st.spinner("🤖 Rédaction du journal détaillé..."):
                        prompt = f"Rédige un journal détaillé de 1000 mots sur : {cfg['hint']}. Voici les sources : " + str(articles[:MAX_ARTICLES])
                        st.session_state.summary = generate_ai_response([
                            {"role": "system", "content": "Tu es un rédacteur en chef expert. Produis un contenu riche, long et structuré avec des ## Titres."},
                            {"role": "user", "content": prompt}
                        ])
                        st.session_state.chat_history = [] # Reset du chat pour ce nouveau résumé

            # Affichage du résumé
            if st.session_state.summary:
                if audio_on:
                    st.audio(generate_audio(st.session_state.summary))
                
                st.markdown(f'<div class="summary-card">{_md_to_html(st.session_state.summary)}</div>', unsafe_allow_html=True)

                # --- ZONE DE DISCUSSION ---
                st.markdown("---")
                st.subheader("💬 En savoir plus")
                st.info("Posez une question sur un sujet mentionné ci-dessus pour obtenir plus de détails.")

                # Affichage de l'historique du chat
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                # Input du chat
                if prompt := st.chat_input("Dites-m'en plus sur..."):
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Recherche de détails..."):
                            chat_context = [
                                {"role": "system", "content": f"Tu es un assistant expert. Utilise ce résumé de presse comme contexte principal : {st.session_state.summary}. Réponds de façon détaillée en t'appuyant sur les faits mentionnés."},
                                *st.session_state.chat_history
                            ]
                            response = generate_ai_response(chat_context, max_tokens=1000)
                            st.write(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
