# Imports:
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_loader import load_all_data

from utils import(
    prepare_analysis_df,
    finde_anzahl_spalte,
    qi_kurzlabel,
)


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
    scroll_to_top_button
)


# Seiteneinstellungen:
st.set_page_config(
    page_title='Datenübersicht | Krankenhausanalyse',
    page_icon='📋',
    layout='wide'
)


# Design anwenden:
apply_design()

sidebar_logo_bottom()
page_top_anchor()
#page_navigation("daten")


# Daten laden:
data = load_all_data()

df = data['df_analyse']
top_indikatoren = data['top_indikatoren']
top_leistungsbereiche = data['top_leistungsbereiche']


# Daten vorbereiten:
df = prepare_analysis_df(df)

# Plot-Hilfsfunktion:
def style_plot(ax):
    '''
    Einheitliches dunkles Plot-Design passend zum App-Hintergrund.
    '''

    ax.set_facecolor('#0e1117')
    ax.figure.set_facecolor('#0e1117')

    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

    for spine in ax.spines.values():
        spine.set_color('white')

# Funktion für Tausenderpunkte und Prozentwerte mit Komma:
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
    title='📋 Datenübersicht',
    text='''
    Diese Seite gibt einen ersten Überblick über die Analysebasis.
    Im Fokus stehen die Anzahl der betrachteten Krankenhäuser, der Anteil auffälliger Häuser
    sowie die Verteilung auffälliger Qualitätsindikatoren.
    <br><br>
    Die Datenübersicht bildet die Grundlage für die späteren Analysen und die interaktive Karte.
    ''',
    note='''
    Die zentrale Zielvariable ist <b>Auffälligkeit</b>: Ein Krankenhaus gilt als auffällig,
    wenn mindestens ein auffälliger Qualitätsindikator vorliegt.
    ''',
)


# Kennzahlen berechnen:
# Kachel 1: Anzahl aller Krankenhäuser im Analysedatensatz
anzahl_haeuser = (
    df["SO.QBID"].nunique()
    if "SO.QBID" in df.columns
    else len(df)
)


# Kachel 2: Anzahl Krankenhäuser mit mindestens einem auffälligen QI
anzahl_auffaellig = int(df["Auffaelligkeit"].sum())


# Kachel 3:
# Anzahl Krankenhäuser ohne auffälligen QI
anzahl_nicht_auffaellig = int((df["Auffaelligkeit"] == 0).sum())


# Kachel 4: Anzahl unterschiedlicher echter Qualitätsindikatoren
# Wert kommt aus eurer Ursprungsauswertung:
# qi["QSQI.Indikator"].nunique()
anzahl_echte_qi = 203


# Kachel 5: Anzahl unterschiedlicher Indikatoren, die mindestens einmal auffällig waren
# Wert kommt aus eurer Ursprungsauswertung:
# auffaellige_indikatoren_detail["QSQI.Indikator"].nunique()
anzahl_unterschiedliche_auffaellige_indikatoren = 131


# Kachel 6: Maximale Anzahl auffälliger QI bei einem Krankenhaus
if "Anzahl_Auffaellig" in df.columns:
    max_auff_qi_je_krankenhaus = int(df["Anzahl_Auffaellig"].max())
else:
    max_auff_qi_je_krankenhaus = 9


# Kachel 7:
# Anteil auffälliger Krankenhäuser
anteil_auffaellige_kh = round(
    (anzahl_auffaellig / anzahl_haeuser) * 100,
    2,
)


# Kachel 8: Anteil der echten Qualitätsindikatoren, die mindestens einmal auffällig waren
anteil_auffaellige_indikatoren = round(
    (anzahl_unterschiedliche_auffaellige_indikatoren / anzahl_echte_qi) * 100,
    2,
)


# Kachel 9:
# Durchschnittlicher Anteil je auffälligem Indikator
durchschnitt_anteil_auffaellige_qi_je_kh = round(
    df["Anteil_Auffaellig_Prozent"].mean(),
    2,
)



