# design.py

from pathlib import Path
import streamlit as st

# Transact-Farben:
TRANSACT_BLUE_1 = "#302683"
TRANSACT_BLUE_2 = "#009ee3"
TRANSACT_GREEN = "#008d36"
TRANSACT_YELLOW = "#dedc00"

PRIMARY_COLOR = TRANSACT_BLUE_2
SECONDARY_COLOR = TRANSACT_GREEN
ACCENT_COLOR = TRANSACT_YELLOW
DARK_ACCENT = TRANSACT_BLUE_1

# Einheitliche Plotfarbe:
BAR_COLOR = "#277c72"


# Pfade:
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "Transact_Hauptlogo_Farbe.png"


# CSS / Design:
def apply_design():
    st.markdown(
        f"""
        <style>
        /* -------------------------------------------------
           Animierter Transact-Hintergrund
        ------------------------------------------------- */
        @keyframes transactGradient {{
            0% {{
                background-position: 0% 50%;
            }}
            50% {{
                background-position: 100% 50%;
            }}
            100% {{
                background-position: 0% 50%;
            }}
        }}

        html, body, .stApp {{
            color: #ffffff;
        }}

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {{
            background: linear-gradient(
                -45deg,
                {TRANSACT_BLUE_1},
                {TRANSACT_BLUE_2},
                rgba(0, 141, 54, 0.88),
                rgba(222, 220, 0, 0.22),
                {TRANSACT_BLUE_1}
            );
            background-size: 360% 360%;
            animation: transactGradient 40s ease infinite;
            background-attachment: fixed;
            min-height: 100vh;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0);
        }}

        [data-testid="stToolbar"] {{
            right: 1rem;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(9, 18, 32, 0.74);
            backdrop-filter: blur(14px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .block-container {{
            padding-top: 3.2rem;
            padding-bottom: 3rem;
            max-width: 1380px;
        }}

        /* -------------------------------------------------
           Text und Grundelemente
        ------------------------------------------------- */
        h1, h2, h3, h4, h5, h6,
        p, span, label, div {{
            color: inherit;
        }}

        .page-kicker {{
            color: {TRANSACT_BLUE_2};
            font-size: 16px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 18px;
        }}

        /* -------------------------------------------------
           Hero-Karte
        ------------------------------------------------- */
        .top-card {{
            background: linear-gradient(
                135deg,
                rgba(13, 27, 42, 0.88),
                rgba(10, 18, 30, 0.95)
            );
            border: 1px solid rgba(0, 158, 227, 0.30);
            border-radius: 18px;
            padding: 36px 40px;
            margin-top: 20px;
            margin-bottom: 42px;
            box-shadow: 0 14px 38px rgba(0, 0, 0, 0.26);
            overflow: visible !important;
            backdrop-filter: blur(8px);
        }}

        .top-title {{
            font-size: 38px;
            font-weight: 850;
            color: #ffffff;
            margin-bottom: 18px;
            line-height: 1.25;
        }}

        .top-text {{
            font-size: 18px;
            color: #d8dee9;
            line-height: 1.75;
            max-width: 1050px;
            margin-bottom: 22px;
        }}

        .top-note {{
            font-size: 16px;
            color: {TRANSACT_BLUE_2};
            margin-top: 14px;
            line-height: 1.55;
        }}

        /* -------------------------------------------------
           Abschnitte
        ------------------------------------------------- */
        .section-line {{
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            margin: 42px 0 36px 0;
        }}

        .section-title {{
            font-size: 34px;
            font-weight: 850;
            color: #ffffff;
            margin-bottom: 12px;
            line-height: 1.25;
        }}

        .section-subtitle {{
            font-size: 18px;
            color: #d7deea;
            margin-bottom: 28px;
            line-height: 1.65;
        }}

        /* -------------------------------------------------
           Kennzahlenkarten
        ------------------------------------------------- */
        .metric-card {{
            background: rgba(13, 27, 42, 0.72);
            border: 1px solid rgba(0, 158, 227, 0.24);
            border-radius: 16px;
            padding: 28px;
            min-height: 150px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.20);
            margin-bottom: 18px;
            backdrop-filter: blur(8px);
        }}

        .metric-card:hover {{
            border-color: rgba(0, 158, 227, 0.60);
            background: rgba(18, 38, 58, 0.86);
        }}

        .metric-label {{
            font-size: 16px;
            color: #c8d3df;
            margin-bottom: 10px;
        }}

        .metric-value {{
            font-size: 42px;
            font-weight: 850;
            color: #ffffff;
            line-height: 1.15;
        }}

        .metric-note {{
            font-size: 15px;
            color: {TRANSACT_BLUE_2};
            margin-top: 10px;
            line-height: 1.45;
        }}

        /* -------------------------------------------------
           Analyse-Kacheln
        ------------------------------------------------- */
        .analysis-card {{
            background: rgba(13, 27, 42, 0.72);
            border: 1px solid rgba(0, 158, 227, 0.22);
            border-radius: 16px;
            padding: 30px 28px 24px 28px;
            min-height: 220px;
            margin-bottom: 18px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.20);
            transition: all 0.18s ease-in-out;
            backdrop-filter: blur(8px);
        }}

        .analysis-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(0, 158, 227, 0.60);
            background: rgba(18, 38, 58, 0.88);
        }}

        .analysis-title {{
            font-size: 26px;
            font-weight: 850;
            color: #ffffff;
            margin-bottom: 14px;
            line-height: 1.3;
        }}

        .analysis-text {{
            font-size: 17px;
            color: #d1d7e0;
            line-height: 1.7;
            min-height: 90px;
            margin-bottom: 20px;
        }}

        /* -------------------------------------------------
           Inhaltskarten und Hinweise
        ------------------------------------------------- */
        .content-card {{
            background: rgba(13, 27, 42, 0.68);
            border: 1px solid rgba(0, 158, 227, 0.18);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 26px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(8px);
        }}

        .interpretation-box {{
            background-color: rgba(0, 158, 227, 0.10);
            border: 1px solid rgba(0, 158, 227, 0.32);
            color: #e1f2ff;
            border-radius: 16px;
            padding: 22px 24px;
            margin-top: 20px;
            margin-bottom: 32px;
            line-height: 1.7;
            font-size: 17px;
            backdrop-filter: blur(6px);
        }}

        .notice-box {{
            background-color: rgba(222, 220, 0, 0.10);
            border: 1px solid rgba(222, 220, 0, 0.36);
            color: #fff2b8;
            border-radius: 16px;
            padding: 22px 24px;
            margin-top: 34px;
            margin-bottom: 24px;
            line-height: 1.7;
            font-size: 17px;
            backdrop-filter: blur(6px);
        }}

        /* -------------------------------------------------
           Buttons / Expander / Tabellen
        ------------------------------------------------- */
        div.stButton > button {{
            border-radius: 11px;
            border: 1px solid rgba(0, 158, 227, 0.38);
            background-color: rgba(0, 158, 227, 0.14);
            color: #ffffff;
            font-weight: 700;
            font-size: 16px;
            padding: 0.72rem 1.15rem;
            min-width: 170px;
        }}

        div.stButton > button:hover {{
            border: 1px solid rgba(0, 158, 227, 0.95);
            background-color: rgba(0, 158, 227, 0.28);
            color: white;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid rgba(0, 158, 227, 0.18);
            border-radius: 14px;
            background-color: rgba(13, 27, 42, 0.42);
            backdrop-filter: blur(8px);
        }}

        div[data-testid="stDataFrame"] {{
            background-color: rgba(13, 27, 42, 0.42);
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Wiederverwendbare Layout-Elemente:
def top_card(title, text, note=None):
    note_html = ""

    if note:
        note_html = f'<div class="top-note">{note}</div>'

    html = f"""
<div class="top-card">
    <div class="top-title">{title}</div>
    <div class="top-text">{text}</div>
    {note_html}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


def section_header(title, subtitle=None):
    subtitle_html = ""

    if subtitle:
        subtitle_html = f'<div class="section-subtitle">{subtitle}</div>'

    html = f"""
<div class="section-title">{title}</div>
{subtitle_html}
"""

    st.markdown(html, unsafe_allow_html=True)


def section_line():
    st.markdown(
        '<div class="section-line"></div>',
        unsafe_allow_html=True,
    )


def metric_card(label, value, note=None):
    note_html = ""

    if note:
        note_html = f'<div class="metric-note">{note}</div>'

    html = f"""
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
    {note_html}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


def interpretation_box(text, title="Interpretation"):
    html = f"""
<div class="interpretation-box">
    <b>{title}:</b><br>
    {text}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


def notice_box(text, title="Hinweis"):
    html = f"""
<div class="notice-box">
    <b>{title}:</b><br>
    {text}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)


# Seiten-Navigation:
NAV_PAGES = [
    {
        "key": "start",
        "label": "Startseite",
        "path": "pages/01_Startseite.py",
    },
    {
        "key": "daten",
        "label": "Datenübersicht",
        "path": "pages/02_Datenuebersicht.py",
    },
    {
        "key": "struktur",
        "label": "Strukturmerkmale",
        "path": "pages/03_Strukturmerkmale.py",
    },
    {
        "key": "personal",
        "label": "Personalstruktur",
        "path": "pages/04_Personalstruktur.py",
    },
    {
        "key": "traeger",
        "label": "Trägerschaft",
        "path": "pages/05_Traegerschaft.py",
    },
    {
        "key": "uni",
        "label": "Universitätsstatus",
        "path": "pages/06_Uni_Status.py",
    },
    {
        "key": "region",
        "label": "Regionale Muster",
        "path": "pages/07_Regionale_Muster.py",
    },
    {
        "key": "fortbildung",
        "label": "Fortbildung",
        "path": "pages/08_Fortbildung.py",
    },
    {
        "key": "korrelationen",
        "label": "Korrelationen",
        "path": "pages/09_Korrelationen.py",
    },
    {
        "key": "karte",
        "label": "Übersichtskarte",
        "path": "pages/10_Uebersichtskarte.py",
    },
    {
        "key": "schlusswort",
        "label": "Schlusswort",
        "path": "pages/11_Schlusswort.py",
    },
]


# def page_navigation(current_page_key: str):
#     """
#     Einheitliche Vorherige-/Startseite-/Nächste-Seite-Navigation.
#     current_page_key muss einem key aus NAV_PAGES entsprechen.
#     """
#
#     current_index = None
#
#     for index, page in enumerate(NAV_PAGES):
#         if page["key"] == current_page_key:
#             current_index = index
#             break
#
#     if current_index is None:
#         return
#
#     previous_page = NAV_PAGES[current_index - 1] if current_index > 0 else None
#
#     next_page = (
#         NAV_PAGES[current_index + 1]
#         if current_index < len(NAV_PAGES) - 1
#         else None
#     )
#
#     st.markdown("<br>", unsafe_allow_html=True)
#
#     col_prev, col_start, col_next = st.columns([1, 1, 1])
#
#     with col_prev:
#         if previous_page is not None:
#             if st.button(
#                 f"← {previous_page['label']}",
#                 key=f"nav_prev_{current_page_key}",
#             ):
#                 st.switch_page(previous_page["path"])
#
#     with col_start:
#         if current_page_key != "start":
#             if st.button(
#                 "🏠 Zur Startseite",
#                 key=f"nav_start_{current_page_key}",
#             ):
#                 st.switch_page("pages/01_Startseite.py")
#
#     with col_next:
#         if next_page is not None:
#             if st.button(
#                 f"{next_page['label']} →",
#                 key=f"nav_next_{current_page_key}",
#             ):
#                 st.switch_page(next_page["path"])



# Transact-Logo in der Sidebar-Navigation:
def sidebar_logo_bottom():
    # Abstand nach unten erzeugen
    st.sidebar.markdown(
        """
        <div style="height: 34vh;"></div>
        """,
        unsafe_allow_html=True,
    )

    # Logo in der Sidebar zentrieren
    col_left, col_logo, col_right = st.sidebar.columns([0.25, 1, 0.25])

    with col_logo:
        st.image(
            str(LOGO_PATH),
            width=170,
        )


# Nach-oben-Button:
def page_top_anchor():
    """
    Unsichtbarer Anker am Seitenanfang.
    Muss oben auf jeder Seite nach apply_design() eingefügt werden.
    """

    st.markdown(
        """
        <div id="seitenanfang"></div>
        """,
        unsafe_allow_html=True,
    )


def scroll_to_top_button():
    """
    Button/Link, um wieder an den Seitenanfang zu springen.
    Kann am Ende langer Seiten eingefügt werden.
    """

    st.markdown(
        """
        <style>
        .scroll-top-button {
            display: inline-block;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            padding: 0.75rem 1.25rem;
            border-radius: 14px;
            background: rgba(0, 158, 227, 0.22);
            border: 1px solid rgba(0, 158, 227, 0.75);
            color: white !important;
            text-decoration: none !important;
            font-weight: 700;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
            transition: all 0.2s ease;
        }

        .scroll-top-button:hover {
            background: rgba(0, 158, 227, 0.42);
            transform: translateY(-2px);
            border-color: white;
        }
        </style>

        <div style="text-align: center;">
            <a href="#seitenanfang" class="scroll-top-button">
                ↑ Nach oben
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


