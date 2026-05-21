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
    page_title="Trägerschaft",
    page_icon="🏛️",
    layout="wide",
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("traeger")


# Daten laden:
data = load_all_data()
df = data["df_analyse"]



# Daten vorbereiten:
df = prepare_analysis_df(df)


# Konstanten / Spaltennamen:
TRAEGER_COL = "KH.Träger.Art"
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
    title="🏛️ Trägerschaft",
    text="""
    Diese Seite untersucht, ob sich Auffälligkeitsmuster nach der Trägerschaft
    der Krankenhäuser unterscheiden.
    <br><br>
    Verglichen werden öffentliche, freigemeinnützige und private Trägerarten. 
    Im Fokus steht, ob bestimmte Trägergruppen häufiger mindestens einen auffälligen Qualitätsindikator aufweisen.
    """,
    note="""
    Hypothese: Die Trägerschaft kann mit unterschiedlichen Struktur- und
    Auffälligkeitsmustern zusammenhängen.
    """,
)


# Benötigte Spalte prüfen:
if TRAEGER_COL not in df.columns:
    st.error(
        f"Die Spalte `{TRAEGER_COL}` wurde im Datensatz nicht gefunden."
    )

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Daten bereinigen:
df = df.copy()

df[TRAEGER_COL] = (
    df[TRAEGER_COL]
    .astype("string")
    .str.strip()
)

df[TRAEGER_COL] = df[TRAEGER_COL].replace(
    {
        "": pd.NA,
        "nan": pd.NA,
        "None": pd.NA,
    }
)

traeger_df = df.dropna(subset=[TRAEGER_COL]).copy()


# Aggregation nach Trägerschaft:
id_col = QBID_COL if QBID_COL in traeger_df.columns else TRAEGER_COL

if traeger_df.empty:
    st.warning("Für die Trägerschaft liegen keine gültigen Werte vor.")
    st.stop()


traeger_agg = (
    traeger_df
    .groupby(TRAEGER_COL, as_index=False)
    .agg(
        Anzahl_Krankenhaeuser=(id_col, "nunique"),
        Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
        Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
        Durchschnitt_Anteil_Auffaellig=("Anteil_Auffaellig", "mean"),
    )
)

traeger_agg["Anteil_Auffaelligkeit_Prozent"] = (
    traeger_agg["Anteil_Auffaelligkeit"] * 100
).round(2)

traeger_agg["Durchschnitt_Anteil_Auffaellig_Prozent"] = (
    traeger_agg["Durchschnitt_Anteil_Auffaellig"] * 100
).round(2)

traeger_agg = traeger_agg.sort_values(
    "Anzahl_Krankenhaeuser",
    ascending=False,
)


# Trägerschaft-Kennzahlen:
anzahl_traegerarten = traeger_agg[TRAEGER_COL].nunique()
anzahl_mit_traegerangabe = int(traeger_agg["Anzahl_Krankenhaeuser"].sum())

groesste_gruppe_name = traeger_agg.iloc[0][TRAEGER_COL]
groesste_gruppe_anzahl = int(traeger_agg.iloc[0]["Anzahl_Krankenhaeuser"])

kleinste_gruppe = traeger_agg.sort_values("Anzahl_Krankenhaeuser").iloc[0]
kleinste_gruppe_name = kleinste_gruppe[TRAEGER_COL]
kleinste_gruppe_anzahl = int(kleinste_gruppe["Anzahl_Krankenhaeuser"])

min_auff_anteil = traeger_agg["Anteil_Auffaelligkeit_Prozent"].min()
max_auff_anteil = traeger_agg["Anteil_Auffaelligkeit_Prozent"].max()


# Trägerschaft-Kennzahlen anzeigen:
section_header(
    "Zentrale Trägerschafts-Kennzahlen",
    "Diese Kennzahlen zeigen die Datenbasis und Spannweite der Trägergruppen.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Trägerarten",
        format_kpi(anzahl_traegerarten),
        "verfügbare Trägergruppen",
    )

with col2:
    metric_card(
        "Mit Trägerangabe",
        format_kpi(anzahl_mit_traegerangabe),
        "Krankenhäuser mit gültiger Angabe",
    )

with col3:
    metric_card(
        "Kleinste Trägergruppe",
        format_kpi(kleinste_gruppe_anzahl),
        str(kleinste_gruppe_name),
    )


col4, col5, col6 = st.columns(3)
with col4:
    metric_card(
        "Größte Trägergruppe",
        format_kpi(groesste_gruppe_anzahl),
        str(groesste_gruppe_name),
    )


# with col5:
#     metric_card(
#         "Min. Auffälligkeitsanteil",
#         format_kpi(min_auff_anteil, 2) + " %",
#         "niedrigster Anteil nach Trägerart",
#     )
#
# with col6:
#     metric_card(
#         "Max. Auffälligkeitsanteil",
#         format_kpi(max_auff_anteil, 2) + " %",
#         "höchster Anteil nach Trägerart",
#     )


interpretation_box(
    """
    Diese Kennzahlen beziehen sich ausschließlich auf die Trägerschaft.
    Im Vordergrund stehen Anzahl, Gruppengröße sowie Minimum und Maximum des
    Auffälligkeitsanteils nach Trägerart. Dadurch wird sichtbar, wie breit die
    Trägergruppen im Datensatz vertreten sind und wie stark die Auffälligkeitsanteile
    zwischen ihnen variieren.
    """
)


# Tabelle: Aggregation nach Trägerschaft:
section_line()

