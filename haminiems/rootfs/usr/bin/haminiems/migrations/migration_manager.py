"""Zentrale Migrations-Logik"""

import logging
import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Any
import sqlite3

logger = logging.getLogger("haminiems.migrations")


class MigrationManager:
    """Verwaltet Datenbank-Migrationen"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self._ensure_schema_tables()
        self.migrations = self._discover_migrations()
    
    def _ensure_schema_tables(self):
        """Erstellt Schema-Version Tabellen falls nicht vorhanden"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                app_version TEXT
            );
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_version INTEGER,
                migration_name TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                error_message TEXT
            );
        """)
        self.conn.commit()
    
    def _discover_migrations(self) -> Dict[int, Any]:
        """Entdeckt alle verfügbaren Migrationen"""
        migrations = {}
        migrations_path = Path(__file__).parent
        
        # Lade alle Migrations-Module
        for module_info in pkgutil.iter_modules([str(migrations_path)]):
            module_name = module_info.name
            if module_name.startswith("__"):
                continue
            
            try:
                # Importiere das Migrations-Modul
                full_module_name = f"haminiems.migrations.{module_name}"
                module = importlib.import_module(full_module_name)
                
                if hasattr(module, "VERSION") and hasattr(module, "up"):
                    version = module.VERSION
                    migrations[version] = module
                    logger.debug(f"Migration {version} gefunden: {module_name}")
            except Exception as e:
                logger.warning(
                    f"Fehler beim Laden von Migration {module_name}: {e}"
                )
        
        return migrations
    
    def get_current_version(self) -> int:
        """Gibt die aktuelle DB-Version zurück"""
        cursor = self.conn.execute(
            "SELECT MAX(version) as version FROM schema_version"
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    
    def get_applied_migrations(self) -> List[int]:
        """Gibt Liste aller angewendeten Migrationen zurück"""
        cursor = self.conn.execute(
            "SELECT DISTINCT migration_version FROM migration_log WHERE success = 1 ORDER BY migration_version"
        )
        return [row[0] for row in cursor.fetchall()]
    
    def migrate_to(self, target_version: int):
        """Führt Migrationen bis zur Ziel-Version aus"""
        current_version = self.get_current_version()
        applied = set(self.get_applied_migrations())
        
        if current_version >= target_version:
            logger.info(f"Keine Migration erforderlich (aktuell: {current_version})")
            return
        
        # Finde alle benötigten Migrationen
        needed_migrations = [
            version for version in sorted(self.migrations.keys())
            if version > current_version and version <= target_version
            and version not in applied
        ]
        
        if not needed_migrations:
            logger.info("Keine neuen Migrationen gefunden")
            return
        
        logger.info(f"Führe {len(needed_migrations)} Migration(en) aus...")
        
        # Führe Migrationen sequenziell aus
        for version in needed_migrations:
            migration_module = self.migrations[version]
            migration_name = migration_module.__name__.split(".")[-1]
            
            logger.info(f"Führe Migration {version} aus: {migration_name}")
            
            try:
                # Führe Migration in Transaktion aus
                self.conn.execute("BEGIN TRANSACTION")
                
                # Rufe up() Funktion auf
                migration_module.up(self.conn)
                
                # Protokolliere erfolgreiche Migration
                self.conn.execute("""
                    INSERT INTO migration_log 
                    (migration_version, migration_name, success)
                    VALUES (?, ?, ?)
                """, (version, migration_name, True))
                
                # Aktualisiere Schema-Version
                self.conn.execute("""
                    INSERT OR REPLACE INTO schema_version (version, app_version)
                    VALUES (?, ?)
                """, (version, "1.0.0"))
                
                self.conn.commit()
                logger.info(f"Migration {version} erfolgreich")
                
            except Exception as e:
                self.conn.rollback()
                error_msg = str(e)
                logger.error(f"Fehler bei Migration {version}: {error_msg}")
                
                # Protokolliere fehlgeschlagene Migration
                self.conn.execute("""
                    INSERT INTO migration_log 
                    (migration_version, migration_name, success, error_message)
                    VALUES (?, ?, ?, ?)
                """, (version, migration_name, False, error_msg))
                self.conn.commit()
                
                raise RuntimeError(
                    f"Migration {version} fehlgeschlagen: {error_msg}"
                ) from e
        
        logger.info("Alle Migrationen erfolgreich abgeschlossen")



