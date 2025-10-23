// motion-settings.js - Motion Tracking Settings Panel
// Provides preset controls and fine-tuning for motion tracking parameters

(function() {
    'use strict';
    
    // Settings state
    let settingsVisible = false;
    let currentSettings = {
        movement_duration: 2.0,
        pause_duration: 1.0,
        motion_threshold: 1000,
        min_contour_area: 1500
    };
    
    // WebSocket management for settings
    function sendSettingsCommand(command) {
        if (typeof wsB !== 'undefined' && wsB.readyState === WebSocket.OPEN) {
            wsB.send(JSON.stringify(command));
            console.log('Motion Settings: Sent command', command);
        } else {
            console.warn('Motion Settings: WebSocket not available');
        }
    }
    
    // Apply preset configuration
    function applyPreset(presetName) {
        const command = {
            action: 'motionSettings',
            type: 'applyPreset',
            data: { preset: presetName }
        };
        sendSettingsCommand(command);
        
        // Update UI feedback
        const presetButtons = document.querySelectorAll('.motion-preset-btn');
        presetButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.preset === presetName) {
                btn.classList.add('active');
            }
        });
        
        console.log(`Motion Settings: Applied preset ${presetName}`);
    }
    
    // Update individual setting
    function updateSetting(settingName, value) {
        currentSettings[settingName] = value;
        
        const command = {
            action: 'motionSettings',
            type: 'updateSettings',
            data: { [settingName]: value }
        };
        sendSettingsCommand(command);
        
        console.log(`Motion Settings: Updated ${settingName} to ${value}`);
    }
    
    // Reset to defaults
    function resetSettings() {
        const command = {
            action: 'motionSettings',
            type: 'resetSettings',
            data: {}
        };
        sendSettingsCommand(command);
        
        // Reset UI
        document.querySelector('#movementDuration').value = 2.0;
        document.querySelector('#pauseDuration').value = 1.0;
        document.querySelector('#motionThreshold').value = 1000;
        document.querySelector('#minContourArea').value = 1500;
        
        console.log('Motion Settings: Reset to defaults');
    }
    
    // Create settings panel
    function createSettingsPanel() {
        // Check if motion tracking switch exists first
        const motionSwitch = document.querySelector('#motionTrackingSwitch');
        if (!motionSwitch) {
            return false;
        }
        
        // Check if settings panel already exists
        if (document.querySelector('#motionSettingsPanel')) {
            return true;
        }
        
        // Create settings panel container
        const settingsPanel = document.createElement('div');
        settingsPanel.id = 'motionSettingsPanel';
        settingsPanel.style.cssText = `
            margin-top: 10px;
            padding: 10px;
            background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
            border-radius: 8px;
            border: 1px solid #333;
            display: none;
        `;
        
        // Create settings header
        const header = document.createElement('div');
        header.style.cssText = `
            color: #fff;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
            text-align: center;
            border-bottom: 1px solid #444;
            padding-bottom: 5px;
        `;
        header.innerHTML = '⚙️ Motion Settings';
        
        // Create preset buttons
        const presetsContainer = document.createElement('div');
        presetsContainer.style.cssText = `
            margin-bottom: 10px;
        `;
        
        const presetsLabel = document.createElement('div');
        presetsLabel.style.cssText = `
            color: #ccc;
            font-size: 10px;
            margin-bottom: 5px;
        `;
        presetsLabel.textContent = 'Presets:';
        
        const presets = ['conservative', 'balanced', 'aggressive', 'indoor', 'outdoor'];
        const presetsButtons = document.createElement('div');
        presetsButtons.style.cssText = `
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3px;
        `;
        
        presets.forEach(preset => {
            const btn = document.createElement('button');
            btn.className = 'motion-preset-btn';
            btn.dataset.preset = preset;
            btn.style.cssText = `
                background: #333;
                color: #fff;
                border: 1px solid #555;
                padding: 3px 6px;
                font-size: 9px;
                border-radius: 3px;
                cursor: pointer;
                transition: all 0.2s;
            `;
            btn.textContent = preset;
            
            btn.addEventListener('click', () => applyPreset(preset));
            btn.addEventListener('mouseenter', () => {
                btn.style.background = '#444';
            });
            btn.addEventListener('mouseleave', () => {
                if (!btn.classList.contains('active')) {
                    btn.style.background = '#333';
                }
            });
            
            presetsButtons.appendChild(btn);
        });
        
        presetsContainer.appendChild(presetsLabel);
        presetsContainer.appendChild(presetsButtons);
        
        // Create fine-tuning controls
        const controlsContainer = document.createElement('div');
        controlsContainer.style.cssText = `
            margin-top: 8px;
        `;
        
        const controlsLabel = document.createElement('div');
        controlsLabel.style.cssText = `
            color: #ccc;
            font-size: 10px;
            margin-bottom: 5px;
        `;
        controlsLabel.textContent = 'Fine Tuning:';
        
        // Movement Duration
        const movementControl = createSliderControl(
            'Movement Duration:', 
            'movementDuration', 
            2.0, 
            0.5, 
            5.0, 
            0.1, 
            's'
        );
        
        // Pause Duration  
        const pauseControl = createSliderControl(
            'Pause Duration:', 
            'pauseDuration', 
            1.0, 
            0.2, 
            3.0, 
            0.1, 
            's'
        );
        
        // Motion Threshold
        const thresholdControl = createSliderControl(
            'Sensitivity:', 
            'motionThreshold', 
            1000, 
            500, 
            3000, 
            100, 
            ''
        );
        
        // Min Contour Area
        const areaControl = createSliderControl(
            'Min Size:', 
            'minContourArea', 
            1500, 
            500, 
            5000, 
            250, 
            'px'
        );
        
        controlsContainer.appendChild(controlsLabel);
        controlsContainer.appendChild(movementControl);
        controlsContainer.appendChild(pauseControl);
        controlsContainer.appendChild(thresholdControl);
        controlsContainer.appendChild(areaControl);
        
        // Reset button
        const resetBtn = document.createElement('button');
        resetBtn.style.cssText = `
            width: 100%;
            background: #d32f2f;
            color: white;
            border: none;
            padding: 5px;
            font-size: 10px;
            border-radius: 3px;
            cursor: pointer;
            margin-top: 8px;
        `;
        resetBtn.textContent = 'Reset to Defaults';
        resetBtn.addEventListener('click', resetSettings);
        
        // Assemble panel
        settingsPanel.appendChild(header);
        settingsPanel.appendChild(presetsContainer);
        settingsPanel.appendChild(controlsContainer);
        settingsPanel.appendChild(resetBtn);
        
        // Insert after motion tracking switch
        const motionContainer = motionSwitch.closest('div');
        motionContainer.parentNode.insertBefore(settingsPanel, motionContainer.nextSibling);
        
        // Add toggle functionality to motion tracking switch
        const switchLabel = motionContainer.querySelector('div');
        if (switchLabel) {
            switchLabel.style.cursor = 'pointer';
            switchLabel.addEventListener('dblclick', toggleSettingsPanel);
        }
        
        console.log('Motion Settings: Panel created successfully');
        return true;
    }
    
    // Create slider control
    function createSliderControl(label, id, defaultValue, min, max, step, unit) {
        const container = document.createElement('div');
        container.style.cssText = `
            margin-bottom: 6px;
        `;
        
        const labelEl = document.createElement('div');
        labelEl.style.cssText = `
            color: #ccc;
            font-size: 9px;
            margin-bottom: 2px;
        `;
        labelEl.textContent = label;
        
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.id = id;
        slider.min = min;
        slider.max = max;
        slider.step = step;
        slider.value = defaultValue;
        slider.style.cssText = `
            width: 100%;
            height: 15px;
        `;
        
        const valueDisplay = document.createElement('span');
        valueDisplay.style.cssText = `
            color: #fff;
            font-size: 9px;
            float: right;
        `;
        valueDisplay.textContent = `${defaultValue}${unit}`;
        
        slider.addEventListener('input', function() {
            const value = parseFloat(this.value);
            valueDisplay.textContent = `${value}${unit}`;
            updateSetting(id, value);
        });
        
        container.appendChild(labelEl);
        container.appendChild(slider);
        container.appendChild(valueDisplay);
        
        return container;
    }
    
    // Toggle settings panel visibility
    function toggleSettingsPanel() {
        const panel = document.querySelector('#motionSettingsPanel');
        if (panel) {
            settingsVisible = !settingsVisible;
            panel.style.display = settingsVisible ? 'block' : 'none';
            console.log(`Motion Settings: Panel ${settingsVisible ? 'opened' : 'closed'}`);
        }
    }
    
    // Initialize settings panel
    function initializeSettings() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(tryCreateSettings, 2000);
            });
        } else {
            setTimeout(tryCreateSettings, 2000);
        }
    }
    
    function tryCreateSettings() {
        let attempts = 0;
        const maxAttempts = 15;
        
        function attemptCreate() {
            attempts++;
            if (createSettingsPanel()) {
                console.log('Motion Settings: Initialized successfully');
            } else if (attempts < maxAttempts) {
                setTimeout(attemptCreate, 1000);
            } else {
                console.warn('Motion Settings: Failed to initialize after multiple attempts');
            }
        }
        
        attemptCreate();
    }
    
    // Start initialization
    initializeSettings();
    
    console.log('Motion Settings Script: Loaded');
})();