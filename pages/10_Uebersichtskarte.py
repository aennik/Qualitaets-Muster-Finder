# Imports:
import json
import re
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

from folium.plugins import FastMarkerCluster, MarkerCluster

from data_loader import load_all_data
from utils import prepare_analysis_df
from design import (
    apply_design,
    top_card,
    section_header,
    section_line,
    metric_card,
    interpretation_box,
    notice_box,
#    page_navigation,
    page_top_anchor,
    scroll_to_top_button,
)


# Seiteneinstellungen:
st.set_page_config(
    page_title="Übersichtskarte",
    page_icon="🗺️",
    layout="wide",
)


# Design anwenden:
apply_design()

#page_navigation("karte")
page_top_anchor()


# Daten laden:
data = load_all_data()

df = data["df_analyse"]
qi_detail = data["qi_detail"]
leistungsbereich_legende = data["leistungsbereich_legende"]
bundeslaender_geojson_path = data["bundeslaender_geojson_path"]

BASE_DIR = Path(__file__).resolve().parents[1]
LOGO_PATH = BASE_DIR / "assets" / "Transact_Hauptlogo_Farbe.png"


# Daten vorbereiten:
df = prepare_analysis_df(df)


# Spaltennamen:
LAT_COL = "SO.Latitude"
LON_COL = "SO.Longitude"
QBID_COL = "SO.QBID"
NAME_COL = "KH.Name"

BUNDESLAND_COL = "SO.Bundesland"
GEMEINDE_COL = "SO.Gemeinde"
STADTKLASSE_COL = "Stadtklasse"

TRAEGER_COL = "KH.Träger.Art"
UNI_COL = "SO.Uni"
BETTEN_COL = "SO.Betten"

AUFFAELLIG_COL = "Auffaelligkeit"
ANZAHL_AUFF_COL = "Anzahl_Auffaellig"
ANTEIL_AUFF_COL = "Anteil_Auffaellig"
ANZAHL_QI_COL = "Anzahl_QI"

FACHABTEILUNGEN_COL = "Anzahl_Fachabteilungen"
SPEZIALISIERUNG_COL = "Spezialisierungsgrad"
FORTBILDUNG_COL = "Fortbildungsquote"

FA_GRUPPEN_COL = "Fa_Fachabteilungen"



# Intro:
col_intro, col_image = st.columns([1.55, 0.75], gap='large')

with col_intro:
    top_card(
        title="🗺️ Übersichtskarte",
        text="""
        Diese Seite zeigt die Krankenhausstandorte aus dem Analysedatensatz auf einer Karte.
        <br><br>
        Über die Filter in der Seitenleiste können Standorte nach Auffälligkeit,
        Bundesland, Stadt/Gemeinde, Trägerschaft, Uni-Status, Bettenzahl,
        Fachabteilungen und Qualitätsindikatoren eingegrenzt werden.
        """,
        note="""
        Die Karte dient der räumlichen Orientierung. Sie ersetzt keine Bewertung einzelner Krankenhäuser.
        """,
    )

with col_image:
    if LOGO_PATH.exists():
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image(
            str(LOGO_PATH),
            use_container_width=True,
        )
    else:
        st.warning(f"Logo nicht gefunden: {LOGO_PATH}")


