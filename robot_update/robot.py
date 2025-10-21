#!/usr/bin/env/python3
# File name   : robot.py
# Description : Robot interfaces.
import time
import json
import serial
import threading

ser = serial.Serial("/dev/ttyS0",115200)
dataCMD = json.dumps({'var':"", 'val':0, 'ip':""})
upperGlobalIP = 'UPPER IP'

pitch, roll = 0, 0

# Integrated Speed Manager Class
class SpeedManager:
    def __init__(self):
        self.current_speed = 100  # Default speed (1-100)
        self.lock = threading.Lock()
        self.speed_history = []
        
    def set_speed(self, speed):
        """Set movement speed with validation and logging"""
        with self.lock:
            # Validate speed range
            if not isinstance(speed, (int, float)):
                try:
                    speed = float(speed)
                except (ValueError, TypeError):
                    print(f"SpeedManager: Invalid speed type: {type(speed)}")
                    return False
            
            # Clamp to valid range
            speed = max(1, min(100, int(speed)))
            
            # Update current speed
            old_speed = self.current_speed
            self.current_speed = speed
            
            # Log speed change
            timestamp = time.time()
            self.speed_history.append((timestamp, old_speed, speed))
            
            # Keep only last 10 speed changes
            if len(self.speed_history) > 10:
                self.speed_history = self.speed_history[-10:]
            
            print(f"SpeedManager: Speed changed from {old_speed} to {speed}")
            return True
    
    def get_speed(self):
        """Get current speed"""
        with self.lock:
            return self.current_speed
    
    def get_history(self):
        """Get speed change history"""
        with self.lock:
            return self.speed_history.copy()

# Global speed manager instance
speed_manager = SpeedManager()


def setUpperIP(ipInput):
	global upperGlobalIP
	upperGlobalIP = ipInput

def forward(speed=None):
	if speed is not None:
		speed_manager.set_speed(speed)
	current_speed = speed_manager.get_speed()
	dataCMD = json.dumps({'var':"move", 'val':1, 'speed':current_speed})
	ser.write(dataCMD.encode())
	print(f'robot-forward at speed {current_speed}')

def backward(speed=None):
	if speed is not None:
		speed_manager.set_speed(speed)
	current_speed = speed_manager.get_speed()
	dataCMD = json.dumps({'var':"move", 'val':5, 'speed':current_speed})
	ser.write(dataCMD.encode())
	print(f'robot-backward at speed {current_speed}')

def left(speed=None):
	if speed is not None:
		speed_manager.set_speed(speed)
	current_speed = speed_manager.get_speed()
	dataCMD = json.dumps({'var':"move", 'val':2, 'speed':current_speed})
	ser.write(dataCMD.encode())
	print(f'robot-left at speed {current_speed}')

def right(speed=None):
	if speed is not None:
		speed_manager.set_speed(speed)
	current_speed = speed_manager.get_speed()
	dataCMD = json.dumps({'var':"move", 'val':4, 'speed':current_speed})
	ser.write(dataCMD.encode())
	print(f'robot-right at speed {current_speed}')

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

def speedSet(speed):
	"""Set the global movement speed (1-100)"""
	if speed_manager.set_speed(speed):
		current_speed = speed_manager.get_speed()
		# Send speed setting to Arduino
		dataCMD = json.dumps({'var':"speed", 'val':current_speed})
		ser.write(dataCMD.encode())
		print(f'robot-speedSet: Set to {current_speed}')
		return True
	else:
		print(f'robot-speedSet: Failed to set speed {speed}')
		return False

def getSpeed():
	"""Get current movement speed"""
	return speed_manager.get_speed()

def getSpeedHistory():
	"""Get speed change history for debugging"""
	return speed_manager.get_history()



if __name__ == '__main__':
    # robotCtrl.moveStart(100, 'forward', 'no', 0)
    # time.sleep(3)
    # robotCtrl.moveStop()
    while 1:
        time.sleep(1)
        pass