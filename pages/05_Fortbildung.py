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
    page_title="Fortbildung",
    page_icon="📚",
    layout="wide",
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("fortbildung")


# Daten laden:
data = load_all_data()
df = data["df_analyse"]


# Daten vorbereiten:
df = prepare_analysis_df(df)


# Konstanten / Spaltennamen:
FORTBILDUNG_COL = "Fortbildungsquote"
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


def add_horizontal_labels(ax, bars, values, digits=1):
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
    title="📚 Fortbildung",
    text="""
    Diese Seite untersucht, ob Fortbildungsmerkmale mit auffälligen Qualitätsindikatoren
    zusammenhängen.
    <br><br>
    Im Fokus steht die Fortbildungsquote. Sie beschreibt, in welchem Umfang Fortbildung
    im Datensatz abgebildet ist und ob sich Unterschiede zwischen auffälligen und nicht
    auffälligen Krankenhäusern zeigen.
    """,
    note="""
    Hypothese: Fortbildungsmerkmale können als Kontextfaktor mit Auffälligkeitsmustern
    zusammenhängen.
    """,
)


# Benötigte Spalte prüfen:
if FORTBILDUNG_COL not in df.columns:
    st.error(
        f"Die Spalte `{FORTBILDUNG_COL}` wurde im Datensatz nicht gefunden."
    )

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Daten bereinigen:
df = df.copy()

df[FORTBILDUNG_COL] = pd.to_numeric(
    df[FORTBILDUNG_COL],
    errors="coerce",
)

df["Hat_Fortbildungswert"] = df[FORTBILDUNG_COL].notna()

fortbildung_df = df.dropna(subset=[FORTBILDUNG_COL]).copy()

if fortbildung_df.empty:
    st.warning("Für die Fortbildungsquote liegen keine gültigen Werte vor.")
    st.stop()


# Fortbildungsquote in Prozent prüfen/erzeugen:
# Falls die Werte zwischen 0 und 1 liegen, werden sie als Anteil interpretiert.
# Falls sie bereits über 1 liegen, werden sie als Prozentwerte interpretiert.

max_rohwert = fortbildung_df[FORTBILDUNG_COL].max()

if max_rohwert <= 1:
    fortbildung_df["Fortbildungsquote_Prozent"] = (
        fortbildung_df[FORTBILDUNG_COL] * 100
    )
    df["Fortbildungsquote_Prozent"] = df[FORTBILDUNG_COL] * 100
else:
    fortbildung_df["Fortbildungsquote_Prozent"] = fortbildung_df[FORTBILDUNG_COL]
    df["Fortbildungsquote_Prozent"] = df[FORTBILDUNG_COL]


# Fortbildungs-Kennzahlen:
fortbildungs_spalten = [
    col for col in df.columns
    if "fortbildung" in col.lower()
]

anzahl_fortbildungsmerkmale = len(fortbildungs_spalten)

anzahl_mit_fortbildungswert = int(df["Hat_Fortbildungswert"].sum())
anzahl_ohne_fortbildungswert = int((~df["Hat_Fortbildungswert"]).sum())

min_fortbildungsquote = fortbildung_df["Fortbildungsquote_Prozent"].min()
max_fortbildungsquote = fortbildung_df["Fortbildungsquote_Prozent"].max()

if "Anzahl_Auffaellig" in fortbildung_df.columns:
    max_auff_qi_mit_fortbildungswert = fortbildung_df["Anzahl_Auffaellig"].max()
else:
    max_auff_qi_mit_fortbildungswert = None


# Fortbildungs-Kennzahlen anzeigen:
section_header(
    "Zentrale Fortbildungs-Kennzahlen",
    "Diese Kennzahlen zeigen Datenverfügbarkeit und Spannweite der Fortbildungsquote.",
)

col1, col2, col3 = st.columns(3)

# with col1:
#     metric_card(
#         "Fortbildung nach Personalgruppe",
#         format_kpi(anzahl_fortbildungsmerkmale),
#         "Spalten mit Fortbildungsbezug",
#     )

