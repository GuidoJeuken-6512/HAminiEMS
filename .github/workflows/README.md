# GitHub Actions Workflows

Dieses Verzeichnis enthält die GitHub Actions Workflows für das HAminiEMS Add-On.

## Workflows

### release.yaml (Standard)

Automatischer Build und Veröffentlichung des Add-Ons auf GitHub Container Registry (ghcr.io) mit der offiziellen `home-assistant/builder` Action.

**Trigger:**
- Push auf `main` Branch (nur bei Änderungen in `haminiems/`)
- Release-Veröffentlichung
- Manueller Trigger via `workflow_dispatch`

**Funktionen:**
- Baut das Add-On für alle unterstützten Architekturen (aarch64, amd64)
- Veröffentlicht Images auf GitHub Container Registry
- Verwendet die offizielle `home-assistant/builder` Action

**Berechtigungen:**
- `contents: read` - Repository lesen
- `packages: write` - Images auf ghcr.io veröffentlichen

### release-alternative.yaml (Alternative)

Alternative Workflow-Version, die direkt mit Docker Buildx arbeitet. Verwenden Sie diese Version, falls die `home-assistant/builder` Action Probleme macht.

**Funktionen:**
- Baut Images direkt mit Docker Buildx
- Unterstützt Multi-Architecture Builds (aarch64, amd64)
- Automatische Tag-Generierung (Version, Branch, SHA, latest)
- Docker Layer Caching für schnellere Builds

## Verwendung

### Automatisch bei Push

1. Änderungen in `haminiems/` committen und pushen
2. Workflow startet automatisch
3. Images werden auf ghcr.io veröffentlicht

### Manuell auslösen

1. Gehe zu **Actions** → **Release Add-on** (oder **Release Add-on (Alternative)**)
2. Klicke auf **Run workflow**
3. Wähle Branch aus (normalerweise `main`)
4. Klicke auf **Run workflow**

### Bei Release

1. Erstelle ein Release auf GitHub
2. Workflow startet automatisch
3. Images werden mit Release-Tags veröffentlicht

## Veröffentlichte Images

Die Images werden unter folgenden Namen veröffentlicht:

- `ghcr.io/guidojeuken-6512/aarch64-addon-haminiems:<tag>`
- `ghcr.io/guidojeuken-6512/amd64-addon-haminiems:<tag>`

**Tags:**
- `latest` - Nur für `main` Branch
- `<version>` - Aus `haminiems/config.yaml` (z.B. `1.0.0`)
- `<major>.<minor>` - Major.Minor Version (z.B. `1.0`)
- `<branch>-<sha>` - Branch und Commit SHA
- Release-Tags - Bei GitHub Releases

## Konfiguration

### Repository-Einstellungen

Stellen Sie sicher, dass folgende Einstellungen aktiviert sind:

1. **Settings** → **Actions** → **General**
   - **Workflow permissions**: "Read and write permissions"
   - **Allow GitHub Actions to create and approve pull requests**: Aktiviert

2. **Settings** → **Actions** → **General** → **Artifact and log retention**
   - Empfohlen: 30 Tage

### Container Registry

Die Images werden automatisch auf GitHub Container Registry (ghcr.io) veröffentlicht. 

**Sichtbarkeit:**
- Standard: Privat
- Um öffentlich zu machen: Gehe zu Package Settings → Change visibility → Public

## Troubleshooting

### Workflow schlägt fehl

1. **Prüfe Logs**: Gehe zu **Actions** → Wähle fehlgeschlagenen Run → Prüfe Logs
2. **Token prüfen**: `GITHUB_TOKEN` sollte automatisch verfügbar sein
3. **Berechtigungen prüfen**: Siehe Repository-Einstellungen oben

### Images werden nicht veröffentlicht

1. **Container Registry prüfen**: Gehe zu **Packages** im Repository
2. **Berechtigungen prüfen**: `packages: write` Permission muss gesetzt sein
3. **Login prüfen**: Workflow muss erfolgreich bei ghcr.io eingeloggt sein

### Build dauert zu lange

1. **Caching aktiviert**: Der alternative Workflow verwendet Docker Layer Caching
2. **Nur relevante Änderungen**: Workflow triggert nur bei Änderungen in `haminiems/`

## Weitere Informationen

- [Home Assistant Add-On Dokumentation](https://developers.home-assistant.io/docs/add-ons)
- [GitHub Actions Dokumentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
