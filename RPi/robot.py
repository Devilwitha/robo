#!/usr/bin/env/python3
# File name   : robot.py
# Description : Robot interfaces.
import time
import json
import serial
import platform

# Try to initialize serial connection.
# If it fails, the program will exit with an error.
try:
    ser = serial.Serial("/dev/ttyS0", 115200)
    print("Successfully connected to the serial port /dev/ttyS0.")
except serial.SerialException as e:
    print("------------------------------------------------------------")
    print(f"FATAL ERROR: Failed to open serial port /dev/ttyS0: {e}")
    print("This is the hardware interface for the robot.")
    print("\nTroubleshooting steps:")
    print("1. Ensure the robot's hardware is correctly connected.")
    print("2. In `sudo raspi-config`, under 'Interface Options' -> 'Serial Port':")
    print("   - Ensure the login shell over serial is DISABLED.")
    print("   - Ensure the serial port hardware is ENABLED.")
    print("3. Check for other processes that might be using the port.")
    print("\nExiting program. The robot cannot be controlled.")
    print("------------------------------------------------------------")
    # Exit the program because the robot is unusable without the serial connection.
    exit()
dataCMD = json.dumps({'var':"", 'val':0, 'ip':""})
upperGlobalIP = 'UPPER IP'


pitch, roll = 0, 0


def setUpperIP(ipInput):
	global upperGlobalIP
	upperGlobalIP = ipInput

def forward(speed=100):
	dataCMD = json.dumps({'var':"move", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-forward')

def backward(speed=100):
	dataCMD = json.dumps({'var':"move", 'val':5})
	ser.write(dataCMD.encode())
	print('robot-backward')

def left(speed=100):
	dataCMD = json.dumps({'var':"move", 'val':2})
	ser.write(dataCMD.encode())
	print('robot-left')

def right(speed=100):
	dataCMD = json.dumps({'var':"move", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-right')

def stopLR():
	dataCMD = json.dumps({'var':"move", 'val':6})
	ser.write(dataCMD.encode())
	print('robot-stop')

def stopFB():
	dataCMD = json.dumps({'var':"move", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-stop')



def lookUp():
	dataCMD = json.dumps({'var':"ges", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-lookUp')

def lookDown():
	dataCMD = json.dumps({'var':"ges", 'val':2})
	ser.write(dataCMD.encode())
	print('robot-lookDown')

def lookStopUD():
	dataCMD = json.dumps({'var':"ges", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-lookStopUD')

def lookLeft():
	dataCMD = json.dumps({'var':"ges", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-lookLeft')

def lookRight():
	dataCMD = json.dumps({'var':"ges", 'val':5})
	ser.write(dataCMD.encode())
	print('robot-lookRight')

def lookStopLR():
	dataCMD = json.dumps({'var':"ges", 'val':6})
	ser.write(dataCMD.encode())
	print('robot-lookStopLR')



def steadyMode():
	dataCMD = json.dumps({'var':"funcMode", 'val':1})
	ser.write(dataCMD.encode())
	print('robot-steady')

def jump():
	dataCMD = json.dumps({'var':"funcMode", 'val':4})
	ser.write(dataCMD.encode())
	print('robot-jump')

def handShake():
	dataCMD = json.dumps({'var':"funcMode", 'val':3})
	ser.write(dataCMD.encode())
	print('robot-handshake')



def lightCtrl(colorName, cmdInput):
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
	dataCMD = json.dumps({'var':"buzzer", 'val':buzzerCtrl})
	ser.write(dataCMD.encode())



if __name__ == '__main__':
    # robotCtrl.moveStart(100, 'forward', 'no', 0)
    # time.sleep(3)
    # robotCtrl.moveStop()
    while 1:
        time.sleep(1)
        pass