# Kennzahlen anzeigen:
section_header(
    "Zentrale Kennzahlen der Datenbasis",
    "Diese Kennzahlen beschreiben Umfang und Spannweite der Analysegrundlage.",
)

# Reihe 1: Krankenhäuser
col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Krankenhäuser",
        format_kpi(anzahl_haeuser),
        "Standorte im Analysedatensatz",
    )

with col2:
    metric_card(
        "Auffällige Krankenhäuser",
        format_kpi(anzahl_auffaellig),
        "mindestens ein auffälliger QI",
    )

with col3:
    metric_card(
        "Anteil auffälliger KH",
        format_kpi(anteil_auffaellige_kh, 2) + " %",
        f"{format_kpi(anzahl_auffaellig)} von {format_kpi(anzahl_haeuser)} Krankenhäusern",
    )

# with col3:
#     metric_card(
#         "Nicht auffällige Krankenhäuser",
#         format_kpi(anzahl_nicht_auffaellig),
#         "kein auffälliger QI",
#     )


# Reihe 2: Qualitätsindikatoren
col4, col5, col6 = st.columns(3)

with col4:
    metric_card(
        "Echte Qualitätsindikatoren",
        format_kpi(anzahl_echte_qi),
        "unterschiedliche betrachtete QI",
    )

with col5:
    metric_card(
        "Auffällige Indikatoren",
        format_kpi(anzahl_unterschiedliche_auffaellige_indikatoren),
        "unterschiedliche QI mit Auffälligkeit",
    )

with col6:
    metric_card(
        "Anteil auffälliger Indikatoren",
        format_kpi(anteil_auffaellige_indikatoren, 2) + " %",
        f"{format_kpi(anzahl_unterschiedliche_auffaellige_indikatoren)} von {format_kpi(anzahl_echte_qi)} echten QI",
    )


# Reihe 3: abgeleitete Kennzahlen
col7, col8, col9 = st.columns(3)
with col7:
    metric_card(
        "Max. auffällige QI",
        format_kpi(max_auff_qi_je_krankenhaus),
        "höchster Wert je Krankenhaus",
    )

with col8:
    metric_card(
        "Ø Auffällige QI nach KH",
        "2-3",
        "durchschnittliche Anzahl auffälliger QI pro Krankenhaus"
    )

with col9:
    metric_card(
        "Ø Anteil auffälliger QI je KH",
        format_kpi(durchschnitt_anteil_auffaellige_qi_je_kh, 2) + " %",
        "durchschnittlicher Anteil auffälliger QI pro Krankenhaus",
    )


interpretation_box(
    """
    Die Kennzahlen beschreiben die Datenbasis der Analyse. Im Mittelpunkt stehen Anzahl und Spannweite: 
    Wie viele Krankenhäuser werden betrachtet, wie viele davon sind auffällig und wie viele Qualitätsindikatoren liegen insgesamt vor.
    """
)


