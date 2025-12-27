# miniEMS Add-On Entwicklung mit DB-Migrationsstrategie

## Architektur-Übersicht

Das Add-On wird als Python-basiertes Web-Application mit folgender Struktur aufgebaut:

```
HAminiEMS/
├── config.yaml          # Add-On Konfiguration
├── build.yaml           # Build-Konfiguration
├── Dockerfile           # Container-Definition
├── rootfs/
│   ├── etc/
│   │   └── services.d/
│   │       └── haminiems/
│   │           └── run  # Service-Start-Script
│   └── usr/
│       └── bin/
│           └── haminiems/ # Python-Anwendung
│               ├── __init__.py
│               ├── main.py           # Flask/FastAPI App
│               ├── const.py          # Konstanten (inkl. DB_VERSION)
│               ├── utils.py          # Hilfsfunktionen
│               ├── database.py       # SQLite-Datenbank-Handler + Migration
│               ├── migrations/       # Migrations-Scripts
│               │   ├── __init__.py
│               │   ├── migration_manager.py
│               │   ├── 001_initial_schema.py
│               │   ├── 002_add_calculations.py
│               │   └── ...
│               ├── ha_client.py      # Home Assistant API Client
│               ├── calculations.py   # Berechnungslogik
│               ├── sensors.py       # Sensor-Management
│               ├── static/          # Web-Assets
│               │   ├── css/
│               │   ├── js/
│               │   └── icons/
│               └── templates/       # HTML-Templates
│                   ├── index.html   # Hauptseite
│                   └── config.html  # Konfigurationsseite
└── translations/
    ├── en.yaml
    └── de.yaml
```

## DB-Migrationsstrategie

### Konzept
- **DB-Version**: Unabhängig von App-Version, definiert in `const.py`
- **Migrations-System**: Automatische Erkennung und Ausführung bei App-Start
- **Versionierung**: Schema-Version in separater Tabelle `schema_version`
- **Rollback**: Optional, für kritische Migrationen

### Implementierung

#### 1. const.py - DB-Version Definition
```python
# App-Version (aus config.yaml)
APP_VERSION = "1.0.0"

# DB-Schema-Version (unabhängig von App-Version)
DB_VERSION = 1  # Erhöht sich nur bei Schema-Änderungen
```

#### 2. database.py - Migration-Integration
- Beim Start: Prüfung der aktuellen DB-Version
- Vergleich mit `const.DB_VERSION`
- Automatische Ausführung fehlender Migrationen
- Fehlerbehandlung und Logging

#### 3. migrations/ - Migrations-System
- **migration_manager.py**: Zentrale Migrations-Logik
  - Erkennt benötigte Migrationen
  - Führt Migrationen sequenziell aus
  - Protokolliert Migrationen in `migration_log` Tabelle
  - Rollback-Unterstützung (optional)

- **Migrations-Dateien**: Format `XXX_description.py`
  - Jede Migration hat eine eindeutige Versionsnummer
  - `up()` Methode für Upgrade
  - `down()` Methode für Rollback (optional)
  - Beispiel: `001_initial_schema.py`, `002_add_calculations.py`

#### 4. Schema-Version Tabelle
```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_version TEXT
);

CREATE TABLE IF NOT EXISTS migration_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_version INTEGER,
    migration_name TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);
```

### Migrations-Workflow

1. **App-Start**:
   - `database.py` initialisiert Verbindung
   - Prüft `schema_version` Tabelle (erstellt falls nicht vorhanden)
   - Liest aktuelle DB-Version
   - Vergleicht mit `const.DB_VERSION`

2. **Migration erforderlich**:
   - `migration_manager.py` wird aufgerufen
   - Findet alle Migrationen zwischen aktueller und Ziel-Version
   - Führt Migrationen sequenziell aus (in Reihenfolge)
   - Protokolliert jeden Schritt in `migration_log`
   - Bei Fehler: Rollback (falls unterstützt) oder Fehlerbehandlung

3. **Migration erfolgreich**:
   - Aktualisiert `schema_version` Tabelle
   - App startet normal

### Migrations-Beispiel

```python
# migrations/001_initial_schema.py
def up(db_connection):
    """Erstellt initiales Schema"""
    db_connection.execute("""
        CREATE TABLE entity_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            entity_id TEXT NOT NULL,
            value REAL,
            state_class TEXT,
            unit TEXT
        );
    """)
    db_connection.execute("""
        CREATE TABLE sensor_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_key TEXT UNIQUE NOT NULL,
            entity_id TEXT,
            daily_total TEXT,
            enabled BOOLEAN DEFAULT 1
        );
    """)
    db_connection.commit()

def down(db_connection):
    """Rollback - entfernt Tabellen"""
    db_connection.execute("DROP TABLE IF EXISTS sensor_config;")
    db_connection.execute("DROP TABLE IF EXISTS entity_values;")
    db_connection.commit()

VERSION = 1
```

