// Complete Feature Control System - All WAVEGO Features
// Master control panel for all implemented features

(function() {
    'use strict';
    
    // Feature state management
    let featureStates = {
        // Computer Vision Features
        faceDetection: { active: false, mode: 'faceDetection' },
        objectRecognition: { active: false, mode: 'objectRecognition' },
        gestureRecognition: { active: false, mode: 'gestureRecognition' },
        motionTracking: { active: false, mode: 'motionTracking' },
        colorRecognition: { active: false, mode: 'findColor' },
        lineFollowing: { active: false, mode: 'findlineCV' },
        watchDog: { active: false, mode: 'watchDog' },
        mediaCapture: { active: false, mode: 'mediaCapture' },
        
        // System Features
        bolliOs: { active: false },
        keyboardShortcuts: { active: true }, // Always active
        speedControl: { active: true, value: 100 },
        
        // Media Features
        photoCapture: { available: true },
        videoRecording: { active: false, recording: false }
    };
    
    let websocketConnection = null;
    let statusUpdateInterval = null;
    let currentCVMode = 'none';
    let currentSpeed = 100;
    
    // WebSocket Management
    function getWebSocketConnection() {
        if (window.websocket && window.websocket.readyState === WebSocket.OPEN) {
            return window.websocket;
        }
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            return window.ws;
        }
        
        if (!websocketConnection || websocketConnection.readyState !== WebSocket.OPEN) {
            try {
                websocketConnection = new WebSocket('ws://' + location.hostname + ':8888');
                
                websocketConnection.onopen = function() {
                    console.log('Feature Controls: WebSocket connected');
                    websocketConnection.send('admin:123456');
                    setTimeout(() => requestAllStatus(), 1000);
                };
                
                websocketConnection.onmessage = function(event) {
                    try {
                        const response = JSON.parse(event.data);
                        handleWebSocketResponse(response);
                    } catch (e) {
                        // Ignore non-JSON messages
                    }
                };
                
                websocketConnection.onclose = function() {
                    console.log('Feature Controls: WebSocket disconnected');
                    websocketConnection = null;
                    setTimeout(() => getWebSocketConnection(), 3000);
                };
                
            } catch (error) {
                console.log('Feature Controls: Failed to create WebSocket:', error);
            }
        }
        
        return websocketConnection;
    }
    
    // Handle WebSocket responses
    function handleWebSocketResponse(response) {
        switch (response.title) {
            case 'bolliOs':
                featureStates.bolliOs.active = response.data === 'activated';
                break;
            case 'bolliOsStatus':
                featureStates.bolliOs.active = response.data.active;
                break;
            case 'motionTracking':
                featureStates.motionTracking.active = response.data === 'activated';
                break;
            case 'cvMode':
                currentCVMode = response.data;
                updateCVModeStates();
                break;
        }
        updateAllUI();
    }
    
    // Send command via WebSocket
    function sendCommand(command, data = null) {
        const ws = getWebSocketConnection();
        if (ws && ws.readyState === WebSocket.OPEN) {
            if (data) {
                ws.send(JSON.stringify({ command: command, data: data }));
            } else {
                ws.send(command);
            }
            console.log('Feature Controls: Sent command:', command, data);
        } else {
            console.log('Feature Controls: WebSocket not ready');
            getWebSocketConnection();
        }
    }
    
    // Update CV mode states
    function updateCVModeStates() {
        // Reset all CV modes
        Object.keys(featureStates).forEach(key => {
            if (featureStates[key].mode) {
                featureStates[key].active = false;
            }
        });
        
        // Set active CV mode
        Object.keys(featureStates).forEach(key => {
            if (featureStates[key].mode === currentCVMode) {
                featureStates[key].active = true;
            }
        });
    }
    
    // Request all status
    function requestAllStatus() {
        sendCommand('bolliOsStatus');
        sendCommand('get_info');
    }
    
    // Create master control panel
    function createMasterControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'feature-control-master';
        panel.innerHTML = `
            <h2>🚀 WAVEGO Complete Feature Controls</h2>
            
            <!-- Master Controls -->
            <div class="master-controls">
                <button id="emergency-stop" class="master-btn master-btn-emergency">🛑 EMERGENCY STOP</button>
                <button id="stop-all-features" class="master-btn master-btn-stop-all">⏹️ STOP ALL</button>
            </div>
            
            <!-- Speed Control -->
            <div class="speed-control">
                <label>🏃 Movement Speed</label>
                <input type="range" id="speed-slider" class="speed-slider" min="1" max="100" value="100">
                <div id="speed-display" class="speed-display">100%</div>
            </div>
            
            <!-- CV Mode Selector -->
            <div class="cv-mode-selector">
                <label>👁️ Computer Vision Mode</label>
                <select id="cv-mode-select" class="cv-mode-select">
                    <option value="none">None - Manual Control</option>
                    <option value="faceDetection">Face Detection & Tracking</option>
                    <option value="objectRecognition">Object Recognition (DNN)</option>
                    <option value="gestureRecognition">Gesture Recognition (MediaPipe)</option>
                    <option value="motionTracking">Motion Tracking & Following</option>
                    <option value="findColor">Color Recognition & Tracking</option>
                    <option value="findlineCV">Line Following</option>
                    <option value="watchDog">Motion Detection (Security)</option>
                    <option value="mediaCapture">Photo/Video Capture Mode</option>
                </select>
            </div>
            
            <!-- Computer Vision Features -->
            <div class="feature-category">
                <h3><span class="feature-category-icon">👁️</span>Computer Vision Features</h3>
                <div class="feature-grid">
                    <div id="face-detection-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Face Detection</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="face-detection-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="faceDetection" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="faceDetection" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Automatic face detection and robot tracking</div>
                    </div>
                    
                    <div id="object-recognition-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Object Recognition</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="object-recognition-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="objectRecognition" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="objectRecognition" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">DNN-based object detection (80+ classes)</div>
                    </div>
                    
                    <div id="gesture-recognition-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Gesture Recognition</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="gesture-recognition-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="gestureRecognition" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="gestureRecognition" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Hand gesture robot control via MediaPipe</div>
                    </div>
                    
                    <div id="motion-tracking-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Motion Tracking</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="motion-tracking-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="motionTracking" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="motionTracking" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Person following with distance control</div>
                    </div>
                    
                    <div id="color-recognition-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Color Recognition</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="color-recognition-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="colorRecognition" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="colorRecognition" data-action="settings">Color</button>
                        </div>
                        <div class="feature-description">HSV color tracking and following</div>
                    </div>
                    
                    <div id="line-following-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Line Following</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="line-following-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="lineFollowing" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="lineFollowing" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Automatic line detection and following</div>
                    </div>
                </div>
            </div>
            
            <!-- System Features -->
            <div class="feature-category">
                <h3><span class="feature-category-icon">⚙️</span>System Features</h3>
                <div class="feature-grid">
                    <div id="bollios-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">BolliOs Gyro Balance</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="bollios-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="bolliOs" data-action="activate">Start</button>
                            <button class="feature-btn feature-btn-deactivate" data-feature="bolliOs" data-action="deactivate">Stop</button>
                        </div>
                        <div class="feature-description">Automatic gyro balance correction</div>
                    </div>
                    
                    <div id="keyboard-shortcuts-control" class="feature-control active">
                        <div class="feature-header">
                            <h4 class="feature-title">Keyboard Shortcuts</h4>
                            <span class="feature-status active">ACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="keyboard-shortcuts-toggle" checked>
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-settings" data-feature="keyboardShortcuts" data-action="settings">Controls</button>
                        </div>
                        <div class="feature-description">WASD movement + Space stop (Always active)</div>
                    </div>
                    
                    <div id="security-mode-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Security Mode</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="security-mode-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="watchDog" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="watchDog" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Motion detection for security monitoring</div>
                    </div>
                </div>
            </div>
            
            <!-- Media Features -->
            <div class="feature-category">
                <h3><span class="feature-category-icon">📷</span>Media Features</h3>
                <div class="feature-grid">
                    <div id="photo-capture-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Photo Capture</h4>
                            <span class="feature-status active">READY</span>
                        </div>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-capture" data-feature="photoCapture" data-action="take">📸 Take Photo</button>
                            <button class="feature-btn feature-btn-settings" data-feature="photoCapture" data-action="settings">Quality</button>
                        </div>
                        <div class="feature-description">High-quality photo capture with metadata</div>
                    </div>
                    
                    <div id="video-recording-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Video Recording</h4>
                            <span class="feature-status inactive">READY</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="video-recording-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-capture" data-feature="videoRecording" data-action="start">🎥 Record</button>
                            <button class="feature-btn feature-btn-deactivate" data-feature="videoRecording" data-action="stop">⏹️ Stop</button>
                        </div>
                        <div class="feature-description">H.264 video recording with quality control</div>
                    </div>
                    
                    <div id="media-capture-mode-control" class="feature-control">
                        <div class="feature-header">
                            <h4 class="feature-title">Media Capture Mode</h4>
                            <span class="feature-status inactive">INACTIVE</span>
                        </div>
                        <label class="feature-toggle">
                            <input type="checkbox" id="media-capture-mode-toggle">
                            <span class="feature-slider"></span>
                        </label>
                        <div class="feature-actions">
                            <button class="feature-btn feature-btn-activate" data-feature="mediaCapture" data-action="activate">Activate</button>
                            <button class="feature-btn feature-btn-settings" data-feature="mediaCapture" data-action="settings">Settings</button>
                        </div>
                        <div class="feature-description">Dedicated photo/video capture interface</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        setTimeout(() => {
            addEventListeners();
        }, 100);
        
        return panel;
    }
    
    // Add all event listeners
    function addEventListeners() {
        // Emergency stop
        const emergencyBtn = document.getElementById('emergency-stop');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => {
                sendCommand('stopCV');
                sendCommand('bolliOsOff');
                sendCommand('{"command": "emergency_stop"}');
                alert('🛑 EMERGENCY STOP ACTIVATED');
            });
        }
        
        // Stop all features
        const stopAllBtn = document.getElementById('stop-all-features');
        if (stopAllBtn) {
            stopAllBtn.addEventListener('click', () => {
                sendCommand('stopCV');
                sendCommand('bolliOsOff');
                updateCVMode('none');
            });
        }
        
        // Speed slider
        const speedSlider = document.getElementById('speed-slider');
        const speedDisplay = document.getElementById('speed-display');
        if (speedSlider && speedDisplay) {
            speedSlider.addEventListener('input', (e) => {
                currentSpeed = e.target.value;
                speedDisplay.textContent = currentSpeed + '%';
                sendCommand('speed', { value: currentSpeed });
            });
        }
        
        // CV Mode selector
        const cvModeSelect = document.getElementById('cv-mode-select');
        if (cvModeSelect) {
            cvModeSelect.addEventListener('change', (e) => {
                updateCVMode(e.target.value);
            });
        }
        
        // Feature toggles and buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-feature]')) {
                const feature = e.target.dataset.feature;
                const action = e.target.dataset.action;
                handleFeatureAction(feature, action);
            }
        });
        
        // Toggle switches
        document.addEventListener('change', (e) => {
            if (e.target.matches('[id$="-toggle"]')) {
                const feature = e.target.id.replace('-toggle', '').replace('-', '');
                handleToggleChange(feature, e.target.checked);
            }
        });
    }
    
    // Handle feature actions
    function handleFeatureAction(feature, action) {
        console.log('Feature action:', feature, action);
        
        switch (feature) {
            case 'bolliOs':
                if (action === 'activate') {
                    sendCommand('bolliOs');
                } else if (action === 'deactivate') {
                    sendCommand('bolliOsOff');
                }
                break;
                
            case 'photoCapture':
                if (action === 'take') {
                    sendCommand('{"command": "photo"}');
                }
                break;
                
            case 'videoRecording':
                if (action === 'start') {
                    sendCommand('{"command": "video_start"}');
                    featureStates.videoRecording.recording = true;
                } else if (action === 'stop') {
                    sendCommand('{"command": "video_stop"}');
                    featureStates.videoRecording.recording = false;
                }
                break;
                
            default:
                // CV Mode features
                if (featureStates[feature] && featureStates[feature].mode) {
                    if (action === 'activate') {
                        updateCVMode(featureStates[feature].mode);
                    }
                }
                break;
        }
        
        setTimeout(() => updateAllUI(), 500);
    }
    
    // Handle toggle changes
    function handleToggleChange(feature, checked) {
        if (featureStates[feature]) {
            if (checked) {
                handleFeatureAction(feature, 'activate');
            } else {
                handleFeatureAction(feature, 'deactivate');
            }
        }
    }
    
    // Update CV mode
    function updateCVMode(mode) {
        currentCVMode = mode;
        updateCVModeStates();
        
        // Send to server
        if (mode === 'none') {
            sendCommand('stopCV');
        } else {
            sendCommand('modeSelect', { mode: mode });
        }
        
        // Update UI
        const cvModeSelect = document.getElementById('cv-mode-select');
        if (cvModeSelect) {
            cvModeSelect.value = mode;
        }
        
        updateAllUI();
    }
    
    // Update all UI elements
    function updateAllUI() {
        Object.keys(featureStates).forEach(feature => {
            updateFeatureUI(feature);
        });
    }
    
    // Update individual feature UI
    function updateFeatureUI(feature) {
        const state = featureStates[feature];
        const control = document.getElementById(feature.replace(/([A-Z])/g, '-$1').toLowerCase() + '-control');
        const toggle = document.getElementById(feature.replace(/([A-Z])/g, '-$1').toLowerCase() + '-toggle');
        const status = control?.querySelector('.feature-status');
        
        if (control && state) {
            // Update active class
            if (state.active) {
                control.classList.add('active');
            } else {
                control.classList.remove('active');
            }
            
            // Update toggle
            if (toggle) {
                toggle.checked = state.active;
            }
            
            // Update status
            if (status) {
                status.textContent = state.active ? 'ACTIVE' : 'INACTIVE';
                status.className = `feature-status ${state.active ? 'active' : 'inactive'}`;
            }
        }
    }
    
    // Add panel to page
    function addControlPanel() {
        const existingPanel = document.querySelector('.feature-control-master');
        if (existingPanel) {
            console.log('Feature Controls: Panel already exists');
            return true;
        }
        
        // Find container
        const allSheets = document.querySelectorAll('.mod-sheet');
        for (let sheet of allSheets) {
            const title = sheet.querySelector('.mod-title');
            if (title && title.textContent.trim() === 'Actions') {
                const wrapper = sheet.querySelector('.mod-wrapper');
                if (wrapper) {
                    const panel = createMasterControlPanel();
                    wrapper.appendChild(panel);
                    console.log('Feature Controls: Master panel added successfully');
                    return true;
                }
            }
        }
        
        // Alternative: Add to main container
        const mainContainer = document.querySelector('.v-application .v-main .container');
        if (mainContainer) {
            const panel = createMasterControlPanel();
            mainContainer.appendChild(panel);
            console.log('Feature Controls: Panel added to main container');
            return true;
        }
        
        return false;
    }
    
    // Start status polling
    function startStatusPolling() {
        statusUpdateInterval = setInterval(() => {
            requestAllStatus();
        }, 10000); // Every 10 seconds
    }
    
    // Initialize
    function init() {
        console.log('Feature Controls: Initializing master control system...');
        
        getWebSocketConnection();
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    if (addControlPanel()) {
                        startStatusPolling();
                        setTimeout(() => requestAllStatus(), 2000);
                    }
                }, 3000);
            });
        } else {
            setTimeout(() => {
                if (addControlPanel()) {
                    startStatusPolling();
                    setTimeout(() => requestAllStatus(), 2000);
                }
            }, 3000);
        }
        
        // Cleanup
        window.addEventListener('beforeunload', () => {
            if (statusUpdateInterval) {
                clearInterval(statusUpdateInterval);
            }
        });
    }
    
    // Export for debugging
    window.FeatureControls = {
        getStates: () => featureStates,
        sendCommand: sendCommand,
        updateCVMode: updateCVMode,
        updateAllUI: updateAllUI
    };
    
    // Start
    init();
    
})();