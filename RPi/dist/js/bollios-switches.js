// BolliOs Advanced Switch Controls
// Enhanced switch interface similar to Motion Detection

(function() {
    'use strict';
    
    let bolliOsStatus = {
        active: false,
        running: false
    };
    let websocketConnection = null;
    let statusUpdateInterval = null;
    
    // System Control Functions
    function showShutdownPopup() {
        const popup = document.getElementById('shutdownPopup');
        if (popup) {
            popup.classList.add('show');
        }
    }
    
    function hideShutdownPopup() {
        const popup = document.getElementById('shutdownPopup');
        if (popup) {
            popup.classList.remove('show');
        }
    }
    
    function confirmShutdown() {
        hideShutdownPopup();
        showSystemMessage('System wird heruntergefahren...', 'warning');
        
        // Send shutdown command via WebSocket
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                action: 'system_shutdown'
            }));
        }
        
        // Alternative: HTTP request for shutdown
        fetch('/system/shutdown', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'shutdown'
            })
        }).then(response => {
            if (response.ok) {
                showSystemMessage('Shutdown-Befehl gesendet!', 'success');
            } else {
                showSystemMessage('Fehler beim Herunterfahren!', 'error');
            }
        }).catch(error => {
            console.log('Shutdown via HTTP failed, trying alternative...');
            // Fallback via WebSocket
            if (ws) {
                ws.send('SHUTDOWN_SYSTEM');
            }
        });
    }
    
    function stowServos() {
        showSystemMessage('Servos werden verstaut...', 'info');
        
        // Send stow servos command
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                action: 'stow_servos'
            }));
        }
        
        // Alternative: HTTP request for servo stowing
        fetch('/servos/stow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'stow',
                positions: {
                    servo1: 90,  // Neutral position
                    servo2: 90,
                    servo3: 0,   // Folded position
                    servo4: 0
                }
            })
        }).then(response => {
            if (response.ok) {
                showSystemMessage('Servos erfolgreich verstaut!', 'success');
            } else {
                showSystemMessage('Fehler beim Verstauen der Servos!', 'error');
            }
        }).catch(error => {
            console.log('Stow servos via HTTP failed, trying WebSocket...');
            // Fallback command via WebSocket
            if (ws) {
                ws.send('STOW_SERVOS');
            }
        });
    }
    
    function showSystemMessage(message, type = 'info') {
        const messageEl = document.getElementById('systemStatusMessage');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = `system-status-message show ${type}`;
            
            setTimeout(() => {
                messageEl.classList.remove('show');
            }, 3000);
        }
    }
    
    // WebSocket Management with Mock Mode
    function getWebSocketConnection() {
        // Try to use existing WebSocket connections
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
                    console.log('BolliOs Switches: WebSocket connected');
                    showSystemMessage('WebSocket-Verbindung hergestellt', 'success');
                    // Send authentication
                    websocketConnection.send('admin:123456');
                    // Request initial status
                    setTimeout(() => requestStatus(), 1000);
                };
                
                websocketConnection.onmessage = function(event) {
                    console.log('BolliOs: WebSocket message received:', event.data);
                    try {
                        const response = JSON.parse(event.data);
                        if (response.title === 'bolliOsStatus') {
                            updateStatus(response.data);
                        } else if (response.title === 'bolliOs') {
                            // Handle activation/deactivation responses
                            bolliOsStatus.active = response.data === 'activated';
                            updateUI();
                            showSystemMessage(`BolliOs ${response.data}`, response.data === 'activated' ? 'success' : 'info');
                        } else if (response.title === 'system_shutdown') {
                            showSystemMessage('System wird heruntergefahren...', 'warning');
                        } else if (response.title === 'stow_servos') {
                            showSystemMessage('Servos verstaut', 'success');
                        }
                    } catch (e) {
                        // Handle non-JSON messages
                        console.log('BolliOs: Non-JSON message:', event.data);
                    }
                };
                
                websocketConnection.onclose = function() {
                    console.log('BolliOs Switches: WebSocket disconnected');
                    showSystemMessage('WebSocket-Verbindung getrennt', 'error');
                    websocketConnection = null;
                    // Try to reconnect
                    setTimeout(() => getWebSocketConnection(), 3000);
                };
                
                websocketConnection.onerror = function(error) {
                    console.log('BolliOs Switches: WebSocket error:', error);
                    showSystemMessage('WebSocket-Fehler - verwende Mock-Modus', 'warning');
                    // Enable mock mode if WebSocket fails
                    enableMockMode();
                };
                
            } catch (error) {
                console.log('BolliOs Switches: Failed to create WebSocket:', error);
            }
        }
        
        return websocketConnection;
    }
    
    // Send command via WebSocket with Mock support
    function sendCommand(command) {
        if (mockMode) {
            mockWebSocketSend(command);
            return;
        }
        
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(command);
            console.log('BolliOs Switches: Sent command:', command);
            // Request status update after command
            setTimeout(() => requestStatus(), 500);
        } else {
            console.log('BolliOs Switches: WebSocket not ready, trying HTTP fallback:', command);
            // Try HTTP fallback first, then enable mock mode if that fails
            fetch(`/command/${command}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }).then(response => {
                if (response.ok) {
                    showSystemMessage(`Befehl ausgeführt: ${command}`, 'success');
                } else {
                    throw new Error('HTTP request failed');
                }
            }).catch(err => {
                console.error('HTTP fallback failed:', err);
                showSystemMessage('Verbindung fehlgeschlagen - Mock-Modus aktiviert', 'warning');
                enableMockMode();
                mockWebSocketSend(command);
            });
        }
    }
    
    // Request status from server
    function requestStatus() {
        sendCommand('bolliOsStatus');
    }
    
    // Update status from server response
    function updateStatus(status) {
        bolliOsStatus = status;
        updateUI();
        console.log('BolliOs Switches: Status updated:', status);
    }
    
    // Update UI based on current status
    function updateUI() {
        const toggle = document.getElementById('bollios-main-toggle');
        const statusDiv = document.getElementById('bollios-status-display');
        const statusIcon = document.getElementById('bollios-status-icon');
        const statusText = document.getElementById('bollios-status-text');
        
        if (toggle) {
            toggle.checked = bolliOsStatus.active;
        }
        
        if (statusDiv) {
            statusDiv.className = `bollios-status ${bolliOsStatus.active ? 'active' : 'inactive'}`;
        }
        
        if (statusIcon) {
            statusIcon.className = `bollios-status-icon ${bolliOsStatus.active ? 'active' : 'inactive'}`;
        }
        
        if (statusText) {
            if (bolliOsStatus.active && bolliOsStatus.running) {
                statusText.textContent = 'Gyro Balance Active & Running';
            } else if (bolliOsStatus.active) {
                statusText.textContent = 'Gyro Balance Active';
            } else {
                statusText.textContent = 'Gyro Balance Inactive';
            }
        }
    }
    
    // Mock Mode Functions
    let mockMode = false;
    
    function enableMockMode() {
        mockMode = true;
        console.log('BolliOs: Mock mode enabled - features will simulate responses');
        showSystemMessage('Mock-Modus aktiviert - Features werden simuliert', 'info');
    }
    
    function mockWebSocketSend(command) {
        console.log('BolliOs Mock: Simulating command:', command);
        
        // Simulate different responses based on command
        setTimeout(() => {
            if (command === 'bolliOs') {
                bolliOsStatus.active = true;
                updateUI();
                showSystemMessage('BolliOs aktiviert (Simulation)', 'success');
            } else if (command === 'bolliOsOff') {
                bolliOsStatus.active = false;
                updateUI();
                showSystemMessage('BolliOs deaktiviert (Simulation)', 'info');
            } else if (command === 'system_shutdown') {
                showSystemMessage('System-Shutdown simuliert', 'warning');
            } else if (command === 'stow_servos') {
                showSystemMessage('Servo-Stowing simuliert', 'success');
            }
        }, 500); // Simulate network delay
    }
    
    // System Message Display Function
    function showSystemMessage(message, type = 'info') {
        // Create or get message container
        let messageContainer = document.getElementById('system-message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'system-message-container';
            messageContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 300px;
            `;
            document.body.appendChild(messageContainer);
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.style.cssText = `
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            opacity: 0;
            transition: opacity 0.3s ease;
            background-color: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : '#2196F3'};
        `;
        messageElement.textContent = message;
        
        messageContainer.appendChild(messageElement);
        
        // Fade in
        setTimeout(() => {
            messageElement.style.opacity = '1';
        }, 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 300);
        }, 3000);
    }
    
    // Create BolliOs Control Panel
    function createBolliOsPanel() {
        // Create container for both system controls and BolliOs
        const container = document.createElement('div');
        container.id = 'system-bollios-container';
        
        // System Control Panel (added above BolliOs)
        const systemPanel = document.createElement('div');
        systemPanel.className = 'system-control-panel';
        systemPanel.innerHTML = `
            <h3>🔧 System Control</h3>
            <div class="system-control-buttons">
                <button id="shutdown-btn" class="system-btn shutdown-btn">
                    🔌 Raspberry Pi Herunterfahren
                </button>
                <button id="stow-servos-btn" class="system-btn stow-servos-btn">
                    📦 Servos Verstauen
                </button>
            </div>
            <div id="systemStatusMessage" class="system-status-message"></div>
        `;
        
        // BolliOs Panel
        const panel = document.createElement('div');
        panel.className = 'bollios-control-panel';
        panel.innerHTML = `
            <h3>🎯 BolliOs Gyro Balance</h3>
            
            <!-- Main Toggle Switch -->
            <div class="bollios-switch-container">
                <span class="bollios-switch-label">Gyro Balance</span>
                <label class="bollios-toggle">
                    <input type="checkbox" id="bollios-main-toggle">
                    <span class="bollios-slider"></span>
                </label>
            </div>
            
            <!-- Status Display -->
            <div id="bollios-status-display" class="bollios-status inactive">
                <div id="bollios-status-icon" class="bollios-status-icon inactive"></div>
                <span id="bollios-status-text">Gyro Balance Inactive</span>
            </div>
            
            <!-- Action Buttons -->
            <div class="bollios-actions">
                <button id="bollios-btn-start" class="bollios-btn-action bollios-btn-start">Start</button>
                <button id="bollios-btn-toggle" class="bollios-btn-action bollios-btn-toggle">Toggle</button>
                <button id="bollios-btn-stop" class="bollios-btn-action bollios-btn-stop">Stop</button>
            </div>
            
            <!-- Information Panel -->
            <div class="bollios-info">
                <h4>ℹ️ Gyro Balance Features:</h4>
                <ul>
                    <li>Automatic robot balance correction</li>
                    <li>LED status indicators (Green = Active)</li>
                    <li>Audio feedback on activation</li>
                    <li>Integration with Motion Tracking</li>
                    <li>Real-time balance monitoring</li>
                </ul>
            </div>
        `;
        
        // Shutdown Popup
        const shutdownPopup = document.createElement('div');
        shutdownPopup.id = 'shutdownPopup';
        shutdownPopup.className = 'shutdown-popup';
        shutdownPopup.innerHTML = `
            <div class="shutdown-popup-content">
                <h4>⚠️ System Herunterfahren</h4>
                <p>Sind Sie sicher, dass Sie den Raspberry Pi herunterfahren möchten?</p>
                <p><strong>Warnung:</strong> Alle aktiven Verbindungen werden getrennt!</p>
                <div class="shutdown-popup-buttons">
                    <button class="popup-btn popup-btn-confirm" id="confirmShutdownBtn">
                        Ja, Herunterfahren
                    </button>
                    <button class="popup-btn popup-btn-cancel" id="cancelShutdownBtn">
                        Abbrechen
                    </button>
                </div>
            </div>
        `;
        
        // Assemble the components
        container.appendChild(systemPanel);
        container.appendChild(panel);
        document.body.appendChild(shutdownPopup);
        
        // Make functions globally accessible
        window.showShutdownPopup = showShutdownPopup;
        window.hideShutdownPopup = hideShutdownPopup;
        window.confirmShutdown = confirmShutdown;
        window.stowServos = stowServos;
        
        // Add event listeners for system controls
        setTimeout(() => {
            const shutdownBtn = document.getElementById('shutdown-btn');
            const stowServosBtn = document.getElementById('stow-servos-btn');
            const confirmBtn = document.getElementById('confirmShutdownBtn');
            const cancelBtn = document.getElementById('cancelShutdownBtn');
            
            if (shutdownBtn) {
                shutdownBtn.addEventListener('click', showShutdownPopup);
            }
            
            if (stowServosBtn) {
                stowServosBtn.addEventListener('click', stowServos);
            }
            
            if (confirmBtn) {
                confirmBtn.addEventListener('click', confirmShutdown);
            }
            
            if (cancelBtn) {
                cancelBtn.addEventListener('click', hideShutdownPopup);
            }
        }, 100);
        
        return container;
        
        // Add event listeners
        setTimeout(() => {
            const mainToggle = document.getElementById('bollios-main-toggle');
            const startBtn = document.getElementById('bollios-btn-start');
            const toggleBtn = document.getElementById('bollios-btn-toggle');
            const stopBtn = document.getElementById('bollios-btn-stop');
            
            if (mainToggle) {
                mainToggle.addEventListener('change', function() {
                    if (this.checked) {
                        sendCommand('bolliOs');
                    } else {
                        sendCommand('bolliOsOff');
                    }
                });
            }
            
            if (startBtn) {
                startBtn.addEventListener('click', function() {
                    sendCommand('bolliOs');
                });
            }
            
            if (toggleBtn) {
                toggleBtn.addEventListener('click', function() {
                    sendCommand('bolliOsToggle');
                });
            }
            
            if (stopBtn) {
                stopBtn.addEventListener('click', function() {
                    sendCommand('bolliOsOff');
                });
            }
        }, 100);
        
        return panel;
    }
    
    // Find location to add panel
    function addBolliOsPanel() {
        // Look for existing Actions section or Motion Tracking panel
        const allSheets = document.querySelectorAll('.mod-sheet');
        
        for (let sheet of allSheets) {
            const title = sheet.querySelector('.mod-title');
            if (title && title.textContent.trim() === 'Actions') {
                const wrapper = sheet.querySelector('.mod-wrapper');
                if (wrapper) {
                    // Check if panel already exists
                    if (document.querySelector('.bollios-control-panel')) {
                        console.log('BolliOs Switches: Panel already exists');
                        return true;
                    }
                    
                    const bolliOsPanel = createBolliOsPanel();
                    wrapper.appendChild(bolliOsPanel);
                    console.log('BolliOs Switches: Panel added successfully');
                    return true;
                }
            }
        }
        
        // Alternative: Add to main container if Actions section not found
        const mainContainer = document.querySelector('.v-application .v-main .container');
        if (mainContainer && !document.querySelector('.bollios-control-panel')) {
            const bolliOsPanel = createBolliOsPanel();
            mainContainer.appendChild(bolliOsPanel);
            console.log('BolliOs Switches: Panel added to main container');
            return true;
        }
        
        return false;
    }
    
    // Start status polling
    function startStatusPolling() {
        // Poll status every 5 seconds
        statusUpdateInterval = setInterval(() => {
            requestStatus();
        }, 5000);
    }
    
    // Stop status polling
    function stopStatusPolling() {
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
            statusUpdateInterval = null;
        }
    }
    
    // Try to add panel with retries
    function tryAddPanel(attempts = 0) {
        const maxAttempts = 10;
        
        if (attempts >= maxAttempts) {
            console.log('BolliOs Switches: Failed to add panel after', maxAttempts, 'attempts');
            return;
        }
        
        if (addBolliOsPanel()) {
            console.log('BolliOs Switches: Successfully added panel on attempt', attempts + 1);
            // Start status polling after successful panel creation
            startStatusPolling();
            // Request initial status
            setTimeout(() => requestStatus(), 2000);
        } else {
            console.log('BolliOs Switches: Attempt', attempts + 1, 'failed, retrying...');
            setTimeout(() => tryAddPanel(attempts + 1), 1000);
        }
    }
    
    // Initialize everything
    function init() {
        console.log('BolliOs Switches: Initializing advanced controls...');
        
        // Initialize WebSocket
        getWebSocketConnection();
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => tryAddPanel(), 2000);
            });
        } else {
            setTimeout(() => tryAddPanel(), 2000);
        }
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            stopStatusPolling();
            if (websocketConnection) {
                websocketConnection.close();
            }
        });
    }
    
    // Export for debugging
    window.BolliOsSwitches = {
        getStatus: () => bolliOsStatus,
        requestStatus: requestStatus,
        sendCommand: sendCommand,
        updateUI: updateUI
    };
    
    // Start initialization
    init();
    
})();