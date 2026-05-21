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


# -------------------------------------------------
# Seiteneinstellungen
# -------------------------------------------------
st.set_page_config(
    page_title="Strukturmerkmale | Krankenhausanalyse",
    page_icon="🏥",
    layout="wide"
)


# -------------------------------------------------
# Design anwenden
# -------------------------------------------------
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("struktur")


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
# Konstanten / Spaltennamen
# -------------------------------------------------
BETTEN_COL = "SO.Betten"
FACHABTEILUNGEN_COL = "Anzahl_Fachabteilungen"
SPEZIALISIERUNG_COL = "Spezialisierungsgrad"



# -------------------------------------------------
# Hilfsfunktion: Tabellen sauber anzeigen
# -------------------------------------------------
def clean_table_for_display(df_table, columns=None, rename_dict=None, round_digits=2):
    """
    Bereitet Tabellen für die Anzeige in Streamlit vor:
    - wählt nur relevante Spalten aus
    - benennt Spalten verständlich um
    - entfernt Unterstriche
    - rundet numerische Werte auf 2 Nachkommastellen
    """

    table = df_table.copy()

    if columns is not None:
        available_columns = [col for col in columns if col in table.columns]
        table = table[available_columns]

    if rename_dict is not None:
        table = table.rename(columns=rename_dict)

    table.columns = (
        table.columns
        .str.replace("_", " ", regex=False)
        .str.replace("Auffaellig", "Auffällig", regex=False)
        .str.replace("auffaellig", "auffällig", regex=False)
        .str.replace("Krankenhaeuser", "Krankenhäuser", regex=False)
        .str.replace("Krankenhaus", "Krankenhaus", regex=False)
    )

    numeric_cols = table.select_dtypes(include="number").columns
    table[numeric_cols] = table[numeric_cols].round(round_digits)

    return table


# -------------------------------------------------
# Plot-Hilfsfunktionen
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


def add_bar_labels(ax, bars, values):
    """
    Schreibt Werte oberhalb der Balken.
    """

    max_value = max(values) if len(values) > 0 else 0

    for bar in bars:
        hoehe = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            hoehe + max_value * 0.02,
            f"{hoehe:.2f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=10,
        )


