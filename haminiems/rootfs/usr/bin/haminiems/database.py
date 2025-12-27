"""SQLite-Datenbank-Handler mit Migration-Integration"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .const import DB_VERSION, DB_PATH
from .migrations.migration_manager import MigrationManager

logger = logging.getLogger("haminiems.database")


class Database:
    """Datenbank-Handler mit automatischer Migration"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        self._run_migrations()
    
    def _ensure_db_directory(self):
        """Stellt sicher, dass das DB-Verzeichnis existiert"""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialisiert die Datenbank-Verbindung"""
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Datenbank verbunden: {self.db_path}")
    
    def _run_migrations(self):
        """Führt automatische Migrationen aus"""
        try:
            manager = MigrationManager(self.conn)
            current_version = manager.get_current_version()
            target_version = DB_VERSION
            
            logger.info(
                f"DB-Version: {current_version} -> {target_version}"
            )
            
            if current_version < target_version:
                logger.info("Starte Datenbank-Migrationen...")
                manager.migrate_to(target_version)
                logger.info("Migrationen erfolgreich abgeschlossen")
            elif current_version > target_version:
                logger.warning(
                    f"DB-Version ({current_version}) ist höher als "
                    f"App-Version ({target_version})"
                )
            else:
                logger.info("Datenbank ist auf dem neuesten Stand")
        except Exception as e:
            logger.error(f"Fehler bei Migration: {e}", exc_info=True)
            raise
    
    @contextmanager
    def get_connection(self):
        """Context Manager für Datenbank-Verbindungen"""
        try:
            yield self.conn
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Datenbank-Fehler: {e}", exc_info=True)
            raise
    
    def execute(self, query: str, params: tuple = ()):
        """Führt eine SQL-Query aus"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Holt einen einzelnen Datensatz"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Holt alle Datensätze"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Schließt die Datenbank-Verbindung"""
        if self.conn:
            self.conn.close()
            logger.info("Datenbank-Verbindung geschlossen")


# Globale Datenbank-Instanz
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Gibt die globale Datenbank-Instanz zurück"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


