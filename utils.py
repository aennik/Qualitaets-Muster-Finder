# Import:
import pandas as pd

# Zielvariable vorbereiten:
def prepare_auffaelligkeit(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Bereitet die Zielvariable Auffaelligkeit einheitlich vor.

    Logik:
    - Falls Auffaelligkeit fehlt, wird Problem_vorhanden als Fallback genutzt.
    - Werte werden numerisch gemacht.
    - Auffaelligkeit_Status wird erzeugt.
    '''

    df = df.copy()

    if 'Auffaelligkeit' not in df.columns:
        if 'Problem_vorhanden' in df.columns:
            df['Auffaelligkeit'] = df['Problem_vorhanden']
        else:
            df['Auffaelligkeit'] = 0

    df['Auffaelligkeit'] = (
        pd.to_numeric(df['Auffaelligkeit'], errors='coerce')
        .fillna(0)
        .astype(int)
    )

    df['Auffaelligkeit'] = df['Auffaelligkeit'].clip(lower=0, upper=1)

    df['Auffaelligkeit_Status'] = df['Auffaelligkeit'].map(
        {
            0: 'nicht auffällig',
            1: 'auffällig',
        }
    )

    return df


# Qualitätsmerkmale vorbereiten:
def prepare_quality_metrics(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Bereitet zentrale Qualitätskennzahlen numerisch vor.
    '''

    df = df.copy()

    numeric_cols = [
        'Anzahl_QI',
        'Anzahl_Auffaellig',
        'Anteil_Auffaellig',
        'Ueber_Median_Auffaellig',
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


# Prozentspalten ergänzen:
def add_percent_columns(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Ergänzt Prozentspalten für Anzeige und Filter.
    '''

    df = df.copy()

    if 'Anteil_Auffaellig' in df.columns:
        df['Anteil_Auffaellig_Prozent'] = df['Anteil_Auffaellig'] * 100

    if 'Fortbildungsquote' in df.columns:
        df['Fortbildungsquote_Prozent'] = df['Fortbildungsquote'] * 100

    return df


# Gesamte Standart-Vorbereitung:
def prepare_analysis_df(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Standard-Vorbereitung für df_analyse.
    Diese Funktion sollte auf fast jeder Page direkt nach dem Laden genutzt werden.
    '''

    df = df.copy()

    df = prepare_auffaelligkeit(df)
    df = prepare_quality_metrics(df)
    df = add_percent_columns(df)

    return df


# Anzahlspalte automatisch finden:
def finde_anzahl_spalte(df_input: pd.DataFrame) -> str:
    '''
    Sucht in aggregierten Tabellen nach einer passenden Anzahlspalte.
    '''

    moegliche_spalten = [
        'Anzahl_betroffener_Krankenhaeuser',
        'Anzahl_Krankenhaeuser',
        'Anzahl_Auffaellige_QI_Zeilen',
        'Anzahl_Unterschiedliche_Indikatoren',
        'Anzahl_Auffaellig',
        'Anzahl',
        'Haeufigkeit',
        'count',
    ]

    for spalte in moegliche_spalten:
        if spalte in df_input.columns:
            return spalte

    numerische_spalten = df_input.select_dtypes(include='number').columns

    if len(numerische_spalten) > 0:
        return numerische_spalten[-1]

    return df_input.columns[-1]



# Qualitätsindikatoren = Kurzlabel:
def qi_kurzlabel(text) -> str:
    '''
    Kürzt lange QI-Bezeichnungen für lesbare Diagramme.
    '''

    text = str(text)
    code = text.split()[0] if text else ''

    qi_labels = {
        '52010': 'Komplikationen im Krankenhaus',
        '161800': 'Komplikationen bei Eingriff',
        '50722': 'Atemfrequenz',
        '52009': 'Behandlungsverlauf',
        '54030': 'Wartezeit vor OP',
        '54003': 'Wartezeit vor Eingriff',
        '101800': 'Erhöhtes OP-Risiko',
        '56005': 'Röntgenbelastung',
        '2194': 'Ist-/Soll-Verhältnis',
        '52249': 'Kaiserschnitt',
    }

    if code in qi_labels:
        return qi_labels[code]

    if len(text) > 42:
        return text[:42] + '...'

    return text



# Gruppierung nach Auffälligkeit:
def gruppiere_nach_auffaelligkeit(
    df: pd.DataFrame,
    gruppen_spalte: str,
    anteil_spalte: str = 'Anteil_Auffaellig',
) -> pd.DataFrame:
    '''
    Erstellt eine Standard-Auswertung nach einer Kategorie.
    Beispiel:
    - Trägerschaft
    - Bundesland
    - Stadtklasse
    - Uni_Status
    '''

    if gruppen_spalte not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    qbid_col = 'SO.QBID' if 'SO.QBID' in df.columns else df.columns[0]

    agg_df = (
        df.groupby(gruppen_spalte, as_index=False)
        .agg(
            Anzahl_Krankenhaeuser=(qbid_col, 'nunique'),
            Anzahl_Auffaellig=('Auffaelligkeit', 'sum'),
            Anteil_Auffaelligkeit=('Auffaelligkeit', 'mean'),
            Durchschnitt_Anteil_Auffaellig=(anteil_spalte, 'mean'),
        )
    )

    agg_df['Anteil_Auffaelligkeit_Prozent'] = (
        agg_df['Anteil_Auffaelligkeit'] * 100
    )

    agg_df['Durchschnitt_Anteil_Auffaellig_Prozent'] = (
        agg_df['Durchschnitt_Anteil_Auffaellig'] * 100
    )

    return agg_df


# Standarddaten für Pages laden:
#def load_prepared_analysis_data():
#   """
#    Lädt df_analyse über data_loader und bereitet die Analyse-Daten standardisiert vor.
#    Diese Funktion kann auf allen Pages genutzt werden.
#   """
#
#   from data_loader import load_all_data
#
#   data = load_all_data()
#  df = data["df_analyse"]
# df = prepare_analysis_df(df)
#
#   return data, df