with col1:
    metric_card(
        "Mit Fortbildungswert",
        format_kpi(anzahl_mit_fortbildungswert),
        "Krankenhäuser mit gültiger Fortbildungsangabe",
    )

with col2:
    metric_card(
        "Ohne Fortbildungswert",
        format_kpi(anzahl_ohne_fortbildungswert),
        "fehlende Fortbildungsangabe",
    )


col4, col5, col6 = st.columns(3)

# with col4:
#     metric_card(
#         "Min. Fortbildungsquote",
#         f"{format_metric(min_fortbildungsquote)} %",
#         "kleinster gültiger Wert",
#     )
#
# with col5:
#     metric_card(
#         "Max. Fortbildungsquote",
#         f"{format_metric(max_fortbildungsquote)} %",
#         "größter gültiger Wert",
#     )

with col3:
    metric_card(
        "Max. auffällige QI",
        format_kpi(max_auff_qi_mit_fortbildungswert),
        "bei Häusern mit Fortbildungswert",
    )


interpretation_box(
    """
    Diese Kennzahlen beziehen sich ausschließlich auf die Fortbildungsdaten.
    Im Vordergrund stehen Datenverfügbarkeit sowie Minimum und Maximum der Fortbildungsquote.
    Damit wird sichtbar, ob die Fortbildungsvariable ausreichend gefüllt ist und welche
    Spannweite sie im Datensatz aufweist.
    """
)


# Tabelle: Fortbildungsdaten nach Auffälligkeitsstatus:
section_line()

section_header(
    "Fortbildungswerte nach Auffälligkeitsstatus",
    "Die Tabelle zeigt zentrale Fortbildungswerte für auffällige und nicht auffällige Krankenhäuser.",
)

fort_status_agg = (
    fortbildung_df
    .groupby("Auffaelligkeit_Status", as_index=False)
    .agg(
        Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
        Min_Fortbildungsquote=("Fortbildungsquote_Prozent", "min"),
        Max_Fortbildungsquote=("Fortbildungsquote_Prozent", "max"),
        Durchschnitt_Fortbildungsquote=("Fortbildungsquote_Prozent", "mean"),
        Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
    ).round(2)
)

with st.expander("Tabelle: Fortbildung nach Auffälligkeitsstatus anzeigen", expanded=True):
    tabelle = fort_status_agg.rename(
        columns={
            "Auffaelligkeit_Status": "Auffälligkeitsstatus",
            "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            "Min_Fortbildungsquote": "Min. Fortbildungsquote in %",
            "Max_Fortbildungsquote": "Max. Fortbildungsquote in %",
            "Durchschnitt_Fortbildungsquote": "Ø Fortbildungsquote in %",
            "Anzahl_Auffaellig": "Anzahl auffällig",
        }
    )

    st.dataframe(
        tabelle,
        use_container_width=True,
        hide_index=True,
    )


# Plot 1: Durchschnittliche Fortbildungsquote nach Auffälligkeitsstatus:
section_line()

section_header(
    "Fortbildungsquote nach Auffälligkeitsstatus",
    "Das Diagramm vergleicht die durchschnittliche Fortbildungsquote von auffälligen und nicht auffälligen Krankenhäusern.",
)

plot_status = fort_status_agg.copy()

plot_status["Auffaelligkeit_Status"] = pd.Categorical(
    plot_status["Auffaelligkeit_Status"],
    categories=["nicht auffällig", "auffällig"],
    ordered=True,
)

plot_status = plot_status.sort_values("Auffaelligkeit_Status")

fig, ax = plt.subplots(figsize=(8, 5.5))

bars = ax.bar(
    plot_status["Auffaelligkeit_Status"].astype(str),
    plot_status["Durchschnitt_Fortbildungsquote"],
    color=BAR_COLOR,
)

style_plot(ax)

ax.set_title("Ø Fortbildungsquote nach Auffälligkeitsstatus")
ax.set_xlabel("Auffälligkeitsstatus")
ax.set_ylabel("Ø Fortbildungsquote in %")

values = plot_status["Durchschnitt_Fortbildungsquote"].fillna(0).tolist()
add_bar_labels(ax, bars, values, digits=2)

