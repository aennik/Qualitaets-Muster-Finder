# Imports:
import streamlit as st
import pandas as pd
import numpy as np
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
    page_title="Personalstruktur",
    page_icon="👥",
    layout="wide",
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("personal")


# Daten laden:
data = load_all_data()
df = data["df_analyse"]


# Daten vorbereiten:
df = prepare_analysis_df(df)


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


def schoener_spaltenname(spalte):
    """
    Macht technische Spaltennamen lesbarer.
    """

    mapping = {
        "Aerzte_pro_Bett": "Ärzte pro Bett",
        "Pflegekraefte_pro_Bett": "Pflegekräfte pro Bett",
        "Hygienekraefte_pro_Bett": "Hygienekräfte pro Bett",
        "Psychisches_Personal_pro_Bett": "Psychisches Personal pro Bett",
        "Sonstige_Therapien_pro_Bett": "Sonstige Therapien pro Bett",
        "Personal_Gesamt_pro_Bett": "Gesamtpersonal pro Bett",
    }

    return mapping.get(spalte, spalte.replace("_", " "))


def mittelwert_oder_none(df_input, spalte):
    """
    Gibt den Mittelwert einer Spalte zurück oder None, falls die Spalte fehlt.
    """

    if spalte in df_input.columns:
        return df_input[spalte].mean()

    return None


def min_oder_none(df_input, spalte):
    """
    Gibt den Minimalwert einer Spalte zurück oder None, falls die Spalte fehlt.
    """

    if spalte in df_input.columns:
        return df_input[spalte].min()

    return None


def max_oder_none(df_input, spalte):
    """
    Gibt den Maximalwert einer Spalte zurück oder None, falls die Spalte fehlt.
    """

    if spalte in df_input.columns:
        return df_input[spalte].max()

    return None


def format_metric(value, digits=2):
    """
    Formatiert Kennzahlen robust.
    """

    if value is None or pd.isna(value):
        return "-"

    return f"{value:.{digits}f}"

# Intro:
top_card(
    title="👥 Personalstruktur",
    text="""
    Diese Seite untersucht, ob Personalrelationen mit auffälligen Qualitätsindikatoren
    zusammenhängen.
    <br><br>
    Betrachtet werden Personalwerte relativ zur Bettenanzahl, zum Beispiel ärztliches Personal,
    Pflegekräfte, Hygienekräfte und weitere therapeutische oder psychische Personalgruppen.
    """,
    note="""
    Hypothese: Krankenhäuser mit unterschiedlichen Personalrelationen zeigen unterschiedliche
    Auffälligkeitsmuster.
    """,
)


# Mögliche Personalspalten:
personal_spalten = [
    "Aerzte_pro_Bett",
    "Pflegekraefte_pro_Bett",
    "Hygienekraefte_pro_Bett",
    "Psychisches_Personal_pro_Bett",
    "Sonstige_Therapien_pro_Bett",
    "Personal_Gesamt_pro_Bett",
]

vorhandene_personal_spalten = [
    col for col in personal_spalten
    if col in df.columns
]


# Falls keine Personalspalten vorhanden sind:
if not vorhandene_personal_spalten:
    st.warning(
        """
        In `df_analyse` wurden keine der erwarteten Personalspalten gefunden.
        Bitte prüfe, ob die Personalmerkmale in deiner Voranalyse anders benannt wurden.
        """
    )

    with st.expander("Vorhandene Spalten anzeigen"):
        st.write(df.columns.tolist())

    st.stop()


# Personalspalten numerisch machen:
df = df.copy()

for col in vorhandene_personal_spalten:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# Personal-Kennzahlen:
anzahl_personalmerkmale = len(vorhandene_personal_spalten)


def min_oder_none(df_input, spalte):
    """
    Gibt den Minimalwert einer Spalte zurück oder None, falls die Spalte fehlt.
    """

    if spalte in df_input.columns:
        return df_input[spalte].min()

    return None


def max_oder_none(df_input, spalte):
    """
    Gibt den Maximalwert einer Spalte zurück oder None, falls die Spalte fehlt.
    """

    if spalte in df_input.columns:
        return df_input[spalte].max()

    return None


def format_kpi(value, decimals=0):
    if value is None or pd.isna(value):
        return "-"

    formatted = f"{value:,.{decimals}f}"

    formatted = formatted.replace(",", "X")
    formatted = formatted.replace(".", ",")
    formatted = formatted.replace("X", ".")

    return formatted