# Wichtige Spalten prüfen:
required_columns = [
    LAT_COL,
    LON_COL,
    QBID_COL,
    NAME_COL,
    BUNDESLAND_COL,
    GEMEINDE_COL,
    TRAEGER_COL,
    BETTEN_COL,
    AUFFAELLIG_COL,
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("Diese wichtigen Spalten fehlen in `df_analyse`:")
    st.write(missing_columns)

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Datentypen bereinigen:
df = df.copy()

df[QBID_COL] = df[QBID_COL].astype("string").str.strip()

df[LAT_COL] = pd.to_numeric(df[LAT_COL], errors="coerce")
df[LON_COL] = pd.to_numeric(df[LON_COL], errors="coerce")
df[BETTEN_COL] = pd.to_numeric(df[BETTEN_COL], errors="coerce").fillna(0)

for col in [
    ANZAHL_AUFF_COL,
    ANTEIL_AUFF_COL,
    ANZAHL_QI_COL,
    FACHABTEILUNGEN_COL,
    SPEZIALISIERUNG_COL,
    FORTBILDUNG_COL,
]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# Nur Standorte mit gültigen Koordinaten:
df = df.dropna(subset=[LAT_COL, LON_COL]).copy()


# Anzeige-Spalten ergänzen:
df["Auffaelligkeit_Status"] = df[AUFFAELLIG_COL].map(
    {
        0: "nicht auffällig",
        1: "auffällig",
    }
)

if UNI_COL in df.columns:
    df["Uni_Status"] = df[UNI_COL].map(
        {
            0: "keine Uni-Klinik",
            1: "Uni-Klinik",
        }
    )

    df["Uni_Status"] = df["Uni_Status"].fillna(df[UNI_COL].astype(str))


if ANTEIL_AUFF_COL in df.columns:
    df["Anteil_Auffaellig_Prozent"] = df[ANTEIL_AUFF_COL] * 100

if FORTBILDUNG_COL in df.columns:
    df["Fortbildungsquote_Prozent"] = df[FORTBILDUNG_COL] * 100


# Fachabteilungen bereinigen:
if FA_GRUPPEN_COL in df.columns:

    def entferne_sonstige(value):
        if pd.isna(value):
            return value

        fachabteilungen = [
            item.strip()
            for item in str(value).split(";")
            if "Sonstige" not in item
        ]

        return "; ".join(fachabteilungen)

    df[FA_GRUPPEN_COL] = df[FA_GRUPPEN_COL].apply(entferne_sonstige)


# QI-Detailtabelle vorbereiten:
if not qi_detail.empty:
    qi_detail = qi_detail.copy()

    if QBID_COL in qi_detail.columns:
        qi_detail[QBID_COL] = qi_detail[QBID_COL].astype("string").str.strip()

    if (
        "Leistungsbereich_Code" not in qi_detail.columns
        and "QSQI.Leistungsbereich" in qi_detail.columns
    ):
        qi_detail["Leistungsbereich_Code"] = (
            qi_detail["QSQI.Leistungsbereich"]
            .astype("string")
            .str.strip()
            .str.extract(r"^([A-ZÄÖÜ0-9]+(?:-[A-ZÄÖÜ0-9]+)*)", expand=False)
        )


# Karten-Kennzahlen nach Schema:
anzahl_standorte_mit_koordinaten = len(df)
anzahl_bundeslaender = df[BUNDESLAND_COL].dropna().nunique()
anzahl_auffaellige_standorte = int(df[AUFFAELLIG_COL].sum())
anzahl_nicht_auffaellige_standorte = int((df[AUFFAELLIG_COL] == 0).sum())

min_betten = df[BETTEN_COL].min()
max_betten = df[BETTEN_COL].max()


def format_kpi(value, decimals=0):
    if value is None or pd.isna(value):
        return "-"

    formatted = f"{value:,.{decimals}f}"

    formatted = formatted.replace(",", "X")
    formatted = formatted.replace(".", ",")
    formatted = formatted.replace("X", ".")

    return formatted


section_header(
    "Zentrale Karten-Kennzahlen",
    "Diese Kennzahlen zeigen Datenbasis und Spannweite der Standorte auf der Karte.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Standorte mit Koordinaten",
        format_kpi(anzahl_standorte_mit_koordinaten),
        "darstellbare Krankenhausstandorte",
    )

with col2:
    metric_card(
        "Bundesländer",
        format_kpi(anzahl_bundeslaender),
        "regionale Gruppen auf der Karte",
    )

with col3:
    metric_card(
        "Auffällige Standorte",
        format_kpi(anzahl_auffaellige_standorte),
        "mindestens ein auffälliger QI",
    )


# col4, col5, col6 = st.columns(3)
#
# with col4:
#     metric_card(
#         "Nicht auffällige Standorte",
#         f"{anzahl_nicht_auffaellige_standorte}",
#         "kein auffälliger QI",
#     )
#
# with col5:
#     metric_card(
#         "Min. Bettenanzahl",
#         format_metric(min_betten),
#         "kleinstes Krankenhaus auf Karte",
#     )
#
# with col6:
#     metric_card(
#         "Max. Bettenanzahl",
#         format_metric(max_betten),
#         "größtes Krankenhaus auf Karte",
#     )


# interpretation_box(
#     """
#     Diese Kennzahlen beziehen sich ausschließlich auf die Kartengrundlage.
#     Im Vordergrund stehen Anzahl, regionale Abdeckung sowie Minimum und Maximum der Bettenanzahl.
#     Damit wird sichtbar, welche Standorte räumlich darstellbar sind und welche Spannweite
#     die Krankenhausgrößen auf der Karte besitzen.
#     """
# )


# Bundesländer-Grenzen herunterladen, falls Datei fehlt:
BUNDESLAENDER_URL = (
    "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/"
    "2_bundeslaender/4_niedrig.geo.json"
)

bundeslaender_geojson_path = Path(bundeslaender_geojson_path)

if not bundeslaender_geojson_path.exists():
    try:
        bundeslaender_geojson_path.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(BUNDESLAENDER_URL, timeout=10)
        response.raise_for_status()

        bundeslaender_geojson_path.write_text(
            response.text,
            encoding="utf-8",
        )

    except Exception:
        st.warning(
            "Die Bundesländergrenzen konnten nicht automatisch geladen werden. "
            "Die Karte wird ohne Bundesländergrenzen angezeigt."
        )


# Sidebar-Filter:
st.sidebar.header("Filter")

suchtext = st.sidebar.text_input(
    "Krankenhaus suchen",
    value="",
)

kh_optionen_df = df.copy()

if suchtext.strip():
    kh_optionen_df = kh_optionen_df[
        kh_optionen_df[NAME_COL]
        .astype(str)
        .str.contains(suchtext.strip(), case=False, na=False)
    ]

selected_kh = st.sidebar.multiselect(
    "Krankenhaus auswählen",
    options=sorted(kh_optionen_df[NAME_COL].dropna().unique()),
    default=[],
)


# Fachabteilung:
if FA_GRUPPEN_COL in df.columns:
    alle_fa_gruppen = (
        df[FA_GRUPPEN_COL]
        .dropna()
        .astype(str)
        .str.split(";")
        .explode()
        .str.strip()
    )

    alle_fa_gruppen = sorted(
        alle_fa_gruppen[
            (alle_fa_gruppen.notna())
            & (alle_fa_gruppen != "")
            & (alle_fa_gruppen.str.lower() != "nan")
        ].unique()
    )

    selected_fa_gruppen = st.sidebar.multiselect(
        "Fachabteilung",
        options=alle_fa_gruppen,
        default=[],
    )
else:
    selected_fa_gruppen = []


# Auffälligkeit:
selected_auffaelligkeit = st.sidebar.multiselect(
    "Auffälligkeit",
    options=["nicht auffällig", "auffällig"],
    default=[],
)


# Bundesland:
selected_bundesland = st.sidebar.multiselect(
    "Bundesland",
    options=sorted(df[BUNDESLAND_COL].dropna().unique()),
    default=[],
)


# Stadt/Gemeinde abhängig vom Bundesland:
if selected_bundesland:
    gemeinde_basis = df[df[BUNDESLAND_COL].isin(selected_bundesland)]
else:
    gemeinde_basis = df

selected_gemeinde = st.sidebar.multiselect(
    "Stadt/Gemeinde",
    options=sorted(gemeinde_basis[GEMEINDE_COL].dropna().unique()),
    default=[],
)


# Stadtklasse:
if STADTKLASSE_COL in df.columns:
    selected_stadtklasse = st.sidebar.multiselect(
        "Stadtklasse",
        options=sorted(df[STADTKLASSE_COL].dropna().unique()),
        default=[],
    )
else:
    selected_stadtklasse = []


# Trägerart:
selected_traeger = st.sidebar.multiselect(
    "Trägerart",
    options=sorted(df[TRAEGER_COL].dropna().unique()),
    default=[],
)


# Uni-Status:
if "Uni_Status" in df.columns:
    selected_uni = st.sidebar.multiselect(
        "Uni-Status",
        options=sorted(df["Uni_Status"].dropna().unique()),
        default=[],
    )
else:
    selected_uni = []



# Qualitätsindikatoren:
# st.sidebar.markdown("---")
# st.sidebar.subheader("Qualitätsindikatoren")
#
# if not qi_detail.empty and QBID_COL in qi_detail.columns:
#     if "Leistungsbereich_Code" in qi_detail.columns:
#         selected_leistungsbereich = st.sidebar.multiselect(
#             "Leistungsbereich-Code",
#             options=sorted(qi_detail["Leistungsbereich_Code"].dropna().unique()),
#             default=[],
#         )
#     else:
#         selected_leistungsbereich = []
#
#     if "QSQI.Indikator" in qi_detail.columns:
#         selected_indikator = st.sidebar.multiselect(
#             "Auffälliger Qualitätsindikator",
#             options=sorted(qi_detail["QSQI.Indikator"].dropna().unique()),
#             default=[],
#         )
#     else:
#         selected_indikator = []
# else:
#     selected_leistungsbereich = []
#     selected_indikator = []
#     st.sidebar.info(
#         "Keine QI-Detailtabelle gefunden. Indikator-Filter sind deaktiviert."
#     )


# Wertebereiche:
st.sidebar.markdown("---")
st.sidebar.subheader("Wertebereiche")


# Bettenanzahl:
min_betten_filter = int(df[BETTEN_COL].fillna(0).min())
max_betten_filter = int(df[BETTEN_COL].fillna(0).max())

if min_betten_filter < max_betten_filter:
    selected_betten = st.sidebar.slider(
        "Bettenanzahl",
        min_value=min_betten_filter,
        max_value=max_betten_filter,
        value=(min_betten_filter, max_betten_filter),
    )
else:
    selected_betten = (min_betten_filter, max_betten_filter)
    st.sidebar.write(f"Bettenanzahl: {min_betten_filter}")


# Anzahl auffälliger QI:
if ANZAHL_AUFF_COL in df.columns:
    min_anzahl_auff = int(df[ANZAHL_AUFF_COL].fillna(0).min())
    max_anzahl_auff = int(df[ANZAHL_AUFF_COL].fillna(0).max())

    if min_anzahl_auff < max_anzahl_auff:
        selected_anzahl_auff = st.sidebar.slider(
            "Anzahl auffälliger QI",
            min_value=min_anzahl_auff,
            max_value=max_anzahl_auff,
            value=(min_anzahl_auff, max_anzahl_auff),
        )
    else:
        selected_anzahl_auff = (min_anzahl_auff, max_anzahl_auff)
else:
    selected_anzahl_auff = None
    min_anzahl_auff = None
    max_anzahl_auff = None


# Anzahl Fachabteilungen:
if FACHABTEILUNGEN_COL in df.columns:
    min_fa = int(df[FACHABTEILUNGEN_COL].fillna(0).min())
    max_fa = int(df[FACHABTEILUNGEN_COL].fillna(0).max())

    if min_fa < max_fa:
        selected_fachabteilungen = st.sidebar.slider(
            "Anzahl Fachabteilungen",
            min_value=min_fa,
            max_value=max_fa,
            value=(min_fa, max_fa),
        )
    else:
        selected_fachabteilungen = (min_fa, max_fa)
else:
    selected_fachabteilungen = None
    min_fa = None
    max_fa = None


# Filter anwenden:
filtered_df = df.copy()
aktive_filter = []


if suchtext.strip():
    filtered_df = filtered_df[
        filtered_df[NAME_COL]
        .astype(str)
        .str.contains(suchtext.strip(), case=False, na=False)
    ]

    aktive_filter.append(f"Krankenhaus-Suche: {suchtext}")


if selected_kh:
    filtered_df = filtered_df[
        filtered_df[NAME_COL].isin(selected_kh)
    ]

    aktive_filter.append("Krankenhaus")


if selected_auffaelligkeit:
    filtered_df = filtered_df[
        filtered_df["Auffaelligkeit_Status"].isin(selected_auffaelligkeit)
    ]

    aktive_filter.append("Auffälligkeit")


if selected_fa_gruppen and FA_GRUPPEN_COL in filtered_df.columns:
    pattern = "|".join(re.escape(x) for x in selected_fa_gruppen)

    filtered_df = filtered_df[
        filtered_df[FA_GRUPPEN_COL]
        .astype(str)
        .str.contains(pattern, case=False, na=False)
    ]

    aktive_filter.append("Fachabteilung")


if selected_bundesland:
    filtered_df = filtered_df[
        filtered_df[BUNDESLAND_COL].isin(selected_bundesland)
    ]

    aktive_filter.append("Bundesland")


if selected_gemeinde:
    filtered_df = filtered_df[
        filtered_df[GEMEINDE_COL].isin(selected_gemeinde)
    ]

    aktive_filter.append("Stadt/Gemeinde")


if selected_stadtklasse and STADTKLASSE_COL in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df[STADTKLASSE_COL].isin(selected_stadtklasse)
    ]

    aktive_filter.append("Stadtklasse")