max_y = max(values) if values else 0
ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

plt.tight_layout()
st.pyplot(fig)

interpretation_box(
    """
    Das Diagramm zeigt, ob sich die durchschnittliche Fortbildungsquote zwischen auffälligen
    und nicht auffälligen Krankenhäusern unterscheidet.
    Ein sichtbarer Unterschied ist ein Muster im Datensatz, aber keine direkte Ursache.
    """
)


# Plot 2: Fortbildungsgruppen und Auffälligkeit:
# section_line()
#
# section_header(
#     "Auffälligkeit nach Fortbildungsgruppen",
#     "Die Fortbildungsquote wird in Gruppen eingeteilt, um mögliche Muster besser sichtbar zu machen.",
# )
#
# try:
#     fortbildung_df["Fortbildungsgruppe"] = pd.qcut(
#         fortbildung_df["Fortbildungsquote_Prozent"],
#         q=4,
#         duplicates="drop",
#     )
#
#     fort_gruppen_agg = (
#         fortbildung_df
#         .dropna(subset=["Fortbildungsgruppe"])
#         .groupby("Fortbildungsgruppe", observed=True)
#         .agg(
#             Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
#             Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
#             Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
#             Min_Fortbildungsquote=("Fortbildungsquote_Prozent", "min"),
#             Max_Fortbildungsquote=("Fortbildungsquote_Prozent", "max"),
#         )
#         .reset_index()
#     )
#
#     fort_gruppen_agg["Anteil_Auffaelligkeit_Prozent"] = (
#         fort_gruppen_agg["Anteil_Auffaelligkeit"] * 100
#     )
#
#     fort_gruppen_agg["Fortbildungsgruppe_Label"] = (
#         fort_gruppen_agg["Fortbildungsgruppe"].astype(str)
#     )
#
#     with st.expander("Tabelle: Auffälligkeit nach Fortbildungsgruppen anzeigen"):
#         tabelle_gruppen = fort_gruppen_agg.rename(
#             columns={
#                 "Fortbildungsgruppe_Label": "Fortbildungsgruppe",
#                 "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
#                 "Anzahl_Auffaellig": "Anzahl auffällig",
#                 "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
#                 "Min_Fortbildungsquote": "Min. Fortbildungsquote in %",
#                 "Max_Fortbildungsquote": "Max. Fortbildungsquote in %",
#             }
#         )
#
#         st.dataframe(
#             tabelle_gruppen[
#                 [
#                     "Fortbildungsgruppe",
#                     "Anzahl Krankenhäuser",
#                     "Anzahl auffällig",
#                     "Anteil auffällig in %",
#                     "Min. Fortbildungsquote in %",
#                     "Max. Fortbildungsquote in %",
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True,
#         )
#
#     fig, ax = plt.subplots(figsize=(10, 5.8))
#
#     bars = ax.bar(
#         fort_gruppen_agg["Fortbildungsgruppe_Label"],
#         fort_gruppen_agg["Anteil_Auffaelligkeit_Prozent"],
#         color=BAR_COLOR,
#     )
#
#     style_plot(ax)
#
#     ax.set_title("Anteil auffälliger Krankenhäuser nach Fortbildungsgruppe")
#     ax.set_xlabel("Fortbildungsgruppe")
#     ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")
#     ax.tick_params(axis="x", rotation=20)
#
#     values = fort_gruppen_agg["Anteil_Auffaelligkeit_Prozent"].fillna(0).tolist()
#     add_bar_labels(ax, bars, values, digits=1)
#
#     max_y = max(values) if values else 0
#     ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)
#
#     plt.tight_layout()
#     st.pyplot(fig)
#
#     interpretation_box(
#         """
#         Die Gruppierung der Fortbildungsquote zeigt, ob Krankenhäuser mit niedrigerer oder
#         höherer Fortbildungsquote unterschiedlich häufig auffällig sind.
#         Die Gruppen dienen der Mustererkennung und sollten nicht als harte Grenzwerte
#         interpretiert werden.
#         """
#     )
#
# except ValueError:
#     st.info(
#         "Die Fortbildungsquote enthält zu wenige unterschiedliche Werte für eine Gruppierung."
#     )