def add_horizontal_bar_labels(ax, bars, values):
    """
    Schreibt Werte rechts neben horizontale Balken.
    """

    max_value = max(values) if len(values) > 0 else 0

    for bar in bars:
        breite = bar.get_width()
        ax.text(
            breite + max_value * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{breite:.2f}",
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


# -------------------------------------------------
# Intro
# -------------------------------------------------
top_card(
    title="🏥 Krankenhausstruktur",
    text="""
    Diese Seite untersucht, ob strukturelle Merkmale eines Krankenhauses
    mit Auffälligkeiten in Qualitätsindikatoren zusammenhängen.
    <br><br>
    Betrachtet werden insbesondere die Bettenanzahl, die Anzahl der Fachabteilungen
    und der Spezialisierungsgrad. Diese Merkmale beschreiben Größe und Komplexität
    eines Krankenhauses.
    """,
    note="""
    Hypothese: Größere und komplexer strukturierte Krankenhäuser weisen häufiger
    mindestens einen auffälligen Qualitätsindikator auf.
    """,
)


# -------------------------------------------------
# Benötigte Spalten prüfen
# -------------------------------------------------
fehlende_spalten = []

for col in [BETTEN_COL]:
    if col not in df.columns:
        fehlende_spalten.append(col)

if fehlende_spalten:
    st.error("Für diese Seite fehlen wichtige Spalten im Datensatz:")
    st.write(fehlende_spalten)
    st.stop()


# -------------------------------------------------
# Numerische Strukturspalten vorbereiten
# -------------------------------------------------
df = df.copy()

df[BETTEN_COL] = pd.to_numeric(df[BETTEN_COL], errors="coerce")

if FACHABTEILUNGEN_COL in df.columns:
    df[FACHABTEILUNGEN_COL] = pd.to_numeric(
        df[FACHABTEILUNGEN_COL],
        errors="coerce",
    )

if SPEZIALISIERUNG_COL in df.columns:
    df[SPEZIALISIERUNG_COL] = pd.to_numeric(
        df[SPEZIALISIERUNG_COL],
        errors="coerce",
    )


# -------------------------------------------------
# Bettenklassen erzeugen
# -------------------------------------------------
df["Bettenklasse"] = pd.cut(
    df[BETTEN_COL],
    bins=[-1, 99, 299, 599, 999, float("inf")],
    labels=[
        "bis 99",
        "100–299",
        "300–599",
        "600–999",
        "1000+",
    ],
)


# -------------------------------------------------
# Struktur-Kennzahlen berechnen
# -------------------------------------------------
struktur_spalten = [
    BETTEN_COL,
    FACHABTEILUNGEN_COL,
    SPEZIALISIERUNG_COL,
]

vorhandene_struktur_spalten = [
    col for col in struktur_spalten
    if col in df.columns
]

anzahl_strukturmerkmale = len(vorhandene_struktur_spalten)

min_betten = df[BETTEN_COL].min()
max_betten = df[BETTEN_COL].max()

if FACHABTEILUNGEN_COL in df.columns:
    min_fachabteilungen = df[FACHABTEILUNGEN_COL].min()
    max_fachabteilungen = df[FACHABTEILUNGEN_COL].max()
else:
    min_fachabteilungen = None
    max_fachabteilungen = None

if SPEZIALISIERUNG_COL in df.columns:
    min_spezialisierung = df[SPEZIALISIERUNG_COL].min()
    max_spezialisierung = df[SPEZIALISIERUNG_COL].max()
else:
    min_spezialisierung = None
    max_spezialisierung = None


# -------------------------------------------------
# Struktur-Kennzahlen anzeigen
# -------------------------------------------------
section_header(
    "Zentrale Struktur-Kennzahlen",
    "Diese Kennzahlen zeigen die verfügbare Datenbasis und die Spannweite der wichtigsten Strukturmerkmale.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Strukturmerkmale",
        "2",
        "verfügbare Strukturspalten",
    )

# with col2:
#     metric_card(
#         "Min. Bettenzahl",
#         format_kpi(min_betten),
#         "kleinstes Krankenhaus im Datensatz",
#     )

with col2:
    metric_card(
        "Max. Bettenzahl",
        format_kpi(max_betten),
        "größtes Krankenhaus im Datensatz(Charité Berlin)",
    )

col4, col5, col6 = st.columns(3)

# with col4:
#     metric_card(
#         "Min. Fachabteilungen",
#         format_kpi(min_fachabteilungen),
#         "kleinste Angebotsbreite",
#     )

with col3:
    metric_card(
        "Max. Fachabteilungen",
        format_kpi(max_fachabteilungen),
        "größte Angebotsbreite (Uni-Klinik Leipzig)",
    )

# with col6:
#     metric_card(
#         "Max. Spezialisierungsgrad",
#         format_kpi(max_spezialisierung, 2) + " %",
#         "höchster Spezialisierungswert",
#     )

interpretation_box(
    """
    Diese Kennzahlen beschreiben die Struktur der Krankenhäuser. Im Fokus stehen Anzahl, Minimum und Maximum, 
    weil sie die verfügbare Datenbasis und die Spannweite der Strukturmerkmale sichtbar machen.
    """
)


# -------------------------------------------------
# Analyse 1: Auffälligkeit nach Bettenklasse
# -------------------------------------------------
section_line()

section_header(
    "Anteil der Auffälligkeit nach Bettenklasse",
    "Die Bettenzahl dient als Näherung für die Größe eines Krankenhauses.",
)

bettenklasse_df = (
    df.dropna(subset=["Bettenklasse"])
    .groupby("Bettenklasse", observed=True)
    .agg(
        Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
        Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
        Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
    )
    .reset_index()
)

bettenklasse_df["Anteil_Auffaelligkeit_Prozent"] = (
    bettenklasse_df["Anteil_Auffaelligkeit"] * 100
)

with st.expander("Tabelle: Auffälligkeit nach Bettenklasse anzeigen"):

    bettenklasse_tabelle = clean_table_for_display(
        bettenklasse_df,
        columns=[
            "Bettenklasse",
            "Anzahl_Krankenhaeuser",
            "Anzahl_Auffaellig",
            "Anteil_Auffaelligkeit_Prozent",
        ],
        rename_dict={
            "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            "Anzahl_Auffaellig": "Anzahl auffällig",
            "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
        },
    )

    st.dataframe(
        bettenklasse_tabelle,
        use_container_width=True,
        hide_index=True,
    )

if not bettenklasse_df.empty:
    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.bar(
        bettenklasse_df["Bettenklasse"].astype(str),
        bettenklasse_df["Anteil_Auffaelligkeit_Prozent"],
        color=BAR_COLOR,
    )

    style_plot(ax)

    ax.set_title("Anteil auffälliger Krankenhäuser nach Bettenklasse")
    ax.set_xlabel("Bettenklasse")
    ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")

    add_bar_labels(
        ax,
        bars,
        bettenklasse_df["Anteil_Auffaelligkeit_Prozent"].tolist(),
    )

    max_y = bettenklasse_df["Anteil_Auffaelligkeit_Prozent"].max()
    ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

    plt.tight_layout()
    st.pyplot(fig)

    interpretation_box(
        """
        Mit zunehmender Bettenklasse steigt der Anteil auffälliger Krankenhäuser deutlich. Große Krankenhäuser haben 
        häufiger mindestens eine Auffälligkeit, was auch mit mehr Fällen, mehr Abteilungen und 
        komplexeren Behandlungen zusammenhängen kann.
        """
    )
else:
    st.info("Für die Auswertung nach Bettenklasse liegen keine ausreichenden Daten vor.")


# -------------------------------------------------
# Analyse 2: Durchschnittlicher Anteil auffälliger QI nach Bettenklasse
# -------------------------------------------------
section_line()

section_header(
    "Durchschnittlicher Anteil auffälliger Qualitätsindikatoren nach Bettenklasse",
    "Neben der binären Auffälligkeit wird betrachtet, wie hoch der Anteil auffälliger QI je Krankenhaus ist.",
)

if "Anteil_Auffaellig" in df.columns:
    anteil_qi_betten_df = (
        df.dropna(subset=["Bettenklasse"])
        .groupby("Bettenklasse", observed=True)
        .agg(
            Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
            Durchschnitt_Anteil_Auffaellig=("Anteil_Auffaellig", "mean"),
            Median_Anteil_Auffaellig=("Anteil_Auffaellig", "median"),
        )
        .reset_index()
    )

    anteil_qi_betten_df["Durchschnitt_Anteil_Auffaellig_Prozent"] = (
        anteil_qi_betten_df["Durchschnitt_Anteil_Auffaellig"] * 100
    )

    anteil_qi_betten_df["Median_Anteil_Auffaellig_Prozent"] = (
        anteil_qi_betten_df["Median_Anteil_Auffaellig"] * 100
    )

    with st.expander("Tabelle: Anteil auffälliger QI nach Bettenklasse anzeigen"):

        anteil_qi_tabelle = clean_table_for_display(
            anteil_qi_betten_df,
            columns=[
                "Bettenklasse",
                "Anzahl_Krankenhaeuser",
                "Durchschnitt_Anteil_Auffaellig_Prozent",
                "Median_Anteil_Auffaellig_Prozent",
            ],
            rename_dict={
                "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
                "Durchschnitt_Anteil_Auffaellig_Prozent": "Ø Anteil auffälliger QI in %",
                "Median_Anteil_Auffaellig_Prozent": "Median Anteil auffälliger QI in %",
            },
        )

        st.dataframe(
            anteil_qi_tabelle,
            use_container_width=True,
            hide_index=True,
        )

    fig, ax = plt.subplots(figsize=(9, 5.5))

    bars = ax.bar(
        anteil_qi_betten_df["Bettenklasse"].astype(str),
        anteil_qi_betten_df["Durchschnitt_Anteil_Auffaellig_Prozent"],
        color=BAR_COLOR,
    )

    style_plot(ax)

    ax.set_title("Ø Anteil auffälliger QI nach Bettenklasse")
    ax.set_xlabel("Bettenklasse")
    ax.set_ylabel("Ø Anteil auffälliger QI in %")

    add_bar_labels(
        ax,
        bars,
        anteil_qi_betten_df["Durchschnitt_Anteil_Auffaellig_Prozent"].tolist(),
    )

    max_y = anteil_qi_betten_df["Durchschnitt_Anteil_Auffaellig_Prozent"].max()
    ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

    plt.tight_layout()
    st.pyplot(fig)

    interpretation_box(
        """
        Kleine Krankenhäuser weisen im Durchschnitt den höchsten Anteil auffälliger QI auf. Bei größeren Häusern ist 
        der Anteil niedriger, da sich Auffälligkeiten auf mehr Qualitätsindikatoren verteilen können.
        """
    )

else:
    st.info("Die Spalte 'Anteil_Auffaellig' ist nicht vorhanden.")


# -------------------------------------------------
# Analyse 3: Anzahl Fachabteilungen
# -------------------------------------------------
section_line()

section_header(
    "Fachabteilungen und Auffälligkeit",
    "Die Anzahl der Fachabteilungen beschreibt die Breite des medizinischen Angebots.",
)

if FACHABTEILUNGEN_COL in df.columns:
    fach_df = df.dropna(subset=[FACHABTEILUNGEN_COL]).copy()

    if not fach_df.empty:
        fach_df["Fachabteilungsgruppe"] = pd.cut(
            fach_df[FACHABTEILUNGEN_COL],
            bins=[-1, 3, 6, 10, float("inf")],
            labels=[
                "0–3",
                "4–6",
                "7–10",
                "11+",
            ],
        )

        fach_gruppen_df = (
            fach_df.dropna(subset=["Fachabteilungsgruppe"])
            .groupby("Fachabteilungsgruppe", observed=True)
            .agg(
                Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
                Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
                Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
            )
            .reset_index()
        )

        fach_gruppen_df["Anteil_Auffaelligkeit_Prozent"] = (
            fach_gruppen_df["Anteil_Auffaelligkeit"] * 100
        )

        with st.expander("Tabelle: Auffälligkeit nach Fachabteilungen anzeigen"):

            fachabteilung_tabelle = clean_table_for_display(
                fach_gruppen_df,
                columns=[
                    "Fachabteilungsgruppe",
                    "Anzahl_Krankenhaeuser",
                    "Anzahl_Auffaellig",
                    "Anteil_Auffaelligkeit_Prozent",
                ],
                rename_dict={
                    "Fachabteilungsgruppe": "Anzahl Fachabteilungen",
                    "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
                    "Anzahl_Auffaellig": "Anzahl auffällig",
                    "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
                },
            )

            st.dataframe(
                fachabteilung_tabelle,
                use_container_width=True,
                hide_index=True,
            )

        fig, ax = plt.subplots(figsize=(9, 5.5))

        bars = ax.bar(
            fach_gruppen_df["Fachabteilungsgruppe"].astype(str),
            fach_gruppen_df["Anteil_Auffaelligkeit_Prozent"],
            color=BAR_COLOR,
        )

        style_plot(ax)

        ax.set_title("Anteil auffälliger Krankenhäuser nach Anzahl Fachabteilungen")
        ax.set_xlabel("Anzahl Fachabteilungen")
        ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")

        add_bar_labels(
            ax,
            bars,
            fach_gruppen_df["Anteil_Auffaelligkeit_Prozent"].tolist(),
        )

        max_y = fach_gruppen_df["Anteil_Auffaelligkeit_Prozent"].max()
        ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)

        plt.tight_layout()
        st.pyplot(fig)

        interpretation_box(
            """
            Eine höhere Anzahl an Fachabteilungen kann auf ein breiteres und komplexeres Leistungsspektrum hinweisen. 
            Dadurch können mehr Qualitätsindikatoren relevant sein, was die Wahrscheinlichkeit erhöht, 
            dass mindestens ein auffälliger Indikator auftritt.
            """
        )

    else:
        st.info("Für die Anzahl der Fachabteilungen liegen keine ausreichenden Werte vor.")
