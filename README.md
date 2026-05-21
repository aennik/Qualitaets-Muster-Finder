<div align="center">

# Qualitäts-Muster-Finder 🏥

### Krankenhausanalyse · Qualitätsindikatoren · Mustererkennung

![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=plastic&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=plastic&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualisierung-3F4F75?style=plastic&logo=plotly&logoColor=white)
![KNIME](https://img.shields.io/badge/KNIME-Modell-FDD800?style=plastic&logoColor=black)
![Healthcare](https://img.shields.io/badge/Healthcare-Data%20Analysis-2E8B57?style=plastic)

</div>

---

## Worum geht es?

Der **Qualitäts-Muster-Finder** ist mein Abschlussprojekt aus der Weiterbildung zur Data Analystin.

In dem Projekt analysiere ich Qualitätsdaten deutscher Krankenhäuser und untersuche, ob sich Muster zwischen auffälligen Qualitätsindikatoren und strukturellen Merkmalen erkennen lassen.

Dabei geht es nicht darum, einzelne Krankenhäuser zu bewerten.  
Der Fokus liegt darauf, Daten aufzubereiten, Zusammenhänge sichtbar zu machen und Ergebnisse verständlich darzustellen.

---

## Fragestellungen

Im Projekt geht es unter anderem um Fragen wie:

- Welche Qualitätsindikatoren treten besonders häufig auffällig auf?
- Gibt es Unterschiede nach Krankenhausgröße?
- Spielen Uni-Status, Trägerschaft oder Fachabteilungen eine Rolle?
- Lassen sich regionale Muster erkennen?
- Wie können die Ergebnisse interaktiv dargestellt werden?

---

## Was ich dabei gemacht habe

| Bereich | Inhalt |
|---|---|
| Datenaufbereitung | Einlesen, Bereinigen und Zusammenführen verschiedener Datentabellen |
| Zielvariable | Erstellung einer Logik für auffällige Qualitätsindikatoren |
| Analyse | Untersuchung von Qualitätsindikatoren und Krankenhausmerkmalen |
| Visualisierung | Diagramme, Kennzahlen und Vergleichsansichten |
| Streamlit-App | Interaktive Darstellung der Ergebnisse mit mehreren Seiten |
| KNIME-Modell | Einfacher Decision Tree zur Einschätzung einer Risikogruppe |

---

## App-Bereiche

Die Streamlit-App enthält mehrere Bereiche, zum Beispiel:

- Startseite mit Projektüberblick
- Daten- und Kennzahlenübersicht
- Analyse auffälliger Qualitätsindikatoren
- Strukturmerkmale von Krankenhäusern
- Hypothesenbasierte Auswertungen
- Interaktive Kartenansicht
- KNIME-Modell / Risiko-Rechner

---

## Projektstruktur

```text
qualitaets-muster-finder/
│
├── 00_Krankenhausanalyse.py
├── data_loader.py
├── design.py
├── utils.py
│
├── pages/
│   ├── 01_Startseite.py
│   ├── 02_Datenuebersicht.py
│   ├── 03_Krankenhausstruktur.py
│   ├── 04_Personalstruktur.py
│   ├── 05_Fortbildung.py
│   ├── 06_Uni_Status.py
│   ├── 07_Traegerschaft.py
│   ├── 08_Korrelationen.py
│   ├── 09_Regionale_Muster.py
│   ├── 10_Uebersichtskarte.py
│   └── 11_Schlusswort.py
│
├── assets/
├── .streamlit/
│
├── README.md
├── requirements.txt
└── .gitignore