if selected_traeger:
    filtered_df = filtered_df[
        filtered_df[TRAEGER_COL].isin(selected_traeger)
    ]

    aktive_filter.append("Trägerart")


if selected_uni and "Uni_Status" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Uni_Status"].isin(selected_uni)
    ]

    aktive_filter.append("Uni-Status")


if selected_betten != (min_betten_filter, max_betten_filter):
    filtered_df = filtered_df[
        filtered_df[BETTEN_COL].between(
            selected_betten[0],
            selected_betten[1],
        )
    ]

    aktive_filter.append("Bettenanzahl")


if (
    selected_anzahl_auff is not None
    and ANZAHL_AUFF_COL in filtered_df.columns
    and min_anzahl_auff is not None
    and max_anzahl_auff is not None
):
    if selected_anzahl_auff != (min_anzahl_auff, max_anzahl_auff):
        filtered_df = filtered_df[
            filtered_df[ANZAHL_AUFF_COL]
            .fillna(0)
            .between(
                selected_anzahl_auff[0],
                selected_anzahl_auff[1],
            )
        ]

        aktive_filter.append("Anzahl auffälliger QI")


if (
    selected_fachabteilungen is not None
    and FACHABTEILUNGEN_COL in filtered_df.columns
    and min_fa is not None
    and max_fa is not None
):
    if selected_fachabteilungen != (min_fa, max_fa):
        filtered_df = filtered_df[
            filtered_df[FACHABTEILUNGEN_COL]
            .fillna(0)
            .between(
                selected_fachabteilungen[0],
                selected_fachabteilungen[1],
            )
        ]

        aktive_filter.append("Anzahl Fachabteilungen")


