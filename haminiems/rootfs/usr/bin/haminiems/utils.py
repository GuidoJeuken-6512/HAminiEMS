"""Hilfsfunktionen für HAminiEMS"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Konfiguriert das Logging-System"""
    logger = logging.getLogger("haminiems")
    logger.setLevel(getattr(logging, level.upper()))
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def parse_float(value: Any) -> Optional[float]:
    """Konvertiert einen Wert zu float, gibt None bei Fehler"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Konvertiert einen ISO-Format String zu datetime"""
    if not dt_str:
        return None
    try:
        # Home Assistant verwendet ISO-Format
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def get_state_class(entity: Dict[str, Any]) -> Optional[str]:
    """Extrahiert state_class aus Entity-Attributen"""
    attributes = entity.get("attributes", {})
    return attributes.get("state_class")


def get_unit(entity: Dict[str, Any]) -> Optional[str]:
    """Extrahiert unit_of_measurement aus Entity-Attributen"""
    attributes = entity.get("attributes", {})
    return attributes.get("unit_of_measurement")


def is_energy_entity(entity: Dict[str, Any]) -> bool:
    """Prüft ob eine Entity eine Energie-Entity ist"""
    state_class = get_state_class(entity)
    return state_class in ["total", "total_increasing", "measurement"]


def filter_energy_entities(entities: list) -> list:
    """Filtert Entities nach state_class für Energie"""
    return [
        entity for entity in entities
        if is_energy_entity(entity)
    ]

