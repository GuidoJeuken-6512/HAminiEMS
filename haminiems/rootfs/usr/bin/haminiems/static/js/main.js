// HAminiEMS Main JavaScript

const API_BASE = '';
const REFRESH_INTERVAL = 30000; // 30 Sekunden

let refreshTimer = null;

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadSensors();
    loadEnergyBalance();
    setupAutoRefresh();
    
    document.getElementById('refresh-btn').addEventListener('click', () => {
        refreshAll();
    });
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
        
        displaySensors(data.data);
        updateLastUpdate();
    } catch (error) {
        console.error('Error loading sensors:', error);
        document.getElementById('sensors-grid').innerHTML = 
            `<div class="error">Fehler beim Laden der Sensoren: ${error.message}</div>`;
    }
}

function displaySensors(sensors) {
    const grid = document.getElementById('sensors-grid');
    
    if (Object.keys(sensors).length === 0) {
        grid.innerHTML = '<div class="loading">Keine Sensoren konfiguriert</div>';
        return;
    }
    
    grid.innerHTML = Object.entries(sensors).map(([key, sensor]) => {
        const value = sensor.value !== null && sensor.value !== undefined 
            ? sensor.value.toLocaleString('de-DE', { maximumFractionDigits: 2 })
            : '-';
        const unit = sensor.unit || '';
        const entityId = sensor.entity_id || '';
        
        return `
            <div class="sensor-card">
                <h3>${formatSensorKey(key)}</h3>
                <div class="sensor-value">${value}</div>
                <div class="sensor-unit">${unit}</div>
                <div class="sensor-entity">${entityId}</div>
            </div>
        `;
    }).join('');
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
        
        displayEnergyBalance(data.data);
    } catch (error) {
        console.error('Error loading energy balance:', error);
        document.getElementById('energy-balance').innerHTML = 
            `<h2>Energiebilanz</h2><div class="error">Fehler beim Laden: ${error.message}</div>`;
    }
}

function displayEnergyBalance(balance) {
    const container = document.getElementById('energy-balance');
    
    const html = `
        <h2>Energiebilanz</h2>
        <div class="balance-grid">
            <div class="balance-item">
                <div class="balance-item-label">PV-Produktion</div>
                <div class="balance-item-value">${formatValue(balance.production.pv)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Hausverbrauch</div>
                <div class="balance-item-value">${formatValue(balance.consumption.house)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Netzbezug</div>
                <div class="balance-item-value">${formatValue(balance.grid.import)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Netzeinspeisung</div>
                <div class="balance-item-value">${formatValue(balance.grid.export)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Selbstverbrauch</div>
                <div class="balance-item-value">${formatValue(balance.balance.self_consumption)}</div>
            </div>
            <div class="balance-item">
                <div class="balance-item-label">Selbstverbrauchsrate</div>
                <div class="balance-item-value">${formatValue(balance.balance.self_consumption_rate)}%</div>
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
    loadEnergyBalance();
    checkHealth();
}

// Cleanup beim Verlassen der Seite
window.addEventListener('beforeunload', () => {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
});