# QI-Filter über Detailtabelle:
# if (selected_leistungsbereich or selected_indikator) and not qi_detail.empty:
# if (selected_indikator) and not qi_detail.empty:
#     qi_filter = qi_detail.copy()
#
#     if selected_leistungsbereich and "Leistungsbereich_Code" in qi_filter.columns:
#         qi_filter = qi_filter[
#             qi_filter["Leistungsbereich_Code"].isin(selected_leistungsbereich)
#         ]
#
#         aktive_filter.append("Leistungsbereich-Code")
#
#     if selected_indikator and "QSQI.Indikator" in qi_filter.columns:
#         qi_filter = qi_filter[
#             qi_filter["QSQI.Indikator"].isin(selected_indikator)
#         ]
#
#         aktive_filter.append("Qualitätsindikator")
#
#     passende_qbid = (
#         qi_filter[QBID_COL]
#         .dropna()
#         .astype("string")
#         .unique()
#     )
#
#     filtered_df = filtered_df[
#         filtered_df[QBID_COL]
#         .astype("string")
#         .isin(passende_qbid)
#     ]


# Filterstatus:
# section_line()
#
# section_header(
#     "Gefilterte Kartenansicht",
#     "Die folgenden Werte und die Karte beziehen sich auf die aktuell gesetzten Filter.",
# )
#
# if aktive_filter:
#     st.info(
#         "Aktive Filter: "
#         + ", ".join(sorted(set(aktive_filter)))
#     )
# else:
#     st.info("Keine Filter aktiv. Es werden alle Krankenhausstandorte angezeigt.")


