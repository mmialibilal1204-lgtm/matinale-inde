"""
╔══════════════════════════════════════════════════════╗
║          MA MATINALE INDÉ  —  v4.0                   ║
║  Design Magazine · Catalogue Complet · Chat · Audio  ║
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
#  1. CATALOGUE COMPLET (Restauré de la v2)
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
            ("Marianne", "https://www.marianne.net/feed"),
            ("Mediapart", "https://www.mediapart.fr/articles/feed"),
            ("Reporterre", "https://reporterre.net/spip.php?page=backend"),
        ],
        "Économie": [
            ("Les Échos", "https://www.lesechos.fr/rss/rss_une.xml"),
            ("Capital", "https://www.capital.fr/feed"),
        ],
        "Environnement": [
            ("Reporterre", "https://reporterre.net/spip.php?page=backend"),
            ("Vert.eco", "https://vert.eco/feed"),
        ],
    },
    "🇪🇺 Europe": {
        "Général": [
            ("Euronews FR", "https://fr.euronews.com/rss?level=theme&name=news"),
            ("The Guardian Europe", "https://www.theguardian.com/world/europe-news/rss"),
            ("Courrier International", "https://www.courrierinternational.com/feed/all/rss.xml"),
        ],
        "Politique": [("Politico Europe", "https://www.politico.eu/feed/")],
    },
    "🌍 Monde": {
        "Général": [
            ("The Guardian World", "https://www.theguardian.com/world/rss"),
            ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Reuters", "https://feeds.reuters.com/reuters/topNews"),
            ("Le Monde Diplo", "https://www.monde-diplomatique.fr/recents.atom"),
        ],
    },
    "🌍 Afrique": {
        "Général": [
            ("RFI Afrique", "https://www.rfi.fr/fr/afrique/rss"),
            ("Jeune Afrique", "https://www.jeuneafrique.com/feed/"),
            ("Le Monde Afrique", "https://www.lemonde.fr/afrique/rss_full.xml"),
        ],
    },
    "🌎 Amériques": {
        "Général": [
            ("New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
            ("The Guardian US", "https://www.theguardian.com/us-news/rss"),
        ],
    },
    "🌏 Asie & M.-Orient": {
        "Général": [
            ("BBC Asia", "https://feeds.bbci.co.uk/news/world/asia/rss.xml"),
            ("Al Jazeera ME", "https://www.aljazeera.com/xml/rss/all.xml"),
        ],
    }
}

TABS_CONFIG = {
    "🗞️ À la une": {"regions": ["🇫🇷 France", "🌍 Monde"], "categories": ["Général"], "color": "#c0392b", "icon": "🗞️", "hint": "Général France et Monde"},
    "🇫🇷 France": {"regions": ["🇫🇷 France"], "categories": ["Général", "Politique", "Économie"], "color": "#2980b9", "icon": "🇫🇷", "hint": "Focus France"},
    "🌍 Monde": {"regions": ["🌍 Monde", "🌎 Amériques", "🌏 Asie & M.-Orient"], "categories": ["Général"], "color": "#16a085", "icon": "🌍", "hint": "Focus International"},
    "⚖️ Politique": {"regions": ["🇫🇷 France", "🇪🇺 Europe"], "categories": ["Politique"], "color": "#8e44ad", "icon": "⚖️", "hint": "Analyse Politique"},
    "🌱 Environnement": {"regions": ["🇫🇷 France", "🌍 Monde"], "categories": ["Environnement"], "color": "#27ae60", "icon": "🌱", "hint": "Écologie et Climat"},
}

GROQ_MODEL = "llama-3.3-70b-versatile"
HOURS_BACK = 24
MAX_ARTICLES = 45 # Légèrement réduit pour éviter l'erreur API

# ═══════════════════════════════════════════════════════
#  2. CSS — DESIGN MAGAZINE RESPONSIVE
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
        --text-muted: #888898;
        --radius: 12px;
    }}

    /* Global */
    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }}
    .block-container {{ padding-top: 1rem !important; max-width: 900px; }}

    /* Masthead */
    .masthead {{ text-align: center; padding: 2rem 0; border-bottom: 2px solid var(--border); margin-bottom: 1.5rem; }}
    .masthead-title {{ font-family: 'DM Serif Display', serif; font-size: clamp(2.2rem, 8vw, 3.8rem); line-height: 1; }}
    .masthead-title span {{ color: var(--accent); }}
    .masthead-date {{ font-size: 0.75rem; color: var(--text-muted); letter-spacing: 3px; text-transform: uppercase; margin-top: 0.5rem; }}

    /* Résumé Card */
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
    .summary-card h2 {{ font-family: 'DM Serif Display', serif; font-size: 1.8rem; margin-top: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
    
    /* Onglets */
    [data-testid="stTabs"] [role="tab"] {{ font-size: 0.85rem !important; font-weight: 600 !important; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{ border-top: 2px solid var(--accent) !important; }}

    /* Chat Section */
    .chat-section {{ margin-top: 3rem; padding: 1.5rem; background: var(--bg2); border-radius: var(--radius); border: 1px solid var(--border); }}
    
    /* Responsive Mobile */
    @media (max-width: 768px) {{
        .summary-card {{ padding: 1.2rem; font-size: 0.98rem; }}
        .masthead-title {{ font-size: 2.4rem; }}
        .block-container {{ padding: 0.5rem !important; }}
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
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Clé API manquante dans les secrets.")
        return "Erreur : Clé API non configurée."
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Désolé, une erreur API est survenue. Vérifiez vos quotas ou la taille du texte. (Détails: {str(e)[:100]})"

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
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n\n", "<br><br>")

# ═══════════════════════════════════════════════════════
#  4. APPLICATION
# ═══════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title="Matinale Indé", page_icon="🗞️", layout="centered")
    
    if "summary" not in st.session_state: st.session_state.summary = None
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    # Header Date
    today = datetime.date.today()
    date_str = today.strftime("%A %d %B %Y").upper()

    inject_css()

    # Masthead
    st.markdown(f"""
    <div class="masthead">
        <h1 class="masthead-title">Ma Matinale <span>Indé</span></h1>
        <div class="masthead-date">{date_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # Onglets
    tab_labels = list(TABS_CONFIG.keys())
    tabs = st.tabs(tab_labels)

    for i, tab in enumerate(tabs):
        with tab:
            cfg = TABS_CONFIG[tab_labels[i]]
            inject_css(cfg["color"]) # Change la couleur d'accent selon l'onglet
            
            if st.button(f"🗞️ Générer l'édition : {tab_labels[i]}", key=f"btn_{i}"):
                with st.spinner("📡 Collecte des sources indépendantes..."):
                    feeds = []
                    for r in cfg["regions"]:
                        for c in cfg["categories"]:
                            if c in RSS_CATALOG[r]: feeds.extend(RSS_CATALOG[r][c])
                    
                    articles = fetch_articles(tuple(feeds))
                
                if articles:
                    with st.spinner("✍️ Rédaction de votre grand format (IA)..."):
                        sys_prompt = "Tu es rédacteur en chef d'un grand journal. Produis une édition détaillée, longue (800-1000 mots), avec des paragraphes riches. Utilise des ## Titres pour les sections."
                        user_prompt = f"Fais un grand journal basé sur ces articles ({cfg['hint']}) : " + str(articles[:MAX_ARTICLES])
                        
                        st.session_state.summary = generate_ai_response([
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": user_prompt}
                        ])
                        st.session_state.chat_history = [] # Reset chat
                else:
                    st.warning("Aucun article récent trouvé pour cette section.")

            # Affichage du contenu
            if st.session_state.summary:
                # Audio
                with st.expander("🔊 Écouter la matinale"):
                    audio_data = generate_audio(st.session_state.summary)
                    st.audio(audio_data)

                # Article
                st.markdown(f'<div class="summary-card">{_md_to_html(st.session_state.summary)}</div>', unsafe_allow_html=True)

                # --- CHAT INTERACTIF ---
                st.markdown('<div class="chat-section">', unsafe_allow_html=True)
                st.subheader("💬 Approfondir un sujet")
                
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                if q := st.chat_input("Une question sur ces news ?"):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    with st.chat_message("user"): st.write(q)

                    with st.chat_message("assistant"):
                        context = [{"role": "system", "content": f"Tu es un journaliste expert. Réponds en te basant sur ce journal : {st.session_state.summary}"}]
                        context.extend(st.session_state.chat_history)
                        ans = generate_ai_response(context, max_tokens=800)
                        st.write(ans)
                        st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
