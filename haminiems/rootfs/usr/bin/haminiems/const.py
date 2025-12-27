"""Konstanten für HAminiEMS"""

# App-Version (aus config.yaml)
APP_VERSION = "1.0.0"

# DB-Schema-Version (unabhängig von App-Version)
# Erhöht sich nur bei Schema-Änderungen
DB_VERSION = 1

# Sensor-Keys (definierte Sensoren im System)
SENSOR_KEYS = [
    "pv_production",           # PV-Produktion
    "grid_import",             # Netzbezug
    "grid_export",             # Netzeinspeisung
    "battery_charge",          # Batterie-Ladung
    "battery_discharge",       # Batterie-Entladung
    "battery_soc",             # Batterie-Ladezustand
    "house_consumption",       # Hausverbrauch
    "ev_charging",             # E-Auto-Ladung
    "heat_pump",               # Wärmepumpe
    "other_consumption",       # Sonstiger Verbrauch
]

# Home Assistant API Endpunkte
HA_API_STATES = "/api/states"
HA_API_SERVICES = "/api/services"
HA_API_HISTORY = "/api/history/period"

# Datenbank-Pfad
DB_PATH = "/config/haminiems.db"

# Standard-Refresh-Interval (Sekunden)
DEFAULT_REFRESH_INTERVAL = 30

