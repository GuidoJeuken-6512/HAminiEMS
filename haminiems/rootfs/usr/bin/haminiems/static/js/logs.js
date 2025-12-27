// HAminiEMS Logs JavaScript

const API_BASE = '';

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    loadLogs();

    document.getElementById('refresh-logs-btn').addEventListener('click', () => {
        loadLogs();
    });

    document.getElementById('clear-logs-btn').addEventListener('click', () => {
        if (confirm('Möchten Sie wirklich alle Logs löschen?')) {
            clearLogs();
        }
    });
});

async function loadLogs() {
    try {
        const container = document.getElementById('logs-container');
        container.innerHTML = '<div class="loading">Lade Logs...</div>';

        const response = await fetch(`${API_BASE}/api/logs`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Fehler beim Laden');
        }

        displayLogs(data.data || []);
    } catch (error) {
        console.error('Error loading logs:', error);
        document.getElementById('logs-container').innerHTML =
            `<div class="error">Fehler beim Laden der Logs: ${error.message}</div>`;
    }
}

function displayLogs(logs) {
    const container = document.getElementById('logs-container');

    if (!logs || logs.length === 0) {
        container.innerHTML = '<div class="loading">Keine Logs verfügbar</div>';
        return;
    }

    const html = `
        <div class="logs-list">
            ${logs.map(log => `
                <div class="log-entry log-${log.level?.toLowerCase() || 'info'}">
                    <div class="log-timestamp">${formatTimestamp(log.timestamp)}</div>
                    <div class="log-level">${log.level || 'INFO'}</div>
                    <div class="log-message">${escapeHtml(log.message || '')}</div>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = html;

    // Scroll zum Ende
    container.scrollTop = container.scrollHeight;
}

async function clearLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/logs`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            loadLogs();
        } else {
            alert('Fehler beim Löschen der Logs: ' + (data.error || 'Unbekannter Fehler'));
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        alert('Fehler beim Löschen der Logs: ' + error.message);
    }
}

function formatTimestamp(timestamp) {
    if (!timestamp) return '-';
    try {
        const date = new Date(timestamp);
        return date.toLocaleString('de-DE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        return timestamp;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

