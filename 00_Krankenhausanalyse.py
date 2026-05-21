# Imports:
import streamlit as st
from design import sidebar_logo_bottom

# Zentrale Navigation:
pages = {
    "App": [
        st.Page(
            "pages/01_Startseite.py",
            title="🏠 Startseite"
        ),
        st.Page(
            "pages/02_Datenuebersicht.py",
            title="📋 Datenübersicht"
        ),
    ],
    "Hypothesen": [
        st.Page(
            "pages/03_Krankenhausstruktur.py",
            title="🏥 Krankenhausstruktur"
        ),
        st.Page(
            "pages/04_Personalstruktur.py",
            title="👥 Personalstruktur"
        ),
        st.Page(
            "pages/05_Fortbildung.py",
            title="📚 Fortbildung"
        ),
        st.Page(
            "pages/06_Uni_Status.py",
            title="🎓 Universitätsstatus"
            ),
        st.Page(
            "pages/07_Traegerschaft.py",
            title="🏛️ Trägerschaft"
        ),
        st.Page(
            "pages/08_Korrelationen.py",
            title="📈 Korrelationen"
        ),
    ],
    "Regionale Muster & Karte": [
        st.Page(
            "pages/09_Regionale_Muster.py",
            title = "🗺️ Regionale Muster"
        ),
        st.Page(
            "pages/10_Uebersichtskarte.py",
            title="🗺️ Übersichtskarte"

        ),
    ],

    "Schlusswort": [
        st.Page(
            "pages/11_Schlusswort.py",
            title="🙏 Schlusswort"
        )
    ]
}


pg = st.navigation(pages)
pg.run()