# Plot 1: Problemstatus:
# section_line()
#
# section_header(
#     'Verteilung der Krankenhäuser nach Auffälligkeit',
#     'Der Plot zeigt, wie viele Krankenhäuser mindestens einen auffälligen Qualitätsindikator aufweisen.',
# )
#
# status_counts = (
#     df['Auffaelligkeit_Status']
#     .value_counts()
#     .reindex(['nicht auffällig', 'auffällig'])
#     .fillna(0)
#     .astype(int)
# )
#
# gesamt = status_counts.sum()
#
# if gesamt > 0:
#     plot_labels = [
#         f'nicht auffällig\n({status_counts['nicht auffällig'] / gesamt * 100:.2f}%)',
#         f'auffällig\n({status_counts['auffällig'] / gesamt * 100:.2f}%)',
#     ]
#
#     plot_values = [
#         status_counts['nicht auffällig'],
#         status_counts['auffällig'],
#     ]
#
#     fig, ax = plt.subplots(figsize=(8, 5))
#
#     bars = ax.bar(
#         plot_labels,
#         plot_values,
#         color=BAR_COLOR,
#     )
#
#     style_plot(ax)
#
#     ax.set_title('Verteilung der Krankenhäuser nach Auffälligkeit')
#     ax.set_ylabel('Anzahl Krankenhäuser')
#
#     for bar in bars:
#         hoehe = bar.get_height()
#         ax.text(
#             bar.get_x() + bar.get_width() / 2,
#             hoehe + max(plot_values) * 0.02,
#             f'{int(hoehe)}',
#             ha='center',
#             va='bottom',
#             color='white',
#         )
#
#     ax.set_ylim(0, max(plot_values) * 1.15 if max(plot_values) > 0 else 1)
#     plt.tight_layout()
#
#     st.pyplot(fig)
#
#     interpretation_box(
#         '''
#         Die Mehrheit der Krankenhäuser weist keinen auffälligen Qualitätsindikator auf.
#         Gleichzeitig zeigt der Anteil der auffälligen Krankenhäuser, dass Auffälligkeiten
#         im Datensatz eine relevante Gruppe bilden und für die weiteren Analysen berücksichtigt werden sollten.
#         '''
#     )
#
# else:
#     st.warning('Für die Verteilung der Auffälligkeit sind keine Daten vorhanden.')


# Plot 1: Verteilung der Auffälligkeiten
section_line()

section_header(
    "Wie häufig treten statistische Auffälligkeiten auf?",
    "Das Diagramm vergleicht alle Krankenhäuser mit den auffälligen Krankenhäusern.",
)

if "Anteil_Auffaellig" in df.columns and "Auffaelligkeit" in df.columns:
    overlay_df = df.copy()

    overlay_df["Anteil_Auffaellig_Prozent"] = (
        pd.to_numeric(overlay_df["Anteil_Auffaellig"], errors="coerce") * 100
    )

    overlay_df["Auffaelligkeit"] = pd.to_numeric(
        overlay_df["Auffaelligkeit"],
        errors="coerce",
    )

    overlay_df = overlay_df.dropna(
        subset=["Anteil_Auffaellig_Prozent", "Auffaelligkeit"]
    )

    alle_haeuser = overlay_df["Anteil_Auffaellig_Prozent"]

    auffaellige_haeuser = overlay_df.loc[
        overlay_df["Auffaelligkeit"] == 1,
        "Anteil_Auffaellig_Prozent",
    ]

    if not overlay_df.empty and not auffaellige_haeuser.empty:
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(
            alle_haeuser,
            bins=30,
            alpha=0.35,
            label="Alle Krankenhäuser",
            color="#60A5FA",
            linewidth=0.8,
        )

        ax.hist(
            auffaellige_haeuser,
            bins=30,
            alpha=0.75,
            label="Auffällige Krankenhäuser",
            color="#14B8A6",
            linewidth=0.8,
        )

        durchschnitt = alle_haeuser.mean()
        median = alle_haeuser.median()

        ax.axvline(
            durchschnitt,
            color="white",
            linestyle="--",
            linewidth=2.0,
            label=f"Ø Anteil je Krankenhaus: {durchschnitt:.2f} %",
        )

        ax.axvline(
            median,
            color="#EF4444",
            linestyle=":",
            linewidth=2.8,
            label=f"Median je Krankenhaus: {median:.2f} %",
        )

        ax.set_xlim(-2, 30)
        style_plot(ax)

        ax.set_title("Verteilung des Anteils auffälliger QI je Krankenhaus")
        ax.set_xlabel("Anteil auffälliger QI in %")
        ax.set_ylabel("Anzahl Krankenhäuser")

        ax.legend(
            facecolor="#0e1117",
            edgecolor="white",
            labelcolor="white",
        )

        ax.grid(axis="y", alpha=0.15)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info("Für das Histogramm liegen keine ausreichenden Werte vor.")

else:
    st.info(
        "Die Spalten `Anteil_Auffaellig` und/oder `Auffaelligkeit` sind im Datensatz nicht vorhanden."
    )