min_aerzte = min_oder_none(df, "Aerzte_pro_Bett")
max_aerzte = max_oder_none(df, "Aerzte_pro_Bett")

min_pflege = min_oder_none(df, "Pflegekraefte_pro_Bett")
max_pflege = max_oder_none(df, "Pflegekraefte_pro_Bett")

min_hygiene = min_oder_none(df, "Hygienekraefte_pro_Bett")
max_hygiene = max_oder_none(df, "Hygienekraefte_pro_Bett")

min_psych = min_oder_none(df, "Psychisches_Personal_pro_Bett")
max_psych = max_oder_none(df, "Psychisches_Personal_pro_Bett")

min_therapie = min_oder_none(df, "Sonstige_Therapien_pro_Bett")
max_therapie = max_oder_none(df, "Sonstige_Therapien_pro_Bett")

min_gesamtpersonal = min_oder_none(df, "Personal_Gesamt_pro_Bett")
max_gesamtpersonal = max_oder_none(df, "Personal_Gesamt_pro_Bett")


# Personal-Kennzahlen anzeigen:
section_header(
    "Zentrale Personal-Kennzahlen",
    "Diese Kennzahlen zeigen die verfügbare Datenbasis und die Spannweite der wichtigsten Personalrelationen.",
)

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Personalgruppen",
        format_kpi(anzahl_personalmerkmale),
        "verfügbare Personalspalten",
    )

# with col2:
#     metric_card(
#         "Min. Ärzte pro Bett",
#         format_kpi(min_aerzte),
#         "kleinster ärztlicher Wert",
#     )

with col3:
    metric_card(
        "Max. Ärzte pro Bett",
        format_kpi(max_aerzte, 1),
        "größter ärztlicher Wert",
    )


col4, col5, col6 = st.columns(3)

# with col4:
#     metric_card(
#         "Min. Pflegekräfte pro Bett",
#         format_kpi(min_pflege),
#         "kleinster pflegerischer Wert",
#     )

with col2:
    metric_card(
        "Max. Pflegekräfte pro Bett",
        format_kpi(max_pflege, 1),
        "größter pflegerischer Wert",
    )

# with col6:
#     if max_hygiene is not None:
#         metric_card(
#             "Max. Hygienekräfte pro Bett",
#             format_kpi(max_hygiene, 1),
#             "höchster Hygiene-Personalwert",
#       )
#     elif max_psych is not None:
#         metric_card(
#             "Max. psychisches Personal pro Bett",
#             format_kpi(max_psych, 1),
#             "höchster weiterer Personalwert",
#         )
#     elif max_therapie is not None:
#         metric_card(
#             "Max. sonstige Therapien pro Bett",
#             format_kpi(max_therapie, 1),
#             "höchster weiterer Personalwert",
#         )
#     elif max_gesamtpersonal is not None:
#         metric_card(
#             "Max. Gesamtpersonal pro Bett",
#             format_kpi(max_gesamtpersonal, 1),
#             "höchster Gesamtpersonalwert",
#         )
#     else:
#         metric_card(
#             "Max. weiteres Personal pro Bett",
#             "-",
#             "Spalte nicht vorhanden",
#         )


interpretation_box(
    """
    Diese Kennzahlen beziehen sich ausschließlich auf die Personalstruktur.
    Im Vordergrund stehen die Maximalwerte von Ärzten und Pflegern, da diese
    den größten Teil des Personalwesens darstellen.
    """
)



# Analyse 1: Durchschnittliche Personalrelation nach Auffälligkeitsstatus:
section_line()

section_header(
    "Personalrelationen nach Auffälligkeitsstatus",
    "Verglichen werden die durchschnittlichen Personalwerte von auffälligen und nicht auffälligen Krankenhäusern.",
)

vergleich_df = (
    df.groupby("Auffaelligkeit_Status")[vorhandene_personal_spalten]
    .mean()
    .reset_index()
)

vergleich_long = vergleich_df.melt(
    id_vars="Auffaelligkeit_Status",
    value_vars=vorhandene_personal_spalten,
    var_name="Personalmerkmal",
    value_name="Durchschnitt",
)

vergleich_long["Personalmerkmal_Anzeige"] = vergleich_long["Personalmerkmal"].apply(
    schoener_spaltenname
)

