"""
╔══════════════════════════════════════════════════════╗
║          MA MATINALE INDÉ  —  v3.3                   ║
║  Agrégateur RSS · IA Groq · Chat avec Recherche Web  ║
║  + Catalogue Massif (+250 Sources)                   ║
╚══════════════════════════════════════════════════════╝
"""

import re
import os
import random
import datetime
import tempfile
import urllib.parse

import feedparser
import streamlit as st
from groq import Groq
from gtts import gTTS

# ═══════════════════════════════════════════════════════
#  1. CATALOGUE DES FLUX RSS (Massivement Étendu)
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
            ("HuffPost FR",         "https://www.huffingtonpost.fr/rss.xml"),
            ("La Croix",            "https://www.la-croix.com/RSS/UNIVERS"),
            ("L'Obs",               "https://www.nouvelobs.com/rss.xml"),
            ("France 24 FR",        "https://www.france24.com/fr/rss"),
            ("RFI France",          "https://www.rfi.fr/fr/france/rss"),
            ("Le Point",            "https://www.lepoint.fr/flux-rss.xml"),
            ("L'Express",           "https://www.lexpress.fr/arc/outboundfeeds/rss/"),
            ("Ouest-France",        "https://www.ouest-france.fr/rss/une"),
            ("Sud Ouest",           "https://www.sudouest.fr/rss/une.xml"),
            ("Le Parisien",         "https://www.leparisien.fr/arc/outboundfeeds/rss/"),
            ("La Dépêche",          "https://www.ladepeche.fr/rss.xml"),
        ],
        "Politique": [
            ("L'Humanité",          "https://www.humanite.fr/feed"),
            ("Marianne",            "https://www.marianne.net/feed"),
            ("Politis",             "https://www.politis.fr/feed/"),
            ("Le Monde Politique",  "https://www.lemonde.fr/politique/rss_full.xml"),
            ("Mediapart",           "https://www.mediapart.fr/articles/feed"),
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
            ("Regards",             "https://regards.fr/feed/"),
            ("Basta!",              "https://bastamag.net/spip.php?page=backend"),
            ("Acrimed",             "https://www.acrimed.org/spip.php?page=backend"),
            ("Le Vent Se Lève",     "https://lvsl.fr/feed/"),
            ("Contretemps",         "https://www.contretemps.eu/feed/"),
            ("Fondation J. Jaurès", "https://www.jean-jaures.org/feed/"),
        ],
        "Économie": [
            ("Les Échos",           "https://www.lesechos.fr/rss/rss_une.xml"),
            ("Le Figaro Éco",       "https://www.lefigaro.fr/rss/figaro_economie.xml"),
            ("La Tribune",          "https://www.latribune.fr/feed.xml"),
            ("Capital",             "https://www.capital.fr/feed"),
            ("Alternatives Éco",    "https://www.alternatives-economiques.fr/rss.xml"),
            ("L'Usine Nouvelle",    "https://www.usinenouvelle.com/rss/"),
            ("BFM Business",        "https://bfmbusiness.bfmtv.com/rss/info/flux-rss/flux-toutes-les-actualites/"),
            ("Challenges",          "https://www.challenges.fr/feed/"),
            ("Investir",            "https://investir.lesechos.fr/rss/rss_une.xml"),
            ("Boursorama",          "https://www.boursorama.com/rss/actualites.xml"),
            ("L'Agefi",             "https://www.agefi.fr/feed"),
        ],
        "Santé": [
            ("Le Monde Santé",      "https://www.lemonde.fr/sante/rss_full.xml"),
            ("Pourquoi Docteur",    "https://www.pourquoidocteur.fr/feed"),
            ("Sciences et Avenir",  "https://www.sciencesetavenir.fr/sante.rss"),
            ("Santé Magazine",      "https://www.santemagazine.fr/feeds/rss"),
            ("Futura Santé",        "https://www.futura-sciences.com/rss/sante/actualites.xml"),
            ("Quotidien du Médecin","https://www.lequotidiendumedecin.fr/rss.xml"),
            ("AlloDocteurs",        "https://www.allodocteurs.fr/rss.xml"),
            ("Top Santé",           "https://www.topsante.com/feed"),
            ("Inserm",              "https://www.inserm.fr/feed/"),
            ("Vidal",               "https://www.vidal.fr/actualites/rss.xml"),
        ],
        "Culture & Société": [
            ("Télérama",            "https://www.telerama.fr/rss.xml"),
            ("Beaux Arts",          "https://www.beauxarts.com/feed/"),
            ("Slate FR",            "https://www.slate.fr/rss"),
            ("France Culture",      "https://www.radiofrance.fr/franceculture/rss"),
            ("Les Inrocks",         "https://www.lesinrocks.com/feed/"),
            ("Trois Couleurs",      "https://www.troiscouleurs.fr/feed"),
            ("Le Monde Culture",    "https://www.lemonde.fr/culture/rss_full.xml"),
            ("Numerama Pop",        "https://www.numerama.com/pop-culture/feed/"),
            ("Konbini",             "https://www.konbini.com/fr/feed/"),
            ("ActuaLitté",          "https://actualitte.com/rss/actualites.xml"),
            ("Causette",            "https://www.causette.fr/feed"),
        ],
        "Environnement": [
            ("Reporterre",          "https://reporterre.net/spip.php?page=backend"),
            ("Le Monde Planète",    "https://www.lemonde.fr/planete/rss_full.xml"),
            ("Vert.eco",            "https://vert.eco/feed"),
            ("We Demain",           "https://www.wedemain.fr/feed/"),
            ("Novethic",            "https://www.novethic.fr/feed"),
            ("Geo Environnement",   "https://www.geo.fr/environnement/rss"),
            ("Futura Planète",      "https://www.futura-sciences.com/rss/planete/actualites.xml"),
            ("Actu-Environnement",  "https://www.actu-environnement.com/flux/actu.xml"),
            ("GoodPlanet",          "https://www.goodplanet.info/feed/"),
            ("Usbek & Rica",        "https://usbeketrica.com/fr/rss"),
            ("Sciences Avenir Nat", "https://www.sciencesetavenir.fr/nature-environnement.rss"),
        ],
    },

    # ── EUROPE ──────────────────────────────────────────
    "🇪🇺 Europe": {
        "Général": [
            ("Euronews FR",         "https://fr.euronews.com/rss?level=theme&name=news"),
            ("The Guardian Europe", "https://www.theguardian.com/world/europe-news/rss"),
            ("Deutsche Welle FR",   "https://rss.dw.com/rdf/rss-fr-all"),
            ("The Independent",     "https://www.independent.co.uk/news/europe/rss"),
            ("Courrier International","https://www.courrierinternational.com/feed/all/rss.xml"),
            ("RTBF",                "https://rss.rtbf.be/article/rss/rtbf_info_homepage.xml"),
            ("RTS Info",            "https://www.rts.ch/info/rss/2022.xml"),
            ("Le Temps",            "https://www.letemps.ch/rss.xml"),
            ("Politico Europe",     "https://www.politico.eu/feed/"),
            ("El País (ES)",        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
            ("Corriere della Sera", "https://xml2.corriereobjects.it/rss/homepage.xml"),
            ("FAZ (EN)",            "https://www.faz.net/rss/aktuell/"),
            ("BBC Europe",          "https://feeds.bbci.co.uk/news/world/europe/rss.xml"),
            ("France 24 Europe",    "https://www.france24.com/fr/europe/rss"),
        ],
        "Politique": [
            ("Euractiv FR",         "https://www.euractiv.fr/feed/"),
            ("Politico Europe Pol", "https://www.politico.eu/section/politics/feed/"),
            ("The Guardian Politics","https://www.theguardian.com/politics/rss"),
            ("EUobserver",          "https://euobserver.com/rss/news"),
            ("VoxEurop",            "https://voxeurop.eu/fr/feed/"),
            ("Le Taurillon",        "https://www.taurillon.org/spip.php?page=backend"),
            ("Social Europe",       "https://socialeurope.eu/feed"),
            ("Carnegie Europe",     "https://carnegieeurope.eu/rss/"),
            ("Europarl Press",      "https://www.europarl.europa.eu/rss/doc/top-stories/en.xml"),
            ("CEPS",                "https://www.ceps.eu/feed/"),
        ],
        "Économie": [
            ("Les Échos Europe",    "https://www.lesechos.fr/rss/rss_finance_marches.xml"),
            ("Financial Times EU",  "https://www.ft.com/world/europe?format=rss"),
            ("Bloomberg Europe",    "https://feeds.bloomberg.com/markets/news.rss"),
            ("CNBC Europe",         "https://www.cnbc.com/id/19794221/device/rss/rss.html"),
            ("Reuters Europe",      "https://feeds.reuters.com/reuters/europe"),
            ("ECB Press",           "https://www.ecb.europa.eu/rss/press.html"),
            ("WSJ Europe",          "https://feeds.a.dj.com/rss/RSSWSJEurope.xml"),
            ("MarketWatch Europe",  "https://www.marketwatch.com/rss/topstories"),
            ("La Tribune Europe",   "https://www.latribune.fr/economie/union-europeenne/feed.xml"),
            ("Eurostat",            "https://ec.europa.eu/eurostat/rss/news"),
        ],
        "Environnement": [
            ("Euronews Green",      "https://fr.euronews.com/rss?level=vertical&name=green"),
            ("The Guardian Env.",   "https://www.theguardian.com/environment/rss"),
            ("Climate Home",        "https://www.climatechangenews.com/feed/"),
            ("Carbon Brief",        "https://www.carbonbrief.org/feed"),
            ("ENDS Europe",         "https://www.endseurope.com/feed"),
            ("Edie",                "https://www.edie.net/feed/"),
            ("EEA",                 "https://www.eea.europa.eu/en/newsroom/news/rss"),
            ("Greenpeace EU",       "https://www.greenpeace.org/eu-unit/feed/"),
            ("WWF EU",              "https://www.wwf.eu/?format=rss"),
            ("EEB",                 "https://eeb.org/feed/"),
        ],
    },

    # ── MONDE ───────────────────────────────────────────
    "🌍 Monde": {
        "Général": [
            ("The Guardian World",  "https://www.theguardian.com/world/rss"),
            ("BBC World",           "https://feeds.bbci.co.uk/news/world/rss.xml"),
            ("Reuters",             "https://feeds.reuters.com/reuters/topNews"),
            ("Al Jazeera EN",       "https://www.aljazeera.com/xml/rss/all.xml"),
            ("UN News",             "https://news.un.org/feed/subscribe/fr/news/all/rss.xml"),
            ("France 24 EN",        "https://www.france24.com/en/rss"),
            ("Le Monde Diplo",      "https://www.monde-diplomatique.fr/recents.atom"),
            ("AP News",             "https://newsfeed.ap.org/rss/all.xml"),
            ("CNN World",           "http://rss.cnn.com/rss/edition_world.rss"),
            ("Time",                "https://time.com/feed/"),
            ("Newsweek",            "https://www.newsweek.com/rss"),
            ("The Atlantic",        "https://www.theatlantic.com/feed/all/"),
            ("Foreign Policy",      "https://foreignpolicy.com/feed/"),
            ("The Diplomat",        "https://thediplomat.com/feed/"),
            ("RTBF Monde",          "https://rss.rtbf.be/article/rss/rtbf_info_monde.xml"),
            ("Radio Canada Monde",  "https://ici.radio-canada.ca/rss/4159"),
        ],
        "Politique": [
            ("Politico",            "https://www.politico.com/rss/politicopicks.xml"),
            ("Foreign Affairs",     "https://www.foreignaffairs.com/rss.xml"),
            ("The Atlantic Pol",    "https://www.theatlantic.com/feed/category/politics/"),
            ("Mediapart Inter.",    "https://www.mediapart.fr/articles/feed/international"),
            ("Jacobin",             "https://jacobin.com/feed/"),
            ("The Intercept",       "https://theintercept.com/feed/?lang=en"),
            ("Democracy Now!",      "https://www.democracynow.org/democracynow.rss"),
            ("Crisis Group",        "https://www.crisisgroup.org/rss/news"),
            ("CFR",                 "https://www.cfr.org/rss/publication/latest"),
            ("Brookings",           "https://www.brookings.edu/feed/"),
            ("Chatham House",       "https://www.chathamhouse.org/rss"),
        ],
        "Économie": [
            ("Financial Times",     "https://www.ft.com/?format=rss"),
            ("The Economist",       "https://www.economist.com/the-world-this-week/rss.xml"),
            ("Bloomberg",           "https://feeds.bloomberg.com/markets/news.rss"),
            ("WSJ",                 "https://feeds.a.dj.com/rss/RSSWorldNews.xml"),
            ("Forbes",              "https://www.forbes.com/real-time/feed2/"),
            ("Business Insider",    "https://www.businessinsider.com/rss"),
            ("CNBC",                "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
            ("Reuters Business",    "https://feeds.reuters.com/reuters/businessNews"),
            ("MarketWatch",         "https://www.marketwatch.com/rss/topstories"),
            ("Yahoo Finance",       "https://finance.yahoo.com/news/rssindex"),
        ],
        "Technologie": [
            ("Wired",               "https://www.wired.com/feed/rss"),
            ("The Verge",           "https://www.theverge.com/rss/index.xml"),
            ("TechCrunch",          "https://techcrunch.com/feed/"),
            ("Numerama",            "https://www.numerama.com/feed/"),
            ("MIT Tech Review",     "https://www.technologyreview.com/feed/"),
            ("Ars Technica",        "https://arstechnica.com/feed/"),
            ("Gizmodo",             "https://gizmodo.com/rss"),
            ("Engadget",            "https://www.engadget.com/rss.xml"),
            ("ZDNet",               "https://www.zdnet.com/news/rss.xml"),
            ("Mashable",            "https://mashable.com/feeds/rss/all"),
            ("VentureBeat",         "https://venturebeat.com/feed/"),
            ("CNET",                "https://www.cnet.com/rss/news/"),
            ("IEEE Spectrum",       "https://spectrum.ieee.org/rss/fullsite"),
        ],
        "Santé": [
            ("WHO News",            "https://www.who.int/rss-feeds/news-english.xml"),
            ("The Guardian Health", "https://www.theguardian.com/society/health/rss"),
            ("Science Daily",       "https://www.sciencedaily.com/rss/health_medicine.xml"),
            ("Nature Medicine",     "https://www.nature.com/nm.rss"),
            ("The Lancet",          "https://www.thelancet.com/rssfeed/lancet_current.xml"),
            ("Stat News",           "https://www.statnews.com/feed/"),
            ("WebMD",               "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC"),
            ("Medical Xpress",      "https://medicalxpress.com/rss-feed/"),
            ("NIH News",            "https://www.nih.gov/news-events/news-releases/rss.xml"),
            ("Medscape",            "https://www.medscape.com/cx/rssfeeds/2700.xml"),
        ],
    },

    # ── AFRIQUE ─────────────────────────────────────────
    "🌍 Afrique": {
        "Général": [
            ("RFI Afrique",         "https://www.rfi.fr/fr/afrique/rss"),
            ("Jeune Afrique",       "https://www.jeuneafrique.com/feed/"),
            ("Africanews",          "https://fr.africanews.com/feed/"),
            ("Le Monde Afrique",    "https://www.lemonde.fr/afrique/rss_full.xml"),
            ("Al Jazeera Africa",   "https://www.aljazeera.com/xml/rss/all.xml"),
            ("The Africa Report",   "https://www.theafricareport.com/feed/"),
            ("AllAfrica",           "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf"),
            ("BBC Africa",          "https://feeds.bbci.co.uk/news/world/africa/rss.xml"),
            ("France 24 Africa",    "https://www.france24.com/en/africa/rss"),
            ("Mail & Guardian",     "https://mg.co.za/feed/"),
            ("News24",              "https://feeds.news24.com/articles/news24/Africa/rss"),
        ],
        "Économie": [
            ("Jeune Afrique Éco",   "https://www.jeuneafrique.com/cat/economie-entreprises/feed/"),
            ("Les Afriques",        "https://www.lesafriques.com/feed/"),
            ("Financial Afrik",     "https://www.financialafrik.com/feed/"),
            ("Ecofin",              "https://www.agenceecofin.com/rss"),
            ("African Business",    "https://african.business/feed/"),
            ("La Tribune Afrique",  "https://afrique.latribune.fr/feed.xml"),
            ("Forbes Africa",       "https://www.forbesafrica.com/feed/"),
            ("Bloomberg Africa",    "https://feeds.bloomberg.com/markets/news.rss"),
            ("CNBC Africa",         "https://www.cnbcafrica.com/feed/"),
            ("Reuters Africa",      "https://feeds.reuters.com/reuters/AFRICA"),
        ],
        "Politique": [
            ("Jeune Afrique Pol.",  "https://www.jeuneafrique.com/cat/politique/feed/"),
            ("Africa Intelligence", "https://www.africaintelligence.fr/feed"),
            ("ISS Africa",          "https://issafrica.org/rss.xml"),
            ("Africa Confidential", "https://www.africa-confidential.com/rss"),
            ("WARA",                "https://www.warontherocks.com/feed/"),
            ("Conversation Africa", "https://theconversation.com/africa/articles.rss"),
            ("Premium Times",       "https://www.premiumtimesng.com/feed"),
            ("East African",        "https://www.theeastafrican.co.ke/tea/rss"),
        ],
    },

    # ── AMÉRIQUES ───────────────────────────────────────
    "🌎 Amériques": {
        "Général": [
            ("New York Times",      "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
            ("Washington Post",     "https://feeds.washingtonpost.com/rss/world"),
            ("The Guardian US",     "https://www.theguardian.com/us-news/rss"),
            ("The Intercept",       "https://theintercept.com/feed/?lang=en"),
            ("BBC Americas",        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
            ("CBC News Canada",     "https://www.cbc.ca/cmlink/rss-world"),
            ("RFI Amériques",       "https://www.rfi.fr/fr/ameriques/rss"),
            ("NPR",                 "https://feeds.npr.org/1001/rss.xml"),
            ("CNN Americas",        "http://rss.cnn.com/rss/edition_americas.rss"),
            ("AP Americas",         "https://newsfeed.ap.org/rss/all.xml"),
            ("Reuters Americas",    "https://feeds.reuters.com/reuters/USdomesticNews"),
            ("LA Times",            "https://www.latimes.com/world/rss2.0.xml"),
            ("Chicago Tribune",     "https://www.chicagotribune.com/arcio/rss/category/news/"),
        ],
        "Politique": [
            ("Politico US",         "https://www.politico.com/rss/politicopicks.xml"),
            ("The Hill",            "https://thehill.com/feed/"),
            ("Slate US",            "https://slate.com/feeds/all.rss"),
            ("HuffPost US",         "https://www.huffpost.com/section/politics/feed"),
            ("Fox News Politics",   "https://moxie.foxnews.com/google-publisher/politics.xml"),
            ("MSNBC",               "https://www.msnbc.com/feeds/latest"),
            ("Vox",                 "https://www.vox.com/rss/index.xml"),
            ("Axios",               "https://www.axios.com/feeds/feed.rss"),
            ("Mother Jones",        "https://www.motherjones.com/feed/"),
            ("The Nation",          "https://www.thenation.com/feed/"),
        ],
        "Économie": [
            ("WSJ",                 "https://feeds.a.dj.com/rss/RSSWorldNews.xml"),
            ("Forbes",              "https://www.forbes.com/real-time/feed2/"),
            ("Fortune",             "https://fortune.com/feed/"),
            ("Bloomberg US",        "https://feeds.bloomberg.com/markets/news.rss"),
            ("CNBC US",             "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
            ("Fox Business",        "https://moxie.foxbusiness.com/google-publisher/latest.xml"),
            ("MarketWatch US",      "https://www.marketwatch.com/rss/topstories"),
            ("Barron's",            "https://feeds.barrons.com/v1/articles/search?query=headline%3A%22%22&sort=time"),
            ("Yahoo Finance US",    "https://finance.yahoo.com/news/rssindex"),
            ("FT US",               "https://www.ft.com/world/us?format=rss"),
        ],
    },

    # ── ASIE & MOYEN-ORIENT ─────────────────────────────
    "🌏 Asie & M.-Orient": {
        "Général": [
            ("BBC Asia",            "https://feeds.bbci.co.uk/news/world/asia/rss.xml"),
            ("Al Jazeera ME",       "https://www.aljazeera.com/xml/rss/all.xml"),
            ("CNA Asia",            "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml"),
            ("The Hindu",           "https://www.thehindu.com/news/international/feeder/default.rss"),
            ("RFI Asie",            "https://www.rfi.fr/fr/asie-pacifique/rss"),
            ("South China Morning", "https://www.scmp.com/rss/91/feed"),
            ("The Diplomat",        "https://thediplomat.com/feed/"),
            ("Kyodo News",          "https://english.kyodonews.net/rss/news.xml"),
            ("Times of India",      "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"),
            ("Dawn",                "https://www.dawn.com/feeds/home/"),
            ("Straits Times",       "https://www.straitstimes.com/news/world/rss.xml"),
            ("Mainichi",            "https://mainichi.jp/english/rss/"),
            ("Middle East Eye",     "https://www.middleeasteye.net/rss"),
            ("Orient XXI",          "https://orientxxi.info/feed"),
            ("Arab News",           "https://www.arabnews.com/rss.xml"),
        ],
        "Économie": [
            ("Nikkei Asia",         "https://asia.nikkei.com/rss/feed/nar"),
            ("Bloomberg Asia",      "https://feeds.bloomberg.com/asia/news.rss"),
            ("CNBC Asia",           "https://www.cnbc.com/id/19832390/device/rss/rss.html"),
            ("Reuters Asia",        "https://feeds.reuters.com/reuters/businessNews"),
            ("SCMP Economy",        "https://www.scmp.com/rss/91/feed"),
            ("Business Times",      "https://www.businesstimes.com.sg/rss/news/world"),
            ("ET Asia",             "https://economictimes.indiatimes.com/news/international/rssfeeds/2884705.cms"),
            ("FT Asia",             "https://www.ft.com/world/asia-pacific?format=rss"),
            ("Caixin",              "https://www.caixinglobal.com/rss/"),
            ("WSJ Asia",            "https://feeds.a.dj.com/rss/RSSWSJAsia.xml"),
        ],
        "Politique": [
            ("Middle East Eye Pol", "https://www.middleeasteye.net/rss"),
            ("Orient XXI",          "https://orientxxi.info/feed"),
            ("Al Monitor",          "https://www.al-monitor.com/rss/all"),
            ("The Diplomat Pol",    "https://thediplomat.com/category/politics/feed/"),
            ("SCMP Politics",       "https://www.scmp.com/rss/91/feed"),
            ("Haaretz",             "https://www.haaretz.com/cmlink/1.4725302"),
            ("Times of Israel",     "https://www.timesofisrael.com/feed/"),
            ("Jerusalem Post",      "https://www.jpost.com/rss/rssfeedsfrontpage.aspx"),
            ("Dawn Politics",       "https://www.dawn.com/feeds/home/"),
        ],
    },
}

# ── ONGLETS de l'interface (thème + catégories liées) ──
TABS_CONFIG = {
    "🗞️ À la une": {
        "regions_default": ["🇫🇷 France", "🌍 Monde"],
        "categories": ["Général"],
        "prompt_hint": "Fais un tour d'horizon général de l'actualité.",
        "color":      "#c0392b",
        "icon":       "🗞️",
    },
    "⚖️ Politique": {
        "regions_default": ["🇫🇷 France", "🇪🇺 Europe", "🌍 Monde"],
        "categories": ["Politique"],
        "prompt_hint": "Analyse l'actualité politique et géopolitique.",
        "color":      "#8e44ad",
        "icon":       "⚖️",
    },
    "💶 Économie": {
        "regions_default": ["🇫🇷 France", "🌍 Monde"],
        "categories": ["Économie"],
        "prompt_hint": "Décrypte les grandes tendances économiques et financières du jour.",
        "color":      "#f39c12",
        "icon":       "💶",
    },
    "🌱 Environnement": {
        "regions_default": ["🇫🇷 France", "🌍 Monde"],
        "categories": ["Environnement"],
        "prompt_hint": "Mets en avant les enjeux environnementaux et climatiques du jour.",
        "color":      "#27ae60",
        "icon":       "🌱",
    },
    "💻 Tech & Santé": {
        "regions_default": ["🌍 Monde", "🇫🇷 France", "🌎 Amériques"],
        "categories": ["Technologie", "Santé"],
        "prompt_hint": "Passe en revue les grandes actualités technologiques, numériques et médicales.",
        "color":      "#1abc9c",
        "icon":       "💻",
    },
}

GROQ_MODEL   = "llama-3.3-70b-versatile"
HOURS_BACK   = 24
MAX_ARTICLES = 45   # Limite globale pour l'IA
MAX_PER_FEED = 3    # DIVERSITÉ MAX : 3 articles max par journal !
MAX_DISPLAY  = 40   # Limite affichage UI

SYSTEM_PROMPT_TEMPLATE = """Tu es le rédacteur en chef d'une matinale d'information indépendante, progressive et experte en analyse géopolitique et sociale.
{hint}
À partir des articles fournis, crée un grand journal détaillé, approfondi et structuré d'environ 800 à 1200 mots. 

Structure ton édition avec de vrais paragraphes étoffés :

## 🔴 À la Une (Analyse Majeure)
Détaille les 2 ou 3 faits les plus importants du jour. Ne fais pas que résumer : explique les enjeux, le contexte, et les conséquences possibles. Rédige de longs paragraphes.

## 🌍 Panorama Détaillé (National & International)
Passe en revue au moins 5 à 7 autres actualités significatives. Regroupe-les par thématiques (Politique, Économie, Société, etc.) et donne du fond à chaque information.

## 🔎 Le Décryptage
Choisis une information complexe ou technique parmi les sources fournies et explique-la en profondeur pour la rendre accessible à tous.

## ✅ L'Initiative 
Termine par 1 ou 2 nouvelles encourageantes (écologie, avancées sociales, etc.) expliquées en détail.

**Règles absolues :**
- Rédige un texte long, dense et riche en informations.
- CITE UN MAXIMUM DE JOURNAUX ET SOURCES DIFFÉRENTES parmi celles fournies pour croiser les regards.
- N'invente AUCUN fait, utilise exclusivement les sources fournies.
- Style journalistique professionnel, objectif mais captivant.
"""

# ═══════════════════════════════════════════════════════
#  2. CSS — DESIGN ÉDITORIAL MAGAZINE
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

    /* Reset global */
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

    /* Masthead */
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

    /* --- STYLE DES BULLES (st.pills) POUR LES RÉGIONS --- */
    /* On cible spécifiquement les bulles dans la zone principale (Main) */
    [data-testid="stMain"] [data-testid="stPill"] {{
        background-color: #7f1d1d !important; /* ROUGE SOMBRE (non sélectionné) */
        border: 1px solid #b91c1c !important;
        padding: 0.2rem 1rem !important;
        border-radius: 20px !important;
        transition: all 0.3s;
    }}
    [data-testid="stMain"] [data-testid="stPill"] * {{
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }}
    [data-testid="stMain"] [data-testid="stPill"][aria-selected="true"] {{
        background-color: #065f46 !important; /* VERT (sélectionné) */
        border: 1px solid #10b981 !important;
        transform: scale(1.05);
    }}
    [data-testid="stMain"] [data-testid="stPill"][aria-selected="true"] * {{
        font-weight: 700 !important;
    }}

    /* Onglets Streamlit */
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
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: var(--bg3) !important;
        color: var(--text) !important;
        border-bottom-color: var(--bg3) !important;
        border-top: 2px solid var(--accent) !important;
    }}

    /* Bouton principal */
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
        box-shadow: 0 4px 14px color-mix(in srgb, var(--accent) 40%, transparent) !important;
    }}

    /* Carte résumé */
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
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem;
    }}
    .summary-card h2:first-child {{ margin-top: 0; }}

    /* Méta-infos */
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

    /* Source badge */
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

    hr {{ border-color: var(--border) !important; }}
    [data-testid="stChatMessage"] {{ background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }}
    
    @media (min-width: 769px) {{
        .block-container {{ max-width: 900px !important; }}
        .masthead-title {{ font-size: 4rem; }}
        .summary-card {{ padding: 2.5rem 3rem; font-size: 1.05rem; line-height: 1.8; }}
    }}
    @media (max-width: 768px) {{
        .block-container {{ padding: 1rem 0.5rem !important; }}
        .masthead-title {{ font-size: 2.2rem; }}
        .summary-card {{ padding: 1.2rem; font-size: 0.95rem; }}
    }}
    #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
