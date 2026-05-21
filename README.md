<div align="center">

# Qualitäts-Muster-Finder

### Krankenhausanalyse · Datenvisualisierung · Streamlit-App

Dieses Projekt ist mein Abschlussprojekt aus der Weiterbildung zur Data Analystin.

Ziel war es, Qualitätsdaten deutscher Krankenhäuser zu analysieren und Muster zwischen auffälligen Qualitätsindikatoren und strukturellen Krankenhausmerkmalen sichtbar zu machen.

</div>

---

## Projektidee

In diesem Projekt geht es nicht darum, einzelne Krankenhäuser direkt zu bewerten.

Stattdessen sollen Daten verständlich aufbereitet und Zusammenhänge sichtbar gemacht werden, zum Beispiel:

- Welche Qualitätsindikatoren treten besonders häufig auffällig auf?
- Gibt es Unterschiede nach Krankenhausgröße?
- Spielen Uni-Status, Trägerschaft oder Fachabteilungen eine Rolle?
- Lassen sich regionale Muster erkennen?
- Wie können die Ergebnisse interaktiv dargestellt werden?

---

## Tools & Technologien

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=plastic&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=plastic&logo=streamlit&logoColor=white)
![matplotlib](https://img.shields.io/badge/matplotlib-11557C?style=plastic&logoColor=white)
![plotly](https://img.shields.io/badge/plotly-3F4F75?style=plastic&logo=plotly&logoColor=white)
![KNIME](https://img.shields.io/badge/KNIME-FDD800?style=plastic&logoColor=black)

</div>

---

## Inhalte des Projekts

| Bereich | Beschreibung |
|---|---|
| Datenaufbereitung | Einlesen, Bereinigen und Zusammenführen verschiedener Datentabellen |
| Zielvariable | Erstellung einer Auffälligkeitslogik auf Basis auffälliger Qualitätsindikatoren |
| Analyse | Untersuchung von Qualitätsindikatoren und Krankenhausmerkmalen |
| Visualisierung | Diagramme, Kennzahlen und Vergleichsansichten |
| Streamlit-App | Interaktive Darstellung der Ergebnisse mit mehreren Seiten |
| KNIME-Modell | Einfacher Decision Tree zur Einschätzung einer Risikogruppe über dem Median |

---

## App-Bereiche

Die Streamlit-App enthält verschiedene Seiten, unter anderem:

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
├── app.py
├── data_loader.py
├── design.py
├── ui.py
├── utils4.py
│
├── pages/
├── assets/
├── .streamlit/
│
├── README.md
├── requirements.txt
└── .gitignore
