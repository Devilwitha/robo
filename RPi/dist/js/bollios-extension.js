// BolliOs Button Extension
// This script adds a BolliOs button to the face detection controls

(function() {
    'use strict';
    
    let bolliOsActive = false;
    let websocketConnection = null;
    let reconnectInterval = null;
    
    // Initialize WebSocket connection
    function initWebSocket() {
        try {
            websocketConnection = new WebSocket('ws://' + location.hostname + ':8888');
            
            websocketConnection.onopen = function() {
                console.log('BolliOs: WebSocket connected');
                // Send authentication (if needed)
                websocketConnection.send('admin:123456');
            };
            
            websocketConnection.onclose = function() {
                console.log('BolliOs: WebSocket disconnected, attempting to reconnect...');
                setTimeout(initWebSocket, 3000);
            };
            
            websocketConnection.onerror = function(error) {
                console.log('BolliOs: WebSocket error:', error);
            };
            
        } catch (error) {
            console.log('BolliOs: Failed to create WebSocket:', error);
            setTimeout(initWebSocket, 3000);
        }
    }
    
    // Send command via WebSocket
    function sendCommand(command) {
        if (websocketConnection && websocketConnection.readyState === WebSocket.OPEN) {
            websocketConnection.send(command);
            console.log('BolliOs: Sent command:', command);
        } else {
            console.log('BolliOs: WebSocket not ready, command not sent:', command);
            // Try to reconnect
            initWebSocket();
        }
    }
    
    // Create BolliOs button
    function createBolliOsButton() {
        const button = document.createElement('button');
        button.id = 'bollios-btn';
        button.className = 'v-btn v-size--small buttons clickable';
        button.innerHTML = '<span class="v-btn__content"><span class="texts">BolliOs</span></span>';
        
        // Add styles
        Object.assign(button.style, {
            width: '100%',
            height: '36px',
            margin: '8px 0',
            backgroundColor: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            textTransform: 'uppercase',
            transition: 'all 0.3s ease',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
            position: 'relative',
            overflow: 'hidden'
        });
        
        // Add click handler
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (!bolliOsActive) {
                // Activate BolliOs
                sendCommand('bolliOs');
                button.style.backgroundColor = '#4caf50';
                button.innerHTML = '<span class="v-btn__content"><span class="texts">BolliOs ON</span></span>';
                bolliOsActive = true;
                console.log('BolliOs: Activated');
            } else {
                // Deactivate BolliOs
                sendCommand('bolliOsOff');
                button.style.backgroundColor = '#1976d2';
                button.innerHTML = '<span class="v-btn__content"><span class="texts">BolliOs</span></span>';
                bolliOsActive = false;
                console.log('BolliOs: Deactivated');
            }
        });
        
        // Add hover effects
        button.addEventListener('mouseenter', function() {
            if (!bolliOsActive) {
                this.style.backgroundColor = '#1565c0';
            } else {
                this.style.backgroundColor = '#45a049';
            }
        });
        
        button.addEventListener('mouseleave', function() {
            if (!bolliOsActive) {
                this.style.backgroundColor = '#1976d2';
            } else {
                this.style.backgroundColor = '#4caf50';
            }
        });
        
        return button;
    }
    
    // Find actions container and add button
    function addBolliOsButton() {
        // Look for the Actions section
        const allSheets = document.querySelectorAll('.mod-sheet');
        
        for (let sheet of allSheets) {
            const title = sheet.querySelector('.mod-title');
            if (title && title.textContent.trim() === 'Actions') {
                const wrapper = sheet.querySelector('.mod-wrapper');
                if (wrapper) {
                    // Check if button already exists
                    if (document.getElementById('bollios-btn')) {
                        return;
                    }
                    
                    const bolliOsBtn = createBolliOsButton();
                    
                    // Find the button container or create one
                    let buttonContainer = wrapper.querySelector('.button-child');
                    if (!buttonContainer) {
                        // Create a new container if it doesn't exist
                        buttonContainer = document.createElement('div');
                        buttonContainer.className = 'button-child';
                        buttonContainer.style.display = 'flex';
                        buttonContainer.style.flexDirection = 'column';
                        buttonContainer.style.gap = '8px';
                        wrapper.appendChild(buttonContainer);
                    }
                    
                    // Add the button
                    buttonContainer.appendChild(bolliOsBtn);
                    console.log('BolliOs: Button added successfully');
                    return true;
                }
            }
        }
        return false;
    }
    
    // Try to add button with retries
    function tryAddButton(attempts = 0) {
        const maxAttempts = 10;
        
        if (attempts >= maxAttempts) {
            console.log('BolliOs: Failed to add button after', maxAttempts, 'attempts');
            return;
        }
        
        if (addBolliOsButton()) {
            console.log('BolliOs: Successfully added button on attempt', attempts + 1);
        } else {
            console.log('BolliOs: Attempt', attempts + 1, 'failed, retrying...');
            setTimeout(() => tryAddButton(attempts + 1), 1000);
        }
    }
    
    // Initialize everything
    function init() {
        console.log('BolliOs: Extension initializing...');
        initWebSocket();
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => tryAddButton(), 2000);
            });
        } else {
            setTimeout(() => tryAddButton(), 2000);
        }
    }
    
    // Start initialization
    init();
    
})();