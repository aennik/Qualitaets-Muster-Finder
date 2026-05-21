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
#    page_navigation,
    sidebar_logo_bottom,
    page_top_anchor,
    scroll_to_top_button,
)


# Seiteneinstellungen:
st.set_page_config(
    page_title="Uni-Status",
    page_icon="🎓",
    layout="wide",
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("uni")


# Daten laden:
data = load_all_data()
df = data["df_analyse"]


# Daten vorbereiten:
df = prepare_analysis_df(df)


# Konstanten / Spaltennamen:
UNI_COL = "SO.Uni"
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
    title="🎓 Uni-Status",
    text="""
    Diese Seite untersucht, ob sich Auffälligkeitsmuster zwischen Universitätskliniken
    und Nicht-Universitätskliniken unterscheiden.
    <br><br>
    Universitätskliniken haben häufig besondere Versorgungsaufträge, komplexere Fälle,
    Forschungsschwerpunkte und ein breiteres Leistungsspektrum. Deshalb kann der Uni-Status
    ein relevanter Kontextfaktor für Qualitätsindikatoren sein.
    """,
    note="""
    Hypothese: Universitätskliniken weisen aufgrund ihrer Struktur und ihres Versorgungsauftrags
    andere Auffälligkeitsmuster auf als Nicht-Universitätskliniken.
    """,
)


# Benötigte Spalte prüfen:
if UNI_COL not in df.columns:
    st.error(
        f"Die Spalte `{UNI_COL}` wurde im Datensatz nicht gefunden."
    )

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Daten bereinigen / Uni-Status erzeugen:
df = df.copy()

df[UNI_COL] = pd.to_numeric(df[UNI_COL], errors="coerce")

uni_df = df.dropna(subset=[UNI_COL]).copy()

if uni_df.empty:
    st.warning("Für den Uni-Status liegen keine gültigen Werte vor.")
    st.stop()


uni_df["Uni_Status"] = uni_df[UNI_COL].map(
    {
        0: "keine Uni-Klinik",
        1: "Uni-Klinik",
    }
)

uni_df["Uni_Status"] = uni_df["Uni_Status"].fillna(
    uni_df[UNI_COL].astype(str)
)


# Aggregation nach Uni-Status:
id_col = QBID_COL if QBID_COL in uni_df.columns else "Uni_Status"

uni_agg = (
    uni_df
    .groupby("Uni_Status", as_index=False)
    .agg(
        Anzahl_Krankenhaeuser=(id_col, "nunique"),
        Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
        Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
        Durchschnitt_Anteil_Auffaellig=("Anteil_Auffaellig", "mean"),
    )
)

uni_agg["Anteil_Auffaelligkeit_Prozent"] = (
    uni_agg["Anteil_Auffaelligkeit"] * 100
).round(2)

uni_agg["Durchschnitt_Anteil_Auffaellig_Prozent"] = (
    uni_agg["Durchschnitt_Anteil_Auffaellig"] * 100
).round(2)

uni_agg = uni_agg.sort_values("Uni_Status")


# Uni-Kennzahlen:
anzahl_uni_status_gruppen = uni_agg["Uni_Status"].nunique()
anzahl_mit_uni_angabe = int(uni_agg["Anzahl_Krankenhaeuser"].sum())

uni_kliniken = uni_agg.loc[
    uni_agg["Uni_Status"] == "Uni-Klinik",
    "Anzahl_Krankenhaeuser",
]

nicht_uni_kliniken = uni_agg.loc[
    uni_agg["Uni_Status"] == "keine Uni-Klinik",
    "Anzahl_Krankenhaeuser",
]

anzahl_uni_kliniken = int(uni_kliniken.iloc[0]) if not uni_kliniken.empty else 0
anzahl_nicht_uni_kliniken = (
    int(nicht_uni_kliniken.iloc[0]) if not nicht_uni_kliniken.empty else 0
)

min_auff_anteil = uni_agg["Anteil_Auffaelligkeit_Prozent"].min()
max_auff_anteil = uni_agg["Anteil_Auffaelligkeit_Prozent"].max()