with st.expander("Tabelle: Durchschnittliche Personalrelationen anzeigen"):
    tabelle = vergleich_long[
        [
            "Auffaelligkeit_Status",
            "Personalmerkmal_Anzeige",
            "Durchschnitt",
        ]
    ].copy()

    tabelle["Durchschnitt"] = tabelle["Durchschnitt"].round(2)

    tabelle = tabelle.rename(
        columns={
            "Auffaelligkeit_Status": "Auffälligkeitsstatus",
            "Personalmerkmal_Anzeige": "Personalmerkmal",
            "Durchschnitt": "Durchschnittlicher Wert",
        }
    )

    st.dataframe(
        tabelle,
        use_container_width=True,
        hide_index=True,
    )


# Plot 1: Überblick aller Personalrelationen:
section_line()

section_header(
    "Überblick aller Personalrelationen",
    "Dieses Diagramm zeigt alle verfügbaren Personalrelationen im direkten Vergleich zwischen auffälligen und nicht auffälligen Krankenhäusern.",
)

ueberblick_df = vergleich_long.copy()

if not ueberblick_df.empty:
    pivot_df = (
        ueberblick_df.pivot(
            index="Personalmerkmal_Anzeige",
            columns="Auffaelligkeit_Status",
            values="Durchschnitt",
        )
        .fillna(0)
    )

    merkmal_reihenfolge = [
        schoener_spaltenname(spalte)
        for spalte in vorhandene_personal_spalten
    ]

    pivot_df = pivot_df.reindex(merkmal_reihenfolge)

    if "nicht auffällig" in pivot_df.columns:
        status_nicht = pivot_df["nicht auffällig"]
    else:
        status_nicht = pd.Series([0] * len(pivot_df), index=pivot_df.index)

    if "auffällig" in pivot_df.columns:
        status_auff = pivot_df["auffällig"]
    else:
        status_auff = pd.Series([0] * len(pivot_df), index=pivot_df.index)

    y_pos = list(range(len(pivot_df)))
    bar_height = 0.36
    max_value = max(status_nicht.max(), status_auff.max())

    fig, ax = plt.subplots(figsize=(11, 6.5))

    bars1 = ax.barh(
        [y - bar_height / 2 for y in y_pos],
        status_nicht.values,
        height=bar_height,
        color=BAR_COLOR,
        alpha=0.45,
        label="nicht auffällig",
    )

    bars2 = ax.barh(
        [y + bar_height / 2 for y in y_pos],
        status_auff.values,
        height=bar_height,
        color=BAR_COLOR,
        alpha=0.95,
        label="auffällig",
    )

    style_plot(ax)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(pivot_df.index)
    ax.set_xlabel("Durchschnittliche Personalrelation")
    ax.set_ylabel("Personalmerkmal")
    ax.set_title("Überblick aller Personalrelationen nach Auffälligkeitsstatus")

    for bar in bars1:
        breite = bar.get_width()
        ax.text(
            breite + max_value * 0.01 if max_value > 0 else 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{breite:.2f}",
            va="center",
            ha="left",
            color="white",
            fontsize=9,
        )

    for bar in bars2:
        breite = bar.get_width()
        ax.text(
            breite + max_value * 0.01 if max_value > 0 else 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{breite:.2f}",
            va="center",
            ha="left",
            color="white",
            fontsize=9,
        )

    ax.set_xlim(0, max_value * 1.18 if max_value > 0 else 1)
    ax.legend(facecolor="#0e1117", edgecolor="white", labelcolor="white")

    plt.tight_layout()
    st.pyplot(fig)

    interpretation_box(
        """
        Dieses Diagramm zeigt alle Personalrelationen gebündelt in einer Grafik.
        So lässt sich schnell erkennen, bei welchen Personalmerkmalen die Unterschiede
        zwischen auffälligen und nicht auffälligen Krankenhäusern besonders groß oder eher gering ausfallen.
        """,
        title="Interpretation",
    )

else:
    st.info("Für den Überblicksplot liegen keine ausreichenden Personaldaten vor.")


# Scatterplot: Ärzte pro Bett vs. Anteil auffälliger QI:
section_line()

