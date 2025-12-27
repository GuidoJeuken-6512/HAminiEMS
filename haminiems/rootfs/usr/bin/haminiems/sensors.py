"""Sensor-Management für HAminiEMS"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .database import get_database
from .const import SENSOR_KEYS
from .utils import parse_float

logger = logging.getLogger("haminiems.sensors")


class SensorManager:
    """Verwaltet Sensor-Konfigurationen und Werte"""
    
    def __init__(self):
        self.db = get_database()
    
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """Holt alle Sensor-Konfigurationen"""
        rows = self.db.fetch_all(
            "SELECT * FROM sensor_config ORDER BY sensor_key"
        )
        return [dict(row) for row in rows]
    
    def get_config(self, sensor_key: str) -> Optional[Dict[str, Any]]:
        """Holt Konfiguration für einen Sensor"""
        row = self.db.fetch_one(
            "SELECT * FROM sensor_config WHERE sensor_key = ?",
            (sensor_key,)
        )
        return dict(row) if row else None
    
    def save_config(
        self,
        sensor_key: str,
        entity_id: Optional[str] = None,
        daily_total: Optional[str] = None,
        enabled: bool = True
    ) -> bool:
        """Speichert oder aktualisiert eine Sensor-Konfiguration"""
        try:
            self.db.execute("""
                INSERT OR REPLACE INTO sensor_config
                (sensor_key, entity_id, daily_total, enabled)
                VALUES (?, ?, ?, ?)
            """, (sensor_key, entity_id, daily_total, enabled))
            logger.info(f"Konfiguration gespeichert: {sensor_key} -> {entity_id}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def save_configs(self, configs: List[Dict[str, Any]]) -> bool:
        """Speichert mehrere Konfigurationen"""
        try:
            for config in configs:
                self.save_config(
                    sensor_key=config.get("sensor_key"),
                    entity_id=config.get("entity_id"),
                    daily_total=config.get("daily_total"),
                    enabled=config.get("enabled", True)
                )
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfigurationen: {e}")
            return False
    
    def delete_config(self, sensor_key: str) -> bool:
        """Löscht eine Sensor-Konfiguration"""
        try:
            self.db.execute(
                "DELETE FROM sensor_config WHERE sensor_key = ?",
                (sensor_key,)
            )
            logger.info(f"Konfiguration gelöscht: {sensor_key}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Konfiguration: {e}")
            return False
    
    def save_entity_value(
        self,
        entity_id: str,
        value: float,
        state_class: Optional[str] = None,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Speichert einen Entity-Wert"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            self.db.execute("""
                INSERT INTO entity_values
                (timestamp, entity_id, value, state_class, unit)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, entity_id, value, state_class, unit))
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Entity-Werts: {e}")
            return False
    
    def get_entity_values(
        self,
        entity_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Holt historische Werte für eine Entity"""
        query = "SELECT * FROM entity_values WHERE entity_id = ?"
        params = [entity_id]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        rows = self.db.fetch_all(query, tuple(params))
        return [dict(row) for row in rows]
    
    def get_latest_value(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Holt den neuesten Wert für eine Entity"""
        rows = self.get_entity_values(entity_id, limit=1)
        return rows[0] if rows else None
    
    def get_all_sensor_keys(self) -> List[str]:
        """Gibt alle definierten Sensor-Keys zurück"""
        return SENSOR_KEYS
    
    def get_enabled_sensors(self) -> List[Dict[str, Any]]:
        """Holt alle aktivierten Sensor-Konfigurationen"""
        rows = self.db.fetch_all(
            "SELECT * FROM sensor_config WHERE enabled = 1 ORDER BY sensor_key"
        )
        return [dict(row) for row in rows]

