// Motion Tracking Extension - Based on BolliOs pattern
// This script adds a Motion Tracking switch to the face detection controls

(function() {
    'use strict';
    
    let motionTrackingActive = false;
    let websocketConnection = null;
    
    // Use existing WebSocket or create new one
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
                    console.log('Motion Tracking: WebSocket connected');
                    // Send authentication (if needed)
                    websocketConnection.send('admin:123456');
                };
                
                websocketConnection.onclose = function() {
                    console.log('Motion Tracking: WebSocket disconnected');
                    websocketConnection = null;
                };
                
                websocketConnection.onerror = function(error) {
                    console.log('Motion Tracking: WebSocket error:', error);
                };
                
            } catch (error) {
                console.log('Motion Tracking: Failed to create WebSocket:', error);
            }
        }
        
        return websocketConnection;
    }
    
    // Send command via WebSocket
    function sendCommand(command) {
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(command);
            console.log('Motion Tracking: Sent command:', command);
            return true;
        } else {
            console.log('Motion Tracking: WebSocket not ready, command not sent:', command);
            return false;
        }
    }
    
    // Create Motion Tracking switch container
    function createMotionTrackingSwitch() {
        const container = document.createElement('div');
        container.id = 'motion-tracking-container';
        container.className = 'motion-tracking-extension';
        
        // Container styles
        Object.assign(container.style, {
            width: '100%',
            margin: '12px 0',
            padding: '16px',
            backgroundColor: '#E3F2FD',
            border: '2px solid #2196F3',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(33, 150, 243, 0.3)',
            transition: 'all 0.3s ease'
        });
        
        // Title
        const title = document.createElement('div');
        title.textContent = '🎯 Motion Tracking';
        Object.assign(title.style, {
            fontSize: '14px',
            fontWeight: '600',
            color: '#1565C0',
            marginBottom: '8px',
            textAlign: 'center'
        });
        
        // Description
        const description = document.createElement('div');
        description.textContent = 'Silent motion detection - follows movement without beeping';
        Object.assign(description.style, {
            fontSize: '11px',
            color: '#424242',
            marginBottom: '12px',
            textAlign: 'center',
            fontStyle: 'italic'
        });
        
        // Switch row
        const switchRow = document.createElement('div');
        Object.assign(switchRow.style, {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '10px'
        });
        
        // Label
        const label = document.createElement('label');
        label.textContent = 'Follow Motion';
        Object.assign(label.style, {
            fontSize: '13px',
            color: '#1565C0',
            fontWeight: '500',
            cursor: 'pointer'
        });
        
        // Toggle switch
        const toggleContainer = document.createElement('div');
        Object.assign(toggleContainer.style, {
            position: 'relative',
            width: '60px',
            height: '28px',
            cursor: 'pointer'
        });
        
        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.id = 'motion-tracking-toggle';
        Object.assign(toggleInput.style, {
            opacity: '0',
            width: '0',
            height: '0'
        });
        
        const toggleSlider = document.createElement('span');
        Object.assign(toggleSlider.style, {
            position: 'absolute',
            cursor: 'pointer',
            top: '0',
            left: '0',
            right: '0',
            bottom: '0',
            backgroundColor: '#ccc',
            transition: '0.4s',
            borderRadius: '28px',
            boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.3)'
        });
        
        const toggleKnob = document.createElement('span');
        Object.assign(toggleKnob.style, {
            position: 'absolute',
            content: '""',
            height: '22px',
            width: '22px',
            left: '3px',
            bottom: '3px',
            backgroundColor: 'white',
            transition: '0.4s',
            borderRadius: '50%',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
        });
        
        toggleSlider.appendChild(toggleKnob);
        
        // Status indicator
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'motion-tracking-status';
        statusIndicator.textContent = '🔘 Motion Tracking OFF';
        Object.assign(statusIndicator.style, {
            padding: '6px 12px',
            backgroundColor: '#f5f5f5',
            border: '1px solid #ddd',
            borderRadius: '15px',
            fontSize: '12px',
            textAlign: 'center',
            color: '#666',
            transition: 'all 0.3s ease'
        });
        
        // Event handlers
        function toggleMotionTracking() {
            motionTrackingActive = toggleInput.checked;
            
            if (motionTrackingActive) {
                // Activate motion tracking
                if (sendCommand('motionTracking')) {
                    statusIndicator.textContent = '🔵 Motion Tracking ACTIVE - Blue LEDs ON';
                    statusIndicator.style.backgroundColor = '#E3F2FD';
                    statusIndicator.style.color = '#1565C0';
                    statusIndicator.style.borderColor = '#2196F3';
                    
                    toggleSlider.style.backgroundColor = '#2196F3';
                    toggleKnob.style.transform = 'translateX(32px)';
                    
                    console.log('Motion Tracking: ACTIVATED');
                } else {
                    // Revert if command failed
                    toggleInput.checked = false;
                    motionTrackingActive = false;
                }
            } else {
                // Deactivate motion tracking
                if (sendCommand('motionTrackingOff')) {
                    statusIndicator.textContent = '🔘 Motion Tracking OFF';
                    statusIndicator.style.backgroundColor = '#f5f5f5';
                    statusIndicator.style.color = '#666';
                    statusIndicator.style.borderColor = '#ddd';
                    
                    toggleSlider.style.backgroundColor = '#ccc';
                    toggleKnob.style.transform = 'translateX(0px)';
                    
                    console.log('Motion Tracking: DEACTIVATED');
                } else {
                    // Revert if command failed
                    toggleInput.checked = true;
                    motionTrackingActive = true;
                }
            }
        }
        
        toggleInput.addEventListener('change', toggleMotionTracking);
        label.addEventListener('click', function() {
            toggleInput.checked = !toggleInput.checked;
            toggleMotionTracking();
        });
        
        // Assemble elements
        toggleContainer.appendChild(toggleInput);
        toggleContainer.appendChild(toggleSlider);
        
        switchRow.appendChild(label);
        switchRow.appendChild(toggleContainer);
        
        container.appendChild(title);
        container.appendChild(description);
        container.appendChild(switchRow);
        container.appendChild(statusIndicator);
        
        return container;
    }
    
    // Find actions container and add motion tracking switch
    function addMotionTrackingSwitch() {
        // Look for the Actions section (same as BolliOs)
        const allSheets = document.querySelectorAll('.mod-sheet');
        
        for (let sheet of allSheets) {
            const title = sheet.querySelector('.mod-title');
            if (title && title.textContent.trim() === 'Actions') {
                const wrapper = sheet.querySelector('.mod-wrapper');
                if (wrapper) {
                    // Check if switch already exists
                    if (document.getElementById('motion-tracking-container')) {
                        return;
                    }
                    
                    const motionTrackingSwitch = createMotionTrackingSwitch();
                    
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
                    
                    // Add the switch (after BolliOs button if it exists)
                    const bolliOsBtn = document.getElementById('bollios-btn');
                    if (bolliOsBtn) {
                        bolliOsBtn.parentNode.insertBefore(motionTrackingSwitch, bolliOsBtn.nextSibling);
                    } else {
                        buttonContainer.appendChild(motionTrackingSwitch);
                    }
                    
                    console.log('Motion Tracking: Switch added successfully');
                    return true;
                }
            }
        }
        return false;
    }
    
    // Try to add switch with retries
    function tryAddSwitch(attempts = 0) {
        const maxAttempts = 15;
        
        if (attempts >= maxAttempts) {
            console.log('Motion Tracking: Failed to add switch after', maxAttempts, 'attempts');
            return;
        }
        
        if (addMotionTrackingSwitch()) {
            console.log('Motion Tracking: Successfully added switch on attempt', attempts + 1);
        } else {
            console.log('Motion Tracking: Attempt', attempts + 1, 'failed, retrying...');
            setTimeout(() => tryAddSwitch(attempts + 1), 1000);
        }
    }
    
    // Initialize everything
    function init() {
        console.log('Motion Tracking: Extension initializing...');
        
        // Wait for page to load and BolliOs to be added first
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => tryAddSwitch(), 3000); // Wait a bit longer for BolliOs
            });
        } else {
            setTimeout(() => tryAddSwitch(), 3000);
        }
    }
    
    // Expose global debug functions
    window.motionTrackingDebug = {
        addSwitch: addMotionTrackingSwitch,
        sendCommand: sendCommand,
        isActive: () => motionTrackingActive,
        retryIntegration: () => tryAddSwitch(0)
    };
    
    // Start initialization
    init();
    
    console.log('Motion Tracking: Extension loaded - Use motionTrackingDebug for manual control');
    
})();