/**
 * Keyboard Shortcut Controls for WAVEGO Robot Web Interface
 * 
 * Features:
 * - WASD movement controls
 * - Function key shortcuts for CV modes
 * - Number key shortcuts for robot actions
 * - Emergency stop functionality
 * - Visual feedback for active shortcuts
 */

class KeyboardController {
    constructor() {
        this.enabled = true;
        this.activeKeys = new Set();
        this.shortcuts = this.initializeShortcuts();
        this.helpVisible = false;
        
        // Bind event handlers
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleKeyUp = this.handleKeyUp.bind(this);
        
        this.init();
    }
    
    initializeShortcuts() {
        return {
            // Movement Controls
            'w': { action: 'forward', description: 'Move Forward', category: 'Movement' },
            's': { action: 'backward', description: 'Move Backward', category: 'Movement' },
            'a': { action: 'left', description: 'Turn Left', category: 'Movement' },
            'd': { action: 'right', description: 'Turn Right', category: 'Movement' },
            'q': { action: 'DS', description: 'Stop Forward/Backward', category: 'Movement' },
            'e': { action: 'TS', description: 'Stop Left/Right', category: 'Movement' },
            
            // Camera Controls
            'ArrowUp': { action: 'up', description: 'Look Up', category: 'Camera' },
            'ArrowDown': { action: 'down', description: 'Look Down', category: 'Camera' },
            'ArrowLeft': { action: 'lookleft', description: 'Look Left', category: 'Camera' },
            'ArrowRight': { action: 'lookright', description: 'Look Right', category: 'Camera' },
            
            // Robot Actions
            '1': { action: 'jump', description: 'Jump', category: 'Actions' },
            '2': { action: 'handshake', description: 'Handshake', category: 'Actions' },
            '3': { action: 'steady', description: 'Steady Mode', category: 'Actions' },
            '4': { action: 'bolliOs', description: 'BolliOs Mode', category: 'Actions' },
            
            // Computer Vision
            'f': { action: 'faceDetection', description: 'Face Detection', category: 'Computer Vision' },
            'o': { action: 'objectRecognition', description: 'Object Recognition', category: 'Computer Vision' },
            'g': { action: 'gestureRecognition', description: 'Gesture Recognition', category: 'Computer Vision' },
            'm': { action: 'motionTracking', description: 'Motion Tracking', category: 'Computer Vision' },
            'c': { action: 'findColor', description: 'Color Tracking', category: 'Computer Vision' },
            'l': { action: 'trackLine', description: 'Line Tracking', category: 'Computer Vision' },
            
            // Utility
            'Escape': { action: 'emergencyStop', description: 'Emergency Stop All', category: 'Utility' },
            'r': { action: 'resetPosition', description: 'Reset Position', category: 'Utility' },
            'p': { action: 'takePhoto', description: 'Take Photo', category: 'Utility' },
            'v': { action: 'recordVideo', description: 'Record Video', category: 'Utility' },
            
            // Help
            'h': { action: 'toggleHelp', description: 'Toggle Help', category: 'Help' },
            'F1': { action: 'showHelp', description: 'Show Help', category: 'Help' }
        };
    }
    
    init() {
        // Add event listeners
        document.addEventListener('keydown', this.handleKeyDown);
        document.addEventListener('keyup', this.handleKeyUp);
        
        // Prevent default browser shortcuts for our keys
        document.addEventListener('keydown', (e) => {
            if (this.shortcuts[e.key] && this.enabled) {
                e.preventDefault();
            }
        });
        
        // Create help overlay
        this.createHelpOverlay();
        
        // Create keyboard status indicator
        this.createStatusIndicator();
        
        console.log('Keyboard Controller initialized');
        this.showNotification('Keyboard controls active! Press H for help');
    }
    