# Gefilterte Kennzahlen:
# col1, col2, col3, col4 = st.columns(4)
#
# with col1:
#     metric_card(
#         "Gefilterte Standorte",
#         f"{len(filtered_df)}",
#         "nach aktueller Auswahl",
#     )
#
# if len(filtered_df) > 0:
#     with col2:
#         metric_card(
#             "Auffällig",
#             f"{int(filtered_df[AUFFAELLIG_COL].sum())}",
#             "gefilterte Standorte",
#         )
#
#     with col3:
#         metric_card(
#             "Nicht auffällig",
#             f"{int((filtered_df[AUFFAELLIG_COL] == 0).sum())}",
#             "gefilterte Standorte",
#         )
#
#     with col4:
#         metric_card(
#             "Max. Bettenanzahl",
#             f"{filtered_df[BETTEN_COL].max():.0f}",
#             "in gefilterter Auswahl",
#         )
# else:
#     with col2:
#         metric_card("Auffällig", "0", "gefilterte Standorte")
#
#     with col3:
#         metric_card("Nicht auffällig", "0", "gefilterte Standorte")
#
#     with col4:
#         metric_card("Max. Bettenanzahl", "-", "keine Daten")
#
#
# if filtered_df.empty:
#     st.warning("Keine Standorte für die ausgewählten Filter gefunden.")
#     st.stop()


