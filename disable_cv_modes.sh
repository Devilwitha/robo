#!/bin/bash

# WAVEGO Startup Script - Deaktiviert CV-Modi automatisch
# Wird nach dem Server-Start ausgeführt

echo "Waiting for WAVEGO server to start..."
sleep 15

echo "Disabling CV modes..."
echo "stopCV" | nc localhost 8888 2>/dev/null
echo "faceDetectionOff" | nc localhost 8888 2>/dev/null  
echo "trackLineOff" | nc localhost 8888 2>/dev/null

echo "CV modes disabled. WAVEGO ready for manual control."