# HAminiEMS - Installationsanleitung

Diese Anleitung führt Sie Schritt für Schritt durch die Installation von HAminiEMS.

## Voraussetzungen

- Home Assistant mit Supervisor (HassOS, Home Assistant OS, oder Supervised Installation)
- Internetverbindung für den ersten Download
- Zugriff auf Home Assistant Web-Interface

## Schritt 1: Repository hinzufügen

1. Öffne dein Home Assistant Web-Interface
2. Gehe zu **Einstellungen** (⚙️)
3. Wähle **Add-ons** aus dem Menü
4. Klicke auf **Add-on Store** (falls nicht bereits geöffnet)
5. Klicke auf die drei Punkte (⋮) oben rechts
6. Wähle **Repositories** aus dem Menü
7. Füge folgende URL hinzu:
   ```
   https://github.com/GuidoJeuken-6512/HAminiEMS
   ```
8. Klicke auf **Hinzufügen**

## Schritt 2: Add-On installieren

1. Suche im Add-On Store nach **"HAminiEMS"**
2. Klicke auf das HAminiEMS Add-On
3. Klicke auf **Installieren**
4. Warte, bis die Installation abgeschlossen ist (kann einige Minuten dauern)

## Schritt 3: Home Assistant Token erstellen

Ein Long-Lived Access Token ist erforderlich, damit HAminiEMS auf die Home Assistant API zugreifen kann.

1. Gehe zu deinem **Profil** (klicke auf deinen Benutzernamen unten links)
2. Scrolle nach unten zu **Long-Lived Access Tokens**
3. Klicke auf **Token erstellen**
4. Gib einen Namen ein (z.B. "HAminiEMS")
5. **WICHTIG**: Kopiere den generierten Token sofort - er wird nur einmal angezeigt!
6. Speichere den Token an einem sicheren Ort

## Schritt 4: Add-On konfigurieren

1. Öffne die HAminiEMS Add-On Seite (falls nicht bereits geöffnet)
2. Gehe zum Tab **Konfiguration**
3. Füge den kopierten Token in das Feld `ha_token` ein:
   ```yaml
   ha_url: "http://supervisor/core"
   ha_token: "eyJ0eXAiOiJKV1QiLCJhbGc..."  # Hier deinen Token einfügen
   refresh_interval: 30
   ```
4. Passe die anderen Optionen an, falls nötig:
   - `ha_url`: Standard ist `http://supervisor/core`. Für Supervised Installationen kann dies `http://homeassistant:8123` sein.
   - `refresh_interval`: Standard ist 30 Sekunden. Minimum: 1 Sekunde.
5. Klicke auf **Speichern**

## Schritt 5: Add-On starten

1. Gehe zum Tab **Info**
2. Klicke auf **Start**
3. Warte, bis der Status **"Running"** anzeigt
4. Prüfe die **Logs**, falls es Probleme gibt

## Schritt 6: Web-Interface öffnen

1. Auf der Add-On Seite findest du einen Button **"ÖFFNEN"** oder **"WEITERLEITEN"**
2. Klicke darauf, um das Web-Interface zu öffnen
3. Alternativ: Öffne die URL direkt (wird im Add-On angezeigt)

## Schritt 7: Sensoren konfigurieren

1. Im Web-Interface: Navigiere zur **Konfigurationsseite** (Link oben rechts)
2. Für jeden Sensor:
   - Wähle die entsprechende Home Assistant Entity aus dem Dropdown
   - Wähle den Typ (nur bei Energie-Entities):
     - **Tageswert**: Für tägliche Energie-Werte
     - **Gesamtwert**: Für Gesamtenergie seit Installation
   - Aktiviere/Deaktiviere den Sensor mit der Checkbox
3. Klicke auf **Speichern**
4. Gehe zurück zur Hauptseite, um die Werte zu sehen

## Verifikation

Um zu prüfen, ob alles funktioniert:

1. **Status prüfen**: Auf der Hauptseite sollte "Status: Verbunden" angezeigt werden
2. **Sensoren prüfen**: Konfigurierte Sensoren sollten Werte anzeigen
3. **Logs prüfen**: Im Add-On Tab **Logs** sollten keine Fehler sein

## Häufige Probleme

### Add-On startet nicht

- **Lösung**: Prüfe die Logs im Add-On Tab. Häufige Ursachen:
  - Fehlender oder ungültiger Token
  - Falsche `ha_url`
  - Netzwerkprobleme

### Keine Sensoren sichtbar

- **Lösung**: 
  - Gehe zur Konfigurationsseite
  - Ordne Sensoren zu Home Assistant Entities zu
  - Stelle sicher, dass die Entities in Home Assistant existieren

### Token-Fehler

- **Lösung**: 
  - Erstelle einen neuen Token in Home Assistant
  - Kopiere den Token vollständig (kann sehr lang sein)
  - Füge den Token ohne Leerzeichen ein

## Nächste Schritte

Nach erfolgreicher Installation:

1. Konfiguriere alle Sensoren auf der Konfigurationsseite
2. Prüfe die Energiebilanz auf der Hauptseite
3. Passe das Refresh-Interval an, falls nötig
4. Nutze die API für externe Integrationen (siehe [API-Dokumentation](README.md#api-dokumentation))

## Unterstützung

Bei Problemen:

1. Prüfe die [Troubleshooting Sektion](../README.md#troubleshooting) in der Hauptdokumentation
2. Öffne ein [Issue auf GitHub](https://github.com/GuidoJeuken-6512/HAminiEMS/issues)
3. Prüfe die Logs im Add-On Tab



