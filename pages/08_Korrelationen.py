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
    scroll_to_top_button
)


# -------------------------------------------------
# Seiteneinstellungen
# -------------------------------------------------
st.set_page_config(
    page_title="Korrelationen",
    page_icon="📈",
    layout="wide",
)


# -------------------------------------------------
# Design anwenden
# -------------------------------------------------
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("korrelationen")


# -------------------------------------------------
# Daten laden
# -------------------------------------------------
data = load_all_data()
df = data["df_analyse"]


# -------------------------------------------------
# Daten vorbereiten
# -------------------------------------------------
df = prepare_analysis_df(df)


# -------------------------------------------------
# Zielvariable und ausgewählte Merkmale
# -------------------------------------------------
HAUPTZIEL = "Anteil_Auffaellig"

AUSGEWAEHLTE_MERKMALE = [
    "Anteil_Auffaellig",
    "Anzahl_Fachabteilungen",
    "SO.Betten",
    "Aerzte_pro_Bett",
    "Pflegekraefte_pro_Bett",
    "Hygienekraefte_pro_Bett",
]


# -------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------
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


def schoener_spaltenname(spalte):
    """
    Macht technische Spaltennamen für die Anzeige lesbarer.
    """

    mapping = {
        "Anteil_Auffaellig": "Auffälligkeit",
        "SO.Betten": "Bettenanzahl",
        "Anzahl_Fachabteilungen": "Anzahl der Fachabteilungen",
        "Aerzte_pro_Bett": "Ärzte pro Bett",
        "Pflegekraefte_pro_Bett": "Pflegekräfte pro Bett",
        "Hygienekraefte_pro_Bett": "Hygienekräfte pro Bett",
    }

    if spalte in mapping:
        return mapping[spalte]

    return (
        str(spalte)
        .replace("_", " ")
        .replace("Auffaellig", "Auffälligkeit")
        .replace("auffaellig", "auffällig")
        .replace("Aerzte", "Ärzte")
        .replace("Pflegekraefte", "Pflegekräfte")
        .replace("Hygienekraefte", "Hygienekräfte")
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
    title="📈 Korrelationsanalyse",
    text="""
    Diese Seite zeigt rechnerische Zusammenhänge zwischen ausgewählten Krankenhausmerkmalen
    und dem Anteil auffälliger Qualitätsindikatoren.
    <br><br>
    Berücksichtigt werden nur zentrale und vergleichbare Merkmale:
    Bettenanzahl, Anzahl der Fachabteilungen sowie Personalrelationen pro Bett.
    """,
    note="""
    Wichtig: Eine Korrelation beschreibt einen statistischen Zusammenhang,
    aber keine Ursache-Wirkungs-Beziehung.
    """,
)


# -------------------------------------------------
# Daten für Korrelationsanalyse vorbereiten
# -------------------------------------------------
fehlende_spalten = [
    col for col in AUSGEWAEHLTE_MERKMALE
    if col not in df.columns
]

