#!/usr/bin/env/python3
# File name   : robot.py
# Description : Robot interfaces.
import time
import json
import serial

import os
import sys

# Global variables
ser = None

dataCMD = json.dumps({'var':"", 'val':0, 'ip':""})
upperGlobalIP = 'UPPER IP'

def init_serial():
    """Initialize serial connection with error handling"""
    global ser
    
    # List of possible serial ports to try
    possible_ports = ["/dev/ttyS0", "/dev/ttyAMA0", "/dev/serial0"]
    
    for port in possible_ports:
        try:
            if os.path.exists(port):
                ser = serial.Serial(port, 115200, timeout=1)
                print(f"Successfully connected to {port}")
                return True
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error connecting to {port}: {e}")
            continue
    
    print("Warning: No serial port available. Robot functions will be disabled.")
    ser = None
    return False

def ensure_serial():
    """Ensure serial connection is available before sending commands"""
    if ser is None:
        if not init_serial():
            print("Serial connection not available - command ignored")
            return False
    return True

# Initialize serial connection on module import
init_serial()


pitch, roll = 0, 0


def setUpperIP(ipInput):
	global upperGlobalIP
	upperGlobalIP = ipInput

def forward(speed=100):
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-forward')

def backward(speed=100):
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':5})
	ser.write(dataCMD.encode())
	print('robot-backward')

def left(speed=100):
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':2})
	ser.write(dataCMD.encode())
	print('robot-left')

def right(speed=100):
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-right')

def stopLR():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':6})
	ser.write(dataCMD.encode())
	print('robot-stop')

def stopFB():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"move", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-stop')



def lookUp():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-lookUp')

def lookDown():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':2})
	ser.write(dataCMD.encode())
	print('robot-lookDown')

def lookStopUD():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-lookStopUD')

def lookLeft():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-lookLeft')

def lookRight():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':5})
	ser.write(dataCMD.encode())
	print('robot-lookRight')

def lookStopLR():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"ges", 'val':6})
	ser.write(dataCMD.encode())
	print('robot-lookStopLR')



def steadyMode():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"funcMode", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-steady')

def jump():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"funcMode", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-jump')

def handShake():
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"funcMode", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-handshake')



def lightCtrl(colorName, cmdInput):
	if not ensure_serial():
		return
	colorNum = 0
	if colorName == 'off':
		colorNum = 0
	elif colorName == 'blue':
		colorNum = 1
	elif colorName == 'red':
		colorNum = 2
	elif colorName == 'green':
		colorNum = 3
	elif colorName == 'yellow':
		colorNum = 4
	elif colorName == 'cyan':
		colorNum = 5
	elif colorName == 'magenta':
		colorNum = 6
	elif colorName == 'cyber':
		colorNum = 7
	dataCMD = json.dumps({'var':"light", 'val':colorNum})
	ser.write(dataCMD.encode())


def buzzerCtrl(buzzerCtrl, cmdInput):
	if not ensure_serial():
		return
	dataCMD = json.dumps({'var':"buzzer", 'val':buzzerCtrl})
	ser.write(dataCMD.encode())



if __name__ == '__main__':
    # robotCtrl.moveStart(100, 'forward', 'no', 0)
    # time.sleep(3)
    # robotCtrl.moveStop()
    while 1:
        time.sleep(1)
        pass