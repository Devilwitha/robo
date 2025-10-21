// motion-tracking.js - Vue.js compatible Motion Tracking Switch
// Integrates with existing WAVEGO web interface following BolliOs pattern

(function() {
    'use strict';
    
    // Motion tracking state
    let motionTrackingActive = false;
    
    // WebSocket management (uses existing connection)
    function sendMotionCommand(command) {
        if (typeof wsB !== 'undefined' && wsB.readyState === WebSocket.OPEN) {
            wsB.send(command);
            console.log(`Motion Tracking: Sent command ${command}`);
        } else {
            console.warn('Motion Tracking: WebSocket not available');
        }
    }
    
    // Create motion tracking switch UI
    function createMotionTrackingSwitch() {
        // Find the BolliOs button container
        const bolliosContainer = document.querySelector('#bolliOs');
        if (!bolliosContainer) {
            console.warn('Motion Tracking: BolliOs container not found, retrying...');
            return false;
        }
        
        // Check if motion tracking switch already exists
        if (document.querySelector('#motionTrackingSwitch')) {
            return true; // Already exists
        }
        
        // Create switch container
        const switchContainer = document.createElement('div');
        switchContainer.style.cssText = `
            margin-top: 10px;
            padding: 8px;
            background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
            border-radius: 8px;
            border: 1px solid #444;
        `;
        
        // Create switch label
        const switchLabel = document.createElement('div');
        switchLabel.style.cssText = `
            color: #fff;
            font-size: 12px;
            margin-bottom: 5px;
            text-align: center;
        `;
        switchLabel.innerHTML = '🎯 Follow Motion';
        
        // Create toggle switch
        const switchElement = document.createElement('div');
        switchElement.id = 'motionTrackingSwitch';
        switchElement.style.cssText = `
            width: 50px;
            height: 25px;
            background: #666;
            border-radius: 25px;
            position: relative;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 auto;
        `;
        
        // Create switch toggle
        const switchToggle = document.createElement('div');
        switchToggle.style.cssText = `
            width: 21px;
            height: 21px;
            background: white;
            border-radius: 50%;
            position: absolute;
            top: 2px;
            left: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        `;
        
        switchElement.appendChild(switchToggle);
        
        // Add click handler
        switchElement.addEventListener('click', function() {
            motionTrackingActive = !motionTrackingActive;
            updateSwitchUI();
            
            if (motionTrackingActive) {
                sendMotionCommand('motionTracking');
            } else {
                sendMotionCommand('motionTrackingOff');
            }
        });
        
        // Update switch UI function
        function updateSwitchUI() {
            if (motionTrackingActive) {
                switchElement.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
                switchToggle.style.left = '27px';
                switchToggle.style.background = '#fff';
                switchLabel.innerHTML = '🎯 Follow Motion <span style="color: #4CAF50;">ON</span>';
            } else {
                switchElement.style.background = '#666';
                switchToggle.style.left = '2px';
                switchToggle.style.background = '#fff';
                switchLabel.innerHTML = '🎯 Follow Motion';
            }
        }
        
        // Assemble the switch
        switchContainer.appendChild(switchLabel);
        switchContainer.appendChild(switchElement);
        
        // Insert after BolliOs button
        bolliosContainer.parentNode.insertBefore(switchContainer, bolliosContainer.nextSibling);
        
        console.log('Motion Tracking: Switch created successfully');
        return true;
    }
    
    // Initialize when DOM is ready
    function initializeMotionTracking() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(createMotionTrackingSwitch, 1000);
            });
        } else {
            // Try multiple times in case Vue.js is still loading
            let attempts = 0;
            const maxAttempts = 10;
            
            function tryCreate() {
                attempts++;
                if (createMotionTrackingSwitch()) {
                    console.log('Motion Tracking: Initialized successfully');
                } else if (attempts < maxAttempts) {
                    setTimeout(tryCreate, 500);
                } else {
                    console.warn('Motion Tracking: Failed to initialize after multiple attempts');
                }
            }
            
            tryCreate();
        }
    }
    
    // Handle WebSocket messages for motion tracking status
    if (typeof window !== 'undefined') {
        window.addEventListener('motion-tracking-status', function(event) {
            const data = event.detail;
            if (data.title === 'motionTracking') {
                motionTrackingActive = (data.data === 'activated');
                if (document.querySelector('#motionTrackingSwitch')) {
                    updateSwitchUI();
                }
            }
        });
    }
    
    // Start initialization
    initializeMotionTracking();
    
    console.log('Motion Tracking Script: Loaded');
})();