# Imports:
from pathlib import Path

import pandas as pd
import streamlit as st


# Pfade:
BASE_DIR = Path(__file__).resolve().parent
DATA = BASE_DIR / 'data'

DF_PATH = DATA / 'df_analyse.parquet'
QI_DETAIL_PATH = DATA / 'auffaellige_indikatoren_detail.parquet'
TOP_INDIKATOR_PATH = DATA / 'top_auffaellige_indikatoren.parquet'
TOP_LEISTUNGSBEREICH_PATH = DATA / 'top_auffaellige_leistungsbereiche.parquet'
INDIKATOR_VERGLEICH_PATH = DATA / 'indikator_vergleich.parquet'
INDIKATOR_VERGLEICH_GEFILTERT_PATH = DATA / 'indikator_vergleich_gefiltert.parquet'
LEGENDE_PATH = DATA / 'leistungsbereich_legende_final.parquet'
CODE_INDIKATOR_LEGENDE_PATH = DATA / 'code_indikator_legende.parquet'

BUNDESLAENDER_GEOJSON_PATH = DATA / 'bundeslaender.geojson'


# Ladefunktionen:
@st.cache_data
def load_parquet(path: Path) -> pd.DataFrame:
    '''
    Lädt eine verpflichtende Parquet-Datei.
    Wenn sie fehlt, wird ein verständlicher Fehler ausgelöst.
    '''

    if not path.exists():
        raise FileNotFoundError(f'Datei nicht gefunden: {path}')

    return pd.read_parquet(path)


@st.cache_data
def load_optional_parquet(path: Path) -> pd.DataFrame:
    '''
    Lädt eine optionale Parquet-Datei.
    Falls die Datei fehlt, wird ein leerer DataFrame zurückgegeben.
    '''

    if path.exists():
        return pd.read_parquet(path)

    return pd.DataFrame()


def load_all_data() -> dict:
    '''
    Lädt alle vorbereiteten Analyse-Dateien für die Streamlit-App.
    '''

    df_analyse = load_parquet(DF_PATH)

    qi_detail = load_optional_parquet(QI_DETAIL_PATH)

    top_indikatoren = load_optional_parquet(TOP_INDIKATOR_PATH)
    top_leistungsbereiche = load_optional_parquet(TOP_LEISTUNGSBEREICH_PATH)

    indikator_vergleich = load_optional_parquet(INDIKATOR_VERGLEICH_PATH)
    indikator_vergleich_gefiltert = load_optional_parquet(
        INDIKATOR_VERGLEICH_GEFILTERT_PATH
    )

    leistungsbereich_legende = load_optional_parquet(LEGENDE_PATH)
    code_indikator_legende = load_optional_parquet(CODE_INDIKATOR_LEGENDE_PATH)

    return {
        'df_analyse': df_analyse,
        'qi_detail': qi_detail,
        'top_indikatoren': top_indikatoren,
        'top_leistungsbereiche': top_leistungsbereiche,
        'indikator_vergleich': indikator_vergleich,
        'indikator_vergleich_gefiltert': indikator_vergleich_gefiltert,
        'leistungsbereich_legende': leistungsbereich_legende,
        'code_indikator_legende': code_indikator_legende,
        'bundeslaender_geojson_path': BUNDESLAENDER_GEOJSON_PATH,
    }