interpretation_box(
    """
    Das Histogramm zeigt die Verteilung des Anteils auffälliger Qualitätsindikatoren je Krankenhaus. Die meisten Krankenhäuser
    liegen bei sehr niedrigen Werten oder bei 0 %. Deshalb liegt auch der Median bei 0,00 %.

    Der Durchschnitt liegt mit rund 1,84 % höher, weil einige wenige Krankenhäuser deutlich höhere Auffälligkeitsanteile
    aufweisen und den Mittelwert nach oben ziehen.

    Die auffälligen Krankenhäuser bilden dabei die Teilgruppe der Häuser mit mindestens einem auffälligen Qualitätsindikator.
    """,
    title="Interpretation",
)

# Zusatzplot: Anteil auffälliger QI nach Anzahl QI:
section_line()

section_header(
    "Zusammenhang zwischen Anzahl QI und Anteil auffälliger QI",
    "Der Plot zeigt, wie stark der Anteil auffälliger Qualitätsindikatoren von der Anzahl betrachteter QI abhängen kann.",
)

if "Anzahl_QI" in df.columns and "Anteil_Auffaellig" in df.columns:
    plot_df = df.copy()

    plot_df["Anzahl_QI"] = pd.to_numeric(
        plot_df["Anzahl_QI"],
        errors="coerce",
    )

    plot_df["Anteil_Auffaellig_Prozent"] = (
        pd.to_numeric(
            plot_df["Anteil_Auffaellig"],
            errors="coerce",
        )
        * 100
    )

    plot_df = plot_df.dropna(
        subset=[
            "Anzahl_QI",
            "Anteil_Auffaellig_Prozent",
            "Auffaelligkeit",
        ]
    )

    if not plot_df.empty:
        fig, ax = plt.subplots(figsize=(10, 5.8))

        # Nicht auffällige Krankenhäuser heller darstellen
        nicht_auff = plot_df[plot_df["Auffaelligkeit"] == 0]

        ax.scatter(
            nicht_auff["Anzahl_QI"],
            nicht_auff["Anteil_Auffaellig_Prozent"],
            color=BAR_COLOR,
            alpha=0.22,
            s=40,
            label="nicht auffällig",
        )

        # Auffällige Krankenhäuser kräftiger darstellen
        auff = plot_df[plot_df["Auffaelligkeit"] == 1]

        ax.scatter(
            auff["Anzahl_QI"],
            auff["Anteil_Auffaellig_Prozent"],
            color=BAR_COLOR,
            alpha=0.85,
            s=48,
            label="auffällig",
        )

        # Trendlinie über alle Punkte
        if len(plot_df) >= 2 and plot_df["Anzahl_QI"].nunique() > 1:
            x = plot_df["Anzahl_QI"]
            y = plot_df["Anteil_Auffaellig_Prozent"]

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)

            x_line = np.linspace(x.min(), x.max(), 200)
            y_line = p(x_line)

            ax.plot(
                x_line,
                y_line,
                color="white",
                linestyle="--",
                linewidth=2.2,
                label="Trendlinie",
            )

        style_plot(ax)

        ax.set_title("Anteil auffälliger QI nach Anzahl betrachteter QI")
        ax.set_xlabel("Anzahl Qualitätsindikatoren")
        ax.set_ylabel("Anteil auffälliger QI in %")

        ax.legend(
            facecolor="#0e1117",
            edgecolor="white",
            labelcolor="white",
        )

        plt.tight_layout()
        st.pyplot(fig)

        interpretation_box(
            """
            Der Plot zeigt, dass der Anteil auffälliger QI bei wenigen Indikatoren stark schwanken kann.
            Eine einzelne Auffälligkeit wirkt dort besonders stark. Bei vielen QI ist der Anteil stabiler, 
            da einzelne Auffälligkeiten weniger Gewicht haben. Die Trendlinie zeigt die grobe Richtung des Zusammenhangs.
            """,
            title="Interpretation",
        )

        # notice_box(
        #     """
        #     Ein hoher Anteil auffälliger QI sollte immer zusammen mit der Anzahl der betrachteten
        #     Qualitätsindikatoren interpretiert werden.
        #     """,
        #     title="Hinweis zur Interpretation:",
        # )

    else:
        st.info("Für den Plot liegen keine ausreichenden Werte vor.")