section_header(
    "Auswertung nach Trägerschaft",
    "Die Tabelle zeigt zentrale Kennzahlen je Trägerart.",
)

with st.expander("Tabelle: Kennzahlen nach Trägerschaft anzeigen", expanded=True):
    tabelle = traeger_agg.copy()

    tabelle = tabelle.rename(
        columns={
            TRAEGER_COL: "Trägerschaft",
            "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            "Anzahl_Auffaellig": "Anzahl auffällig",
            "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
            "Durchschnitt_Anteil_Auffaellig_Prozent": "Ø Anteil auffälliger QI in %",
        }
    )

    anzeige_spalten = [
        "Trägerschaft",
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


# Plot 1: Anzahl Krankenhäuser nach Trägerschaft:
section_line()

section_header(
    "Anzahl Krankenhäuser nach Trägerschaft",
    "Dieses Balkendiagramm zeigt, wie stark die einzelnen Trägerarten im Datensatz vertreten sind.",
)

plot_anzahl = traeger_agg.sort_values("Anzahl_Krankenhaeuser")

fig, ax = plt.subplots(figsize=(10, 5.8))

bars = ax.barh(
    plot_anzahl[TRAEGER_COL].astype(str),
    plot_anzahl["Anzahl_Krankenhaeuser"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Anzahl Krankenhäuser nach Trägerschaft")
ax.set_xlabel("Anzahl Krankenhäuser")
ax.set_ylabel("Trägerschaft")

values = plot_anzahl["Anzahl_Krankenhaeuser"].tolist()
add_horizontal_labels(ax, bars, values, digits=0)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Die Verteilung der Krankenhäuser nach Trägerschaft ist wichtig für die spätere Interpretation. 
    Wenn eine Trägergruppe deutlich größer ist als andere, können ihre Muster im Gesamtdatensatz 
    stärker ins Gewicht fallen.
    """
)


# Plot 2: Anteil auffälliger Krankenhäuser nach Trägerschaft:
section_line()

section_header(
    "Anteil auffälliger Krankenhäuser nach Trägerschaft",
    "Hier wird verglichen, welcher Anteil der Krankenhäuser je Trägerart mindestens einen auffälligen Qualitätsindikator aufweist.",
)

plot_auff = traeger_agg.sort_values("Anteil_Auffaelligkeit_Prozent")

fig, ax = plt.subplots(figsize=(10, 5.8))

bars = ax.barh(
    plot_auff[TRAEGER_COL].astype(str),
    plot_auff["Anteil_Auffaelligkeit_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Anteil auffälliger Krankenhäuser nach Trägerschaft")
ax.set_xlabel("Anteil auffälliger Krankenhäuser in %")
ax.set_ylabel("Trägerschaft")

values = plot_auff["Anteil_Auffaelligkeit_Prozent"].tolist()
add_horizontal_labels(ax, bars, values, digits=1)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Dieses Balkendiagramm prüft die zentrale Trägerschafts-Hypothese.
    Unterschiede zwischen Trägerarten können auf unterschiedliche Versorgungsaufträge,
    Krankenhausgrößen, Spezialisierungen oder Dokumentationsstrukturen hinweisen.
    Eine höhere Auffälligkeit bedeutet jedoch nicht automatisch eine schlechtere Qualität.
    """
)


# Plot 3: Durchschnittlicher Anteil auffälliger QI nach Trägerschaft:
section_line()

section_header(
    "Durchschnittlicher Anteil auffälliger QI nach Trägerschaft",
    "Neben der Ja/Nein-Auffälligkeit wird betrachtet, wie hoch der durchschnittliche Anteil auffälliger Qualitätsindikatoren je Trägerart ist.",
)

plot_qi = traeger_agg.sort_values("Durchschnitt_Anteil_Auffaellig_Prozent")

fig, ax = plt.subplots(figsize=(10, 5.8))

bars = ax.barh(
    plot_qi[TRAEGER_COL].astype(str),
    plot_qi["Durchschnitt_Anteil_Auffaellig_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Ø Anteil auffälliger QI nach Trägerschaft")
ax.set_xlabel("Ø Anteil auffälliger QI in %")
ax.set_ylabel("Trägerschaft")

values = plot_qi["Durchschnitt_Anteil_Auffaellig_Prozent"].fillna(0).tolist()
add_horizontal_labels(ax, bars, values, digits=2)

max_x = max(values) if values else 0
ax.set_xlim(0, max_x * 1.15 if max_x > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Diese Auswertung ist feiner als die reine binäre Auffälligkeit.
    Sie zeigt, ob eine Trägerart nicht nur häufiger mindestens eine Auffälligkeit aufweist,
    sondern auch im Durchschnitt einen höheren Anteil auffälliger Qualitätsindikatoren hat.
    """
)


# Zusammenfassung:
section_line()

section_header(
    "Zwischenfazit zur Trägerschaft",
    "Die Trägerschaft kann ein Kontextmerkmal für Auffälligkeitsmuster sein.",
)

notice_box(
    text="""
    Unterschiede nach Trägerschaft sollten vorsichtig interpretiert werden.
    Trägerarten können mit weiteren Merkmalen zusammenhängen, zum Beispiel Größe,
    Spezialisierung, regionaler Lage, Versorgungsauftrag oder Fallmix.
    
    Die Analyse zeigt daher Muster nach Trägerschaft, aber keine direkte Ursache.
    Für eine fachliche Bewertung müssten weitere Kontextfaktoren gemeinsam betrachtet werden.
    """,
    title="Fachliche Einordnung",
)


scroll_to_top_button()