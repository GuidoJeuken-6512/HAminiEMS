"""Flask Web-Application für HAminiEMS"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request
from typing import Dict, Any

# bashio importieren (verfügbar in Home Assistant Add-Ons)
try:
    import bashio
    HAS_BASHIO = True
except ImportError:
    # Fallback für lokale Entwicklung
    HAS_BASHIO = False
    import json
    class BashioMock:
        @staticmethod
        def config(key, default=None):
            # Versuche zuerst Umgebungsvariable
            value = os.environ.get(key.upper(), None)
            if value is not None:
                return value
            # Dann versuche /data/options.json zu lesen
            try:
                options_path = "/data/options.json"
                if os.path.exists(options_path):
                    with open(options_path, 'r') as f:
                        options = json.load(f)
                        return options.get(key, default)
            except Exception:
                pass
            return default
    bashio = BashioMock()

from .utils import setup_logging
from .database import get_database
from .ha_client import HAClient
from .sensors import SensorManager
from .calculations import CalculationEngine
from .const import DEFAULT_REFRESH_INTERVAL

# Logging einrichten
logger = setup_logging()

# Flask App erstellen
# Pfade relativ zum Modul-Verzeichnis
import pathlib
BASE_DIR = pathlib.Path(__file__).parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

# Globale Instanzen
ha_client: HAClient = None
sensor_manager: SensorManager = None
calculation_engine: CalculationEngine = None


def init_app():
    """Initialisiert die Anwendung"""
    global ha_client, sensor_manager, calculation_engine

    # Konfiguration aus Home Assistant lesen
    ha_url = bashio.config("ha_url", "http://supervisor/core")
    ha_token = bashio.config("ha_token", "")

    # Falls URL "http://supervisor/core" ist, versuche "http://homeassistant:8123" als Fallback
    if ha_url == "http://supervisor/core":
        # Teste ob supervisor/core funktioniert, falls nicht verwende homeassistant:8123
        try:
            import requests
            test_response = requests.get("http://homeassistant:8123/api/", timeout=2)
            if test_response.status_code == 200 or test_response.status_code == 401:
                # 401 bedeutet, dass der Server erreichbar ist, nur der Token fehlt
                ha_url = "http://homeassistant:8123"
                logger.info("Verwende http://homeassistant:8123 statt http://supervisor/core")
        except Exception:
            # Falls homeassistant:8123 nicht erreichbar, versuche supervisor/core
            pass

    # Falls kein Token in der Konfiguration, versuche SUPERVISOR_TOKEN zu verwenden
    if not ha_token:
        # Versuche zuerst SUPERVISOR_TOKEN aus Umgebungsvariable
        ha_token = os.environ.get("SUPERVISOR_TOKEN", "")

        # Falls nicht gefunden, versuche aus Datei zu lesen
        if not ha_token:
            try:
                token_file = "/run/s6/container_environment/SUPERVISOR_TOKEN"
                if os.path.exists(token_file):
                    with open(token_file, "r") as f:
                        ha_token = f.read().strip()
            except Exception:
                pass

        # Falls immer noch nicht gefunden, versuche HASSIO_TOKEN
        if not ha_token:
            ha_token = os.environ.get("HASSIO_TOKEN", "")
            if not ha_token:
                try:
                    token_file = "/run/s6/container_environment/HASSIO_TOKEN"
                    if os.path.exists(token_file):
                        with open(token_file, "r") as f:
                            ha_token = f.read().strip()
                except Exception:
                    pass

        if not ha_token:
            logger.warning("Kein HA-Token konfiguriert und kein SUPERVISOR_TOKEN verfügbar!")
        else:
            logger.info("Verwende SUPERVISOR_TOKEN für Home Assistant Verbindung")

    # Clients initialisieren
    ha_client = HAClient(ha_url, ha_token)
    sensor_manager = SensorManager()
    calculation_engine = CalculationEngine(ha_client, sensor_manager)

    # Verbindung testen
    if ha_client.test_connection():
        logger.info("Home Assistant Verbindung erfolgreich")
    else:
        logger.warning("Home Assistant Verbindung fehlgeschlagen")

    logger.info("HAminiEMS initialisiert")


@app.route("/")
def index():
    """Hauptseite"""
    return render_template("index.html")


@app.route("/config")
def config_page():
    """Konfigurationsseite"""
    return render_template("config.html")


@app.route("/logs")
def logs_page():
    """Logs-Seite"""
    return render_template("logs.html")


@app.route("/energy-costs")
def energy_costs_page():
    """Energiekosten-Seite (Platzhalter)"""
    return render_template("energy_costs.html")


# API Endpunkte

@app.route("/api/entities")
def api_entities():
    """Gibt alle konfigurierten Entitäten mit aktuellen Werten zurück"""
    try:
        values = calculation_engine.get_current_values()
        return jsonify({"success": True, "data": values})
    except Exception as e:
        logger.error(f"Fehler bei /api/entities: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/entities/<entity_id>")
def api_entity(entity_id: str):
    """Gibt eine einzelne Entität zurück"""
    try:
        state = ha_client.get_state(entity_id)
        if state:
            return jsonify({"success": True, "data": state})
        return jsonify({"success": False, "error": "Entity nicht gefunden"}), 404
    except Exception as e:
        logger.error(f"Fehler bei /api/entities/{entity_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config", methods=["GET"])
def api_get_config():
    """Gibt die aktuelle Konfiguration zurück"""
    try:
        configs = sensor_manager.get_all_configs()
        energy_entities = ha_client.get_energy_entities()

        return jsonify({
            "success": True,
            "data": {
                "sensor_configs": configs,
                "available_entities": [
                    {
                        "entity_id": e.get("entity_id"),
                        "friendly_name": e.get("attributes", {}).get("friendly_name"),
                        "state_class": e.get("attributes", {}).get("state_class"),
                        "unit": e.get("attributes", {}).get("unit_of_measurement"),
                    }
                    for e in energy_entities
                ],
                "sensor_keys": sensor_manager.get_all_sensor_keys(),
            }
        })
    except Exception as e:
        logger.error(f"Fehler bei /api/config: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config", methods=["POST"])
def api_save_config():
    """Speichert die Konfiguration"""
    try:
        data = request.get_json()
        configs = data.get("configs", [])

        if sensor_manager.save_configs(configs):
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Fehler beim Speichern"}), 500
    except Exception as e:
        logger.error(f"Fehler bei POST /api/config: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/data")
def api_data():
    """Gibt historische Daten zurück"""
    try:
        entity_id = request.args.get("entity_id")
        start = request.args.get("start")
        end = request.args.get("end")

        if not entity_id:
            return jsonify({"success": False, "error": "entity_id fehlt"}), 400

        values = sensor_manager.get_entity_values(entity_id, start, end)
        return jsonify({"success": True, "data": values})
    except Exception as e:
        logger.error(f"Fehler bei /api/data: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/calculations")
def api_calculations():
    """Gibt Berechnungsergebnisse zurück"""
    try:
        calc_type = request.args.get("type", "balance")

        if calc_type == "balance":
            balance = calculation_engine.calculate_energy_balance()
            return jsonify({"success": True, "data": balance})
        elif calc_type == "daily":
            stats = calculation_engine.get_daily_statistics()
            return jsonify({"success": True, "data": stats})
        else:
            return jsonify({"success": False, "error": "Unbekannter Typ"}), 400
    except Exception as e:
        logger.error(f"Fehler bei /api/calculations: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/refresh")
def api_refresh():
    """Aktualisiert alle Werte von Home Assistant"""
    try:
        configs = sensor_manager.get_enabled_sensors()
        updated = 0

        for config in configs:
            entity_id = config.get("entity_id")
            if not entity_id:
                continue

            state = ha_client.get_state(entity_id)
            if state:
                value = state.get("state")
                if value:
                    from .utils import parse_float, parse_datetime
                    from datetime import datetime

                    float_value = parse_float(value)
                    if float_value is not None:
                        sensor_manager.save_entity_value(
                            entity_id=entity_id,
                            value=float_value,
                            state_class=state.get("attributes", {}).get("state_class"),
                            unit=state.get("attributes", {}).get("unit_of_measurement"),
                            timestamp=parse_datetime(state.get("last_updated")) or datetime.now()
                        )
                        updated += 1

        return jsonify({"success": True, "updated": updated})
    except Exception as e:
        logger.error(f"Fehler bei /api/refresh: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health")
def api_health():
    """Health-Check Endpunkt"""
    try:
        ha_connected = ha_client.test_connection() if ha_client else False
        return jsonify({
            "success": True,
            "ha_connected": ha_connected,
            "status": "ok"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logs", methods=["GET"])
def api_get_logs():
    """Gibt die Logs zurück"""
    try:
        # Lese Log-Datei falls vorhanden
        log_file = "/config/haminiems.log"
        logs = []

        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Nimm die letzten 100 Zeilen
                    for line in lines[-100:]:
                        line = line.strip()
                        if line:
                            # Einfaches Parsing der Log-Zeile
                            # Format: YYYY-MM-DD HH:MM:SS,mmm - LEVEL - MESSAGE
                            import re
                            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)', line)
                            if match:
                                logs.append({
                                    "timestamp": match.group(1).replace(',', '.'),
                                    "level": match.group(2),
                                    "message": match.group(3)
                                })
                            else:
                                logs.append({
                                    "timestamp": "",
                                    "level": "INFO",
                                    "message": line
                                })
            except Exception as e:
                logger.error(f"Fehler beim Lesen der Log-Datei: {e}")

        # Falls keine Logs gefunden, gebe leere Liste zurück
        return jsonify({
            "success": True,
            "data": logs
        })
    except Exception as e:
        logger.error(f"Fehler bei /api/logs: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logs", methods=["DELETE"])
def api_clear_logs():
    """Löscht die Logs"""
    try:
        log_file = "/config/haminiems.log"
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write('')
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Logs: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


def main():
    """Hauptfunktion - startet den Web-Server"""
    try:
        init_app()

        # Port aus Umgebungsvariable lesen (Home Assistant)
        port = int(os.environ.get("PORT", 8099))

        logger.info(f"Starte HAminiEMS Web-Server auf Port {port}")

        app.run(
            host="0.0.0.0",
            port=port,
            debug=False
        )
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