else:
    st.info(
        "Die Spalten `Anzahl_QI` und/oder `Anteil_Auffaellig` sind im Datensatz nicht vorhanden."
    )



# Plot 2: Top 10 Leistungsbereiche:
section_line()

section_header(
    'Top 10 Leistungsbereiche mit auffälligen Qualitätsindikatoren',
    'Leistungsbereiche fassen auffällige Qualitätsindikatoren thematisch zusammen.',
)

if not top_leistungsbereiche.empty:
    top_lb = top_leistungsbereiche.copy()

    if 'Leistungsbereich_Code' in top_lb.columns:
        leistungsbereich_col = 'Leistungsbereich_Code'
    else:
        leistungsbereich_col = top_lb.columns[0]

    anzahl_col_lb = finde_anzahl_spalte(top_lb)

    top10_lb = (
        top_lb
        .sort_values(anzahl_col_lb, ascending=False)
        .head(10)
        .copy()
    )

    with st.expander("Top 10 Leistungsbereiche als Tabelle anzeigen"):
        tabelle_leistungsbereiche = top_leistungsbereiche.copy()

        tabelle_leistungsbereiche = tabelle_leistungsbereiche.rename(
            columns={
                "QSQI.Leistungsbereich": "Leistungsbereich",
                "Anzahl_Auffaellige_QI_Zeilen": "Anzahl auffälliger QI-Zeilen",
                "Anzahl_Unterschiedliche_Indikatoren": "Anzahl unterschiedlicher Indikatoren",
                "Anzahl betroffener Krankenhaeuser": "Anzahl betroffener Krankenhäuser",
                "Anzahl_betroffener_Krankenhaeuser": "Anzahl betroffener Krankenhäuser",
                "Leistungsbereich_Code": "Leistungsbereich-Code",
                "Anzahl_Krankenhaeuser": "Anzahl Krankenhäuser",
            }
        )

        st.dataframe(
            tabelle_leistungsbereiche,
            use_container_width=True,
            hide_index=True,
        )

    plot_lb = top10_lb.sort_values(anzahl_col_lb)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(
        plot_lb[leistungsbereich_col].astype(str),
        plot_lb[anzahl_col_lb],
        color=BAR_COLOR,
    )

    style_plot(ax)

    ax.set_title('Top 10 Leistungsbereiche mit auffälligen Qualitätsindikatoren')
    ax.set_xlabel('Anzahl betroffener Krankenhäuser')
    ax.set_ylabel('Leistungsbereich')

    max_value_lb = plot_lb[anzahl_col_lb].max()

    for bar in bars:
        breite = bar.get_width()
        ax.text(
            breite + max_value_lb * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{int(breite)}',
            va='center',
            ha='left',
            color='white',
        )

    ax.set_xlim(0, max_value_lb * 1.12 if max_value_lb > 0 else 1)
    plt.tight_layout()

    st.pyplot(fig)

    interpretation_box(
        '''
        Die Leistungsbereiche zeigen, in welchen medizinischen Themenfeldern Auffälligkeiten besonders häufig auftreten.
        Dadurch lassen sich einzelne Qualitätsindikatoren besser fachlich einordnen.
        '''
    )

else:
    st.info('Die Datei mit den Top-Leistungsbereichen wurde nicht gefunden oder ist leer.')


# Plot 3: Top 10 einzelne auffällige Qualitätsindikatoren:
section_line()

section_header(
    'Top 10 einzelne auffällige Qualitätsindikatoren',
    'Die langen Indikatorbeschreibungen werden für die Grafik auf kurze Schlagwörter reduziert.',
)

