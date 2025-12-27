# HAminiEMS - Mini Energy Management System

Ein Home Assistant Add-On zur Verwaltung und Visualisierung von Energieflüssen.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FGuidoJeuken-6512%2FHAminiEMS)

## Features

- ✅ Automatische Erkennung von Energie-Entitäten aus Home Assistant
- ✅ Konfigurierbare Sensor-Zuordnung
- ✅ Energiefluss-Visualisierung
- ✅ Historische Daten-Speicherung in SQLite
- ✅ Automatische Datenbank-Migrationen
- ✅ Zweisprachige Benutzeroberfläche (Deutsch/Englisch)
- ✅ Responsive Web-Interface
- ✅ REST API für Integration

## Installation

1. Füge dieses Repository zu deinem Home Assistant hinzu:
   - Gehe zu **Einstellungen** → **Add-ons** → **Add-on Store**
   - Klicke auf die drei Punkte oben rechts → **Repositories**
   - Füge `https://github.com/GuidoJeuken-6512/HAminiEMS` hinzu
2. Installiere das Add-On "HAminiEMS"
3. Konfiguriere die Home Assistant URL und den Token
4. Starte das Add-On

## Konfiguration

### Optionen

- `ha_url`: Home Assistant URL (Standard: `http://supervisor/core`)
- `ha_token`: Home Assistant Long-Lived Access Token (erforderlich)
- `refresh_interval`: Aktualisierungsintervall in Sekunden (Standard: 30)

### Home Assistant Token erstellen

1. Gehe zu deinem Home Assistant Profil
2. Scrolle nach unten zu **Long-Lived Access Tokens**
3. Klicke auf **Token erstellen**
4. Kopiere den Token und füge ihn in die Add-On Konfiguration ein

## Verwendung

Nach dem Start ist das Web-Interface unter dem Add-On Port erreichbar. Öffne das Add-On im Home Assistant Dashboard.

### Sensor-Konfiguration

1. Gehe zur **Konfigurationsseite**
2. Wähle für jeden Sensor die entsprechende Home Assistant Entity aus
3. Wähle den Typ (Tageswert oder Gesamtwert) für Energie-Entities
4. Speichere die Konfiguration

### Unterstützte Sensoren

- PV-Produktion
- Netzbezug / Netzeinspeisung
- Batterie-Ladung / Entladung
- Batterie-Ladezustand (SOC)
- Hausverbrauch
- E-Auto-Ladung
- Wärmepumpe
- Sonstiger Verbrauch

## API-Endpunkte

- `GET /api/entities` - Alle konfigurierten Entitäten mit aktuellen Werten
- `GET /api/entities/<entity_id>` - Einzelne Entität
- `GET /api/config` - Konfiguration laden
- `POST /api/config` - Konfiguration speichern
- `GET /api/data?entity_id=X&start=Y&end=Z` - Historische Daten
- `GET /api/calculations?type=balance` - Energiebilanz
- `GET /api/health` - Health-Check

## Architektur

Das Add-On verwendet:
- **Python 3** mit Flask für das Web-Interface
- **SQLite** für die Datenbank
- **Automatisches Migrations-System** für Schema-Updates
- **Home Assistant REST API** für Datenabfrage

## Dokumentation

Vollständige Dokumentation finden Sie im [docs/](docs/) Verzeichnis:

- **[Hauptdokumentation](docs/README.md)** - Vollständige Projekt-Dokumentation
- **[Installationsanleitung](docs/INSTALLATION.md)** - Schritt-für-Schritt Installation
- **[API-Dokumentation](docs/API.md)** - REST API Referenz
- **[Entwicklungsplan](docs/plan.md)** - Technischer Entwicklungsplan
- **[Dokumentations-Index](docs/INDEX.md)** - Übersicht aller Dokumentationen

## Unterstützte Architekturen

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg

## Lizenz

Apache License 2.0
