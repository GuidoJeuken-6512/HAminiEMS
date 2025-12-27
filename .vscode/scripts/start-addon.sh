#!/bin/bash
# Script zum Starten eines Add-Ons mit automatischem Build falls nötig

ADDON_NAME="local_${1:-haminiems}"

echo "🔍 Prüfe Add-On Status für: $ADDON_NAME"

# Prüfe ob Add-On installiert ist
if ha addons info "$ADDON_NAME" 2>&1 | grep -q "installed: true"; then
    echo "✅ Add-On ist installiert"
else
    echo "⚠️  Add-On nicht installiert. Registriere und baue es lokal..."
    ha addons reload
    sleep 3

    # Erkenne Architektur
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        BUILD_ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        BUILD_ARCH="aarch64"
    else
        BUILD_ARCH="amd64"  # Fallback
    fi

    echo "🔨 Baue Add-On lokal mit Docker (Architektur: $BUILD_ARCH)..."
    # Wechsle ins haminiems-Verzeichnis (relativ zum Workspace-Root)
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    WORKSPACE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
    cd "$WORKSPACE_DIR/haminiems" || {
        echo "❌ Konnte nicht ins haminiems-Verzeichnis wechseln"
        exit 1
    }

    # Baue das Image direkt mit Docker
    docker build \
        --build-arg BUILD_ARCH="$BUILD_ARCH" \
        --build-arg BUILD_FROM="ghcr.io/home-assistant/${BUILD_ARCH}-base:3.15" \
        --build-arg TEMPIO_VERSION="2021.09.0" \
        -t "addon_local_${1:-haminiems}:1.0.0" \
        . || {
        echo "❌ Fehler beim Bauen des Docker-Images"
        exit 1
    }

    echo "✅ Docker-Image erfolgreich gebaut!"

    # Wechsle zurück ins Workspace-Verzeichnis für ha addons build
    cd "$WORKSPACE_DIR" || {
        echo "❌ Konnte nicht ins Workspace-Verzeichnis wechseln"
        exit 1
    }

    # Verwende ha addons build, damit der Supervisor das lokale Image verwendet
    echo "🔨 Baue Add-On über Supervisor (verwendet lokales Image)..."
    BUILD_OUTPUT=$(ha addons build "$ADDON_NAME" 2>&1)
    if echo "$BUILD_OUTPUT" | grep -q "Error\|error\|500\|unexpected\|failed"; then
        echo "⚠️  Build über Supervisor fehlgeschlagen, versuche direkt zu installieren..."
        # Versuche jetzt, es über den Supervisor zu installieren
        echo "📦 Versuche Add-On über Supervisor zu installieren..."
        INSTALL_OUTPUT=$(ha addons install "$ADDON_NAME" 2>&1)
        if echo "$INSTALL_OUTPUT" | grep -q "Error\|error\|500\|unexpected"; then
            echo "⚠️  Automatische Installation über CLI fehlgeschlagen"
            echo ""
            echo "📋 Bitte installiere das Add-On manuell über die Home Assistant UI:"
            echo "   1. Öffne Home Assistant Web-Interface"
            echo "   2. Gehe zu Einstellungen → Add-ons → Add-on Store"
            echo "   3. Klicke auf 'local_haminiems'"
            echo "   4. Klicke auf 'Installieren'"
            echo ""
            echo "   Das Docker-Image wurde bereits gebaut."
            echo "   Der Supervisor sollte das lokale Image verwenden können."
            echo ""
            echo "   Nach der Installation kannst du das Add-On starten."
            exit 1
        fi
    else
        echo "✅ Add-On erfolgreich über Supervisor gebaut!"
    fi

    echo "✅ Add-On erfolgreich installiert!"

    # Warte kurz, damit der Supervisor den Status aktualisiert
    sleep 3
fi

# Stoppe Add-On falls es läuft
echo "🛑 Stoppe Add-On (falls läuft)..."
ha addons stop "$ADDON_NAME" 2>/dev/null || true

# Starte Add-On
echo "🚀 Starte Add-On..."
ha addons start "$ADDON_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Add-On gestartet!"
    sleep 2
    echo "📋 Zeige Logs..."
    docker logs --follow "addon_${1:-haminiems}"
else
    echo "❌ Fehler beim Starten des Add-Ons"
    exit 1
fi