#  3. PARSING RSS
# ═══════════════════════════════════════════════════════

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_articles(feed_urls: tuple) -> list[dict]:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)
    all_articles = []

    for source, url in feed_urls:
        feed_articles = []
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
                    feed_articles.append({
                        "source":    source,
                        "title":     title,
                        "summary":   summary[:450],
                        "link":      entry.get("link", "")
                    })
        except Exception:
            pass
        
        # DIVERSITÉ MAX : on ne prend que les X premiers articles de ce journal précis
        all_articles.extend(feed_articles[:MAX_PER_FEED])

    # On mélange aléatoirement les articles pour une meilleure diversité
    random.shuffle(all_articles)
    return all_articles


def get_feeds_for_tab(active_regions: list,
                      tab_categories: list,
                      extra_cats: list) -> list[tuple]:
    cats = list(set(tab_categories + extra_cats))
    feeds = []
    seen  = set()
    for region in active_regions:
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
#  4. LLM — GROQ & RECHERCHE WEB
# ═══════════════════════════════════════════════════════

def build_user_prompt(articles: list[dict]) -> str:
    if not articles:
        return "Aucun article disponible."
    lines = [f"Voici {len(articles)} articles récents de sources variées :\n"]
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
        max_tokens=2500,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def generate_chat_response_with_search(summary: str, chat_history: list) -> str:
    api_key = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=api_key)

    last_question = chat_history[-1]["content"]

    keyword_prompt = f"Génère une requête de recherche Google (2 à 5 mots clés) pour trouver des informations répondant à cette question: '{last_question}'. Renvoie UNIQUEMENT les mots-clés."
    try:
        res = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": keyword_prompt}],
            max_tokens=15,
            temperature=0.1
        )
        keywords = res.choices[0].message.content.strip().replace('"', '')

        safe_query = urllib.parse.quote(keywords)
        url = f"https://news.google.com/rss/search?q={safe_query}&hl=fr&gl=FR&ceid=FR:fr"
        feed = feedparser.parse(url)

        live_news = ""
        if feed.entries:
            live_news = f"\n\nINFOS WEB DIRECT (Recherche: {keywords}):\n"
            for entry in feed.entries[:5]: 
                title = strip_html(entry.get("title", ""))
                live_news += f"- {title}\n"
    except Exception:
        live_news = ""

    sys_msg = f"Tu es un journaliste expert. Réponds à l'utilisateur avec ce journal ET les infos live du web si pertinentes.\n\nJOURNAL:\n{summary}{live_news}"

    messages = [{"role": "system", "content": sys_msg}]
    messages.extend(chat_history)

    final_res = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.4,
    )
    return final_res.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════
