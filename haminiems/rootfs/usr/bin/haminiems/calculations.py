"""Berechnungslogik für HAminiEMS"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .sensors import SensorManager
from .ha_client import HAClient
from .utils import parse_float

logger = logging.getLogger("haminiems.calculations")


class CalculationEngine:
    """Berechnet Energieflüsse und Statistiken"""
    
    def __init__(self, ha_client: HAClient, sensor_manager: SensorManager):
        self.ha_client = ha_client
        self.sensor_manager = sensor_manager
    
    def get_current_values(self) -> Dict[str, Any]:
        """Holt aktuelle Werte aller konfigurierten Sensoren"""
        configs = self.sensor_manager.get_enabled_sensors()
        values = {}
        
        for config in configs:
            sensor_key = config.get("sensor_key")
            entity_id = config.get("entity_id")
            
            if not entity_id:
                continue
            
            # Hole aktuellen State von Home Assistant
            state = self.ha_client.get_state(entity_id)
            if state:
                value = parse_float(state.get("state"))
                if value is not None:
                    values[sensor_key] = {
                        "value": value,
                        "unit": state.get("attributes", {}).get("unit_of_measurement"),
                        "entity_id": entity_id,
                        "state": state.get("state"),
                        "last_updated": state.get("last_updated"),
                    }
        
        return values
    
    def calculate_energy_balance(self) -> Dict[str, Any]:
        """Berechnet Energiebilanz"""
        values = self.get_current_values()
        
        # Energiequellen
        pv_production = values.get("pv_production", {}).get("value", 0.0)
        grid_import = values.get("grid_import", {}).get("value", 0.0)
        battery_discharge = values.get("battery_discharge", {}).get("value", 0.0)
        
        # Energieverbraucher
        grid_export = values.get("grid_export", {}).get("value", 0.0)
        battery_charge = values.get("battery_charge", {}).get("value", 0.0)
        house_consumption = values.get("house_consumption", {}).get("value", 0.0)
        ev_charging = values.get("ev_charging", {}).get("value", 0.0)
        heat_pump = values.get("heat_pump", {}).get("value", 0.0)
        other_consumption = values.get("other_consumption", {}).get("value", 0.0)
        
        # Berechnungen
        total_production = pv_production
        total_available = total_production + grid_import + battery_discharge
        
        total_consumption = (
            house_consumption +
            ev_charging +
            heat_pump +
            other_consumption +
            battery_charge
        )
        
        self_consumption = min(total_production, total_consumption - grid_import - battery_discharge)
        self_consumption_rate = (
            (self_consumption / total_production * 100)
            if total_production > 0 else 0
        )
        
        return {
            "production": {
                "pv": pv_production,
                "total": total_production,
            },
            "consumption": {
                "house": house_consumption,
                "ev": ev_charging,
                "heat_pump": heat_pump,
                "other": other_consumption,
                "battery_charge": battery_charge,
                "total": total_consumption,
            },
            "grid": {
                "import": grid_import,
                "export": grid_export,
            },
            "battery": {
                "charge": battery_charge,
                "discharge": battery_discharge,
                "soc": values.get("battery_soc", {}).get("value"),
            },
            "balance": {
                "self_consumption": self_consumption,
                "self_consumption_rate": self_consumption_rate,
                "total_available": total_available,
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_daily_statistics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Berechnet Tagesstatistiken"""
        if date is None:
            date = datetime.now()
        
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # Hier könnten historische Daten aus der DB verwendet werden
        # Für jetzt verwenden wir aktuelle Werte
        balance = self.calculate_energy_balance()
        
        return {
            "date": date.date().isoformat(),
            "balance": balance,
            "summary": {
                "total_production": balance["production"]["total"],
                "total_consumption": balance["consumption"]["total"],
                "self_consumption_rate": balance["balance"]["self_consumption_rate"],
            }
        }



