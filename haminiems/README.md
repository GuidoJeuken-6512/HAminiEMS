# HAminiEMS - Mini Energy Management System

Ein Home Assistant Add-On zur Verwaltung und Visualisierung von Energieflüssen.

## Features

- Automatische Erkennung von Energie-Entitäten aus Home Assistant
- Konfigurierbare Sensor-Zuordnung
- Energiefluss-Visualisierung mit Sankey-Diagramm
- Historische Daten-Speicherung in SQLite
- Automatische Datenbank-Migrationen
- Zweisprachige Benutzeroberfläche (Deutsch/Englisch)
- Responsive Web-Interface

## Installation

1. Füge dieses Repository zu deinem Home Assistant hinzu
2. Installiere das Add-On "HAminiEMS"
3. Konfiguriere die Home Assistant URL und den Token
4. Starte das Add-On

## Konfiguration

- `ha_url`: Home Assistant URL (Standard: http://supervisor/core)
- `ha_token`: Home Assistant Long-Lived Access Token
- `refresh_interval`: Aktualisierungsintervall in Sekunden (Standard: 30)

## Verwendung

Nach dem Start ist das Web-Interface unter dem Add-On Port erreichbar.

