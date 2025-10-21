// Speed Control Debug Extension
// This script helps debug speed slider functionality

(function() {
    'use strict';
    
    console.log('Speed Debug: Extension loaded');
    
    // Debug WebSocket messages
    function debugWebSocket() {
        // Try to hook into existing WebSocket
        const originalSend = WebSocket.prototype.send;
        WebSocket.prototype.send = function(data) {
            if (typeof data === 'string' && data.includes('wsB')) {
                console.log('Speed Debug: Sending speed command:', data);
            }
            return originalSend.call(this, data);
        };
    }
    
    // Monitor slider changes
    function monitorSlider() {
        // Look for speed sliders
        const checkSliders = () => {
            const sliders = document.querySelectorAll('[role="slider"]');
            sliders.forEach((slider, index) => {
                if (!slider.hasAttribute('data-debug-attached')) {
                    slider.setAttribute('data-debug-attached', 'true');
                    
                    // Add event listeners
                    slider.addEventListener('input', (e) => {
                        console.log(`Speed Debug: Slider ${index} changed to:`, e.target.value);
                    });
                    
                    slider.addEventListener('change', (e) => {
                        console.log(`Speed Debug: Slider ${index} final value:`, e.target.value);
                    });
                    
                    console.log(`Speed Debug: Attached to slider ${index}, current value:`, slider.value);
                }
            });
        };
        
        // Check for sliders periodically
        setInterval(checkSliders, 2000);
        checkSliders();
    }
    
    // Add manual speed test buttons
    function addTestControls() {
        // Wait for page to load
        setTimeout(() => {
            const testContainer = document.createElement('div');
            testContainer.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                z-index: 10000;
                font-size: 12px;
            `;
            
            testContainer.innerHTML = `
                <div>Speed Debug Controls:</div>
                <button onclick="speedDebugTest(25)">Test Speed 25</button>
                <button onclick="speedDebugTest(50)">Test Speed 50</button>
                <button onclick="speedDebugTest(75)">Test Speed 75</button>
                <button onclick="speedDebugTest(100)">Test Speed 100</button>
                <div id="speedDebugStatus">Status: Ready</div>
            `;
            
            document.body.appendChild(testContainer);
            
            // Global test function
            window.speedDebugTest = function(speed) {
                const statusDiv = document.getElementById('speedDebugStatus');
                statusDiv.textContent = `Testing speed: ${speed}`;
                
                // Try to send speed command
                const command = `wsB ${speed}`;
                console.log('Speed Debug: Manual test sending:', command);
                
                // Find WebSocket connection
                if (window.websocketConnection) {
                    window.websocketConnection.send(command);
                } else {
                    // Try alternative method
                    const ws = new WebSocket('ws://' + location.hostname + ':8888');
                    ws.onopen = function() {
                        ws.send('admin:123456');
                        setTimeout(() => {
                            ws.send(command);
                            statusDiv.textContent = `Sent: ${command}`;
                            ws.close();
                        }, 100);
                    };
                }
            };
            
        }, 3000);
    }
    
    // Initialize debug features
    function init() {
        debugWebSocket();
        monitorSlider();
        addTestControls();
        
        console.log('Speed Debug: All debug features initialized');
    }
    
    // Start when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();