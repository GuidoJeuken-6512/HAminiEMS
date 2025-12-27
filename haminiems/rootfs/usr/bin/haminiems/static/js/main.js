// HAminiEMS Main JavaScript

const API_BASE = '';
const REFRESH_INTERVAL = 30000; // 30 Sekunden

let refreshTimer = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadSensors();
    setupAutoRefresh();

    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            refreshAll();
        });
    }
});

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();

        const statusEl = document.getElementById('connection-status');
        if (data.ha_connected) {
            statusEl.textContent = 'Verbunden';
            statusEl.style.color = '#4caf50';
        } else {
            statusEl.textContent = 'Nicht verbunden';
            statusEl.style.color = '#f44336';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('connection-status').textContent = 'Fehler';
        document.getElementById('connection-status').style.color = '#f44336';
    }
}

async function loadSensors() {
    try {
        const response = await fetch(`${API_BASE}/api/entities`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Fehler beim Laden');
        }

        // Prüfe ob data.data existiert und ein Objekt ist
        const sensors = data.data || {};
        displaySensors(sensors);
        updateLastUpdate();
    } catch (error) {
        console.error('Error loading sensors:', error);
        document.getElementById('sensors-grid').innerHTML =
            `<div class="error">Fehler beim Laden der Sensoren: ${error.message}</div>`;
    }
}

function displaySensors(sensors) {
    // Aktualisiere die vorhandenen Sensor-Karten
    Object.entries(sensors).forEach(([key, sensor]) => {
        const valueEl = document.getElementById(`${key}-value`);
        const unitEl = document.getElementById(`${key}-unit`);
        const entityEl = document.getElementById(`${key}-entity`);

        if (valueEl) {
            const value = sensor.value !== null && sensor.value !== undefined
                ? sensor.value.toLocaleString('de-DE', { maximumFractionDigits: 2 })
                : '-';
            valueEl.textContent = value;
        }

        if (unitEl) {
            unitEl.textContent = sensor.unit || '';
        }

        if (entityEl) {
            entityEl.textContent = sensor.entity_id || 'Nicht konfiguriert';
        }
    });

    // Wenn keine Sensoren konfiguriert sind, zeige "Nicht konfiguriert" für alle
    if (Object.keys(sensors).length === 0) {
        const sensorKeys = ['pv_production', 'grid_import', 'grid_export', 'battery_charge', 'battery_discharge', 'battery_soc', 'house_consumption'];
        sensorKeys.forEach(key => {
            const entityEl = document.getElementById(`${key}-entity`);
            if (entityEl) {
                entityEl.textContent = 'Nicht konfiguriert';
            }
        });
    }
}

function formatSensorKey(key) {
    return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

async function loadEnergyBalance() {
    try {
        const response = await fetch(`${API_BASE}/api/calculations?type=balance`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Fehler beim Laden');
        }

        // Prüfe ob data.data existiert
        const balance = data.data || {};
        displayEnergyBalance(balance);
    } catch (error) {
        console.error('Error loading energy balance:', error);
        document.getElementById('energy-balance').innerHTML =
            `<h2>Energiebilanz</h2><div class="error">Fehler beim Laden: ${error.message}</div>`;
    }
}

function displayEnergyBalance(balance) {
    const container = document.getElementById('energy-balance');

    // Prüfe ob balance die erwartete Struktur hat
    if (!balance || !balance.production || !balance.consumption || !balance.grid || !balance.balance) {
        container.innerHTML = `
            <h2>Energiebilanz</h2>
            <div class="loading">Keine Daten verfügbar. Bitte konfigurieren Sie zuerst Sensoren.</div>
        `;
        return;
    }

    const html = `
        <h2>Energiebilanz</h2>
        <div class="balance-grid">
            <div class="balance-item">
                <div class="balance-item-label">PV-Produktion</div>
                <div class="balance-item-value">${formatValue(balance.production?.pv)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Hausverbrauch</div>
                <div class="balance-item-value">${formatValue(balance.consumption?.house)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Netzbezug</div>
                <div class="balance-item-value">${formatValue(balance.grid?.import)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Netzeinspeisung</div>
                <div class="balance-item-value">${formatValue(balance.grid?.export)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Selbstverbrauch</div>
                <div class="balance-item-value">${formatValue(balance.balance?.self_consumption)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Selbstverbrauchsrate</div>
                <div class="balance-item-value">${formatValue(balance.balance?.self_consumption_rate)}%</div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function formatValue(value) {
    if (value === null || value === undefined) return '-';
    return value.toLocaleString('de-DE', { maximumFractionDigits: 2 });
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('last-update').textContent =
        now.toLocaleTimeString('de-DE');
}

function setupAutoRefresh() {
    refreshTimer = setInterval(() => {
        refreshAll();
    }, REFRESH_INTERVAL);
}

function refreshAll() {
    loadSensors();
    checkHealth();
}

// Cleanup beim Verlassen der Seite
window.addEventListener('beforeunload', () => {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
});



