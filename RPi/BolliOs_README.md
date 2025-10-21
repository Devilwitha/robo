# BolliOs - Gyro Balance System

## Übersicht
BolliOs ist ein Gyro-Balance-System für den WaveShare-Roboter, das automatische Ausgleichsbewegungen ermöglicht, ähnlich wie der "Steady"-Modus.

## Features
- **Automatischer Gyro-Ausgleich**: Aktiviert kontinuierliche Balance-Korrekturen
- **Web-Interface Integration**: Neuer "BolliOs" Button im Actions-Bereich
- **Visuelle Rückmeldung**: LED-Anzeigen für aktiven/inaktiven Status
- **Thread-basierte Ausführung**: Läuft im Hintergrund ohne die Hauptanwendung zu blockieren

## Installation
Die BolliOs-Funktionalität ist bereits in das bestehende System integriert:

1. `BollshiiOs.py` - Haupt-Balance-System
2. `bollios-extension.js` - Frontend-Button-Integration
3. `bollios-extension.css` - Button-Styling
4. Modifikationen in `webServer.py`, `camera_opencv.py` und `app.py`

## Verwendung

### Web-Interface
1. Öffnen Sie die Robot-Controller-Webseite
2. Navigieren Sie zum "Actions"-Bereich
3. Klicken Sie auf den "BolliOs" Button, um die Balance-Funktion zu aktivieren
4. Der Button zeigt "BolliOs ON" an, wenn aktiv (grün)
5. Klicken Sie erneut, um die Funktion zu deaktivieren

### Befehle
- `bolliOs` - Aktiviert den Gyro-Balance-Modus
- `bolliOsOff` - Deaktiviert den Gyro-Balance-Modus

### Visuelle Indikatoren
- **Grün**: BolliOs ist aktiv und balanciert
- **Cyan**: Periodische Statusanzeige während der Balance
- **Blau**: BolliOs ist inaktiv

## Technische Details

### Python-Module
- **BollshiiOs.py**: Hauptlogik für die Balance-Steuerung
- Verwendet `robot.steadyMode()` für tatsächliche Gyro-Korrekturen
- Thread-basierte Ausführung für kontinuierliche Balance
- Saubere Start/Stop-Mechanismen

### Frontend-Integration
- **bollios-extension.js**: Dynamisches Hinzufügen des Buttons zur bestehenden UI
- WebSocket-Kommunikation für Echtzeit-Steuerung
- Robuste DOM-Manipulation mit Wiederholungsversuchen

### WebSocket-Protokoll
```javascript
// Aktivierung
websocket.send('bolliOs');

// Deaktivierung  
websocket.send('bolliOsOff');
```

## Sicherheit
- Automatisches Stoppen bei Fehlern
- Thread-sichere Implementierung
- Timeout-basierte Thread-Beendigung
- Graceful Degradation bei WebSocket-Verbindungsproblemen

## Troubleshooting

### Button erscheint nicht
- Überprüfen Sie, dass `bollios-extension.js` geladen wird
- Konsole auf JavaScript-Fehler prüfen
- Sicherstellen, dass die "Actions"-Sektion vorhanden ist

### Balance funktioniert nicht
- Überprüfen Sie die WebSocket-Verbindung
- Stellen Sie sicher, dass der Arduino korrekt verbunden ist
- Prüfen Sie die Konsolenausgabe für Fehlermeldungen

### Performance-Probleme
- Der Balance-Loop läuft mit 100ms Verzögerung
- Bei Bedarf kann die Verzögerung in `BollshiiOs.py` angepasst werden

## Kompatibilität
- Python 3.x
- WebSocket-fähiger Browser
- WaveShare Robot Hardware mit Gyro-Sensor
- Bestehende Robot-Controller-Software

## Erweiterungsmöglichkeiten
- PID-Controller für präzisere Balance
- Konfigurierbare Balance-Parameter
- Erweiterte Sensor-Integration
- Logging und Telemetrie