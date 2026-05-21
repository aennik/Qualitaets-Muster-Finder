# Imports:
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
    BAR_COLOR,
    sidebar_logo_bottom,
#    page_navigation,
    page_top_anchor,
    scroll_to_top_button,
)


# Seiteneinstellungen:
st.set_page_config(
    page_title="Regionale Muster",
    page_icon="🗺️",
    layout="wide",
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("region")

# Daten laden:
data = load_all_data()
df = data["df_analyse"]


# Daten vorbereiten:
df = prepare_analysis_df(df)


# Konstanten / Spaltennamen:
BUNDESLAND_COL = "SO.Bundesland"
STADTKLASSE_COL = "Stadtklasse"
GEMEINDE_COL = "SO.Gemeinde"
QBID_COL = "SO.QBID"


# Plot-Hilfsfunktionen:
def style_plot(ax):
    """
    Einheitliches dunkles Plot-Design passend zum App-Hintergrund.
    """

    ax.set_facecolor("#0e1117")
    ax.figure.set_facecolor("#0e1117")

    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")

    for spine in ax.spines.values():
        spine.set_color("white")


def add_horizontal_labels(ax, bars, values, digits=0):
    """
    Schreibt Werte rechts neben horizontale Balken.
    """

    max_value = max(values) if len(values) > 0 else 0

    for bar in bars:
        breite = bar.get_width()
        ax.text(
            breite + max_value * 0.01 if max_value > 0 else 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{breite:.{digits}f}",
            ha="left",
            va="center",
            color="white",
            fontsize=10,
        )


def add_bar_labels(ax, bars, values, digits=1):
    """
    Schreibt Werte oberhalb der Balken.
    """

    max_value = max(values) if len(values) > 0 else 0

    for bar in bars:
        hoehe = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            hoehe + max_value * 0.02 if max_value > 0 else 0.01,
            f"{hoehe:.{digits}f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=10,
        )


def format_kpi(value, decimals=0):
    if value is None or pd.isna(value):
        return "-"

    formatted = f"{value:,.{decimals}f}"

    formatted = formatted.replace(",", "X")
    formatted = formatted.replace(".", ",")
    formatted = formatted.replace("X", ".")

    return formatted


# Intro:
top_card(
    title="🗺️ Regionale Muster",
    text="""
    Diese Seite untersucht, ob sich Auffälligkeitsmuster regional unterscheiden.
    <br><br>
    Betrachtet werden Bundesländer und, falls vorhanden, Stadtklassen. Dadurch wird sichtbar,
    ob Auffälligkeiten räumlich unterschiedlich verteilt sind oder ob bestimmte regionale
    Gruppen im Datensatz besonders stark vertreten sind.
    """,
    note="""
    Hypothese: Regionale Strukturmerkmale wie Bundesland oder Stadtklasse können mit
    unterschiedlichen Auffälligkeitsmustern zusammenhängen.
    """,
)


# Benötigte Spalte prüfen:
if BUNDESLAND_COL not in df.columns:
    st.error(
        f"Die Spalte `{BUNDESLAND_COL}` wurde im Datensatz nicht gefunden."
    )

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Daten bereinigen:
df = df.copy()

df[BUNDESLAND_COL] = (
    df[BUNDESLAND_COL]
    .astype("string")
    .str.strip()
)

df[BUNDESLAND_COL] = df[BUNDESLAND_COL].replace(
    {
        "": pd.NA,
        "nan": pd.NA,
        "None": pd.NA,
    }
)

if STADTKLASSE_COL in df.columns:
    df[STADTKLASSE_COL] = (
        df[STADTKLASSE_COL]
        .astype("string")
        .str.strip()
    )

    df[STADTKLASSE_COL] = df[STADTKLASSE_COL].replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
        }
    )

region_df = df.dropna(subset=[BUNDESLAND_COL]).copy()

if region_df.empty:
    st.warning("Für die regionale Analyse liegen keine gültigen Bundesland-Werte vor.")
    st.stop()


# Aggregation nach Bundesland:
id_col = QBID_COL if QBID_COL in region_df.columns else BUNDESLAND_COL