else:
    st.info("Die Spalte 'Anzahl_Fachabteilungen' ist im Datensatz nicht vorhanden.")


# Zusatzanalyse: Welche Fachabteilungen sind betroffen?:
section_line()

section_header(
    "Welche Fachabteilungen treten bei auffälligen Krankenhäusern besonders häufig auf?",
    "Diese Auswertung zeigt, welche Fachabteilungsgruppen bei auffälligen Krankenhäusern im Datensatz besonders oft vorkommen.",
)

FA_GRUPPEN_COL = "Fa_Fachabteilungen"

if FA_GRUPPEN_COL in df.columns:
    fa_detail_df = df[
        [
            FA_GRUPPEN_COL,
            "Auffaelligkeit",
            "Auffaelligkeit_Status",
        ]
    ].copy()

    fa_detail_df = fa_detail_df.dropna(subset=[FA_GRUPPEN_COL])

    # Mehrfachnennungen je Krankenhaus aufteilen
    fa_detail_df[FA_GRUPPEN_COL] = (
        fa_detail_df[FA_GRUPPEN_COL]
        .astype(str)
        .str.split(";")
    )

    fa_detail_df = fa_detail_df.explode(FA_GRUPPEN_COL)

    fa_detail_df[FA_GRUPPEN_COL] = (
        fa_detail_df[FA_GRUPPEN_COL]
        .astype(str)
        .str.strip()
        .str.replace(r"^\d+\s*", "", regex=True)
        .str.strip()
    )

    # Leere und wenig aussagekräftige Einträge entfernen
    fa_detail_df = fa_detail_df[
        (fa_detail_df[FA_GRUPPEN_COL] != "")
        & (fa_detail_df[FA_GRUPPEN_COL].str.lower() != "nan")
        & (~fa_detail_df[FA_GRUPPEN_COL].str.contains("Sonstige", case=False, na=False))
    ]

    if not fa_detail_df.empty:
        fa_agg = (
            fa_detail_df
            .groupby(FA_GRUPPEN_COL, as_index=False)
            .agg(
                Anzahl_Nennungen=(FA_GRUPPEN_COL, "count"),
                Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
                Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
            )
        )

        fa_agg["Anteil_Auffaelligkeit_Prozent"] = (
            fa_agg["Anteil_Auffaelligkeit"] * 100
        ).round(2)


        top_fa_auff = (
            fa_agg
            .sort_values("Anzahl_Auffaellig", ascending=False)
            .head(10)
            .copy()
        )

        with st.expander("Tabelle: Fachabteilungen bei auffälligen Krankenhäusern anzeigen"):
            tabelle_fa = top_fa_auff.rename(
                columns={
                    FA_GRUPPEN_COL: "Fachabteilung",
                    "Anzahl_Nennungen": "Anzahl Nennungen",
                    "Anzahl_Auffaellig": "Anzahl auffällige Nennungen",
                    "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
                }
            )

            st.dataframe(
                tabelle_fa[
                    [
                        "Fachabteilung",
                        "Anzahl Nennungen",
                        "Anzahl auffällige Nennungen",
                        "Anteil auffällig in %",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        plot_fa = top_fa_auff.sort_values("Anzahl_Auffaellig")

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.barh(
            plot_fa[FA_GRUPPEN_COL],
            plot_fa["Anzahl_Auffaellig"],
            color=BAR_COLOR,
        )

        style_plot(ax)

        ax.set_title("Top 10 Fachabteilungen bei auffälligen Krankenhäusern")
        ax.set_xlabel("Anzahl auffälliger Nennungen")
        ax.set_ylabel("Fachabteilung")

        max_value = plot_fa["Anzahl_Auffaellig"].max()


        for bar in bars:
            breite = bar.get_width()

            ax.text(
                breite + max_value * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{int(round(breite))}",
                ha="left",
                va="center",
                color="white",
                fontsize=10,
            )

            # Platz rechts für Zahlen
            ax.set_xlim(0, max_value * 1.30)
        plt.tight_layout()
        st.pyplot(fig)

        interpretation_box(
            """
            Der Plot zeigt, welche Fachabteilungsgruppen besonders häufig bei auffälligen Krankenhäusern vorkommen.
        
            Wichtig ist: Eine häufige Nennung bedeutet nicht automatisch, dass diese Fachabteilung die Ursache für 
            Auffälligkeiten ist. Große oder breit aufgestellte Krankenhäuser haben oft mehrere Fachabteilungen und 
            dadurch auch mehr relevante Qualitätsindikatoren.
            """,
            title="Interpretation",
        )

    else:
        st.info("Für die Fachabteilungsgruppen liegen keine auswertbaren Werte vor.")

else:
    st.info("Die Spalte `FA_Gruppen` ist im Datensatz nicht vorhanden.")


# -------------------------------------------------
# Analyse 4: Spezialisierungsgrad
# -------------------------------------------------
# section_line()
#
# section_header(
#     "Spezialisierungsgrad und Auffälligkeit",
#     "Der Spezialisierungsgrad beschreibt, wie stark ein Krankenhaus auf bestimmte Leistungsbereiche fokussiert ist.",
# )
#
# if SPEZIALISIERUNG_COL in df.columns:
#     spez_df = df.dropna(subset=[SPEZIALISIERUNG_COL]).copy()
#
#     if not spez_df.empty:
#         try:
#             spez_df["Spezialisierungsgruppe"] = pd.qcut(
#                 spez_df[SPEZIALISIERUNG_COL],
#                 q=4,
#                 duplicates="drop",
#             )
#
#             spez_grouped = (
#                 spez_df.groupby("Spezialisierungsgruppe", observed=True)
#                 .agg(
#                     Anzahl_Krankenhaeuser=("Auffaelligkeit", "count"),
#                     Anzahl_Auffaellig=("Auffaelligkeit", "sum"),
#                     Anteil_Auffaelligkeit=("Auffaelligkeit", "mean"),
#                     Durchschnitt_Spezialisierungsgrad=(SPEZIALISIERUNG_COL, "mean"),
#                 )
#                 .reset_index()
#             )
#
#             spez_grouped["Anteil_Auffaelligkeit_Prozent"] = (
#                 spez_grouped["Anteil_Auffaelligkeit"] * 100
#             )
#
#             spez_grouped["Spezialisierungsgruppe_Label"] = (
#                 spez_grouped["Spezialisierungsgruppe"].astype(str)
#             )
#
#             with st.expander("Tabelle: Auffälligkeit nach Spezialisierungsgrad anzeigen"):
#
#                 spezialisierung_tabelle = clean_table_for_display(
#                     spez_grouped,
#                     columns=[
#                         "Spezialisierungsgruppe_Label",
#                         "Anzahl_Krankenhaeuser",
#                         "Anzahl_Auffaellig",
#                         "Anteil_Auffaelligkeit_Prozent",
#                         "Durchschnitt_Spezialisierungsgrad",
#                     ],
#                     rename_dict={
#                         "Spezialisierungsgruppe_Label": "Spezialisierungsgruppe",
#                         "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
#                         "Anzahl_Auffaellig": "Anzahl auffällig",
#                         "Anteil_Auffaelligkeit_Prozent": "Anteil auffällig in %",
#                         "Durchschnitt_Spezialisierungsgrad": "Ø Spezialisierungsgrad",
#                     },
#                 )
#
#                 st.dataframe(
#                     spezialisierung_tabelle,
#                     use_container_width=True,
#                     hide_index=True,
#                 )
#
#             fig, ax = plt.subplots(figsize=(10, 5.5))
#
#             bars = ax.bar(
#                 spez_grouped["Spezialisierungsgruppe_Label"],
#                 spez_grouped["Anteil_Auffaelligkeit_Prozent"],
#                 color=BAR_COLOR,
#             )
#
#             style_plot(ax)
#
#             ax.set_title("Anteil auffälliger Krankenhäuser nach Spezialisierungsgrad")
#             ax.set_xlabel("Spezialisierungsgruppe")
#             ax.set_ylabel("Anteil auffälliger Krankenhäuser in %")
#
#             ax.tick_params(axis="x", rotation=20)
#
#             add_bar_labels(
#                 ax,
#                 bars,
#                 spez_grouped["Anteil_Auffaelligkeit_Prozent"].tolist(),
#             )
#
#             max_y = spez_grouped["Anteil_Auffaelligkeit_Prozent"].max()
#             ax.set_ylim(0, max_y * 1.18 if max_y > 0 else 1)
#
#             plt.tight_layout()
#             st.pyplot(fig)
#
#             interpretation_box(
#                 """
#                 Der Spezialisierungsgrad kann Hinweise darauf geben, ob Auffälligkeiten eher
#                 bei breit aufgestellten oder stark spezialisierten Krankenhäusern auftreten.
#                 Die Interpretation hängt davon ab, wie der Spezialisierungsgrad in der Voranalyse
#                 gebildet wurde.
#                 """
#             )
#
#         except ValueError:
#             st.info(
#                 "Der Spezialisierungsgrad enthält zu wenige unterschiedliche Werte für eine Gruppierung."
#             )
#
#     else:
#         st.info("Für den Spezialisierungsgrad liegen keine ausreichenden Werte vor.")
# else:
#     st.info("Die Spalte 'Spezialisierungsgrad' ist im Datensatz nicht vorhanden.")


# -------------------------------------------------
# Zusammenfassung
# -------------------------------------------------
section_line()

section_header(
    "Zwischenfazit zur Strukturhypothese",
    "Die Strukturmerkmale liefern eine erste Einordnung möglicher Auffälligkeitsmuster.",
)

notice_box(
    text="""
    Wenn größere oder komplexer strukturierte Krankenhäuser häufiger auffällig sind, sollte dies nicht automatisch 
    als schlechtere Qualität interpretiert werden. Größere Häuser behandeln häufig komplexere Fälle, haben mehr Fachabteilungen
    und unterliegen mehr Qualitätsindikatoren. Dadurch steigt auch die Wahrscheinlichkeit,
    dass mindestens ein Indikator auffällig wird.

    Die Annahme ist daher eher als Hinweis auf einen Zusammenhang zwischen Struktur,
    Versorgungsauftrag und Auffälligkeitswahrscheinlichkeit zu verstehen.
    """,
    title="Fachliche Einordnung",
)

scroll_to_top_button()