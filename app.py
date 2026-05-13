"""
Ma Matinale Indé
================
Agrégateur RSS + résumé IA (Groq/Llama3) + audio gTTS
Optimisé mobile — Streamlit Community Cloud
"""

import io
import re
import os
import datetime
import tempfile
import feedparser
import streamlit as st
from groq import Groq
from gtts import gTTS

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

RSS_FEEDS = {
    "Le Monde":     "https://www.lemonde.fr/rss/une.xml",
    "L'Humanité":   "https://www.humanite.fr/feed",
    "The Guardian": "https://www.theguardian.com/world/rss",
}

HOURS_BACK = 24
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "Tu es le rédacteur en chef d'une matinale d'information indépendante. "
    "À partir des articles fournis, crée un briefing de 300 mots "
    "divisé en 3 parties :\n"
    "1. **L'Essentiel en France**\n"
    "2. **Le Tour du Monde**\n"
    "3. **La Note Positive**\n\n"
    "Sois neutre, dynamique, et n'invente rien. "
    "Utilise uniquement les informations présentes dans les articles fournis."
)

# ──────────────────────────────────────────────
# 1. PARSING RSS
# ──────────────────────────────────────────────

def strip_html(text: str) -> str:
    """Supprime les balises HTML d'une chaîne."""
    return re.sub(r"<[^>]+>", " ", text).strip()


def fetch_articles() -> list[dict]:
    """
    Parcourt chaque flux RSS et retourne les articles
    publiés dans les dernières HOURS_BACK heures.
    """
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)
    articles = []

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Tentative de récupération de la date
                pub_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub_struct:
                    pub_dt = datetime.datetime(*pub_struct[:6], tzinfo=datetime.timezone.utc)
                    if pub_dt < cutoff:
                        continue  # Trop ancien, on passe

                title   = strip_html(entry.get("title", "")).strip()
                summary = strip_html(entry.get("summary", entry.get("description", ""))).strip()

                if title:
                    articles.append({
                        "source":  source,
                        "title":   title,
                        "summary": summary[:400],  # On tronque pour le contexte LLM
                    })
        except Exception as e:
            st.warning(f"Flux indisponible ({source}) : {e}")

    return articles


# ──────────────────────────────────────────────
# 2. GÉNÉRATION DU RÉSUMÉ VIA GROQ
# ──────────────────────────────────────────────

def build_user_prompt(articles: list[dict]) -> str:
    """Formate les articles en bloc texte pour le LLM."""
    if not articles:
        return "Aucun article disponible pour les dernières 24 heures."
    lines = [f"Voici {len(articles)} articles des dernières 24h :\n"]
    for i, art in enumerate(articles, 1):
        lines.append(f"[{i}] {art['source']} — {art['title']}\n    {art['summary']}\n")
    return "\n".join(lines)


def generate_summary(articles: list[dict]) -> str:
    """
    Envoie les articles à Groq (Llama 3 70B) et retourne le résumé.
    La clé API est lue depuis st.secrets["GROQ_API_KEY"].
    """
    api_key = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(articles)},
        ],
        max_tokens=700,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────
# 3. GÉNÉRATION AUDIO via gTTS + tempfile
# ──────────────────────────────────────────────

def generate_audio(text: str) -> bytes:
    """
    Convertit le texte en MP3 (gTTS) via un fichier temporaire.
    Compatible avec les environnements cloud sans disque permanent.
    """
    tts = gTTS(text=text, lang="fr", slow=False)

    # tempfile.NamedTemporaryFile crée un fichier temporaire sécurisé
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        tmp_path = tmp.name

    # Lecture en bytes puis suppression manuelle
    with open(tmp_path, "rb") as f:
        audio_bytes = f.read()

    os.unlink(tmp_path)  # Nettoyage explicite du fichier temporaire
    return audio_bytes


