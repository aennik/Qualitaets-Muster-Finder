# Imports:
import streamlit as st
from pathlib import Path

from design import (
    apply_design,
    top_card,
    section_header,
#    page_navigation,
    sidebar_logo_bottom,
)


# Seiteneinstellungen:
st.set_page_config(
    page_title="Abschluss | Qualitätsmusterfinder",
    page_icon="🙏",
    layout="wide",
)


# Design anwenden:
apply_design()
sidebar_logo_bottom()
#page_navigation("abschluss")


# Pfade:
BASE_DIR = Path(__file__).resolve().parents[1]
IMAGE_PATH = BASE_DIR / "assets" / "schlusswort_bild.png"



# Abschluss-Seite:
# top_card(
#     title="🙏 Danke fürs Zuhören",
#     text="""
#     Das war unser Projekt <b>Krankenhausanalyse – Qualitätsmusterfinder</b>.
#     <br><br>
#     Nicole und ich haben eine interaktive Streamlit-App erstellt, um auffällige
#     Qualitätsindikatoren deutscher Krankenhäuser verständlich sichtbar zu machen.
#     """,
#     note="""
#     Ziel war nicht die Bewertung einzelner Krankenhäuser, sondern das Erkennen
#     von Mustern und Zusammenhängen innerhalb der Daten.
#     """,
# )


st.markdown("<br>", unsafe_allow_html=True)

# section_header(
#     "Abschluss",
#     "Vielen Dank für eure Aufmerksamkeit."
# )


# Illustration anzeigen:
if IMAGE_PATH.exists():
    st.image(
        str(IMAGE_PATH),
        use_container_width=True,
    )
else:
    st.warning(f"Bild nicht gefunden: {IMAGE_PATH}")


# Kurzer Abschlusstext:
st.markdown(
    """
    <div style="
        margin-top: 2rem;
        padding: 1.4rem 1.8rem;
        border-radius: 18px;
        background: rgba(7, 16, 32, 0.72);
        border: 1px solid rgba(0, 148, 220, 0.35);
        color: white;
        font-size: 1.05rem;
        line-height: 1.7;
        text-align: center;
    ">
        <b>Krankenhausanalyse – Qualitätsmusterfinder</b><br>
        Daten verstehen. Muster erkennen. Ergebnisse verständlich präsentieren.
    </div>
    """,
    unsafe_allow_html=True,
)