bundesland_agg = (
    region_df
    .groupby(BUNDESLAND_COL, as_index=False)
    .agg(
        Anzahl_Krankenhaeuser=(id_col, "nunique"),
        Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
        Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
        Durchschnitt_Anteil_Auffaellig=("Anteil_Auffaellig", "mean"),
    )
)

bundesland_agg["Anteil_Auffaelligkeit_Prozent"] = (
    bundesland_agg["Anteil_Auffaelligkeit"] * 100
).round(2)

bundesland_agg["Durchschnitt_Anteil_Auffaellig_Prozent"] = (
    bundesland_agg["Durchschnitt_Anteil_Auffaellig"] * 100
).round(2)

bundesland_agg = bundesland_agg.sort_values(
    "Anzahl_Krankenhaeuser",
    ascending=False,
)


# Region-Kennzahlen:
anzahl_bundeslaender = bundesland_agg[BUNDESLAND_COL].nunique()
anzahl_mit_bundesland = int(bundesland_agg["Anzahl_Krankenhaeuser"].sum())

groesstes_bundesland = bundesland_agg.iloc[0]
groesstes_bundesland_name = groesstes_bundesland[BUNDESLAND_COL]
groesstes_bundesland_anzahl = int(groesstes_bundesland["Anzahl_Krankenhaeuser"])

kleinstes_bundesland = bundesland_agg.sort_values("Anzahl_Krankenhaeuser").iloc[0]
kleinstes_bundesland_name = kleinstes_bundesland[BUNDESLAND_COL]
kleinstes_bundesland_anzahl = int(kleinstes_bundesland["Anzahl_Krankenhaeuser"])

min_auff_anteil_bl = bundesland_agg["Anteil_Auffaelligkeit_Prozent"].min()
max_auff_anteil_bl = bundesland_agg["Anteil_Auffaelligkeit_Prozent"].max()

if STADTKLASSE_COL in region_df.columns:
    anzahl_stadtklassen = region_df[STADTKLASSE_COL].dropna().nunique()
else:
    anzahl_stadtklassen = None


# Region-Kennzahlen anzeigen:
section_header(
    "Zentrale Regional-Kennzahlen",
    "Diese Kennzahlen zeigen die regionale Datenbasis und die Spannweite der Auffälligkeit nach Bundesland.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Bundesländer",
        format_kpi(anzahl_bundeslaender),
        "verfügbare Bundesland-Gruppen",
    )

# with col2:
#     metric_card(
#         "Mit Bundesland-Angabe",
#         format_kpi(anzahl_mit_bundesland),
#         "Krankenhäuser mit gültiger Angabe",
#     )

with col3:
    metric_card(
        "Stadtklassen",
        format_kpi(anzahl_stadtklassen),
        "verfügbare Stadtklassen",
    )


col4, col5, col6 = st.columns(3)

with col2:
    metric_card(
        "Größte Bundeslandgruppe",
        format_kpi(groesstes_bundesland_anzahl),
        str(groesstes_bundesland_name),
    )

# with col5:
#     metric_card(
#         "Min. Auffälligkeitsanteil",
#         format_kpi(min_auff_anteil_bl, 2) + " %",
#         "niedrigster Anteil nach Bundesland",
#     )
#
# with col6:
#     metric_card(
#         "Max. Auffälligkeitsanteil",
#         format_kpi(max_auff_anteil_bl, 2) + " %",
#         "höchster Anteil nach Bundesland",
#     )


interpretation_box(
    """
    Diese Kennzahlen beziehen sich ausschließlich auf regionale Merkmale.
    Im Vordergrund stehen Anzahl, Gruppengröße sowie Minimum und Maximum des
    Auffälligkeitsanteils nach Bundesland. Dadurch wird sichtbar, wie breit die
    regionale Datenbasis ist und wie stark sich Auffälligkeitsanteile räumlich unterscheiden.
    """
)


# Tabelle: Aggregation nach Bundesland:
section_line()

section_header(
    "Auswertung nach Bundesland",
    "Die Tabelle zeigt zentrale Kennzahlen je Bundesland.",
)

