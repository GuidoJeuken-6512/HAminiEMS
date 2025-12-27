// HAminiEMS Configuration JavaScript

const API_BASE = '';

let availableEntities = [];
let sensorKeys = [];
let currentConfigs = {};

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    
    document.getElementById('config-form').addEventListener('submit', (e) => {
        e.preventDefault();
        saveConfig();
    });
    
    document.getElementById('cancel-btn').addEventListener('click', () => {
        window.location.href = '/';
    });
});

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Fehler beim Laden');
        }
        
        availableEntities = data.data.available_entities || [];
        sensorKeys = data.data.sensor_keys || [];
        currentConfigs = {};
        
        // Erstelle Mapping von entity_id zu Config
        (data.data.sensor_configs || []).forEach(config => {
            currentConfigs[config.sensor_key] = config;
        });
        
        displayConfigForm();
    } catch (error) {
        console.error('Error loading config:', error);
        document.getElementById('sensor-configs').innerHTML = 
            `<div class="error">Fehler beim Laden der Konfiguration: ${error.message}</div>`;
    }
}

function displayConfigForm() {
    const container = document.getElementById('sensor-configs');
    
    if (sensorKeys.length === 0) {
        container.innerHTML = '<div class="loading">Keine Sensoren definiert</div>';
        return;
    }
    
    // Header
    let html = `
        <div class="sensor-config" style="font-weight: bold; background-color: #f5f5f5;">
            <div>Sensor</div>
            <div>Home Assistant Entity</div>
            <div>Typ</div>
            <div>Aktiviert</div>
        </div>
    `;
    
    // Sensor-Konfigurationen
    sensorKeys.forEach(key => {
        const config = currentConfigs[key] || {};
        const entityId = config.entity_id || '';
        const dailyTotal = config.daily_total || '';
        const enabled = config.enabled !== false;
        
        html += `
            <div class="sensor-config">
                <label>${formatSensorKey(key)}</label>
                <select name="${key}_entity" data-sensor-key="${key}">
                    <option value="">-- Keine Auswahl --</option>
                    ${availableEntities.map(entity => `
                        <option value="${entity.entity_id}" 
                                ${entity.entity_id === entityId ? 'selected' : ''}>
                            ${entity.friendly_name || entity.entity_id}
                            ${entity.unit ? ` (${entity.unit})` : ''}
                        </option>
                    `).join('')}
                </select>
                <select name="${key}_type" data-sensor-key="${key}">
                    <option value="">--</option>
                    <option value="daily" ${dailyTotal === 'daily' ? 'selected' : ''}>Tageswert</option>
                    <option value="total" ${dailyTotal === 'total' ? 'selected' : ''}>Gesamtwert</option>
                </select>
                <input type="checkbox" name="${key}_enabled" 
                       data-sensor-key="${key}" 
                       ${enabled ? 'checked' : ''}>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function formatSensorKey(key) {
    return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

async function saveConfig() {
    const form = document.getElementById('config-form');
    const configs = [];
    
    // Sammle alle Konfigurationen
    sensorKeys.forEach(key => {
        const entitySelect = form.querySelector(`select[data-sensor-key="${key}"][name$="_entity"]`);
        const typeSelect = form.querySelector(`select[data-sensor-key="${key}"][name$="_type"]`);
        const enabledCheckbox = form.querySelector(`input[data-sensor-key="${key}"][name$="_enabled"]`);
        
        const entityId = entitySelect ? entitySelect.value : '';
        const dailyTotal = typeSelect ? typeSelect.value : '';
        const enabled = enabledCheckbox ? enabledCheckbox.checked : true;
        
        configs.push({
            sensor_key: key,
            entity_id: entityId || null,
            daily_total: dailyTotal || null,
            enabled: enabled
        });
    });
    
    try {
        const response = await fetch(`${API_BASE}/api/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ configs })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Konfiguration erfolgreich gespeichert!', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showMessage(`Fehler: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error saving config:', error);
        showMessage(`Fehler beim Speichern: ${error.message}`, 'error');
    }
}

function showMessage(message, type) {
    const container = document.querySelector('.config-section');
    const messageEl = document.createElement('div');
    messageEl.className = type === 'success' ? 'success-message' : 'error';
    messageEl.textContent = message;
    
    container.insertBefore(messageEl, container.firstChild);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}


