"""Initiales Datenbank-Schema - Migration 001"""

VERSION = 1


def up(db_connection):
    """Erstellt initiales Schema"""
    db_connection.execute("""
        CREATE TABLE IF NOT EXISTS entity_values (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            entity_id TEXT NOT NULL,
            value REAL,
            state_class TEXT,
            unit TEXT
        );
    """)
    
    db_connection.execute("""
        CREATE TABLE IF NOT EXISTS sensor_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_key TEXT UNIQUE NOT NULL,
            entity_id TEXT,
            daily_total TEXT,
            enabled BOOLEAN DEFAULT 1
        );
    """)
    
    # Index für bessere Performance
    db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_values_timestamp
        ON entity_values(timestamp);
    """)
    
    db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_values_entity_id
        ON entity_values(entity_id);
    """)
    
    db_connection.commit()


def down(db_connection):
    """Rollback - entfernt Tabellen"""
    db_connection.execute("DROP INDEX IF EXISTS idx_entity_values_entity_id;")
    db_connection.execute("DROP INDEX IF EXISTS idx_entity_values_timestamp;")
    db_connection.execute("DROP TABLE IF EXISTS sensor_config;")
    db_connection.execute("DROP TABLE IF EXISTS entity_values;")
    db_connection.commit()