# Uni-Kennzahlen anzeigen:
section_header(
    "Zentrale Uni-Status-Kennzahlen",
    "Diese Kennzahlen zeigen die Datenbasis und Spannweite der Uni-Status-Gruppen.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Uni-Status-Gruppen",
        format_kpi(anzahl_uni_status_gruppen),
        "verfügbare Gruppen",
    )

# with col2:
#     metric_card(
#         "Mit Uni-Angabe",
#         format_kpi(anzahl_mit_uni_angabe),
#         "Krankenhäuser mit gültiger Angabe",
#     )

with col3:
    metric_card(
        "Uni-Kliniken",
        format_kpi(anzahl_uni_kliniken),
        "Krankenhäuser mit Uni-Status",
    )


col4, col5, col6 = st.columns(3)

with col2:
    metric_card(
        "Nicht-Uni-Kliniken",
        format_kpi(anzahl_nicht_uni_kliniken),
        "Krankenhäuser ohne Uni-Status",
    )

# with col5:
#     metric_card(
#         "Min. Auffälligkeitsanteil",
#         format_kpi(min_auff_anteil, 2) + " %",
#         "niedrigster Anteil nach Uni-Status",
#     )
#
# with col6:
#     metric_card(
#         "Max. Auffälligkeitsanteil",
#         format_kpi(max_auff_anteil, 2) + " %",
#         "höchster Anteil nach Uni-Status",
#     )


interpretation_box(
    """
    Diese Kennzahlen beziehen sich ausschließlich auf den Uni-Status.
    Im Vordergrund stehen Anzahl, Gruppengröße sowie Minimum und Maximum des Auffälligkeitsanteils nach Uni-Status.
    Dadurch wird sichtbar, wie stark Universitätskliniken und Nicht-Universitätskliniken im Datensatz vertreten sind
    und wie deutlich sich ihre Auffälligkeitsanteile unterscheiden.
    """
)


# Tabelle: Aggregation nach Uni-Status:
section_line()

section_header(
    "Auswertung nach Uni-Status",
    "Die Tabelle zeigt zentrale Kennzahlen für Uni-Kliniken und Nicht-Uni-Kliniken.",
)