with st.expander("Tabelle: Kennzahlen nach Bundesland anzeigen", expanded=True):
    tabelle = bundesland_agg.copy()

    tabelle = tabelle.rename(
        columns={
            BUNDESLAND_COL: "Bundesland",
            "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            "Anzahl_Auffaellig": "Anzahl auffällig",
            "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
            "Durchschnitt_Anteil_Auffaellig_Prozent": "Ø Anteil auffälliger QI in %",
        }
    )

    anzeige_spalten = [
        "Bundesland",
        "Anzahl Krankenhäuser",
        "Anzahl auffällig",
        "Anteil auffällig in %",
        "Ø Anteil auffälliger QI in %",
    ]

    st.dataframe(
        tabelle[anzeige_spalten],
        use_container_width=True,
        hide_index=True,
    )


# Plot 1: Anzahl Krankenhäuser nach Bundesland:
section_line()

section_header(
    "Anzahl Krankenhäuser nach Bundesland",
    "Dieses Diagramm zeigt, wie stark die Bundesländer im Datensatz vertreten sind.",
)

plot_anzahl_bl = bundesland_agg.sort_values("Anzahl_Krankenhaeuser")

fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.barh(
    plot_anzahl_bl[BUNDESLAND_COL].astype(str),
    plot_anzahl_bl["Anzahl_Krankenhaeuser"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Anzahl Krankenhäuser nach Bundesland")
ax.set_xlabel("Anzahl Krankenhäuser")
ax.set_ylabel("Bundesland")

values = plot_anzahl_bl["Anzahl_Krankenhaeuser"].tolist()
add_horizontal_labels(ax, bars, values, digits=0)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Die Anzahl der Krankenhäuser je Bundesland ist wichtig für die Interpretation.
    In Bundesländern mit wenigen Krankenhäusern können einzelne auffällige Häuser den Anteil
    stärker beeinflussen als in großen Gruppen.
    """
)


# Plot 2: Anteil auffälliger Krankenhäuser nach Bundesland:
section_line()

section_header(
    "Anteil auffälliger Krankenhäuser nach Bundesland",
    "Hier wird verglichen, welcher Anteil der Krankenhäuser je Bundesland mindestens einen auffälligen Qualitätsindikator aufweist.",
)

plot_auff_bl = bundesland_agg.sort_values("Anteil_Auffaelligkeit_Prozent")

fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.barh(
    plot_auff_bl[BUNDESLAND_COL].astype(str),
    plot_auff_bl["Anteil_Auffaelligkeit_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Anteil auffälliger Krankenhäuser nach Bundesland")
ax.set_xlabel("Anteil auffälliger Krankenhäuser in %")
ax.set_ylabel("Bundesland")

values = plot_auff_bl["Anteil_Auffaelligkeit_Prozent"].tolist()
add_horizontal_labels(ax, bars, values, digits=1)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Dieses Diagramm zeigt regionale Unterschiede im Anteil auffälliger Krankenhäuser.
    Unterschiede können mit Versorgungsstruktur, Krankenhausgröße, Spezialisierung,
    Datenverfügbarkeit oder regionalen Rahmenbedingungen zusammenhängen.
    Eine direkte Qualitätsbewertung einzelner Bundesländer ist daraus nicht ableitbar.
    """
)


# Plot 3: Durchschnittlicher Anteil auffälliger QI nach Bundesland:
section_line()

section_header(
    "Durchschnittlicher Anteil auffälliger QI nach Bundesland",
    "Neben der Ja/Nein-Auffälligkeit wird betrachtet, wie hoch der durchschnittliche Anteil auffälliger Qualitätsindikatoren je Bundesland ist.",
)

plot_qi_bl = bundesland_agg.sort_values("Durchschnitt_Anteil_Auffaellig_Prozent")

fig, ax = plt.subplots(figsize=(10, 7))

bars = ax.barh(
    plot_qi_bl[BUNDESLAND_COL].astype(str),
    plot_qi_bl["Durchschnitt_Anteil_Auffaellig_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Ø Anteil auffälliger QI nach Bundesland")
ax.set_xlabel("Ø Anteil auffälliger QI in %")
ax.set_ylabel("Bundesland")

values = plot_qi_bl["Durchschnitt_Anteil_Auffaellig_Prozent"].fillna(0).tolist()
add_horizontal_labels(ax, bars, values, digits=2)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Diese Auswertung ist feiner als die reine binäre Auffälligkeit.
    Sie zeigt, ob Krankenhäuser in bestimmten Bundesländern im Durchschnitt einen höheren
    Anteil auffälliger Qualitätsindikatoren aufweisen.
    """
)


# Zusatzanalyse: Stadtklasse:
section_line()

section_header(
    "Stadtklasse und Auffälligkeit",
    "Falls verfügbar, wird zusätzlich geprüft, ob sich Auffälligkeitsmuster nach Stadtklasse unterscheiden.",
)

if STADTKLASSE_COL in region_df.columns:
    stadt_df = region_df.dropna(subset=[STADTKLASSE_COL]).copy()

    if not stadt_df.empty:
        stadt_agg = (
            stadt_df
            .groupby(STADTKLASSE_COL, as_index=False)
            .agg(
                Anzahl_Krankenhaeuser=(id_col, "nunique"),
                Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
                Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
                Durchschnitt_Anteil_Auffaellig=("Anteil_Auffaellig", "mean"),
            )
        )

        stadt_agg["Anteil_Auffaelligkeit_Prozent"] = (
            stadt_agg["Anteil_Auffaelligkeit"] * 100
        ).round(2)

        stadt_agg["Durchschnitt_Anteil_Auffaellig_Prozent"] = (
            stadt_agg["Durchschnitt_Anteil_Auffaellig"] * 100
        ).round(2)

        stadt_agg = stadt_agg.sort_values("Anteil_Auffaelligkeit_Prozent")

        with st.expander("Tabelle: Kennzahlen nach Stadtklasse anzeigen"):
            tabelle_stadt = stadt_agg.rename(
                columns={
                    STADTKLASSE_COL: "Stadtklasse",
                    "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
                    "Anzahl_Auffaellig": "Anzahl auffällig",
                    "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
                    "Durchschnitt_Anteil_Auffaellig_Prozent": "Ø Anteil auffälliger QI in %",
                }
            )

            st.dataframe(
                tabelle_stadt[
                    [
                        "Stadtklasse",
                        "Anzahl Krankenhäuser",
                        "Anzahl auffällig",
                        "Anteil auffällig in %",
                        "Ø Anteil auffälliger QI in %",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        fig, ax = plt.subplots(figsize=(10, 5.8))

        bars = ax.bar(
            stadt_agg[STADTKLASSE_COL].astype(str),
            stadt_agg["Anteil_Auffaelligkeit_Prozent"],
            color=BAR_COLOR,
        )

        style_plot(ax)

        ax.set_title("Anteil auffälliger Krankenhäuser nach Stadtklasse")
        ax.set_xlabel("Stadtklasse")
        ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")

        values = stadt_agg["Anteil_Auffaelligkeit_Prozent"].tolist()
        add_bar_labels(ax, bars, values, digits=1)

        max_y = max(values) if values else 0
        ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

        plt.tight_layout()
        st.pyplot(fig)

        interpretation_box(
            """
            Die Stadtklasse kann Hinweise darauf geben, ob Auffälligkeiten eher in städtischen, ländlichen oder 
            gemischten Versorgungsräumen auftreten. Auch hier gilt: Unterschiede zeigen Muster, 
            aber keine direkte Ursache.
            """
        )

    else:
        st.info("Für die Stadtklasse liegen keine ausreichenden gültigen Werte vor.")
else:
    st.info("Die Spalte 'Stadtklasse' ist im Datensatz nicht vorhanden.")


# Hinweis zur Karte:
section_line()

section_header(
    "Räumliche Einordnung",
    "Für die Standortperspektive ergänzt die Übersichtskarte diese regionale Analyse.",
)

notice_box(
    text="""
    Die regionale Analyse zeigt aggregierte Muster nach Bundesland und Stadtklasse.
    Für eine detailliertere räumliche Betrachtung können die Krankenhausstandorte
    zusätzlich auf der Übersichtskarte untersucht werden.
    <br><br>
    Regionale Unterschiede sollten immer gemeinsam mit Strukturmerkmalen wie Bettenzahl,
    Fachabteilungen, Trägerschaft, Uni-Status und Spezialisierung betrachtet werden.
    """,
    title="Fachliche Einordnung",
)

if st.button("Zur Übersichtskarte", key="btn_region_karte"):
    st.switch_page("pages/10_Uebersichtskarte.py")

scroll_to_top_button()