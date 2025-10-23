// BolliOs Simple Switch Controls
// Original simple switch interface for BolliOs gyro balance

(function() {
    'use strict';
    
    let bolliOsStatus = {
        active: false,
        running: false
    };
    let websocketConnection = null;
    
    // Simple WebSocket connection
    function getWebSocketConnection() {
        // Try to use existing global WebSocket connections
        if (window.websocket && window.websocket.readyState === WebSocket.OPEN) {
            return window.websocket;
        }
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            return window.ws;
        }
        
        // Create new WebSocket if needed
        if (!websocketConnection || websocketConnection.readyState !== WebSocket.OPEN) {
            try {
                websocketConnection = new WebSocket('ws://' + location.hostname + ':8888');
                
                websocketConnection.onopen = function() {
                    console.log('BolliOs: WebSocket connected');
                };
                
                websocketConnection.onmessage = function(event) {
                    try {
                        const response = JSON.parse(event.data);
                        if (response.title === 'bolliOsStatus') {
                            updateStatus(response.data);
                        } else if (response.title === 'bolliOs') {
                            bolliOsStatus.active = response.data === 'activated';
                            updateUI();
                        }
                    } catch (e) {
                        // Ignore non-JSON messages
                    }
                };
                
                websocketConnection.onclose = function() {
                    console.log('BolliOs: WebSocket disconnected');
                    websocketConnection = null;
                };
                
                websocketConnection.onerror = function(error) {
                    console.log('BolliOs: WebSocket error:', error);
                };
                
            } catch (error) {
                console.log('BolliOs: Failed to create WebSocket:', error);
            }
        }
        
        return websocketConnection;
    }
    
    // Send simple command
    function sendCommand(command) {
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(command);
            console.log('BolliOs: Sent command:', command);
        } else {
            console.log('BolliOs: WebSocket not ready');
        }
    }
    
    // Toggle BolliOs on/off
    function toggleBolliOs() {
        if (bolliOsStatus.active) {
            sendCommand('bolliOsOff');
        } else {
            sendCommand('bolliOs');
        }
    }
    
    // Update status
    function updateStatus(data) {
        if (data && typeof data === 'object') {
            bolliOsStatus.active = data.active || false;
            bolliOsStatus.running = data.running || false;
        }
        updateUI();
    }
    
    // Update UI elements
    function updateUI() {
        const toggle = document.getElementById('bollios-main-toggle');
        const statusDiv = document.getElementById('bollios-status-display');
        const statusText = document.getElementById('bollios-status-text');
        
        if (toggle) {
            toggle.checked = bolliOsStatus.active;
        }
        
        if (statusDiv) {
            statusDiv.className = `bollios-status ${bolliOsStatus.active ? 'active' : 'inactive'}`;
        }
        
        if (statusText) {
            if (bolliOsStatus.active) {
                statusText.textContent = 'Gyro Balance Active';
            } else {
                statusText.textContent = 'Gyro Balance Inactive';
            }
        }
    }
    
    // Create simple BolliOs panel
    function createBolliOsPanel() {
        const container = document.createElement('div');
        container.className = 'bollios-control-panel';
        container.innerHTML = `
            <h3>⚖️ BolliOs Gyro Balance</h3>
            <div class="bollios-status-container">
                <div id="bollios-status-display" class="bollios-status inactive">
                    <span id="bollios-status-text">Gyro Balance Inactive</span>
                </div>
            </div>
            <div class="bollios-switch-container">
                <label class="bollios-switch">
                    <input type="checkbox" id="bollios-main-toggle">
                    <span class="bollios-slider"></span>
                </label>
                <span class="bollios-switch-label">BolliOs Enable</span>
            </div>
        `;
        
        return container;
    }
    
    // Initialize controls
    function initializeBolliOsControls() {
        // Find or create container
        let container = document.getElementById('bollios-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'bollios-container';
            document.body.appendChild(container);
        }
        
        // Add panel
        container.innerHTML = '';
        const panel = createBolliOsPanel();
        container.appendChild(panel);
        
        // Add toggle event listener
        const mainToggle = document.getElementById('bollios-main-toggle');
        if (mainToggle) {
            mainToggle.addEventListener('change', toggleBolliOs);
        }
        
        // Connect WebSocket
        getWebSocketConnection();
        
        console.log('BolliOs controls initialized (simple version)');
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeBolliOsControls);
    } else {
        initializeBolliOsControls();
    }
    
})();