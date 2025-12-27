# HAminiEMS - API-Dokumentation

Vollständige Dokumentation der REST API von HAminiEMS.

## Basis-URL

```
http://<add-on-ip>:<port>
```

Der Port wird von Home Assistant automatisch zugewiesen und ist im Add-On Info-Tab sichtbar.

## Authentifizierung

Aktuell ist keine Authentifizierung erforderlich, da das Add-On nur innerhalb des Home Assistant Netzwerks erreichbar ist.

## Response-Format

Alle API-Antworten verwenden JSON-Format.

### Erfolgreiche Antwort

```json
{
  "success": true,
  "data": { ... }
}
```

### Fehler-Antwort

```json
{
  "success": false,
  "error": "Fehlermeldung"
}
```

HTTP-Status-Codes:
- `200`: Erfolgreich
- `400`: Bad Request (ungültige Parameter)
- `404`: Nicht gefunden
- `500`: Server-Fehler

---

## Endpunkte

### GET /api/entities

Gibt alle konfigurierten Entitäten mit aktuellen Werten zurück.

**Request:**
```
GET /api/entities
```

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
    "grid_import": {
      "value": 0.0,
      "unit": "W",
      "entity_id": "sensor.grid_power",
      "state": "0.0",
      "last_updated": "2024-01-15T10:30:00+00:00"
    },
    ...
  }
}
```

**Felder:**
- `value`: Numerischer Wert (float)
- `unit`: Einheit (z.B. "W", "kWh", "%")
- `entity_id`: Home Assistant Entity ID
- `state`: Roher State-Wert als String
- `last_updated`: ISO-Format Zeitstempel

---

### GET /api/entities/<entity_id>

Gibt eine einzelne Entität zurück.

**Request:**
```
GET /api/entities/sensor.pv_power
```

**Response:**
```json
{
  "success": true,
  "data": {
    "entity_id": "sensor.pv_power",
    "state": "2500.5",
    "attributes": {
      "unit_of_measurement": "W",
      "state_class": "measurement",
      "friendly_name": "PV Power"
    },
    "last_changed": "2024-01-15T10:30:00+00:00",
    "last_updated": "2024-01-15T10:30:00+00:00"
  }
}
```

**Fehler (404):**
```json
{
  "success": false,
  "error": "Entity nicht gefunden"
}
```

---

### GET /api/config

Lädt die aktuelle Sensor-Konfiguration und verfügbare Entities.

**Request:**
```
GET /api/config
```

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
      {
        "id": 2,
        "sensor_key": "grid_import",
        "entity_id": "sensor.grid_power",
        "daily_total": "total",
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
      {
        "entity_id": "sensor.grid_power",
        "friendly_name": "Grid Power",
        "state_class": "total",
        "unit": "kWh"
      },
      ...
    ],
    "sensor_keys": [
      "pv_production",
      "grid_import",
      "grid_export",
      "battery_charge",
      "battery_discharge",
      "battery_soc",
      "house_consumption",
      "ev_charging",
      "heat_pump",
      "other_consumption"
    ]
  }
}
```

**Felder:**
- `sensor_configs`: Array aller konfigurierten Sensoren
- `available_entities`: Array aller verfügbaren Energie-Entities aus Home Assistant
- `sensor_keys`: Array aller definierten Sensor-Keys

---

### POST /api/config

Speichert die Sensor-Konfiguration.

**Request:**
```
POST /api/config
Content-Type: application/json

{
  "configs": [
    {
      "sensor_key": "pv_production",
      "entity_id": "sensor.pv_power",
      "daily_total": null,
      "enabled": true
    },
    {
      "sensor_key": "grid_import",
      "entity_id": "sensor.grid_power",
      "daily_total": "total",
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

**Fehler (500):**
```json
{
  "success": false,
  "error": "Fehler beim Speichern"
}
```

**Hinweise:**
- `sensor_key`: Muss einer der definierten Sensor-Keys sein
- `entity_id`: Kann `null` sein, um Zuordnung zu entfernen
- `daily_total`: `"daily"`, `"total"` oder `null`
- `enabled`: Boolean

---

### GET /api/data

Holt historische Daten für eine Entity aus der Datenbank.

**Request:**
```
GET /api/data?entity_id=sensor.pv_power&start=2024-01-15T00:00:00&end=2024-01-15T23:59:59
```

**Query Parameter:**
- `entity_id` (erforderlich): Entity ID
- `start` (optional): Start-Zeitpunkt (ISO-Format)
- `end` (optional): End-Zeitpunkt (ISO-Format)

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
    {
      "id": 2,
      "timestamp": "2024-01-15T10:31:00",
      "entity_id": "sensor.pv_power",
      "value": 2550.0,
      "state_class": "measurement",
      "unit": "W"
    },
    ...
  ]
}
```

