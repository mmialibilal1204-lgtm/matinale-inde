
# Version mise à jour de Ma Matinale Indé
# Responsive + résumés plus détaillés

import re
import os
import datetime
import tempfile

import feedparser
import streamlit as st
from groq import Groq
from gtts import gTTS

GROQ_MODEL   = "llama-3.3-70b-versatile"
HOURS_BACK   = 24
MAX_ARTICLES = 80
MAX_DISPLAY  = 60

SYSTEM_PROMPT_TEMPLATE = """Tu es le rédacteur en chef d'une grande matinale d'information indépendante, moderne et haut de gamme.

{hint}

Tu dois produire une véritable revue de presse détaillée, analytique et agréable à lire.

Le briefing doit faire ENTRE 1200 ET 1800 MOTS.

Structure IMPÉRATIVE :

# 📰 Les Grandes Informations

Développe les événements majeurs.
Explique les faits, les acteurs, les enjeux et les conséquences.
Ajoute plusieurs paragraphes détaillés.

# 🌍 Ce qu'il faut comprendre

Analyse les tendances de fond.
Fais les liens entre plusieurs actualités.
Donne du contexte géopolitique, économique ou social.

# 📊 Focus & Signaux Faibles

Ajoute davantage de news secondaires mais importantes.
Mentionne des sujets émergents.
Diversifie les régions du monde.

# ⚡ En Bref

Ajoute une liste de plusieurs informations rapides importantes.

# ✅ La Note Positive

Termine par une ou plusieurs nouvelles positives.

RÈGLES ABSOLUES :
- N'invente aucun fait.
- Utilise uniquement les informations des articles fournis.
- Style journalistique moderne, fluide et vivant.
- Fais des paragraphes aérés.
- Écris en français.
- Sois très détaillé.
"""

def inject_css(accent="#c0392b"):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --accent: {accent};
    --bg: #0d0d0f;
    --bg2: #151518;
    --bg3: #1d1d22;
    --border: #2b2b35;
    --text: #f2f2f7;
    --text-muted: #9b9baa;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: linear-gradient(to bottom, #0b0b0d, #121216);
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}}

.block-container {{
    max-width: 1200px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

.summary-card {{
    background: linear-gradient(180deg, var(--bg3), var(--bg2));
    border: 1px solid var(--border);
    border-top: 4px solid var(--accent);
    border-radius: 24px;
    padding: 2rem;
    line-height: 1.9;
    font-size: 1.05rem;
}}

.summary-card h1,
.summary-card h2 {{
    font-family: 'DM Serif Display', serif;
}}

@media (max-width: 768px) {{
    .block-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    .summary-card {{
        padding: 1.2rem;
        font-size: 0.96rem;
    }}
}}

#MainMenu,
footer,
[data-testid="stToolbar"] {{
    visibility: hidden;
}}
</style>
""", unsafe_allow_html=True)

def _md_to_html(text: str) -> str:
    text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\n", "<br>")
    return text

def build_user_prompt(articles):
    lines = [f"Voici {len(articles)} articles récents :\n"]
    for i, a in enumerate(articles[:MAX_ARTICLES], 1):
        lines.append(f"[{i}] {a['source']} — {a['title']}\n{a['summary']}\n")
    return "\n".join(lines)

def generate_summary(articles, hint):
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(hint=hint)},
            {"role": "user", "content": build_user_prompt(articles)},
        ],
        max_tokens=2500,
        temperature=0.45,
    )

    return response.choices[0].message.content.strip()

st.set_page_config(
    page_title="Ma Matinale Indé",
    page_icon="📰",
    layout="wide",
)

st.markdown(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    unsafe_allow_html=True,
)

inject_css()

st.title("📰 Ma Matinale Indé")
st.write("Version responsive améliorée avec résumés enrichis.")