section_header(
    "Ärzte pro Bett und Anteil auffälliger QI",
    "Dieses Diagramm zeigt, ob Krankenhäuser mit mehr ärztlichem Personal pro Bett tendenziell andere Auffälligkeitsanteile zeigen.",
)

if (
    "Aerzte_pro_Bett" in df.columns
    and "Anteil_Auffaellig" in df.columns
    and "Auffaelligkeit" in df.columns
):
    plot_df = df.copy()

    plot_df["Aerzte_pro_Bett"] = pd.to_numeric(
        plot_df["Aerzte_pro_Bett"],
        errors="coerce",
    )

    plot_df["Anteil_Auffaellig_Prozent"] = (
        pd.to_numeric(
            plot_df["Anteil_Auffaellig"],
            errors="coerce",
        )
        * 100
    )

    plot_df["Auffaelligkeit"] = pd.to_numeric(
        plot_df["Auffaelligkeit"],
        errors="coerce",
    )

    plot_df = plot_df.dropna(
        subset=[
            "Aerzte_pro_Bett",
            "Anteil_Auffaellig_Prozent",
            "Auffaelligkeit",
        ]
    )

    if not plot_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))

        nicht_auffaellig = plot_df[plot_df["Auffaelligkeit"] == 0]
        auffaellig = plot_df[plot_df["Auffaelligkeit"] == 1]

        ax.scatter(
            nicht_auffaellig["Aerzte_pro_Bett"],
            nicht_auffaellig["Anteil_Auffaellig_Prozent"],
            color="#60A5FA",
            alpha=0.35,
            s=42,
            edgecolor="white",
            linewidth=0.3,
            label="nicht auffällig",
        )

        ax.scatter(
            auffaellig["Aerzte_pro_Bett"],
            auffaellig["Anteil_Auffaellig_Prozent"],
            color="#14B8A6",
            alpha=0.75,
            s=48,
            edgecolor="white",
            linewidth=0.4,
            label="auffällig",
        )

        # Trendlinie berechnen
        x = plot_df["Aerzte_pro_Bett"]
        y = plot_df["Anteil_Auffaellig_Prozent"]

        if len(plot_df) >= 2 and x.nunique() > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)

            x_line = np.linspace(x.min(), x.max(), 200)
            y_line = p(x_line)

            ax.plot(
                x_line,
                y_line,
                color="white",
                linestyle="--",
                linewidth=2.5,
                label="Trendlinie",
            )

        # x-Achse robust begrenzen, damit Ausreißer den Plot nicht zusammendrücken
        x_max = plot_df["Aerzte_pro_Bett"].quantile(0.99)

        if pd.notna(x_max) and x_max > 0:
            ax.set_xlim(0, x_max)

        style_plot(ax)

        ax.set_title("Zusammenhang zwischen Ärzte pro Bett und auffälligen QI")
        ax.set_xlabel("Ärzte pro Bett")
        ax.set_ylabel("Anteil auffälliger QI in %")

        ax.grid(axis="both", alpha=0.18, color="white")

        ax.legend(
            facecolor="#0e1117",
            edgecolor="white",
            labelcolor="white",
        )

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        interpretation_box(
            """
            Der Scatterplot zeigt den Zusammenhang zwischen ärztlicher Personalrelation
            und dem Anteil auffälliger Qualitätsindikatoren.

            Jeder Punkt steht für ein Krankenhaus.

            Die gestrichelte Linie zeigt die allgemeine Tendenz im Datensatz.
            """,
            title="Interpretation",
        )

    else:
        st.info("Für den Scatterplot liegen keine ausreichenden Werte vor.")

else:
    st.info(
        "Für den Scatterplot fehlen eine oder mehrere Spalten: "
        "`Aerzte_pro_Bett`, `Anteil_Auffaellig`, `Auffaelligkeit`."
    )


