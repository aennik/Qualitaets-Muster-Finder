# Imports:
import streamlit as st
from pathlib import Path

from design import (
    apply_design,
    top_card,
    section_header,
    section_line,
    notice_box,
#    page_navigation
)


# Seiteneinstellungen:
st.set_page_config(
    page_title='Startseite | Krankenhausanalyse',
    page_icon='🏥',
    layout='wide'
)


# Design anwenden:
apply_design()
#page_navigation("start")

# Pfade:
BASE_DIR = Path(__file__).resolve().parents[1]
IMAGE_PATH = BASE_DIR / 'assets' / 'Transact_Hauptlogo_Farbe.png'


# Startseite: Intro / Hero-Bereich:
col_intro, col_image = st.columns([1.55, 0.75], gap='large')

with col_intro:
    top_card(
        title='📊 Krankenhausanalyse – Qualitätsmusterfinder',
        text="""
        Krankenhäuser sind dazu verpflichtet, alle zwei Jahre Qualitätsberichte zu veröffentlichen. 
        Unsere Analysen wurden auf Grundlage der Berichte aus dem Jahr 2023 erstellt.
        <br><br>
        Diese App untersucht, welche Muster hinter auffälligen Qualitätsindikatoren
        deutscher Krankenhäuser stehen.
        <br><br>
        Im Fokus stehen Strukturmerkmale wie Bettenanzahl, Fachabteilungen,
        Personal, Trägerschaft, Uni-Status, Stadtgröße,
        regionale Unterschiede und Fortbildungsquote.
        <br><br>
        Ziel ist nicht die Bewertung einzelner Krankenhäuser, sondern das Sichtbarmachen
        von Zusammenhängen und Auffälligkeitsmustern innerhalb der Daten.
        """,
        note="Starte mit der Datenübersicht oder springe direkt in einen Analysebereich.",
    )

with col_image:
    if IMAGE_PATH.exists():
        st.image(str(IMAGE_PATH),
                 use_container_width=True,
                 )


# Abschnitt: Analysebereiche
section_line()

section_header(
    'Welche Muster stecken dahinter?',
    'Die Analysebereiche führen Schritt für Schritt durch Datenbasis, Zusammenhänge und räumliche Verteilung.'
)


# Analyse-Kacheln Reihe 1:
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">📋 Datenübersicht</div>
            <div class="analysis-text">
                Wie viele Krankenhäuser sind auffällig? Wie verteilen sich Qualitätsindikatoren
                und zentrale Strukturmerkmale in der Datenbasis?
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Überblick gewinnen", key="btn_daten"):
        st.switch_page("pages/02_Datenuebersicht.py")


with col2:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🏥 Struktur</div>
            <div class="analysis-text">
                Untersucht wird, ob Bettenanzahl, Fachabteilungen und Spezialisierungen
                mit Auffälligkeiten zusammenhängen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Struktur analysieren", key="btn_struktur"):
        st.switch_page("pages/03_Krankenhausstruktur.py")


with col3:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">👥 Personal</div>
            <div class="analysis-text">
                Vergleich von ärztlichem, pflegerischem und
                weiterem Personal im Hinblick auf Qualitätsauffälligkeiten.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Personal prüfen", key="btn_personal"):
        st.switch_page("pages/04_Personalstruktur.py")

# Analyse-Kacheln Reihe 2:
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🎓 Fortbildung</div>
            <div class="analysis-text">
                Prüft, ob Fortbildungsquoten und Qualifizierungen
                mit Auffälligkeitsmustern zusammenhängen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Fortbildung prüfen", key="btn_fortbildung"):
        st.switch_page("pages/05_Fortbildung.py")

with col5:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🎓 Uni-Status</div>
            <div class="analysis-text">
                Vergleicht Universitätskliniken und Nicht-Universitätskliniken
                hinsichtlich ihrer Auffälligkeitsmuster.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Uni-Status prüfen", key="btn_uni"):
        st.switch_page("pages/06_Uni_Status.py")

with col6:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🏛️ Trägerschaft</div>
            <div class="analysis-text">
                Zeigt Auffälligkeitsmuster nach öffentlicher, freigemeinnütziger
                und privater Trägerschaft.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Träger vergleichen", key="btn_traeger"):
        st.switch_page("pages/07_Traegerschaft.py")


# Analyse-Kacheln Reihe 3
# -------------------------------------------------
col7, col8, col9 = st.columns(3)

with col7:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">📈 Korrelationen</div>
            <div class="analysis-text">
                Ordnet numerische Zusammenhänge ein und trennt statistische Muster
                von vorschnellen Ursacheninterpretationen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Korrelationen ansehen", key="btn_korrelation"):
        st.switch_page("pages/08_Korrelationen.py")

with col8:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🗺️ Region</div>
            <div class="analysis-text">
                Betrachtet Unterschiede nach Bundesland und Stadtgröße,
                um regionale Muster in den Qualitätsdaten sichtbar zu machen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Region analysieren", key="btn_region"):
        st.switch_page("pages/09_Regionale_Muster.py")

with col9:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="analysis-title">🗺️ Übersichtskarte</div>
            <div class="analysis-text">
                Zeigt Krankenhausstandorte mit Filtermöglichkeiten nach Auffälligkeit,
                Eingenschaften und Qualitätsindikatoren.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Karte öffnen", key="btn_karte"):
        st.switch_page("pages/10_Uebersichtskarte.py")


# Hinweis:
notice_box(
    text="""
    Auffällige Qualitätsindikatoren sind Hinweise auf mögliche Auffälligkeiten.
    Sie bedeuten nicht automatisch, dass ein Krankenhaus eine schlechte Qualität aufweist.
    Die Ergebnisse sollten daher immer im Kontext von Struktur, Fallmix,
    Dokumentation, Spezialisierung und Versorgungsauftrag betrachtet werden.
    """,
    title='Hinweis zur Interpretation',
)