# Plot 3: Korrelation mit Anteil auffälliger QI:
section_line()

section_header(
    "Zusammenhang mit dem Anteil auffälliger Qualitätsindikatoren",
    "Hier wird geprüft, ob die Fortbildungsquote mit dem Anteil auffälliger QI zusammenhängt.",
)

if "Anteil_Auffaellig" in fortbildung_df.columns:
    temp = fortbildung_df[
        [
            "Fortbildungsquote_Prozent",
            "Anteil_Auffaellig",
        ]
    ].dropna()

    if len(temp) >= 3:
        corr = temp["Fortbildungsquote_Prozent"].corr(
            temp["Anteil_Auffaellig"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card(
                "Gültige Werte",
                format_kpi(len(temp)),
                "für Korrelationsanalyse",
            )
        #
        # with col2:
        #     metric_card(
        #         "Min. Fortbildungsquote",
        #         f"{temp['Fortbildungsquote_Prozent'].min():.2f} %",
        #         "in Korrelationsbasis",
        #     )
        #
        with col2:
            metric_card(
                "Korrelation",
                format_kpi(corr, 3) + " %",
                "mit Anteil auffälliger QI",
            )

        fig, ax = plt.subplots(figsize=(8, 5.8))

        ax.scatter(
            temp["Fortbildungsquote_Prozent"],
            temp["Anteil_Auffaellig"] * 100,
            color=BAR_COLOR,
            alpha=0.65,
            label="Krankenhaus"
        )

        style_plot(ax)

        ax.set_title("Fortbildungsquote und Anteil auffälliger QI")
        ax.set_xlabel("Fortbildungsquote in %")
        ax.set_ylabel("Anteil auffälliger QI in %")

        legende = ax.legend(
            loc="upper left",
            frameon=True,
            facecolor="#0e1117",
            edgecolor="white",
            framealpha=1,
            fontsize=10
        )

        for text in legende.get_texts():
            text.set_color("white")

        plt.tight_layout()
        st.pyplot(fig)

        interpretation_box(
            f"""
            Der Scatterplot zeigt keinen klaren Zusammenhang zwischen Fortbildungsquote und dem Anteil auffälliger
            Qualitätsindikatoren. Die meisten Krankenhäuser liegen unabhängig von der Fortbildungsquote bei 
            sehr niedrigen Auffälligkeitswerten. Einzelne Ausreißer mit hohen Anteilen sollten vorsichtig interpretiert
            und separat geprüft werden.
            
            Die berechnete Korrelation beträgt {corr:.3f}.
            Werte nahe 0 sprechen für keinen oder nur einen sehr schwachen linearen Zusammenhang.
            Positive Werte bedeuten, dass höhere Fortbildungsquoten tendenziell mit höheren
            Anteilen auffälliger QI einhergehen. Negative Werte bedeuten das Gegenteil.
            Auch hier gilt: Korrelation beschreibt keine Kausalität.
            """
        )

    else:
        st.info("Für eine Korrelationsanalyse liegen zu wenige gültige Werte vor.")

else:
    st.info("Die Spalte 'Anteil_Auffaellig' ist nicht vorhanden.")


# Zusammenfassung:
section_line()

section_header(
    "Zwischenfazit zur Fortbildung",
    "Fortbildungsdaten können ein Kontextmerkmal sein, müssen aber vorsichtig interpretiert werden.",
)

notice_box(
    text="""
    Die Fortbildungsquote kann Hinweise auf Qualifizierungs- oder Dokumentationsstrukturen geben.
    Unterschiede zwischen auffälligen und nicht auffälligen Krankenhäusern sollten jedoch nicht
    als direkte Ursache interpretiert werden.
    
    Fortbildung hängt möglicherweise mit weiteren Faktoren zusammen, zum Beispiel Krankenhausgröße,
    Fachabteilungen, Personalstruktur, Trägerschaft oder Versorgungsauftrag.
    Die Analyse zeigt daher Muster, aber keine abschließende Erklärung.
    """,
    title="Fachliche Einordnung",
)

scroll_to_top_button()