# Karte vorbereiten:
map_df = filtered_df.dropna(subset=[LAT_COL, LON_COL]).copy()

if map_df.empty:
    st.warning("Für die ausgewählten Daten sind keine gültigen Koordinaten vorhanden.")
    st.stop()


# Performance-Schutz:
MAX_MARKER = 2000

if len(map_df) > MAX_MARKER:
    st.info(
        f"Es werden aus Performancegründen zunächst {MAX_MARKER} von {len(map_df)} "
        "Standorten auf der Karte angezeigt. Nutze Filter, um die Auswahl einzugrenzen."
    )

    map_plot_df = map_df.head(MAX_MARKER).copy()
else:
    map_plot_df = map_df.copy()


# Grundkarte:
karte = folium.Map(
    location=[51.1657, 10.4515],
    zoom_start=6,
    tiles=None,
    control_scale=True,
)

folium.TileLayer(
    tiles="OpenStreetMap",
    name="Grundkarte",
    control=False,
).add_to(karte)

karte.fit_bounds(
    [
        [47.0, 5.5],
        [55.2, 15.5],
    ]
)


# Bundesländergrenzen:
if bundeslaender_geojson_path.exists():
    with open(bundeslaender_geojson_path, "r", encoding="utf-8") as file:
        bundeslaender_geojson = json.load(file)

    if "features" in bundeslaender_geojson:
        bundeslaender_geojson["features"] = [
            feature
            for feature in bundeslaender_geojson["features"]
            if feature.get("geometry") is not None
        ]

    bundeslaender_farben = [
        "#f6d7c3",
        "#d8e8c8",
        "#d6d0eb",
        "#f8efb0",
        "#cfe8f6",
        "#f4d6e6",
        "#d9ead3",
        "#fce5cd",
        "#d0e0e3",
        "#ead1dc",
        "#fff2cc",
        "#c9daf8",
        "#d9d2e9",
        "#f9cb9c",
        "#b6d7a8",
        "#cfe2f3",
    ]

    def bundesland_name(feature):
        props = feature.get("properties", {})

        return (
            props.get("name")
            or props.get("NAME_1")
            or props.get("GEN")
            or props.get("NAME")
            or "Bundesland"
        )

    def bundesland_style(feature):
        name = bundesland_name(feature)
        farbe = bundeslaender_farben[hash(name) % len(bundeslaender_farben)]

        return {
            "fillColor": farbe,
            "color": "#6b6b6b",
            "weight": 1.1,
            "fillOpacity": 0.28,
            "opacity": 0.75,
        }

    def bundesland_highlight(feature):
        return {
            "weight": 1.8,
            "color": "#444444",
            "fillOpacity": 0.38,
        }

    folium.GeoJson(
        bundeslaender_geojson,
        name="Bundesländer",
        style_function=bundesland_style,
        highlight_function=bundesland_highlight,
    ).add_to(karte)

else:
    st.info(
        'Hinweis: Die Datei "bundeslaender.geojson" wurde nicht gefunden. '
        "Die Karte wird ohne farbige Bundesländerflächen angezeigt."
    )


# QI-Details pro Krankenhaus vorbereiten:
qi_details_by_qbid = {}