**Fehler (400):**
```json
{
  "success": false,
  "error": "entity_id fehlt"
}
```

---

### GET /api/calculations

Gibt Berechnungsergebnisse zurück.

**Request:**
```
GET /api/calculations?type=balance
```

**Query Parameter:**
- `type`: `balance` (Energiebilanz) oder `daily` (Tagesstatistiken)

#### type=balance

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

#### type=daily

**Response:**
```json
{
  "success": true,
  "data": {
    "date": "2024-01-15",
    "balance": { ... },
    "summary": {
      "total_production": 2500.5,
      "total_consumption": 2500.0,
      "self_consumption_rate": 99.98
    }
  }
}
```

**Fehler (400):**
```json
{
  "success": false,
  "error": "Unbekannter Typ"
}
```

---

### GET /api/refresh

Aktualisiert alle Werte von Home Assistant und speichert sie in der Datenbank.

**Request:**
```
GET /api/refresh
```

**Response:**
```json
{
  "success": true,
  "updated": 8
}
```

**Felder:**
- `updated`: Anzahl der aktualisierten Entities

---

### GET /api/health

Health-Check Endpunkt zur Überprüfung des Systemstatus.

**Request:**
```
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "ha_connected": true,
  "status": "ok"
}
```

**Felder:**
- `ha_connected`: Boolean, ob Verbindung zu Home Assistant besteht
- `status`: Status-String ("ok" oder Fehlermeldung)

---

## Beispiele

### cURL

```bash
# Alle Entities abrufen
curl http://localhost:8099/api/entities

# Konfiguration abrufen
curl http://localhost:8099/api/config

# Konfiguration speichern
curl -X POST http://localhost:8099/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "configs": [
      {
        "sensor_key": "pv_production",
        "entity_id": "sensor.pv_power",
        "enabled": true
      }
    ]
  }'

# Energiebilanz abrufen
curl http://localhost:8099/api/calculations?type=balance

# Health-Check
curl http://localhost:8099/api/health
```

### Python

```python
import requests

BASE_URL = "http://localhost:8099"

# Alle Entities abrufen
response = requests.get(f"{BASE_URL}/api/entities")
data = response.json()
print(data)

# Konfiguration speichern
config = {
    "configs": [
        {
            "sensor_key": "pv_production",
            "entity_id": "sensor.pv_power",
            "enabled": True
        }
    ]
}
response = requests.post(f"{BASE_URL}/api/config", json=config)
print(response.json())

# Energiebilanz abrufen
response = requests.get(f"{BASE_URL}/api/calculations?type=balance")
balance = response.json()["data"]
print(f"PV Produktion: {balance['production']['pv']} W")
print(f"Selbstverbrauchsrate: {balance['balance']['self_consumption_rate']}%")
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8099';

// Alle Entities abrufen
async function getEntities() {
  const response = await fetch(`${BASE_URL}/api/entities`);
  const data = await response.json();
  console.log(data);
}

// Energiebilanz abrufen
async function getBalance() {
  const response = await fetch(`${BASE_URL}/api/calculations?type=balance`);
  const data = await response.json();
  console.log('PV Produktion:', data.data.production.pv, 'W');
  console.log('Selbstverbrauchsrate:', data.data.balance.self_consumption_rate, '%');
}

// Konfiguration speichern
async function saveConfig(configs) {
  const response = await fetch(`${BASE_URL}/api/config`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ configs })
  });
  const data = await response.json();
  console.log(data);
}
```

---

## Rate Limiting

Aktuell gibt es keine Rate-Limits. Bei hoher Last sollte das `refresh_interval` in der Konfiguration angepasst werden.

## Fehlerbehandlung

Alle Fehler werden als JSON-Response mit `success: false` und einer `error`-Nachricht zurückgegeben. Der HTTP-Status-Code gibt zusätzliche Informationen:

- `200`: Erfolgreich
- `400`: Bad Request (ungültige Parameter)
- `404`: Nicht gefunden
- `500`: Server-Fehler

Immer prüfen:
1. HTTP-Status-Code
2. `success` Feld in der JSON-Response
3. `error` Feld bei Fehlern

---

## Versionierung

Die API-Version entspricht der Add-On Version. Aktuelle Version: **1.0.0**

Änderungen an der API werden in der [CHANGELOG.md](../haminiems/CHANGELOG.md) dokumentiert.



