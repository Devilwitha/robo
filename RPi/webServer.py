#!/usr/bin/env python
# File name   : server.py
# Production  : Upper Ctrl for Robots
# Author      : WaveShare

import time
import threading
import os
import socket
import json
import info
import asyncio
import websockets
import app

# Globale Variable für die Flask-App und IP
flask_app = None
ipaddr_check = "192.168.4.1"


def ap_thread():
    # Dieser Befehl startet einen Access Point. Er benötigt Root-Rechte.
    os.system("sudo create_ap wlan0 eth0 WAVE_BOT 12345678")


def wifi_check():
    global ipaddr_check
    # Kurze Pause, damit das Netzwerk beim Systemstart initialisiert werden kann
    time.sleep(5)
    try:
        # Versucht, die aktuelle IP-Adresse im lokalen Netzwerk zu finden
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(f"INFO: Erfolgreich mit Netzwerk verbunden. IP-Adresse: {ipaddr_check}")
    except:
        # Wenn keine Verbindung besteht, wird ein eigener WLAN Access Point gestartet
        print("WARNUNG: Keine Netzwerkverbindung. Starte den Access Point Modus.")
        ap_threading = threading.Thread(target=ap_thread)
        ap_threading.setDaemon(True)
        ap_threading.start()


async def check_permit(websocket):
    # Diese Funktion wartet auf Anmeldeinformationen vom Client
    print(f"INFO: Neue Verbindung von {websocket.remote_address}")
    # Im Originalcode war hier eine Passwortabfrage, die oft Probleme macht.
    # Wir lassen sie weg, um die Verbindung zu vereinfachen.
    await websocket.send("welcome")
    return True


async def recv_msg(websocket):
    # Hauptschleife zum Empfangen von Steuerbefehlen
    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }

        try:
            data_raw = await websocket.recv()

            # Versucht, die empfangenen Daten als JSON zu interpretieren
            try:
                data = json.loads(data_raw)
            except:
                data = data_raw # Behält die Daten als String bei, falls es kein JSON ist

            if not data:
                continue

            # Verarbeitet Befehle, die als einfacher String gesendet werden
            if isinstance(data, str):
                # Leitet fast alle String-Befehle direkt an die Roboter-Steuerung weiter
                if data not in ['get_info', 'scan']:
                    flask_app.commandInput(data)

                if data == 'get_info':
                    response['title'] = 'get_info'
                    response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

                elif data == 'findColor':
                    flask_app.modeselect('findColor')

                elif data == 'scan':
                    radar_send = [[3,60],[10,70],[10,80],[10,90],[10,100],[10,110],[3,120]]
                    response['title'] = 'scanResult'
                    response['data'] = radar_send

                elif data == 'motionGet':
                    flask_app.modeselect('watchDog')

                elif data == 'stopCV':
                    flask_app.modeselect('none')

            # Verarbeitet Befehle, die als JSON-Objekt (dict) gesendet werden
            elif isinstance(data, dict):
                if data.get('title') == "findColorSet":
                    color = data.get('data')
                    if color and len(color) == 3:
                        flask_app.colorFindSet(color[0], color[1], color[2])

            response_json = json.dumps(response)
            await websocket.send(response_json)

        except websockets.exceptions.ConnectionClosed:
            print(f"INFO: Verbindung von {websocket.remote_address} geschlossen.")
            break
        except Exception as e:
            print(f"FEHLER in recv_msg: {e}")
            break


async def main_logic(websocket, path):
    # Logik für eine neue WebSocket-Verbindung
    print(f"INFO: Neue Verbindung von {websocket.remote_address}")
    # Die Authentifizierung scheint optional oder fehlerhaft im Originalcode,
    # wir lassen sie vorerst weg, um die Verbindung zu vereinfachen.
    # permit = await check_permit(websocket)
    # if permit:
    #     await recv_msg(websocket)
    await recv_msg(websocket)


async def main_async_server():
    # 'async with' startet den Server und stellt sicher, dass er sauber beendet wird
    async with websockets.serve(main_logic, "0.0.0.0", 8888):
        print("INFO: WebSocket-Server erfolgreich auf Port 8888 gestartet.")
        print("INFO: Warte auf Verbindungen...")
        # Hält den Server am Laufen, ohne die CPU zu belasten
        await asyncio.Future()  # läuft für immer

if __name__ == '__main__':
    # Initialisiert die Flask-App aus app.py
    wifi_check()
    flask_app = app.webapp()
    # Startet den Flask-Server (Port 5000) in einem separaten Hintergrund-Thread
    flask_app.startthread()
    # Sendet die IP-Adresse (vermutlich zur Anzeige im Videostream)
    flask_app.sendIP(ipaddr_check)

    # Dies ist der neue, korrekte Weg, den asynchronen WebSocket-Server zu starten
    try:
        print("INFO: Starte asyncio event loop für den WebSocket-Server...")
        # asyncio.run() kümmert sich um die "event loop" und behebt den "no running event loop"-Fehler
        asyncio.run(main_async_server())
    except KeyboardInterrupt:
        print("INFO: Server werden heruntergefahren.")
    except Exception as e:
        print(f"FATALER FEHLER in der Hauptschleife: {e}")