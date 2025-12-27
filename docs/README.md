# HAminiEMS - Projekt-Dokumentation

Willkommen zur vollständigen Dokumentation des HAminiEMS (Mini Energy Management System) Add-Ons für Home Assistant.

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Installation](#installation)
3. [Konfiguration](#konfiguration)
4. [Verwendung](#verwendung)
5. [API-Dokumentation](#api-dokumentation)
6. [Architektur](#architektur)
7. [Datenbank-Migrationen](#datenbank-migrationen)
8. [Entwicklung](#entwicklung)
9. [Troubleshooting](#troubleshooting)

---

## Übersicht

HAminiEMS ist ein Home Assistant Add-On zur Verwaltung und Visualisierung von Energieflüssen in einem Smart Home System. Es ermöglicht die zentrale Überwachung von:

- **PV-Produktion** - Solarstrom-Erzeugung
- **Netzbezug/Netzeinspeisung** - Strom aus/vom Netz
- **Batteriespeicher** - Ladung, Entladung und Ladezustand
- **Verbraucher** - Hausverbrauch, E-Auto, Wärmepumpe, etc.

### Hauptfunktionen

- ✅ Automatische Erkennung von Energie-Entitäten aus Home Assistant
- ✅ Konfigurierbare Sensor-Zuordnung über Web-Interface
- ✅ Energiefluss-Visualisierung und Berechnungen
- ✅ Historische Datenspeicherung in SQLite
- ✅ Automatische Datenbank-Migrationen
- ✅ Zweisprachige Benutzeroberfläche (Deutsch/Englisch)
- ✅ Responsive Web-Interface
- ✅ REST API für externe Integrationen

### Technische Details

- **Sprache**: Python 3
- **Web-Framework**: Flask
- **Datenbank**: SQLite
- **Architekturen**: aarch64, amd64
- **Lizenz**: Apache License 2.0

---

## Installation

### Voraussetzungen

- Home Assistant mit Supervisor (HassOS, Home Assistant OS, oder Supervised Installation)
- Internetverbindung für den ersten Download
- Long-Lived Access Token von Home Assistant

### Installationsschritte

1. **Repository hinzufügen**
   - Öffne Home Assistant
   - Gehe zu **Einstellungen** → **Add-ons** → **Add-on Store**
   - Klicke auf die drei Punkte (⋮) oben rechts
   - Wähle **Repositories**
   - Füge folgende URL hinzu: `https://github.com/GuidoJeuken-6512/HAminiEMS`
   - Klicke auf **Hinzufügen**

2. **Add-On installieren**
   - Suche nach "HAminiEMS" im Add-On Store
   - Klicke auf **Installieren**
   - Warte, bis die Installation abgeschlossen ist

3. **Home Assistant Token erstellen**
   - Gehe zu deinem **Profil** (unten links)
   - Scrolle nach unten zu **Long-Lived Access Tokens**
   - Klicke auf **Token erstellen**
   - Gib einen Namen ein (z.B. "HAminiEMS")
   - Kopiere den generierten Token (wird nur einmal angezeigt!)

4. **Konfiguration**
   - Öffne die HAminiEMS Add-On Seite
   - Gehe zum Tab **Konfiguration**
   - Füge den Token in `ha_token` ein
   - Passe `ha_url` an, falls nötig (Standard: `http://supervisor/core`)
   - Speichere die Konfiguration

5. **Add-On starten**
   - Gehe zum Tab **Info**
   - Klicke auf **Start**
   - Warte, bis der Status "Running" anzeigt

6. **Web-Interface öffnen**
   - Klicke auf **ÖFFNEN** oder **WEITERLEITEN**
   - Das Web-Interface sollte sich öffnen

---

## Konfiguration

### Add-On Konfiguration (config.yaml)

Die Konfiguration erfolgt über die Add-On Einstellungen in Home Assistant:

```yaml
ha_url: "http://supervisor/core"  # Home Assistant URL
ha_token: "eyJ0eXAiOiJKV1QiLCJhbGc..."  # Long-Lived Access Token
refresh_interval: 30  # Aktualisierungsintervall in Sekunden
```

#### Optionen im Detail

| Option | Typ | Standard | Beschreibung |
|--------|-----|----------|--------------|
| `ha_url` | String | `http://supervisor/core` | URL zu deiner Home Assistant Instanz. Für Supervised Installationen kann dies `http://homeassistant:8123` sein. |
| `ha_token` | String | (leer) | **Erforderlich!** Long-Lived Access Token von Home Assistant. |
| `refresh_interval` | Integer | `30` | Intervall in Sekunden für die automatische Aktualisierung der Werte. Minimum: 1 Sekunde. |

### Sensor-Konfiguration (Web-Interface)

Die Sensor-Zuordnung erfolgt über das Web-Interface:

1. Öffne das HAminiEMS Web-Interface
2. Navigiere zur **Konfigurationsseite**
3. Für jeden Sensor:
   - Wähle die entsprechende Home Assistant Entity aus dem Dropdown
   - Wähle den Typ (nur bei Energie-Entities):
     - **Tageswert**: Für Entities mit `state_class: total_increasing` (z.B. tägliche Energie)
     - **Gesamtwert**: Für Entities mit `state_class: total` (z.B. Gesamtenergie seit Installation)
   - Aktiviere/Deaktiviere den Sensor mit der Checkbox
4. Klicke auf **Speichern**

#### Unterstützte Sensoren

| Sensor-Key | Beschreibung | Typ |
|------------|--------------|-----|
| `pv_production` | PV-Produktion | Energie (W/kWh) |
| `grid_import` | Netzbezug | Energie (W/kWh) |
| `grid_export` | Netzeinspeisung | Energie (W/kWh) |
| `battery_charge` | Batterie-Ladung | Energie (W/kWh) |
| `battery_discharge` | Batterie-Entladung | Energie (W/kWh) |
| `battery_soc` | Batterie-Ladezustand | Prozent (%) |
| `house_consumption` | Hausverbrauch | Energie (W/kWh) |
| `ev_charging` | E-Auto-Ladung | Energie (W/kWh) |
| `heat_pump` | Wärmepumpe | Energie (W/kWh) |
| `other_consumption` | Sonstiger Verbrauch | Energie (W/kWh) |

---

## Verwendung

### Hauptseite

Die Hauptseite zeigt:

- **Status-Bar**: Verbindungsstatus und letzte Aktualisierung
- **Sensor-Karten**: Aktuelle Werte aller konfigurierten Sensoren
- **Energiebilanz**: Übersicht über Produktion, Verbrauch und Bilanz

Die Seite aktualisiert sich automatisch alle 30 Sekunden (oder entsprechend der Konfiguration).

### Konfigurationsseite

Auf der Konfigurationsseite können Sie:

- Sensoren zu Home Assistant Entities zuordnen
- Den Typ (Tageswert/Gesamtwert) für Energie-Entities wählen
- Sensoren aktivieren/deaktivieren
- Die Konfiguration speichern

### Energiebilanz

Die Energiebilanz zeigt:

- **PV-Produktion**: Aktuelle Solarstrom-Erzeugung
- **Hausverbrauch**: Gesamter Hausverbrauch
- **Netzbezug/Netzeinspeisung**: Strom aus/vom Netz
- **Selbstverbrauch**: Direkt genutzter Solarstrom
- **Selbstverbrauchsrate**: Prozentualer Anteil des selbst genutzten Solarstroms

---

## API-Dokumentation

HAminiEMS bietet eine REST API für externe Integrationen.

### Basis-URL

```
http://<add-on-ip>:<port>
```

### Endpunkte

#### GET /api/entities

Gibt alle konfigurierten Entitäten mit aktuellen Werten zurück.

**Response:**
```json
{
  "success": true,
  "data": {
    "pv_production": {
      "value": 2500.5,
      "unit": "W",
      "entity_id": "sensor.pv_power",
      "state": "2500.5",
      "last_updated": "2024-01-15T10:30:00+00:00"
    },
    ...
  }
}
```

#### GET /api/entities/<entity_id>

Gibt eine einzelne Entität zurück.

**Beispiel:** `GET /api/entities/sensor.pv_power`

**Response:**
```json
{
  "success": true,
  "data": {
    "entity_id": "sensor.pv_power",
    "state": "2500.5",
    "attributes": {
      "unit_of_measurement": "W",
      "state_class": "measurement"
    },
    ...
  }
}
```

#### GET /api/config

Lädt die aktuelle Sensor-Konfiguration.

**Response:**
```json
{
  "success": true,
  "data": {
    "sensor_configs": [
      {
        "id": 1,
        "sensor_key": "pv_production",
        "entity_id": "sensor.pv_power",
        "daily_total": null,
        "enabled": true
      },
      ...
    ],
    "available_entities": [
      {
        "entity_id": "sensor.pv_power",
        "friendly_name": "PV Power",
        "state_class": "measurement",
        "unit": "W"
      },
      ...
    ],
    "sensor_keys": ["pv_production", "grid_import", ...]
  }
}
```

#### POST /api/config

Speichert die Sensor-Konfiguration.

**Request Body:**
```json
{
  "configs": [
    {
      "sensor_key": "pv_production",
      "entity_id": "sensor.pv_power",
      "daily_total": null,
      "enabled": true
    },
    ...
  ]
}
```

**Response:**
```json
{
  "success": true
}
```

#### GET /api/data

Holt historische Daten für eine Entity.

**Query Parameter:**
- `entity_id` (erforderlich): Entity ID
- `start` (optional): Start-Zeitpunkt (ISO-Format)
- `end` (optional): End-Zeitpunkt (ISO-Format)

**Beispiel:** `GET /api/data?entity_id=sensor.pv_power&start=2024-01-15T00:00:00`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "entity_id": "sensor.pv_power",
      "value": 2500.5,
      "state_class": "measurement",
      "unit": "W"
    },
    ...
  ]
}
```

#### GET /api/calculations

Gibt Berechnungsergebnisse zurück.

**Query Parameter:**
- `type`: `balance` (Energiebilanz) oder `daily` (Tagesstatistiken)

**Beispiel:** `GET /api/calculations?type=balance`

**Response:**
```json
{
  "success": true,
  "data": {
    "production": {
      "pv": 2500.5,
      "total": 2500.5
    },
    "consumption": {
      "house": 1500.0,
      "ev": 0.0,
      "heat_pump": 800.0,
      "other": 200.0,
      "battery_charge": 0.0,
      "total": 2500.0
    },
    "grid": {
      "import": 0.0,
      "export": 0.5
    },
    "battery": {
      "charge": 0.0,
      "discharge": 0.0,
      "soc": 75.5
    },
    "balance": {
      "self_consumption": 2500.0,
      "self_consumption_rate": 99.98,
      "total_available": 2500.5
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

#### GET /api/refresh

Aktualisiert alle Werte von Home Assistant und speichert sie in der Datenbank.

**Response:**
```json
{
  "success": true,
  "updated": 8
}
```

#### GET /api/health

Health-Check Endpunkt.

**Response:**
```json
{
  "success": true,
  "ha_connected": true,
  "status": "ok"
}
```

---

## Architektur

### Projektstruktur

```
haminiems/
├── config.yaml              # Add-On Konfiguration
├── build.yaml               # Build-Konfiguration
├── Dockerfile               # Container-Definition
├── rootfs/
│   ├── etc/
│   │   └── services.d/
│   │       └── haminiems/
│   │           └── run      # Service-Start-Script
│   └── usr/
│       └── bin/
│           └── haminiems/   # Python-Anwendung
│               ├── __init__.py
│               ├── main.py           # Flask Web-App
│               ├── const.py          # Konstanten
│               ├── utils.py          # Hilfsfunktionen
│               ├── database.py       # SQLite-Handler
│               ├── migrations/       # Migrations-System
│               │   ├── __init__.py
│               │   ├── migration_manager.py
│               │   └── 001_initial_schema.py
│               ├── ha_client.py     # HA API Client
│               ├── calculations.py  # Berechnungslogik
│               ├── sensors.py      # Sensor-Management
│               ├── static/         # Web-Assets
│               │   ├── css/
│               │   ├── js/
│               │   └── icons/
│               └── templates/      # HTML-Templates
│                   ├── index.html
│                   └── config.html
└── translations/
    ├── de.yaml
    └── en.yaml
```

### Komponenten

#### main.py
Flask Web-Application mit allen API-Endpunkten und Routen.

#### database.py
SQLite-Datenbank-Handler mit automatischer Migration-Integration.

#### ha_client.py
Client für die Home Assistant REST API. Bietet Methoden zum Abrufen von States, History, etc.

#### sensors.py
Verwaltet Sensor-Konfigurationen und speichert Entity-Werte in der Datenbank.

#### calculations.py
Berechnet Energieflüsse, Bilanz und Statistiken aus den Sensor-Werten.

#### migrations/
Automatisches Migrations-System für Datenbank-Schema-Updates.

### Datenfluss

```
Home Assistant
    ↓ (REST API)
HA Client
    ↓
Sensor Manager
    ↓
Database (SQLite)
    ↓
Calculation Engine
    ↓
Web Interface (Flask)
    ↓
Browser
```

---

## Datenbank-Migrationen

HAminiEMS verwendet ein automatisches Migrations-System für Datenbank-Schema-Updates.

### Konzept

- **DB-Version**: Unabhängig von App-Version, definiert in `const.py`
- **Automatische Ausführung**: Migrationen werden beim App-Start automatisch erkannt und ausgeführt
- **Versionierung**: Schema-Version wird in separater Tabelle `schema_version` gespeichert
- **Logging**: Alle Migrationen werden in `migration_log` protokolliert

### Aktuelle Schema-Version

Die aktuelle DB-Version ist **1** (definiert in `const.py`).

### Migration erstellen

1. Erhöhe `DB_VERSION` in `const.py`
2. Erstelle neue Migrations-Datei: `migrations/XXX_description.py`
3. Implementiere `up()` und optional `down()` Funktionen

**Beispiel:**
```python
# migrations/002_add_calculations.py
VERSION = 2

def up(db_connection):
    db_connection.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            calculation_type TEXT,
            result JSON
        );
    """)
    db_connection.commit()

def down(db_connection):
    db_connection.execute("DROP TABLE IF NOT EXISTS calculations;")
    db_connection.commit()
```

### Migration-Workflow

1. **App-Start**: `database.py` prüft aktuelle DB-Version
2. **Vergleich**: Vergleich mit `const.DB_VERSION`
3. **Migration**: `migration_manager.py` führt fehlende Migrationen aus
4. **Protokollierung**: Jede Migration wird in `migration_log` gespeichert
5. **Update**: `schema_version` Tabelle wird aktualisiert

---

## Entwicklung

### Lokale Entwicklung

1. **Repository klonen**
   ```bash
   git clone https://github.com/GuidoJeuken-6512/HAminiEMS.git
   cd HAminiEMS
   ```

2. **Dependencies installieren**
   ```bash
   pip install flask requests sqlalchemy
   ```

3. **Umgebungsvariablen setzen**
   ```bash
   export HA_URL="http://localhost:8123"
   export HA_TOKEN="your-token-here"
   export PORT=8099
   ```

4. **Anwendung starten**
   ```bash
   cd haminiems/rootfs/usr/bin/haminiems
   python3 -m haminiems.main
   ```

### Build und Test

1. **Add-On bauen**
   ```bash
   cd haminiems
   # Build erfolgt über Home Assistant Supervisor
   ```

2. **Logs anzeigen**
   - In Home Assistant: Add-On → **Logs** Tab
   - Oder via SSH: `docker logs addon_haminiems`

### Code-Struktur

- **Modulare Architektur**: Jede Komponente in separatem Modul
- **Type Hints**: Python Type Hints für bessere Code-Qualität
- **Error Handling**: Umfassende Fehlerbehandlung und Logging
- **Dokumentation**: Docstrings für alle Funktionen

---

## Troubleshooting

### Add-On startet nicht

1. **Logs prüfen**: Add-On → **Logs** Tab
2. **Konfiguration prüfen**: Stelle sicher, dass `ha_token` gesetzt ist
3. **Token prüfen**: Teste den Token mit Home Assistant API

### Keine Sensoren sichtbar

1. **Konfiguration prüfen**: Gehe zur Konfigurationsseite und ordne Sensoren zu
2. **Entities prüfen**: Stelle sicher, dass Entities in Home Assistant existieren
3. **State Class prüfen**: Nur Entities mit `state_class` werden als Energie-Entities erkannt

### Datenbank-Fehler

1. **Logs prüfen**: Migration-Fehler werden in den Logs angezeigt
2. **Datenbank zurücksetzen**: Lösche `/config/haminiems.db` (Achtung: Datenverlust!)
3. **Migration-Status prüfen**: API-Endpunkt `/api/migrations/status` (falls implementiert)

### Verbindungsprobleme

1. **HA URL prüfen**: Für Supervised Installationen: `http://homeassistant:8123`
2. **Token prüfen**: Token muss gültig sein und nicht abgelaufen
3. **Netzwerk prüfen**: Add-On muss Zugriff auf Home Assistant haben

### Performance-Probleme

1. **Refresh-Interval erhöhen**: Reduziere die Update-Frequenz
2. **Datenbank optimieren**: Alte Daten regelmäßig löschen
3. **Logs prüfen**: Suche nach langsam laufenden Queries

---

## Weitere Ressourcen

- [Entwicklungsplan](plan.md) - Detaillierter Entwicklungsplan
- [Home Assistant Add-On Dokumentation](https://developers.home-assistant.io/docs/add-ons)
- [GitHub Repository](https://github.com/GuidoJeuken-6512/HAminiEMS)

---

## Support

Bei Problemen oder Fragen:

1. Prüfe die [Troubleshooting](#troubleshooting) Sektion
2. Öffne ein [Issue auf GitHub](https://github.com/GuidoJeuken-6512/HAminiEMS/issues)
3. Prüfe die Logs im Add-On

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2024

