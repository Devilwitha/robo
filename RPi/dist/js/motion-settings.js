// Motion Settings Extension - Adds settings controls to Motion Tracking
// This extends the motion tracking switch with configurable parameters

(function() {
    'use strict';
    
    let settingsVisible = false;
    let currentPreset = 'balanced';
    
    console.log('Motion Settings Extension loading...');

    function addSettingsToMotionTracking() {
        const motionContainer = document.getElementById('motion-tracking-container');
        if (!motionContainer) {
            console.log('Motion Settings: Motion tracking container not found, retrying...');
            setTimeout(addSettingsToMotionTracking, 1000);
            return;
        }
        
        // Check if settings already added
        if (document.getElementById('motion-settings-panel')) {
            return;
        }
        
        // Create settings toggle button
        const settingsToggle = document.createElement('button');
        settingsToggle.textContent = '⚙️ Settings';
        settingsToggle.style.cssText = `
            width: 100%;
            margin-top: 8px;
            padding: 6px;
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid #2196F3;
            border-radius: 15px;
            font-size: 11px;
            color: #1565C0;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        settingsToggle.addEventListener('click', toggleSettings);
        settingsToggle.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(33, 150, 243, 0.1)';
        });
        settingsToggle.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(255, 255, 255, 0.8)';
        });
        
        // Create settings panel
        const settingsPanel = document.createElement('div');
        settingsPanel.id = 'motion-settings-panel';
        settingsPanel.style.cssText = `
            display: none;
            margin-top: 10px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #BBDEFB;
            border-radius: 8px;
            font-size: 11px;
        `;
        
        // Preset selector
        const presetSection = document.createElement('div');
        presetSection.innerHTML = `
            <div style="font-weight: 600; color: #1565C0; margin-bottom: 8px;">Quick Presets:</div>
            <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px;">
                <button class="preset-btn" data-preset="conservative">🐌 Conservative</button>
                <button class="preset-btn" data-preset="balanced">⚖️ Balanced</button>
                <button class="preset-btn" data-preset="aggressive">🏃 Aggressive</button>
                <button class="preset-btn" data-preset="indoor">🏠 Indoor</button>
                <button class="preset-btn" data-preset="outdoor">🌳 Outdoor</button>
            </div>
        `;
        
        // Individual settings
        const settingsControls = document.createElement('div');
        settingsControls.innerHTML = `
            <div style="font-weight: 600; color: #1565C0; margin-bottom: 8px;">Fine Tuning:</div>
            <div style="display: grid; grid-template-columns: 1fr 60px; gap: 4px; font-size: 10px;">
                <label>Movement Time:</label>
                <input type="range" id="movement-duration" min="1" max="4" step="0.1" value="2">
                <label>Pause Time:</label>
                <input type="range" id="pause-duration" min="0.5" max="2" step="0.1" value="1">
                <label>Sensitivity:</label>
                <input type="range" id="sensitivity" min="10" max="40" step="1" value="20">
                <label>Min Area:</label>
                <input type="range" id="min-area" min="500" max="3000" step="100" value="1500">
            </div>
            <div style="margin-top: 8px; display: flex; justify-content: space-between;">
                <button id="apply-settings" style="padding: 4px 8px; background: #4CAF50; color: white; border: none; border-radius: 4px; font-size: 10px;">Apply</button>
                <button id="reset-settings" style="padding: 4px 8px; background: #FF9800; color: white; border: none; border-radius: 4px; font-size: 10px;">Reset</button>
            </div>
        `;
        
        settingsPanel.appendChild(presetSection);
        settingsPanel.appendChild(settingsControls);
        
        // Add CSS for preset buttons
        const style = document.createElement('style');
        style.textContent = `
            .preset-btn {
                padding: 4px 6px;
                font-size: 9px;
                border: 1px solid #BBDEFB;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .preset-btn:hover {
                background: #E3F2FD;
            }
            .preset-btn.active {
                background: #2196F3;
                color: white;
            }
        `;
        document.head.appendChild(style);
        
        // Add event listeners
        setupSettingsEventListeners(settingsPanel);
        
        // Add to motion container
        motionContainer.appendChild(settingsToggle);
        motionContainer.appendChild(settingsPanel);
        
        // Set initial active preset
        updateActivePreset('balanced');
        
        console.log('Motion Settings: Settings panel added successfully');
    }
    
    function setupSettingsEventListeners(panel) {
        // Preset buttons
        panel.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const preset = this.dataset.preset;
                applyPreset(preset);
                updateActivePreset(preset);
            });
        });
        
        // Apply settings button
        panel.querySelector('#apply-settings').addEventListener('click', function() {
            const settings = {
                movement_duration: parseFloat(panel.querySelector('#movement-duration').value),
                pause_duration: parseFloat(panel.querySelector('#pause-duration').value),
                tracking_sensitivity: parseInt(panel.querySelector('#sensitivity').value),
                min_area: parseInt(panel.querySelector('#min-area').value)
            };
            
            sendSettingsCommand('updateSettings', settings);
            console.log('Motion Settings: Applied custom settings:', settings);
        });
        
        // Reset settings button
        panel.querySelector('#reset-settings').addEventListener('click', function() {
            sendSettingsCommand('resetSettings', {});
            applyPreset('balanced');
            updateActivePreset('balanced');
            console.log('Motion Settings: Reset to defaults');
        });
    }
    
    function toggleSettings() {
        settingsVisible = !settingsVisible;
        const panel = document.getElementById('motion-settings-panel');
        if (panel) {
            panel.style.display = settingsVisible ? 'block' : 'none';
            console.log('Motion Settings: Panel', settingsVisible ? 'opened' : 'closed');
        }
    }
    
    function applyPreset(presetName) {
        const presets = {
            conservative: { movement_duration: 1.5, pause_duration: 1.5, tracking_sensitivity: 25, min_area: 1500 },
            balanced: { movement_duration: 2.0, pause_duration: 1.0, tracking_sensitivity: 20, min_area: 1500 },
            aggressive: { movement_duration: 2.5, pause_duration: 0.8, tracking_sensitivity: 15, min_area: 1200 },
            indoor: { movement_duration: 1.8, pause_duration: 1.2, tracking_sensitivity: 22, min_area: 1200 },
            outdoor: { movement_duration: 2.2, pause_duration: 0.9, tracking_sensitivity: 18, min_area: 2000 }
        };
        
        const preset = presets[presetName];
        if (preset) {
            // Update UI controls
            const panel = document.getElementById('motion-settings-panel');
            if (panel) {
                panel.querySelector('#movement-duration').value = preset.movement_duration;
                panel.querySelector('#pause-duration').value = preset.pause_duration;
                panel.querySelector('#sensitivity').value = preset.tracking_sensitivity;
                panel.querySelector('#min-area').value = preset.min_area;
            }
            
            // Send to backend
            sendSettingsCommand('applyPreset', { preset: presetName });
            currentPreset = presetName;
            console.log('Motion Settings: Applied preset:', presetName, preset);
        }
    }
    
    function updateActivePreset(presetName) {
        const panel = document.getElementById('motion-settings-panel');
        if (panel) {
            panel.querySelectorAll('.preset-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.preset === presetName) {
                    btn.classList.add('active');
                }
            });
        }
    }
    
    function sendSettingsCommand(action, data) {
        const command = {
            action: 'motionSettings',
            type: action,
            data: data
        };
        
        // Try to use existing WebSocket connections
        const wsConnections = [
            window.websocket,
            window.ws,
            window.socket,
            window.webSocket
        ];
        
        let sent = false;
        for (let ws of wsConnections) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                try {
                    ws.send(JSON.stringify(command));
                    console.log('Motion Settings: Sent command:', command);
                    sent = true;
                    break;
                } catch (error) {
                    console.warn('Motion Settings: WebSocket send failed:', error);
                }
            }
        }
        
        if (!sent) {
            console.warn('Motion Settings: No active WebSocket connection found');
        }
    }
    
    // Initialize when motion tracking is available
    function init() {
        // Wait for motion tracking to be integrated
        const checkInterval = setInterval(() => {
            if (document.getElementById('motion-tracking-container')) {
                clearInterval(checkInterval);
                setTimeout(addSettingsToMotionTracking, 500);
            }
        }, 1000);
        
        // Stop checking after 30 seconds
        setTimeout(() => clearInterval(checkInterval), 30000);
    }
    
    // Expose global functions for debugging
    window.motionSettingsDebug = {
        addSettings: addSettingsToMotionTracking,
        applyPreset: applyPreset,
        toggleSettings: toggleSettings,
        getCurrentPreset: () => currentPreset
    };
    
    // Start initialization
    init();
    
    console.log('Motion Settings Extension initialized');
    
})();