    handleKeyDown(event) {
        if (!this.enabled) return;
        
        const key = event.key;
        
        // Ignore if already pressed (for continuous movement)
        if (this.activeKeys.has(key)) return;
        
        this.activeKeys.add(key);
        
        const shortcut = this.shortcuts[key];
        if (shortcut) {
            event.preventDefault();
            this.executeCommand(shortcut.action, key);
            this.updateStatusIndicator(key, true);
        }
    }
    
    handleKeyUp(event) {
        if (!this.enabled) return;
        
        const key = event.key;
        this.activeKeys.delete(key);
        
        const shortcut = this.shortcuts[key];
        if (shortcut) {
            this.updateStatusIndicator(key, false);
            
            // Stop movement commands when key is released
            if (shortcut.category === 'Movement') {
                this.executeStopCommand(shortcut.action);
            }
        }
    }
    
    executeCommand(action, key) {
        console.log(`Keyboard shortcut: ${key} -> ${action}`);
        
        try {
            switch (action) {
                // Handle special cases
                case 'emergencyStop':
                    this.emergencyStop();
                    break;
                    
                case 'toggleHelp':
                    this.toggleHelp();
                    break;
                    
                case 'showHelp':
                    this.showHelp();
                    break;
                    
                case 'takePhoto':
                    this.takePhoto();
                    break;
                    
                case 'recordVideo':
                    this.toggleVideoRecording();
                    break;
                    
                case 'resetPosition':
                    this.resetRobotPosition();
                    break;
                    
                // CV mode toggles
                case 'faceDetection':
                case 'objectRecognition':
                case 'gestureRecognition':
                case 'motionTracking':
                case 'findColor':
                case 'trackLine':
                    this.toggleCVMode(action);
                    break;
                    
                // Standard robot commands
                default:
                    this.sendRobotCommand(action);
                    break;
            }
        } catch (error) {
            console.error('Error executing keyboard command:', error);
        }
    }
    
    executeStopCommand(action) {
        // Send stop commands when movement keys are released
        switch (action) {
            case 'forward':
            case 'backward':
                this.sendRobotCommand('DS');
                break;
            case 'left':
            case 'right':
                this.sendRobotCommand('TS');
                break;
            case 'up':
            case 'down':
                this.sendRobotCommand('UDstop');
                break;
            case 'lookleft':
            case 'lookright':
                this.sendRobotCommand('LRstop');
                break;
        }
    }
    
    sendRobotCommand(command) {
        // Send command via WebSocket if available
        if (window.websocket && window.websocket.readyState === WebSocket.OPEN) {
            window.websocket.send(command);
            console.log(`Sent command: ${command}`);
        } else {
            console.warn('WebSocket not available for command:', command);
        }
    }
    
    toggleCVMode(mode) {
        // Toggle CV modes on/off
        const isActive = this.isCVModeActive(mode);
        const command = isActive ? `${mode}Off` : mode;
        this.sendRobotCommand(command);
        this.showNotification(`${mode}: ${isActive ? 'OFF' : 'ON'}`);
    }
    
    isCVModeActive(mode) {
        // Check if CV mode is currently active
        // This would need to be integrated with your existing CV state management
        return false; // Placeholder
    }
    
    emergencyStop() {
        // Send multiple stop commands
        const stopCommands = ['DS', 'TS', 'UDstop', 'LRstop', 'faceDetectionOff', 'motionTrackingOff'];
        stopCommands.forEach(cmd => this.sendRobotCommand(cmd));
        this.showNotification('EMERGENCY STOP ACTIVATED!', 'error');
    }
    
    takePhoto() {
        // Trigger photo capture
        this.sendRobotCommand('takePhoto');
        this.showNotification('Photo captured!', 'success');
    }
    
    toggleVideoRecording() {
        // Toggle video recording
        if (this.isRecording) {
            this.sendRobotCommand('stopRecording');
            this.showNotification('Recording stopped', 'info');
            this.isRecording = false;
        } else {
            this.sendRobotCommand('startRecording');
            this.showNotification('Recording started', 'success');
            this.isRecording = true;
        }
    }
    
    resetRobotPosition() {
        // Reset robot to default position
        this.sendRobotCommand('resetPosition');
        this.showNotification('Position reset', 'info');
    }
    
    createHelpOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'keyboard-help-overlay';
        overlay.className = 'keyboard-help-overlay hidden';
        
        const content = document.createElement('div');
        content.className = 'keyboard-help-content';
        
        let helpHTML = '<h3>Keyboard Shortcuts</h3><div class="keyboard-help-grid">';
        
        // Group shortcuts by category
        const categories = {};
        for (const [key, shortcut] of Object.entries(this.shortcuts)) {
            if (!categories[shortcut.category]) {
                categories[shortcut.category] = [];
            }
            categories[shortcut.category].push({ key, ...shortcut });
        }
        
        // Generate help content
        for (const [category, shortcuts] of Object.entries(categories)) {
            helpHTML += `<div class="help-category">`;
            helpHTML += `<h4>${category}</h4>`;
            shortcuts.forEach(shortcut => {
                const keyDisplay = this.formatKeyForDisplay(shortcut.key);
                helpHTML += `<div class="help-item">`;
                helpHTML += `<span class="help-key">${keyDisplay}</span>`;
                helpHTML += `<span class="help-description">${shortcut.description}</span>`;
                helpHTML += `</div>`;
            });
            helpHTML += `</div>`;
        }
        
        helpHTML += '</div>';
        helpHTML += '<p class="help-footer">Press H or ESC to close help</p>';
        
        content.innerHTML = helpHTML;
        overlay.appendChild(content);
        document.body.appendChild(overlay);
        
        // Close help when clicking outside
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.hideHelp();
            }
        });
    }
    
    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'keyboard-status';
        indicator.className = 'keyboard-status';
        indicator.innerHTML = '<div class="status-title">Keyboard</div><div class="status-keys"></div>';
        document.body.appendChild(indicator);
    }
    
    updateStatusIndicator(key, active) {
        const statusKeys = document.querySelector('#keyboard-status .status-keys');
        if (!statusKeys) return;
        
        const keyDisplay = this.formatKeyForDisplay(key);
        const keyElement = statusKeys.querySelector(`[data-key="${key}"]`);
        
        if (active && !keyElement) {
            const keySpan = document.createElement('span');
            keySpan.className = 'active-key';
            keySpan.setAttribute('data-key', key);
            keySpan.textContent = keyDisplay;
            statusKeys.appendChild(keySpan);
        } else if (!active && keyElement) {
            keyElement.remove();
        }
    }
    
    formatKeyForDisplay(key) {
        const keyMap = {
            'ArrowUp': '↑',
            'ArrowDown': '↓',
            'ArrowLeft': '←',
            'ArrowRight': '→',
            'Escape': 'ESC',
            ' ': 'SPACE'
        };
        return keyMap[key] || key.toUpperCase();
    }
    
    toggleHelp() {
        if (this.helpVisible) {
            this.hideHelp();
        } else {
            this.showHelp();
        }
    }
    
    showHelp() {
        const overlay = document.getElementById('keyboard-help-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
            this.helpVisible = true;
        }
    }
    
    hideHelp() {
        const overlay = document.getElementById('keyboard-help-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
            this.helpVisible = false;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create or update notification
        let notification = document.getElementById('keyboard-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'keyboard-notification';
            notification.className = 'keyboard-notification';
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        notification.className = `keyboard-notification ${type} show`;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
    
    enable() {
        this.enabled = true;
        this.showNotification('Keyboard controls enabled');
    }
    
    disable() {
        this.enabled = false;
        this.activeKeys.clear();
        this.showNotification('Keyboard controls disabled');
    }
    
    destroy() {
        document.removeEventListener('keydown', this.handleKeyDown);
        document.removeEventListener('keyup', this.handleKeyUp);
        
        // Remove UI elements
        const elements = ['keyboard-help-overlay', 'keyboard-status', 'keyboard-notification'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.remove();
        });
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.keyboardController = new KeyboardController();
});

// Export for manual control if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeyboardController;
}