# Plot 3: Einzelplots je Personalmerkmal:
# section_line()
#
# section_header(
#     "Einzelvergleich der Personalrelationen",
#     "Die folgenden Diagramme betrachten jedes Personalmerkmal separat.",
# )
#
# for spalte in vorhandene_personal_spalten:
#     plot_df = (
#         df.groupby("Auffaelligkeit_Status", as_index=False)[spalte]
#         .mean()
#         .dropna()
#     )
#
#     plot_df["Auffaelligkeit_Status"] = pd.Categorical(
#         plot_df["Auffaelligkeit_Status"],
#         categories=["nicht auffällig", "auffällig"],
#         ordered=True,
#     )
#
#     plot_df = plot_df.sort_values("Auffaelligkeit_Status")
#
#     if plot_df.empty:
#         continue
#
#     fig, ax = plt.subplots(figsize=(7.5, 4.8))
#
#     bars = ax.bar(
#         plot_df["Auffaelligkeit_Status"].astype(str),
#         plot_df[spalte],
#         color=BAR_COLOR,
#     )
#
#     style_plot(ax)
#
#     ax.set_title(f"{schoener_spaltenname(spalte)} nach Auffälligkeitsstatus")
#     ax.set_xlabel("Auffälligkeitsstatus")
#     ax.set_ylabel(schoener_spaltenname(spalte))
#
#     values = plot_df[spalte].fillna(0).tolist()
#     max_y = max(values) if values else 0
#
#     for bar in bars:
#         hoehe = bar.get_height()
#         ax.text(
#             bar.get_x() + bar.get_width() / 2,
#             hoehe + max_y * 0.02 if max_y > 0 else 0.01,
#             f"{hoehe:.2f}",
#             ha="center",
#             va="bottom",
#             color="white",
#             fontsize=10,
#         )
#
#     ax.set_ylim(0, max_y * 1.20 if max_y > 0 else 1)
#
#     plt.tight_layout()
#     st.pyplot(fig)
#
#
# interpretation_box(
#     """
#     Die Balkendiagramme zeigen, ob sich die durchschnittlichen Personalrelationen
#     zwischen auffälligen und nicht auffälligen Krankenhäusern unterscheiden.
#     Ein sichtbarer Unterschied bedeutet jedoch noch keine Ursache-Wirkungs-Beziehung.
#     Auffällige Krankenhäuser können beispielsweise größer, spezialisierter oder komplexer sein,
#     was sowohl den Personalbedarf als auch die Zahl relevanter Qualitätsindikatoren beeinflusst.
#     """
# )


# Analyse 2: Personalrelation und Anteil auffälliger QI:
# section_line()
#
# section_header(
#     "Zusammenhang mit dem Anteil auffälliger Qualitätsindikatoren",
#     "Hier wird geprüft, ob Personalrelationen mit dem Anteil auffälliger QI zusammenhängen.",
# )
#
# if "Anteil_Auffaellig" in df.columns:
#     korrelationen = []
#
#     for spalte in vorhandene_personal_spalten:
#         temp = df[[spalte, "Anteil_Auffaellig"]].dropna()
#
#         if len(temp) >= 3:
#             corr = temp[spalte].corr(temp["Anteil_Auffaellig"])
#         else:
#             corr = None
#
#         korrelationen.append(
#             {
#                 "Personalmerkmal": schoener_spaltenname(spalte),
#                 "Technische_Spalte": spalte,
#                 "Korrelation_mit_Anteil_Auffaellig": corr,
#                 "Anzahl_Werte": len(temp),
#             }
#         )
#
#     korr_df = pd.DataFrame(korrelationen)

    # with st.expander("Tabelle: Korrelationen anzeigen"):
    #     st.dataframe(
    #         korr_df.rename(
    #             columns={
    #                 "Personalmerkmal": "Personalmerkmal",
    #                 "Korrelation_mit_Anteil_Auffaellig": "Korrelation mit Anteil auffälliger QI",
    #                 "Anzahl_Werte": "Anzahl gültiger Werte",
    #             }
    #         )[
    #             [
    #                 "Personalmerkmal",
    #                 "Korrelation mit Anteil auffälliger QI",
    #                 "Anzahl gültiger Werte",
    #             ]
    #         ],
    #         use_container_width=True,
    #         hide_index=True,
    #     )