if not qi_detail.empty and QBID_COL in qi_detail.columns:
    qi_temp = qi_detail.copy()
    qi_temp[QBID_COL] = qi_temp[QBID_COL].astype("string").str.strip()

    for qbid, group in qi_temp.groupby(QBID_COL):
        indikator_liste = []
        leistungsbereich_liste = []

        if "QSQI.Indikator" in group.columns:
            indikator_liste = (
                group["QSQI.Indikator"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        if "Leistungsbereich_Code" in group.columns:
            leistungsbereich_liste = (
                group["Leistungsbereich_Code"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        qi_details_by_qbid[str(qbid)] = {
            "indikatoren": indikator_liste[:5],
            "leistungsbereiche": leistungsbereich_liste[:5],
            "anzahl": len(indikator_liste),
        }


# Marker setzen:
DETAIL_MODUS = len(aktive_filter) > 0

if not DETAIL_MODUS:
    # st.info(
    #     "Übersichtskarte: Es werden alle Krankenhausstandorte angezeigt. "
    #     "Für Detailinformationen bitte Filter setzen oder Marker anklicken."
    # )

    fast_marker_data = []

    for _, row in map_df.iterrows():
        auff = int(row.get(AUFFAELLIG_COL, 0))
        status = row.get("Auffaelligkeit_Status", "")
        name = str(row.get(NAME_COL, "Krankenhaus"))

        fast_marker_data.append(
            [
                float(row[LAT_COL]),
                float(row[LON_COL]),
                auff,
                name,
                status,
            ]
        )

    callback = """
    function (row) {
        var farbe = row[2] === 1 ? '#c0392b' : '#2e86c1';
        var radius = row[2] === 1 ? 6 : 4;

        var marker = L.circleMarker(
            new L.LatLng(row[0], row[1]),
            {
                radius: radius,
                color: farbe,
                weight: 1,
                fillColor: farbe,
                fillOpacity: 0.75
            }
        );

        marker.bindTooltip(row[3]);

        marker.bindPopup(
            '<b>' + row[3] + '</b><br>' +
            'Auffälligkeit: ' + row[4]
        );

        return marker;
    }
    """

    FastMarkerCluster(
        data=fast_marker_data,
        callback=callback,
    ).add_to(karte)

else:
    marker_cluster = MarkerCluster(
        name="Krankenhäuser",
        overlay=True,
        control=False,
    ).add_to(karte)

    for _, row in map_plot_df.iterrows():
        qbid = str(row.get(QBID_COL, "")).strip()

        name = row.get(NAME_COL, "Unbekannt")
        gemeinde = row.get(GEMEINDE_COL, "")
        bundesland = row.get(BUNDESLAND_COL, "")
        traeger = row.get(TRAEGER_COL, "")
        betten = row.get(BETTEN_COL, "")
        auff = int(row.get(AUFFAELLIG_COL, 0))
        status = row.get("Auffaelligkeit_Status", "")

        uni_status = (
            row.get("Uni_Status", "")
            if "Uni_Status" in map_plot_df.columns
            else ""
        )

        stadtklasse = (
            row.get(STADTKLASSE_COL, "")
            if STADTKLASSE_COL in map_plot_df.columns
            else ""
        )

        anzahl_auff = (
            row.get(ANZAHL_AUFF_COL, "")
            if ANZAHL_AUFF_COL in map_plot_df.columns
            else ""
        )

        anteil_auff = (
            row.get("Anteil_Auffaellig_Prozent", None)
            if "Anteil_Auffaellig_Prozent" in map_plot_df.columns
            else None
        )

        marker_color = "#c0392b" if auff == 1 else "#2e86c1"

        qi_html = ""

        if qbid in qi_details_by_qbid:
            details = qi_details_by_qbid[qbid]

            leistungsbereiche = (
                ", ".join(details["leistungsbereiche"])
                if details["leistungsbereiche"]
                else "-"
            )

            indikatoren = (
                "<br>".join([f"• {ind}" for ind in details["indikatoren"]])
                if details["indikatoren"]
                else "-"
            )

            qi_html = f"""
            <br><b>Auffällige Leistungsbereiche:</b> {leistungsbereiche}<br>
            <b>Auffällige Indikatoren:</b><br>{indikatoren}<br>
            """

        anteil_text = (
            f"{anteil_auff:.2f} %"
            if anteil_auff is not None and pd.notna(anteil_auff)
            else "-"
        )

        popup_html = f"""
        <div style="min-width:260px; font-size:13px;">
            <b>{name}</b><br>
            Gemeinde: {gemeinde}<br>
            Bundesland: {bundesland}<br>
            Stadtklasse: {stadtklasse}<br>
            Trägerschaft: {traeger}<br>
            Uni-Status: {uni_status}<br>
            Betten: {betten}<br>
            <b>Auffälligkeit: {status}</b><br>
            Anzahl auffälliger QI: {anzahl_auff}<br>
            Anteil auffälliger QI: {anteil_text}
            {qi_html}
        </div>
        """

        folium.CircleMarker(
            location=[row[LAT_COL], row[LON_COL]],
            radius=6 if auff == 1 else 4,
            color=marker_color,
            weight=1,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.78,
            popup=folium.Popup(popup_html, max_width=420),
            tooltip=str(name),
        ).add_to(marker_cluster)



# Karte anzeigen:
section_line()

section_header(
    "Karte der Krankenhausstandorte",
    "Rot markierte Standorte sind auffällig, blau markierte Standorte sind nicht auffällig.",
)

with st.expander("Karte anzeigen", expanded=True):
    components.html(
        karte.get_root().render(),
        height=780,
        scrolling=False,
    )


# Tabelle vorbereiten:
anzeige_spalten = [
    NAME_COL,
    GEMEINDE_COL,
    BUNDESLAND_COL,
    TRAEGER_COL,
    BETTEN_COL,
]

optionale_spalten = [
    "Auffaelligkeit_Status",
    "Uni_Status",
    STADTKLASSE_COL,
    ANZAHL_QI_COL,
    ANZAHL_AUFF_COL,
    "Anteil_Auffaellig_Prozent",
    FACHABTEILUNGEN_COL,
    FA_GRUPPEN_COL,
]

for spalte in optionale_spalten:
    if spalte in filtered_df.columns and spalte not in anzeige_spalten:
        anzeige_spalten.append(spalte)

anzeige_spalten = [
    spalte for spalte in anzeige_spalten
    if spalte in filtered_df.columns
]

spaltennamen_anzeige = {
    "KH.Name": "Krankenhaus",
    "SO.Gemeinde": "Gemeinde",
    "SO.Bundesland": "Bundesland",
    "KH.Träger.Art": "Trägerschaft",
    "SO.Betten": "Betten",
    "Auffaelligkeit_Status": "Auffälligkeit",
    "Uni_Status": "Uni-Status",
    "Stadtklasse": "Stadtklasse",
    "Anzahl_QI": "Anzahl QI",
    "Anzahl_Auffaellig": "Anzahl auffälliger QI",
    "Anteil_Auffaellig_Prozent": "Anteil auffälliger QI in %",
    "Anzahl_Fachabteilungen": "Anzahl Fachabteilungen",
    "FA_Gruppen": "Fachabteilungen",
}


# Gefilterte Daten anzeigen:
with st.expander("Gefilterte Daten als Tabelle anzeigen"):
    tabelle_anzeige = filtered_df[anzeige_spalten].copy()

    tabelle_anzeige = tabelle_anzeige.rename(
        columns=spaltennamen_anzeige,
    )

    st.dataframe(
        tabelle_anzeige,
        use_container_width=True,
        height=350,
        hide_index=True,
    )


# Legende anzeigen:
with st.expander("Legende der Leistungsbereich-Codes anzeigen"):
    if not leistungsbereich_legende.empty:
        legende_spalten = [
            spalte
            for spalte in [
                "Leistungsbereich_Code",
                "QSQI.Leistungsbereich",
                "Erklaerung",
            ]
            if spalte in leistungsbereich_legende.columns
        ]

        if legende_spalten:
            legende_anzeige = leistungsbereich_legende[legende_spalten].rename(
                columns={
                    "Leistungsbereich_Code": "Code",
                    "QSQI.Leistungsbereich": "Leistungsbereich",
                    "Erklaerung": "Erklärung",
                }
            )

            st.dataframe(
                legende_anzeige,
                use_container_width=True,
                height=250,
                hide_index=True,
            )
        else:
            st.dataframe(
                leistungsbereich_legende,
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Keine Legende der Leistungsbereich-Codes vorhanden.")


# Abschließender Hinweis:
notice_box(
    text="""
    Die Karte zeigt Standorte und räumliche Muster im Datensatz.
    Auffälligkeiten auf der Karte sind Hinweise auf auffällige Qualitätsindikatoren,
    aber keine direkte Bewertung einzelner Krankenhäuser.
    Für eine fachliche Einordnung sollten zusätzlich Strukturmerkmale, Fallmix,
    Versorgungsauftrag und Spezialisierung betrachtet werden.
    """,
    title="Hinweis zur Interpretation",
)

scroll_to_top_button()