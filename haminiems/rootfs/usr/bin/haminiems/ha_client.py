"""Home Assistant REST API Client"""

import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("haminiems.ha_client")


class HAClient:
    """Client für Home Assistant REST API"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Führt eine HTTP-Anfrage aus"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler bei API-Anfrage {endpoint}: {e}")
            return None
    
    def get_states(self) -> List[Dict[str, Any]]:
        """Holt alle States von Home Assistant"""
        result = self._request("GET", "/api/states")
        return result if result else []
    
    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Holt den State einer einzelnen Entity"""
        result = self._request("GET", f"/api/states/{entity_id}")
        return result
    
    def get_entities_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Holt alle Entities einer Domain"""
        states = self.get_states()
        return [
            state for state in states
            if state.get("entity_id", "").startswith(f"{domain}.")
        ]
    
    def get_energy_entities(self) -> List[Dict[str, Any]]:
        """Holt alle Energie-Entities (mit state_class)"""
        from .utils import filter_energy_entities
        states = self.get_states()
        return filter_energy_entities(states)
    
    def set_state(
        self,
        entity_id: str,
        state: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Setzt den State einer Entity (via service call)"""
        domain = entity_id.split(".")[0]
        service = "set_value" if domain == "input_number" else "set"
        
        data = {
            "entity_id": entity_id,
            **({"attributes": attributes} if attributes else {})
        }
        
        result = self._request(
            "POST",
            f"/api/services/{domain}/{service}",
            json=data
        )
        return result is not None
    
    def get_history(
        self,
        entity_id: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Holt historische Daten für eine Entity"""
        params = {
            "filter_entity_id": entity_id,
            "end_time": end_time.isoformat() if end_time else datetime.now().isoformat(),
        }
        
        # Home Assistant History API erwartet start_time als Query-Parameter
        result = self._request(
            "GET",
            f"/api/history/period/{start_time.isoformat()}",
            params=params
        )
        
        if result and len(result) > 0:
            return result[0]  # API gibt Liste von Listen zurück
        return []
    
    def test_connection(self) -> bool:
        """Testet die Verbindung zu Home Assistant"""
        try:
            result = self._request("GET", "/api/")
            return result is not None and "message" in result
        except Exception as e:
            logger.error(f"Verbindungstest fehlgeschlagen: {e}")
            return False