#     korr_plot_df = korr_df.dropna(
#         subset=["Korrelation_mit_Anteil_Auffaellig"]
#     ).copy()
#
#     if not korr_plot_df.empty:
#         korr_plot_df = korr_plot_df.sort_values(
#             "Korrelation_mit_Anteil_Auffaellig"
#         )
#
#         fig, ax = plt.subplots(figsize=(10, 5.8))
#
#         bars = ax.barh(
#             korr_plot_df["Personalmerkmal"],
#             korr_plot_df["Korrelation_mit_Anteil_Auffaellig"],
#             color=BAR_COLOR,
#         )
#
#         style_plot(ax)
#
#         ax.set_title("Korrelation der Personalrelationen mit Anteil auffälliger QI")
#         ax.set_xlabel("Korrelationswert")
#         ax.set_ylabel("Personalmerkmal")
#         ax.axvline(0, color="white", linewidth=1)
#
#         for bar in bars:
#             breite = bar.get_width()
#             ax.text(
#                 breite + 0.01 if breite >= 0 else breite - 0.01,
#                 bar.get_y() + bar.get_height() / 2,
#                 f"{breite:.2f}",
#                 ha="left" if breite >= 0 else "right",
#                 va="center",
#                 color="white",
#                 fontsize=10,
#             )
#
#         plt.tight_layout()
#         st.pyplot(fig)
#
#     interpretation_box(
#         """
#         Die Korrelationen zeigen lineare Zusammenhänge zwischen Personalrelationen
#         und dem Anteil auffälliger Qualitätsindikatoren.
#         Werte nahe 0 sprechen für keinen oder nur sehr schwachen linearen Zusammenhang.
#         Positive Werte bedeuten, dass höhere Personalrelationen tendenziell mit höheren
#         Anteilen auffälliger QI einhergehen. Negative Werte bedeuten das Gegenteil.
#         Eine Korrelation beschreibt jedoch keine Kausalität.
#         """
#     )
#
# else:
#     st.info("Die Spalte 'Anteil_Auffaellig' ist nicht vorhanden.")


# Analyse 3: Verteilungskennzahlen:
# section_line()
#
# section_header(
#     "Verteilung der Personalrelationen",
#     "Neben Durchschnittswerten werden Minimum, Maximum und Streuung betrachtet.",
# )
#
# verteilung_liste = []
#
# for spalte in vorhandene_personal_spalten:
#     for status, gruppe in df.groupby("Auffaelligkeit_Status"):
#         werte = gruppe[spalte].dropna()
#
#         if werte.empty:
#             continue
#
#         verteilung_liste.append(
#             {
#                 "Auffaelligkeit_Status": status,
#                 "Personalmerkmal": schoener_spaltenname(spalte),
#                 "Anzahl": len(werte),
#                 "Mittelwert": werte.mean(),
#                 "Minimum": werte.min(),
#                 "Maximum": werte.max(),
#                 "Standardabweichung": werte.std(),
#             }
#         )
#
# verteilung_df = pd.DataFrame(verteilung_liste)
#
# if not verteilung_df.empty:
#     with st.expander("Tabelle: Verteilungskennzahlen anzeigen", expanded=True):
#         st.dataframe(
#             verteilung_df.rename(
#                 columns={
#                     "Auffaelligkeit_Status": "Auffälligkeitsstatus",
#                     "Personalmerkmal": "Personalmerkmal",
#                     "Anzahl": "Anzahl Werte",
#                 }
#             ),
#             use_container_width=True,
#             hide_index=True,
#         )
#
#     interpretation_box(
#         """
#         Minimum und Maximum zeigen die Spannweite der Personalrelationen.
#         Der Mittelwert beschreibt die durchschnittliche Ausprägung.
#         Besonders große Spannweiten können auf sehr unterschiedliche Krankenhausstrukturen,
#         Dokumentationsunterschiede oder Extremwerte im Datensatz hinweisen.
#         """
#     )
#
# else:
#     st.info("Für die Verteilungsanalyse liegen keine ausreichenden Personalwerte vor.")


# Zusammenfassung:
section_line()

section_header(
    "Zwischenfazit zur Personalhypothese",
    "Die Personalmerkmale liefern Hinweise auf mögliche Zusammenhänge, aber keine kausale Erklärung.",
)

notice_box(
    text="""
    Unterschiede in Personalrelationen können mit Auffälligkeitsmustern zusammenhängen.
    Gleichzeitig können sie durch Krankenhausgröße, Fachabteilungen, Spezialisierung,
    Fallmix und Versorgungsauftrag beeinflusst sein.
    
    Deshalb sollte diese Hypothese nicht als Aussage verstanden werden,
    dass eine bestimmte Personalrelation automatisch zu mehr oder weniger Qualität führt.
    Sie zeigt vielmehr, ob Personalstruktur im Datensatz als möglicher Kontextfaktor sichtbar wird.
    """,
    title="Fachliche Einordnung",
)


scroll_to_top_button()