#  5. AUDIO — gTTS
# ═══════════════════════════════════════════════════════

def generate_audio(text: str) -> bytes:
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

def render_tab(tab_name: str, tab_cfg: dict, extra_cats: list, audio_enabled: bool):
    accent = tab_cfg["color"]
    inject_css(accent)

    # ── SÉLECTION DES RÉGIONS EN "BULLES" (PILLS) ──
    st.markdown(f"##### 🌍 Ciblez votre veille")
    
    # Utilisation de st.pills (Bulles) si disponible, sinon repli sur st.multiselect
    try:
        selected_regions = st.pills(
            f"Zones pour {tab_name.split(' ', 1)[-1]}",
            options=list(RSS_CATALOG.keys()),
            default=tab_cfg["regions_default"],
            selection_mode="multi",
            key=f"reg_select_{tab_name}",
            label_visibility="collapsed"
        )
        if selected_regions is None:
            selected_regions = []
    except AttributeError:
        selected_regions = st.multiselect(
            f"Zones pour {tab_name.split(' ', 1)[-1]} (Mettez à jour Streamlit >= 1.40 pour avoir les bulles)",
            options=list(RSS_CATALOG.keys()),
            default=tab_cfg["regions_default"],
            key=f"reg_select_{tab_name}",
            label_visibility="collapsed"
        )

    st.markdown(f"""
    <div class="meta-bar" style="margin-top:0.5rem">
        <span class="meta-chip accent">{tab_cfg['icon']} {tab_name.split(' ', 1)[-1]}</span>
        {"".join(f'<span class="meta-chip">{r.split(" ",1)[-1]}</span>' for r in selected_regions[:4])}
    </div>
    """, unsafe_allow_html=True)

    feeds = get_feeds_for_tab(selected_regions, tab_cfg["categories"], extra_cats)
    
    if not feeds:
        st.warning("Aucune source disponible pour ces régions et catégories.")
        return

    # Mémoire de l'onglet
    if tab_name not in st.session_state.app_data:
        st.session_state.app_data[tab_name] = {"summary": None, "articles": [], "chat": []}
    
    tab_state = st.session_state.app_data[tab_name]

    if st.button(f"▶ Générer la matinale — {tab_name}", key=f"btn_{tab_name}"):
        with st.spinner("📡 Lecture & croisement des flux RSS…"):
            articles = fetch_articles(tuple(feeds))

        if not articles:
            st.error("⚠️ Aucun article récupéré.")
            return

        with st.spinner("🤖 Rédaction par Llama 3.3…"):
            try:
                summary = generate_summary(articles, tab_cfg["prompt_hint"])
                tab_state["summary"] = summary
                tab_state["articles"] = articles[:MAX_ARTICLES] # Sauvegarde de la sélection finale
                tab_state["chat"] = [] 
                st.rerun()
            except Exception as e:
                st.error(f"Erreur Groq : {e}")
                return

    # ── AFFICHAGE ──
    if tab_state["summary"]:
        articles = tab_state["articles"]
        summary = tab_state["summary"]

        unique_sources = len(set(a["source"] for a in articles))

        st.markdown(f"""
        <div class="meta-bar" style="margin-top:1rem">
            <span class="meta-chip accent">✅ {len(articles)} articles utilisés</span>
            <span class="meta-chip">📰 {unique_sources} journaux différents</span>
            <span class="meta-chip">🤖 {GROQ_MODEL}</span>
        </div>
        """, unsafe_allow_html=True)

        if audio_enabled:
            with st.spinner("🔊 Synthèse vocale…"):
                try:
                    audio_bytes = generate_audio(summary)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.warning(f"Audio indisponible : {e}")

        st.markdown(f'<div class="summary-card">{_md_to_html(summary)}</div>', unsafe_allow_html=True)

        with st.expander(f"📋 {unique_sources} Sources et {len(articles)} articles croisés — cliquer pour voir"):
            for art in articles[:MAX_DISPLAY]:
                link_md = f"[{art['title']}]({art['link']})" if art["link"] else art["title"]
                st.markdown(f"<span class='src-badge'>{art['source']}</span> {link_md}", unsafe_allow_html=True)

        # ── ZONE DE DISCUSSION (CHAT & RECHERCHE) ──
        st.markdown("<hr style='margin: 3rem 0 1.5rem;' />", unsafe_allow_html=True)
        st.markdown(f"### 💬 En savoir plus")
        st.caption("Posez une question sur l'actualité. L'IA ira chercher en direct sur le web pour compléter sa réponse.")

        for msg in tab_state["chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ex: Quels sont les détails de cette nouvelle loi ?", key=f"chat_{tab_name}"):
            tab_state["chat"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Recherche d'informations récentes sur le web..."):
                    response = generate_chat_response_with_search(summary, tab_state["chat"])
                    st.markdown(response)
                    tab_state["chat"].append({"role": "assistant", "content": response})

    else:
        src_names = list(set([s for s, _ in feeds]))
        st.markdown(f"""
        <div class="summary-card" style="text-align:center; color:var(--text-muted); padding:2.5rem 1rem">
            <div style="font-size:2.5rem; margin-bottom:0.5rem">{tab_cfg['icon']}</div>
            <div style="font-family:'DM Serif Display',serif; font-size:1.1rem; color:var(--text); margin-bottom:0.5rem">
                Prêt à générer
            </div>
            <div style="font-size:0.82rem">
                Analyse prévue sur <strong>{len(feeds)} flux RSS</strong> provenant de <strong>{len(src_names)} médias</strong> distincts.<br>
                <span style="opacity: 0.7">Ex: {", ".join(src_names[:6])}{"…" if len(src_names) > 6 else ""}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _md_to_html(text: str) -> str:
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = text.replace("\n\n", "<br><br>")
    text = re.sub(r"^- (.+)$", r"• \1<br>", text, flags=re.MULTILINE)
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
    
    if "app_data" not in st.session_state:
        st.session_state.app_data = {}

    inject_css()

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
            🎛️ Paramètres
        </div>
        """, unsafe_allow_html=True)

        all_cats = sorted({cat for region in RSS_CATALOG.values() for cat in region})
        
        # Utilisation de st.pills (Bulles) si disponible pour la Sidebar aussi
        try:
            extra_cats = st.pills(
                "Thématiques globales supplémentaires",
                options=all_cats,
                default=[],
                selection_mode="multi"
            )
            if extra_cats is None: extra_cats = []
        except AttributeError:
            extra_cats = st.multiselect(
                "Thématiques globales supplémentaires",
                options=all_cats,
                default=[],
                help="S'ajoutera à toutes vos éditions",
            )

        st.markdown("---")
        audio_enabled = st.toggle("🔊 Activer l'audio (gTTS)", value=True)
        if st.button("🗑️ Vider l'historique"):
            st.session_state.app_data = {}
            st.rerun()

        st.markdown("---")
        total_feeds = sum(len(urls) for region in RSS_CATALOG.values() for urls in region.values())
        unique_media = len(set([name for region in RSS_CATALOG.values() for cat in region.values() for name, url in cat]))
        
        st.markdown(f"""
        <div style="font-size:0.78rem; color:var(--text-muted); line-height:1.8">
            <strong style="color:var(--text)">{unique_media}</strong> médias indépendants et majeurs<br>
            <strong style="color:var(--text)">{total_feeds}</strong> flux RSS scannés<br>
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
                extra_cats    = extra_cats,
                audio_enabled = audio_enabled,
            )

    # ── PIED DE PAGE ──────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-top:3rem; padding-top:1rem;
                border-top:1px solid var(--border); font-size:0.75rem;
                color:var(--text-muted); line-height:2">
        <strong style="color:var(--text)">Ma Matinale Indé</strong> · Open-source · Diversité garantie<br>
        IA : Groq / Llama 3.3 · Recherche Web Live · Sources : presse mondiale
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