with st.expander("Tabelle: Kennzahlen nach Uni-Status anzeigen", expanded=True):
    tabelle = uni_agg.copy()

    tabelle = tabelle.rename(
        columns={
            "Uni_Status": "Uni-Status",
            "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            "Anzahl_Auffaellig": "Anzahl auffällig",
            "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
            "Durchschnitt_Anteil_Auffaellig_Prozent": "Ø Anteil auffälliger QI in %",
        }
    )

    anzeige_spalten = [
        "Uni-Status",
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



# Plot 1: Anzahl Krankenhäuser nach Uni-Status:
# section_line()
#
# section_header(
#     "Anzahl Krankenhäuser nach Uni-Status",
#     "Dieses Diagramm  zeigt, wie viele Uni-Kliniken und Nicht-Uni-Kliniken im Datensatz enthalten sind.",
# )
#
# plot_anzahl = uni_agg.sort_values("Anzahl_Krankenhaeuser", ascending=False)
#
# fig, ax = plt.subplots(figsize=(8, 5.5))
#
# bars = ax.bar(
#     plot_anzahl["Uni_Status"].astype(str),
#     plot_anzahl["Anzahl_Krankenhaeuser"],
#     color=BAR_COLOR,
# )
#
# style_plot(ax)
#
# ax.set_title("Anzahl Krankenhäuser nach Uni-Status")
# ax.set_xlabel("Uni-Status")
# ax.set_ylabel("Anzahl Krankenhäuser")
#
# values = plot_anzahl["Anzahl_Krankenhaeuser"].tolist()
# add_bar_labels(ax, bars, values, digits=0)
#
# max_y = max(values) if values else 0
# ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)
#
# plt.tight_layout()
# st.pyplot(fig)
#
# interpretation_box(
#     """
#     Die Gruppengröße ist entscheidend für die Interpretation.
#     Wenn eine Gruppe deutlich kleiner ist, können einzelne Krankenhäuser den Anteil stärker beeinflussen.
#     Deshalb sollten die Prozentwerte immer zusammen mit der Anzahl der Krankenhäuser betrachtet werden.
#     """
# )


# Plot 2: Anteil auffälliger Krankenhäuser nach Uni-Status:
section_line()

section_header(
    "Anteil auffälliger Krankenhäuser nach Uni-Status",
    "Hier wird verglichen, welcher Anteil der Uni-Kliniken und Nicht-Uni-Kliniken mindestens "
    "einen auffälligen Qualitätsindikator aufweist.",
)

plot_auff = uni_agg.sort_values("Anteil_Auffaelligkeit_Prozent", ascending=False)

fig, ax = plt.subplots(figsize=(8, 5.5))

bars = ax.bar(
    plot_auff["Uni_Status"].astype(str),
    plot_auff["Anteil_Auffaelligkeit_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Anteil auffälliger Krankenhäuser nach Uni-Status")
ax.set_xlabel("Uni-Status")
ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")

values = plot_auff["Anteil_Auffaelligkeit_Prozent"].tolist()
add_bar_labels(ax, bars, values, digits=1)

max_y = max(values) if values else 0
ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Dieses Diagramm prüft die zentrale Uni-Status-Hypothese.
    Unterschiede können mit dem besonderen Versorgungsauftrag, einer höheren Fallkomplexität, Spezialisierung oder 
    einer größeren Anzahl relevanter Qualitätsindikatoren zusammenhängen.
    Die Darstellung zeigt Muster, aber keine direkte Ursache.
    """
)


# Plot 3: Durchschnittlicher Anteil auffälliger QI nach Uni-Status:
section_line()

section_header(
    "Durchschnittlicher Anteil auffälliger QI nach Uni-Status",
    "Neben der Ja/Nein-Auffälligkeit wird betrachtet, wie hoch der durchschnittliche Anteil auffälliger Qualitätsindikatoren je Uni-Status-Gruppe ist.",
)

plot_qi = uni_agg.sort_values(
    "Durchschnitt_Anteil_Auffaellig_Prozent",
    ascending=False,
)

fig, ax = plt.subplots(figsize=(8, 5.5))

bars = ax.bar(
    plot_qi["Uni_Status"].astype(str),
    plot_qi["Durchschnitt_Anteil_Auffaellig_Prozent"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Ø Anteil auffälliger QI nach Uni-Status")
ax.set_xlabel("Uni-Status")
ax.set_ylabel("Ø Anteil auffälliger QI in %")

values = plot_qi["Durchschnitt_Anteil_Auffaellig_Prozent"].fillna(0).tolist()
add_bar_labels(ax, bars, values, digits=2)

max_y = max(values) if values else 0
ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Diese Auswertung ist feiner als die reine binäre Auffälligkeit.
    Sie zeigt, ob Uni-Kliniken oder Nicht-Uni-Kliniken im Durchschnitt einen höheren
    Anteil auffälliger Qualitätsindikatoren aufweisen.
    """
)


# Zusammenfassung:
section_line()

section_header(
    "Zwischenfazit zum Uni-Status",
    "Der Uni-Status ist ein möglicher Kontextfaktor für Auffälligkeitsmuster.",
)

notice_box(
    text="""
    Unterschiede zwischen Uni-Kliniken und Nicht-Uni-Kliniken sollten vorsichtig interpretiert werden.
    Universitätskliniken übernehmen häufig komplexe Versorgungsaufgaben, haben besondere
    Spezialisierungen und behandeln möglicherweise andere Patientengruppen.

    Die Analyse zeigt daher Auffälligkeitsmuster nach Uni-Status, aber keine direkte Qualitätsbewertung.
    Für eine fachliche Einordnung müssten weitere Strukturmerkmale wie Bettenzahl, Fachabteilungen,
    Spezialisierung und Fallmix gemeinsam betrachtet werden.
    """,
    title="Fachliche Einordnung",
)


scroll_to_top_button()