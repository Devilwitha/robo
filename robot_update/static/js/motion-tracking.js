// Motion Tracking Extension for WAVEGO Web Interface - Vue.js Compatible
// Adds motion detection switch under BolliOs button

(function() {
    'use strict';
    
    let motionTrackingActive = false;
    let integrationAttempts = 0;
    const maxAttempts = 20; // More attempts for Vue.js loading
    let observer = null;
    
    console.log('🎯 Motion Tracking Extension loading...');

    function waitForVueAndIntegrate() {
        integrationAttempts++;
        
        // Wait for Vue app to be fully mounted
        const app = document.getElementById('app');
        if (!app || !app.innerHTML || app.innerHTML.trim() === '') {
            if (integrationAttempts < maxAttempts) {
                setTimeout(waitForVueAndIntegrate, 500);
                return;
            }
        }
        
        // Find target element for integration
        const targetElement = findBestInsertionPoint();
        
        if (targetElement) {
            insertMotionTrackingControls(targetElement);
            console.log(`🎯 Motion Tracking integrated successfully (attempt ${integrationAttempts})`);
            
            // Set up observer to re-integrate if content changes
            setupContentObserver();
        } else if (integrationAttempts < maxAttempts) {
            console.log(`🎯 Integration attempt ${integrationAttempts} failed, retrying...`);
            setTimeout(waitForVueAndIntegrate, 1000);
        } else {
            console.warn('🎯 Motion Tracking integration failed after maximum attempts');
            // Last resort - add to app container
            insertMotionTrackingControls(document.getElementById('app'));
        }
    }

    function findBestInsertionPoint() {
        // Strategy 1: Look for BolliOs button by text content
        const allButtons = document.querySelectorAll('button, .btn, .button, [role="button"]');
        for (let btn of allButtons) {
            const text = (btn.textContent || btn.innerText || '').toLowerCase();
            if (text.includes('bolli') || text.includes('gyro') || text.includes('balance')) {
                console.log('🎯 Found BolliOs button:', btn);
                return btn.closest('.action-item') || btn.closest('.button-group') || btn.parentElement;
            }
        }
        
        // Strategy 2: Look for Actions section or similar containers
        const containers = document.querySelectorAll('div, section, .actions, .controls, .action-buttons');
        for (let container of containers) {
            const text = (container.textContent || '').toLowerCase();
            if (text.includes('face detection') || 
                text.includes('action') || 
                text.includes('control') ||
                text.includes('bolli')) {
                return container;
            }
        }
        
        // Strategy 3: Look for Vue component containers
        const vueContainers = document.querySelectorAll('[data-v-]', '.vue-component', '#app > div');
        if (vueContainers.length > 0) {
            // Try to find the most appropriate container
            for (let container of vueContainers) {
                if (container.offsetHeight > 100) { // Has some content
                    return container;
                }
            }
            return vueContainers[0];
        }
        
        // Strategy 4: Use the main app container
        return document.getElementById('app');
    }

    function insertMotionTrackingControls(parentElement) {
        // Remove existing controls if they exist
        const existing = document.getElementById('motionTrackingContainer');
        if (existing) {
            existing.remove();
        }

        if (!parentElement) {
            console.error('🎯 No parent element found for Motion Tracking controls');
            return;
        }

        // Create main container with enhanced styling
        const container = document.createElement('div');
        container.id = 'motionTrackingContainer';
        container.className = 'motion-tracking-extension';
        container.style.cssText = `
            margin: 15px auto;
            padding: 20px;
            max-width: 300px;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border: 2px solid #2196F3;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1000;
        `;

        // Create header section
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        `;

        const icon = document.createElement('span');
        icon.textContent = '🎯';
        icon.style.cssText = `
            font-size: 24px;
            margin-right: 10px;
            animation: pulse 2s infinite;
        `;

        const title = document.createElement('h3');
        title.textContent = 'Motion Tracking';
        title.style.cssText = `
            margin: 0;
            color: #1565C0;
            font-size: 18px;
            font-weight: 600;
            text-align: center;
        `;

        header.appendChild(icon);
        header.appendChild(title);

        // Create description
        const description = document.createElement('p');
        description.textContent = '🔕 Silent motion detection - follows movement without beeping';
        description.style.cssText = `
            margin: 0 0 15px 0;
            color: #424242;
            font-size: 13px;
            text-align: center;
            line-height: 1.4;
        `;

        // Create switch section
        const switchSection = document.createElement('div');
        switchSection.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
        `;

        const switchLabel = document.createElement('label');
        switchLabel.textContent = 'Follow Motion';
        switchLabel.style.cssText = `
            color: #1565C0;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
        `;

        // Create animated toggle switch
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'motion-toggle';
        toggleContainer.style.cssText = `
            position: relative;
            display: inline-block;
            width: 70px;
            height: 34px;
        `;

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.id = 'motionTrackingToggle';
        toggleInput.style.cssText = `
            opacity: 0;
            width: 0;
            height: 0;
        `;

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'motion-toggle-slider';
        toggleSlider.style.cssText = `
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(145deg, #B0BEC5, #90A4AE);
            transition: 0.4s;
            border-radius: 34px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        `;

        const toggleKnob = document.createElement('span');
        toggleKnob.style.cssText = `
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background: linear-gradient(145deg, #ffffff, #f5f5f5);
            transition: 0.4s;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        `;

        toggleSlider.appendChild(toggleKnob);

        // Create status indicator
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'motionStatus';
        statusIndicator.style.cssText = `
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 13px;
            text-align: center;
            background: linear-gradient(145deg, #F5F5F5, #EEEEEE);
            color: #666;
            border: 1px solid #DDD;
            transition: all 0.3s ease;
            font-weight: 500;
        `;
        statusIndicator.textContent = '🔘 Motion Tracking OFF';

        // Add enhanced CSS animations
        const enhancedStyles = document.createElement('style');
        enhancedStyles.textContent = `
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .motion-tracking-extension:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
            }
            
            .motion-toggle input:checked + .motion-toggle-slider {
                background: linear-gradient(145deg, #2196F3, #1976D2);
                box-shadow: inset 0 2px 4px rgba(33, 150, 243, 0.3);
            }
            
            .motion-toggle input:checked + .motion-toggle-slider span {
                transform: translateX(36px);
                background: linear-gradient(145deg, #ffffff, #E3F2FD);
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.5);
            }
            
            .motion-toggle:hover .motion-toggle-slider {
                box-shadow: 0 0 10px rgba(33, 150, 243, 0.5);
            }
        `;
        document.head.appendChild(enhancedStyles);

        // Add event listeners
        toggleInput.addEventListener('change', handleMotionToggle);
        switchLabel.addEventListener('click', () => {
            toggleInput.checked = !toggleInput.checked;
            handleMotionToggle();
        });

        // Assemble all elements
        toggleContainer.appendChild(toggleInput);
        toggleContainer.appendChild(toggleSlider);
        
        switchSection.appendChild(switchLabel);
        switchSection.appendChild(toggleContainer);
        
        container.appendChild(header);
        container.appendChild(description);
        container.appendChild(switchSection);
        container.appendChild(statusIndicator);

        // Smart insertion logic
        if (parentElement.id === 'app') {
            // If inserting into main app, add at the end
            parentElement.appendChild(container);
        } else {
            // Insert after the parent element
            parentElement.parentNode.insertBefore(container, parentElement.nextSibling);
        }

        console.log('🎯 Motion Tracking controls successfully integrated!');
        
        // Add a visible confirmation
        container.style.animation = 'slideIn 0.5s ease-out';
        const slideInKeyframes = `
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        if (!document.querySelector('#slideInAnimation')) {
            const slideInStyle = document.createElement('style');
            slideInStyle.id = 'slideInAnimation';
            slideInStyle.textContent = slideInKeyframes;
            document.head.appendChild(slideInStyle);
        }
    }

    function setupContentObserver() {
        // Watch for DOM changes to re-integrate if content is replaced
        if (observer) {
            observer.disconnect();
        }
        
        observer = new MutationObserver((mutations) => {
            let shouldReintegrate = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // Check if our motion tracking container was removed
                    const motionContainer = document.getElementById('motionTrackingContainer');
                    if (!motionContainer && mutation.removedNodes.length > 0) {
                        shouldReintegrate = true;
                    }
                }
            });
            
            if (shouldReintegrate) {
                console.log('🎯 Motion Tracking container removed, re-integrating...');
                setTimeout(waitForVueAndIntegrate, 500);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    function handleMotionToggle() {
        const toggleInput = document.getElementById('motionTrackingToggle');
        const statusIndicator = document.getElementById('motionStatus');
        
        if (!toggleInput || !statusIndicator) {
            console.error('🎯 Motion tracking elements not found');
            return;
        }
        
        motionTrackingActive = toggleInput.checked;
        
        if (motionTrackingActive) {
            // Activate motion tracking
            sendMotionCommand('motionTracking');
            statusIndicator.textContent = '🔵 Motion Tracking ACTIVE - Blue LEDs ON';
            statusIndicator.style.background = 'linear-gradient(145deg, #E3F2FD, #BBDEFB)';
            statusIndicator.style.color = '#1565C0';
            statusIndicator.style.borderColor = '#2196F3';
            
            console.log('🎯 Motion Tracking ACTIVATED - Robot will follow movement silently');
            
            // Visual feedback
            statusIndicator.style.animation = 'pulse 1s ease-in-out 3';
            
        } else {
            // Deactivate motion tracking
            sendMotionCommand('motionTrackingOff');
            statusIndicator.textContent = '🔘 Motion Tracking OFF';
            statusIndicator.style.background = 'linear-gradient(145deg, #F5F5F5, #EEEEEE)';
            statusIndicator.style.color = '#666';
            statusIndicator.style.borderColor = '#DDD';
            statusIndicator.style.animation = 'none';
            
            console.log('🎯 Motion Tracking DEACTIVATED');
        }
    }

    function sendMotionCommand(command) {
        const wsConnections = [
            window.websocket,
            window.ws,
            window.socket,
            window.webSocket,
            // Try to find WebSocket in Vue instance
            window.Vue && window.Vue.$websocket,
            window.$websocket
        ];
        
        let sent = false;
        
        for (let ws of wsConnections) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                try {
                    ws.send(command);
                    console.log(`🎯 Motion command '${command}' sent successfully via WebSocket`);
                    sent = true;
                    break;
                } catch (error) {
                    console.warn(`🎯 WebSocket send failed: ${error.message}`);
                }
            }
        }
        
        if (!sent) {
            console.error(`🎯 Failed to send motion command '${command}' - no active WebSocket connection`);
            
            // Show user feedback
            const statusIndicator = document.getElementById('motionStatus');
            if (statusIndicator) {
                const originalText = statusIndicator.textContent;
                statusIndicator.textContent = '⚠️ Connection Error - Check WebSocket';
                statusIndicator.style.color = '#D32F2F';
                
                setTimeout(() => {
                    statusIndicator.textContent = originalText;
                    statusIndicator.style.color = motionTrackingActive ? '#1565C0' : '#666';
                }, 3000);
            }
        }
    }

    // Initialize when DOM is ready or Vue is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(waitForVueAndIntegrate, 1000); // Give Vue time to mount
        });
    } else {
        setTimeout(waitForVueAndIntegrate, 1000);
    }

    // Also try to integrate when window loads (fallback)
    window.addEventListener('load', () => {
        if (!document.getElementById('motionTrackingContainer')) {
            setTimeout(waitForVueAndIntegrate, 500);
        }
    });

    // Expose global debug interface
    window.motionTrackingDebug = {
        integrate: waitForVueAndIntegrate,
        toggle: handleMotionToggle,
        isActive: () => motionTrackingActive,
        sendCommand: sendMotionCommand,
        status: () => {
            const container = document.getElementById('motionTrackingContainer');
            return {
                integrated: !!container,
                active: motionTrackingActive,
                attempts: integrationAttempts
            };
        }
    };

    console.log('🎯 Motion Tracking Extension initialized - Use motionTrackingDebug for manual control');

})();