# ──────────────────────────────────────────────
# 4. INTERFACE STREAMLIT (MOBILE-FIRST)
# ──────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Ma Matinale Indé",
        page_icon="📻",
        layout="centered",   # Centré = meilleur sur mobile
    )

    # ── CSS mobile-friendly ────────────────────
    st.markdown("""
    <style>
        /* Polices */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500&display=swap');

        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

        /* Titre principal */
        h1 { font-family: 'Playfair Display', serif !important;
             font-size: 2rem !important; line-height: 1.2; }

        /* Gros bouton rouge pleine largeur */
        .stButton > button {
            width: 100% !important;
            background: #c0392b !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.85rem 1rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        .stButton > button:hover { background: #a93226 !important; }

        /* Bloc résumé */
        .summary-card {
            background: #fafafa;
            border-left: 5px solid #c0392b;
            border-radius: 0 10px 10px 0;
            padding: 1.2rem 1.4rem;
            margin-top: 0.5rem;
            font-size: 1rem;
            line-height: 1.7;
        }

        /* Badge source */
        .badge {
            display: inline-block;
            background: #eee;
            border-radius: 20px;
            padding: 2px 10px;
            font-size: 0.75rem;
            color: #555;
            margin: 2px;
        }

        /* Masquer le menu hamburger Streamlit (optionnel) */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # ── En-tête ────────────────────────────────
    st.markdown("# 📻 Ma Matinale Indé")
    today = datetime.date.today().strftime("%A %d %B %Y")
    st.caption(f"Ton briefing IA du **{today}** — 2 minutes pour tout savoir")
    st.divider()

    # ── Sources actives ─────────────────────────
    st.markdown(
        "**Sources :**  " + "  ".join(
            [f"<span class='badge'>{s}</span>" for s in RSS_FEEDS]
        ),
        unsafe_allow_html=True,
    )
    st.markdown("")  # Espace vertical

    # ── Bouton principal ────────────────────────
    if st.button("▶ Générer ma matinale"):

        # Étape 1 — Récupération RSS
        with st.spinner("📡 Lecture des flux RSS…"):
            articles = fetch_articles()

        if not articles:
            st.error(
                "Aucun article récupéré. "
                "Les flux RSS sont peut-être temporairement indisponibles."
            )
            st.stop()

        st.success(f"✅ {len(articles)} articles collectés")

        # Étape 2 — Résumé IA
        with st.spinner("🤖 Génération du résumé par Llama 3…"):
            try:
                summary = generate_summary(articles)
            except Exception as e:
                st.error(f"Erreur Groq : {e}")
                st.stop()

        # Étape 3 — Audio
        with st.spinner("🔊 Synthèse vocale en cours…"):
            try:
                audio_bytes = generate_audio(summary)
                audio_ok = True
            except Exception as e:
                st.warning(f"Audio indisponible : {e}")
                audio_ok = False

        # ── Affichage : audio EN PREMIER (priorité mobile) ──
        st.divider()
        st.markdown("### 🗞️ Ta matinale")

        if audio_ok:
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                "⬇️ Télécharger le MP3",
                data=audio_bytes,
                file_name="matinale.mp3",
                mime="audio/mpeg",
                use_container_width=True,
            )

        # ── Résumé texte ────────────────────────
        st.markdown(
            f"<div class='summary-card'>{summary.replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

        st.download_button(
            "⬇️ Télécharger le texte",
            data=summary,
            file_name="matinale.txt",
            mime="text/plain",
            use_container_width=True,
        )

        # ── Détail des articles (repliable) ─────
        with st.expander(f"📋 Voir les {len(articles)} articles sources"):
            for art in articles[:25]:
                st.markdown(f"**[{art['source']}]** {art['title']}")

    else:
        # État initial
        st.info("👆 Appuie sur le bouton pour générer ton briefing du jour.")

    # ── Pied de page ────────────────────────────
    st.divider()
    st.caption("Ma Matinale Indé · IA : Groq / Llama 3 · Voix : gTTS")


if __name__ == "__main__":
    main()