if fehlende_spalten:
    st.warning("Für die Korrelationsanalyse fehlen folgende Spalten:")
    st.write(fehlende_spalten)

    with st.expander("Alle vorhandenen Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Nur ausgewählte Spalten verwenden
corr_df = df[AUSGEWAEHLTE_MERKMALE].copy()


# Alle Spalten numerisch machen
for col in corr_df.columns:
    corr_df[col] = pd.to_numeric(corr_df[col], errors="coerce")


# Spalten mit zu wenigen gültigen Werten entfernen
min_gueltige_werte = 3

gueltige_spalten = [
    col for col in corr_df.columns
    if corr_df[col].dropna().nunique() > 1
    and corr_df[col].dropna().shape[0] >= min_gueltige_werte
]

corr_df = corr_df[gueltige_spalten].copy()


if HAUPTZIEL not in corr_df.columns:
    st.warning("Die Zielvariable 'Anteil_Auffaellig' ist nicht ausreichend vorhanden.")
    st.stop()


if len(corr_df.columns) < 2:
    st.warning("Es liegen nicht genügend geeignete Merkmale für eine Korrelationsanalyse vor.")
    st.stop()


# Korrelationsmatrix berechnen
corr_matrix = corr_df.corr(numeric_only=True)


# Korrelationen mit der Zielvariable berechnen:
ziel_korrelationen = (
    corr_matrix[HAUPTZIEL]
    .drop(labels=[HAUPTZIEL], errors="ignore")
    .dropna()
)

ziel_corr_df = ziel_korrelationen.reset_index()
ziel_corr_df.columns = ["Merkmal", "Korrelation"]

ziel_corr_df["Merkmal Anzeige"] = ziel_corr_df["Merkmal"].apply(
    schoener_spaltenname
)

ziel_corr_df = ziel_corr_df.sort_values("Korrelation").reset_index(drop=True)


if ziel_corr_df.empty:
    st.warning("Es konnten keine Korrelationen zur Zielvariable berechnet werden.")
    st.stop()


staerkstes_positives_merkmal = ziel_korrelationen.idxmax()
staerkste_positive_korrelation = ziel_korrelationen.max()

staerkstes_negatives_merkmal = ziel_korrelationen.idxmin()
staerkste_negative_korrelation = ziel_korrelationen.min()


# KPI-Karten:
section_header(
    "Zentrale Korrelations-Kennzahlen",
    "Diese Kennzahlen zeigen, welche ausgewählten Merkmale in die Korrelationsanalyse eingehen.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Ausgewählte Merkmale",
        format_kpi(len(corr_df.columns) -1),
        "ohne Zielvariable",
    )

with col3:
    metric_card(
        "Zielvariable",
        "Auffälligkeit",
        "Anteil auffälliger QI",
    )

with col2:
    metric_card(
        "Berechnete Korrelationen",
        format_kpi(len(ziel_korrelationen)),
        "bezogen auf Auffälligkeit",
    )


col4, col5, col6 = st.columns(3)

with col4:
    metric_card(
        "Stärkster positiver Zusammenhang",
        format_kpi(staerkste_positive_korrelation, 2),
        schoener_spaltenname(staerkstes_positives_merkmal),
    )

with col5:
    metric_card(
        "Stärkster negativer Zusammenhang",
        format_kpi(staerkste_negative_korrelation, 2),
        schoener_spaltenname(staerkstes_negatives_merkmal),
    )

with col6:
    metric_card(
        "Korrelationsskala",
        "-1 bis +1",
        "negativ bis positiv",
    )


interpretation_box(
    """
    Die Kennzahlen zeigen, welche ausgewählten Merkmale mit dem Anteil auffälliger
    Qualitätsindikatoren zusammenhängen. Werte nahe 0 stehen für sehr schwache Zusammenhänge.
    Positive Werte zeigen, dass beide Merkmale tendenziell gemeinsam steigen.
    Negative Werte zeigen, dass ein Merkmal eher sinkt, wenn das andere steigt.
    """
)


# Tabelle: Korrelationen mit Zielvariable:
# section_line()

# section_header(
#     "Korrelationen mit der Auffälligkeit",
#     "Die Tabelle zeigt, wie stark die ausgewählten Merkmale mit dem Anteil auffälliger QI zusammenhängen.",
# )
#
# with st.expander("Tabelle: Korrelationen mit der Auffälligkeit anzeigen", expanded=True):
#
#     ziel_tabelle = ziel_corr_df[
#         [
#             "Merkmal Anzeige",
#             "Korrelation",
#         ]
#     ].copy()
#
#     ziel_tabelle["Korrelation"] = ziel_tabelle["Korrelation"].round(2)
#
#     ziel_tabelle.columns = [
#         "Merkmal",
#         "Korrelationswert",
#     ]
#
#     st.dataframe(
#         ziel_tabelle,
#         use_container_width=True,
#         hide_index=True,
#     )


# Plot 1: Korrelationen mit Zielvariable:
# section_line()
#
# section_header(
#     "Zusammenhänge mit dem Anteil auffälliger QI",
#     "Das Balkendiagramm zeigt die Korrelationen der ausgewählten Merkmale mit der Auffälligkeit.",
# )
#
# if not ziel_corr_df.empty:
#     fig, ax = plt.subplots(figsize=(10, 5.5))
#
#     bars = ax.barh(
#         ziel_corr_df["Merkmal Anzeige"],
#         ziel_corr_df["Korrelation"],
#         color=BAR_COLOR,
#     )
#
#     style_plot(ax)
#
#     ax.axvline(0, color="white", linewidth=1)
#
#     ax.set_title("Korrelationen mit dem Anteil auffälliger QI")
#     ax.set_xlabel("Korrelationswert")
#     ax.set_ylabel("Merkmal")
#
#     # Wertebereich bestimmen
#     min_wert = ziel_corr_df["Korrelation"].min()
#     max_wert = ziel_corr_df["Korrelation"].max()
#     span = max_wert - min_wert
#
#     # Falls alle Werte fast gleich sind
#     if span == 0:
#         span = 0.05
#
#     # Mehr Platz links und rechts schaffen
#     ax.set_xlim(
#         min_wert - span * 0.20,
#         max_wert + span * 0.20
#     )
#
#     # Werte an Balken schreiben
#     for bar in bars:
#         breite = bar.get_width()
#         y_pos = bar.get_y() + bar.get_height() / 2
#
#         if breite >= 0:
#             x_pos = breite + span * 0.03
#             ha = "left"
#         else:
#             x_pos = breite - span * 0.12
#             ha = "right"
#
#         ax.text(
#             x_pos,
#             y_pos,
#             f"{breite:.2f}",
#             ha=ha,
#             va="center",
#             color="white",
#             fontsize=10,
#             clip_on=False,
#         )
#
#     plt.tight_layout()
#     st.pyplot(fig)
#
#     interpretation_box(
#         """
#         Das Balkendiagramm zeigt, welche ausgewählten Merkmale mit dem Anteil auffälliger
#         Qualitätsindikatoren zusammenhängen. Positive Werte bedeuten, dass höhere Werte des
#         Merkmals tendenziell mit einer höheren Auffälligkeit einhergehen. Negative Werte deuten
#         auf einen gegenläufigen Zusammenhang hin.
#         """
#     )
#
# else:
#     st.info("Es liegen keine Korrelationswerte für den Plot vor.")


# Tabelle: Korrelationsmatrix:
section_line()

section_header(
    "Korrelationswerte der ausgewählten Merkmale",
    "Die Tabelle zeigt die Korrelationswerte zwischen den zentralen Merkmalen.",
)

corr_matrix_anzeige = corr_matrix.copy()

corr_matrix_anzeige.index = [
    schoener_spaltenname(col) for col in corr_matrix_anzeige.index
]

corr_matrix_anzeige.columns = [
    schoener_spaltenname(col) for col in corr_matrix_anzeige.columns
]

corr_matrix_anzeige = corr_matrix_anzeige.round(2)


with st.expander("Tabelle: Korrelationsmatrix anzeigen", expanded=False):
    st.dataframe(
        corr_matrix_anzeige,
        use_container_width=True,
    )


# Heatmap: Korrelationsmatrix:
section_line()

section_header(
    "Korrelationsmatrix zentraler Merkmale",
    "Die Heatmap zeigt die linearen Zusammenhänge zwischen Auffälligkeit, Struktur und Personalrelationen.",
)

fig, ax = plt.subplots(figsize=(10, 7))

im = ax.imshow(
    corr_matrix,
    vmin=-1,
    vmax=1,
)

style_plot(ax)

merkmale = corr_matrix.columns.tolist()

ax.set_xticks(range(len(merkmale)))
ax.set_yticks(range(len(merkmale)))

ax.set_xticklabels(
    [schoener_spaltenname(col) for col in merkmale],
    rotation=45,
    ha="right",
)

ax.set_yticklabels(
    [schoener_spaltenname(col) for col in merkmale]
)

ax.set_title("Korrelationsmatrix zentraler Merkmale")

for i in range(len(merkmale)):
    for j in range(len(merkmale)):
        value = corr_matrix.iloc[i, j]

        ax.text(
            j,
            i,
            f"{value:.2f}",
            ha="center",
            va="center",
            color="black",
            fontsize=9,
        )


cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

cbar.ax.yaxis.set_tick_params(color="white")
for label in cbar.ax.get_yticklabels():
    label.set_color("white")

cbar.outline.set_edgecolor("white")

plt.tight_layout()
st.pyplot(fig)


interpretation_box(
    """
    Die Heatmap zeigt keine absoluten Werte, sondern Korrelationswerte zwischen -1 und +1.
    Der Wert 1,00 auf der Diagonale entsteht, weil jedes Merkmal perfekt mit sich selbst
    korreliert.

    Besonders auffällig ist der starke Zusammenhang zwischen Bettenanzahl und Anzahl der
    Fachabteilungen. Die Auffälligkeit zeigt moderate positive Zusammenhänge mit Bettenanzahl
    und Fachabteilungen, während der Zusammenhang mit Hygienekräften pro Bett nahezu nicht
    vorhanden ist.
    """
)


# Zusammenfassung:
section_line()

section_header(
    "Zwischenfazit zur Korrelationsanalyse",
    "Korrelationen helfen bei der Mustererkennung, ersetzen aber keine Ursachenanalyse.",
)

notice_box(
    text="""
    Die Korrelationsanalyse zeigt, welche ausgewählten Merkmale rechnerisch gemeinsam
    mit dem Anteil auffälliger Qualitätsindikatoren variieren.
    
    In dieser Seite wurden bewusst nur zentrale und vergleichbare Merkmale verwendet:
    Bettenanzahl, Anzahl der Fachabteilungen sowie Personalrelationen pro Bett.
    Absolute Auffälligkeitszahlen und doppelte Prozentvarianten wurden nicht verwendet,
    damit die Analyse verständlicher und fachlich sauberer bleibt.
    
    Eine Korrelation bedeutet jedoch nicht, dass ein Merkmal die Auffälligkeit verursacht.
    Für eine kausale Interpretation müssten weitere Faktoren wie Fallmix, Versorgungsauftrag
    und Dokumentationsunterschiede berücksichtigt werden.
    """,
    title="Fachliche Einordnung",
)


scroll_to_top_button()