## Implementierungs-Schritte

### 1. Add-On Grundstruktur
- config.yaml anpassen: Name, Slug, Beschreibung für HAminiEMS
- build.yaml anpassen: Build-Konfiguration
- Dockerfile erweitern: Python, SQLite, notwendige Pakete installieren
- Service-Script erstellen: Python-Anwendung starten

### 2. Python-Backend Struktur
- **const.py**:
  - Konstanten für Sensornamen, API-Endpunkte
  - `DB_VERSION` Definition (unabhängig von App-Version)
  - `APP_VERSION` aus config.yaml lesen
- **database.py**:
  - SQLite-Handler mit Migration-Integration
  - Automatische Migration beim Start
  - Tabellen für Entitätswerte, Konfiguration, Berechnungen
- **migrations/migration_manager.py**:
  - Zentrale Migrations-Logik
  - Versionsvergleich und Migration-Ausführung
  - Fehlerbehandlung und Logging
- **migrations/001_initial_schema.py**:
  - Initiales Datenbank-Schema
  - Schema-Version Tabelle
- **ha_client.py**: Home Assistant REST API Client
- **calculations.py**: Berechnungslogik
- **sensors.py**: Sensor-Management
- **utils.py**: Hilfsfunktionen

### 3. Web-Interface (Flask/FastAPI)
- **main.py**: Web-Server mit Routes
- Statische Assets für Grafiken
- Sankey-Diagramm für Energieflüsse
- Statistiken-Grafiken

### 4. Konfigurationsseite
- Dropdown-Auswahl für Sensoren mit Filter auf `state_class`
- Zuordnung zu allen definierten Sensoren
- Checkbox für daily/total bei Energie-Entitäten
- Refresh-Interval Konfiguration

### 5. Hauptseite
- Anzeige aller konfigurierten HA-Entitäten
- Auto-Refresh alle X Sekunden (konfigurierbar)
- Aktuelle Werte mit Einheiten

### 6. Grafiken und Visualisierungen
- Sankey-Diagramm für Energieflüsse
- Statistiken-Grafiken

### 7. Zweisprachigkeit
- Übersetzungsdateien in `translations/` (de.yaml, en.yaml)
- i18n-Integration im Backend und Frontend

### 8. UI/UX
- Schlanker Header mit Icon aus `icon.png`
- Moderne, responsive Oberfläche

## Datenbank-Schema (Version 1 - Initial)

```sql
-- Schema-Version Tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    app_version TEXT
);

-- Migrations-Log
CREATE TABLE migration_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_version INTEGER,
    migration_name TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- Entitätswerte
CREATE TABLE entity_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    entity_id TEXT NOT NULL,
    value REAL,
    state_class TEXT,
    unit TEXT
);

-- Sensor-Konfiguration
CREATE TABLE sensor_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_key TEXT UNIQUE NOT NULL,
    entity_id TEXT,
    daily_total TEXT,  -- 'daily' oder 'total'
    enabled BOOLEAN DEFAULT 1
);
```

## Migrations-Strategie Details

### Versionsnummern
- Start bei Version 1
- Erhöhung nur bei Schema-Änderungen
- Nicht bei Datenänderungen oder Bugfixes

### Migration-Regeln
1. **Sequenzielle Ausführung**: Migrationen werden in Reihenfolge ausgeführt
2. **Idempotenz**: Migrationen müssen mehrfach ausführbar sein (IF NOT EXISTS)
3. **Transaktionen**: Jede Migration in eigener Transaktion
4. **Fehlerbehandlung**: Bei Fehler wird Migration protokolliert, App startet nicht
5. **Backup**: Optional vor kritischen Migrationen

### Beispiel-Migrations-Szenarien

**Migration 002: Berechnungen-Tabelle hinzufügen**
```python
# const.py: DB_VERSION = 2
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
```

**Migration 003: Index hinzufügen**
```python
# const.py: DB_VERSION = 3
# migrations/003_add_indexes.py
VERSION = 3
def up(db_connection):
    db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_values_timestamp
        ON entity_values(timestamp);
    """)
```

## API-Endpunkte

- `GET /api/entities` - Alle konfigurierten Entitäten mit aktuellen Werten
- `GET /api/entities/<entity_id>` - Einzelne Entität
- `POST /api/config` - Konfiguration speichern
- `GET /api/config` - Konfiguration laden
- `GET /api/data?entity_id=X&start=Y&end=Z` - Historische Daten
- `POST /api/entities/<entity_id>/set` - Entitätswert setzen
- `GET /api/calculations?type=X` - Berechnungsergebnisse
- `GET /api/migrations/status` - Migrations-Status (optional, für Debugging)