if not top_indikatoren.empty:
    top_qi = top_indikatoren.copy()

    if 'QSQI.Indikator' in top_qi.columns:
        indikator_col = 'QSQI.Indikator'
    else:
        indikator_col = top_qi.columns[0]

    anzahl_col = finde_anzahl_spalte(top_qi)

    top10_qi = (
        top_qi
        .sort_values(anzahl_col, ascending=False)
        .head(10)
        .copy()
    )

    top10_qi['QI_Kurzlabel'] = top10_qi[indikator_col].apply(qi_kurzlabel)

    with st.expander("Top 10 einzelne auffällige Qualitätsindikatoren als Tabelle anzeigen"):
        tabelle_indikatoren = top_indikatoren.copy()

        # Technische Spaltennamen in lesbare Namen umbenennen
        tabelle_indikatoren = tabelle_indikatoren.rename(
            columns={
                "QSQI.Indikator": "Qualitätsindikator",
                "QSQI.Leistungsbereich": "Leistungsbereich",
                "Leistungsbereich_Code": "Leistungsbereich-Code",
                "Anzahl_betroffener_Krankenhaeuser": "Anzahl betroffener Krankenhäuser",
                "Anzahl betroffener Krankenhaeuser": "Anzahl betroffener Krankenhäuser",
                "Anzahl_Auffaellige_QI_Zeilen": "Anzahl auffälliger QI-Zeilen",
                "Kurzlabel": "Kurzlabel",
            }
        )

        # Nur die wichtigsten Spalten anzeigen, falls sie vorhanden sind
        spalten_anzeigen = [
            "Qualitätsindikator",
            "Leistungsbereich",
            "Leistungsbereich-Code",
            "Anzahl betroffener Krankenhäuser",
            "Kurzlabel",
        ]

        spalten_anzeigen = [
            spalte for spalte in spalten_anzeigen
            if spalte in tabelle_indikatoren.columns
        ]

        st.dataframe(
            tabelle_indikatoren[spalten_anzeigen],
            use_container_width=True,
            hide_index=True,
        )

    plot_qi = top10_qi.sort_values(anzahl_col)

    fig, ax = plt.subplots(figsize=(11, 6.5))

    bars = ax.barh(
        plot_qi['QI_Kurzlabel'],
        plot_qi[anzahl_col],
        color=BAR_COLOR,
    )

    style_plot(ax)

    ax.set_title('Top 10 einzelne auffällige Qualitätsindikatoren')
    ax.set_xlabel('Anzahl betroffener Krankenhäuser')
    ax.set_ylabel('Qualitätsindikator')

    max_value_qi = plot_qi[anzahl_col].max()

    for bar in bars:
        breite = bar.get_width()
        ax.text(
            breite + max_value_qi * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{int(breite)}',
            va='center',
            ha='left',
            color='white',
        )

    ax.set_xlim(0, max_value_qi * 1.12 if max_value_qi > 0 else 1)
    plt.tight_layout()

    st.pyplot(fig)

    interpretation_box(
        '''
        Der Plot zeigt, welche Qualitätsindikatoren am häufigsten bei auffälligen Krankenhäusern vorkommen.
        Besonders sichtbar sind Themen wie Komplikationen, Atemfrequenz und Behandlungsverlauf.
        Die Darstellung zeigt Häufigkeiten im Datensatz, aber keine direkte Bewertung einzelner Krankenhäuser. 
        '''
    )

else:
    st.info('Die Datei mit den Top-Indikatoren wurde nicht gefunden oder ist leer.')


# Abschließender Hinweis:
notice_box(
    '''
    Die Datenübersicht beschreibt erste Muster im Datensatz. Sie liefert jedoch noch keine Ursachenanalyse.
    Auffälligkeiten sollten deshalb immer zusammen mit Krankenhausgröße,
    Versorgungsauftrag, Spezialisierung und regionalen Unterschieden betrachtet werden.
    ''',
    title='Hinweis zur Interpretation',
)

scroll_to_top_button()