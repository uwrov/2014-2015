from serial import Serial
import numpy
import math
import cv2
from time import clock, sleep
from thread import start_new_thread

# Data Headers
HEADER_1 = 17
HEADER_2 = 151
EXPECTED_SENSOR_HEADER_1 = 74
EXPECTED_SENSOR_HEADER_2 = 225
PNEUMATIC_KEY = 100
COMM_KEY = 101
PING_KEY = 102

# Communication
ser = None
pingTime = -1
pingStartTime = 0

# Sensors
sensor1Name = 0
sensor2Name = 1
sensors = {sensor1Name : 0, sensor2Name : 0}

# Image
IMAGE_SIZE = [480, 640]
image = numpy.zeros((IMAGE_SIZE[0], IMAGE_SIZE[1] * 2, 3), numpy.uint8)

# THE BOT
#
#     FRONT
#
#  1 /_____\ 2
#    |     |
#    |  5  |
#    |  6  |
#    |_____|
#  4 \     / 3

# Updates the sensor data and ping time from the Arduino. Runs on
# a separate thread after setup runs
def updateData():
	global sensors
	global pingTime
	global pingStartTime
	while True:
		sleep(0.1)
		# Packets should be received in sets of 4
		while ser.inWaiting() > 0:
			sensorHeader1 = readByte(ser)
			while sensorHeader1 != EXPECTED_SENSOR_HEADER_1:
				sensorHeader1 = readByte(ser)
			sensorHeader2 = readByte(ser)
			if sensorHeader2 == EXPECTED_SENSOR_HEADER_2:
				sensorName = readByte(ser)
				sensorValue = readByte(ser)
				# Check if sent byte is returned ping
				if sensorName == PING_KEY:
					pingEndTime = clock()
					pingTime = pingEndTime - pingStartTime
					pingStartTime += pingEndTime
				else:
					sensors[sensorName] = sensorValue

# Set up serial communication and cameras, and start data reading thread
# Run this once program begins
def setup(serialPort):
	global ser
	ser = Serial(serialPort)
	if ser == None:
		print "Error: Did not connect"
	cam1 = cv2.VideoCapture(0)
	cam2 = cv2.VideoCapture(1)
	cam1.set(3, IMAGE_SIZE[0])
	cam1.set(4, IMAGE_SIZE[1])
	cam2.set(3, IMAGE_SIZE[0])
	cam2.set(4, IMAGE_SIZE[1])
	start_new_thread(updateData, ())

# Set the motor speeds based on the given speeds
def setMotors(xSpeed, ySpeed, zSpeed, rotation):
	zPow, zDir = setZ(zSpeed)
	clockPow, counterPow = setMotorTranslate(xSpeed, ySpeed)
	clockPow -= 0.5 * rotation
	counterPow += 0.5 * rotation
	clockDir, oppClockDir = setMotorDir(clockPow)
	clockPow = abs(clockPow)
	counterDir, oppCounterDir = setMotorDir(counterPow)
	counterPow = abs(counterPow)
	normClockPow, normCounterPow = normalize(clockPow, counterPow)
	# Write motor values to the Arduino
	ser.write([HEADER_1, HEADER_2, 0, clockPow, clockDir])
	ser.write([HEADER_1, HEADER_2, 1, counterPow, counterDir])
	ser.write([HEADER_1, HEADER_2, 2, clockPow, oppClockDir])
	ser.write([HEADER_1, HEADER_2, 3, counterPow, oppCounterDir])
	ser.write([HEADER_1, HEADER_2, 4, zPow, zDir])
	ser.write([HEADER_1, HEADER_2, 5, zPow, zDir])

def setZ(zSpeed):
	zDir = 0
	# direction: 2 is forward, 1 is backward
	if zSpeed < 0:
		zDir = 1
	else:
		zDir = 2
	zPow = abs(zSpeed) * 255
	return [zPow, zDir]

def setMotorTranslate(xSpeed, ySpeed):
	m1 = .5 * xSpeed + ySpeed / (2 * math.sqrt(3))
	m2 = -.5 * xSpeed + ySpeed / (2 * math.sqrt(3))
	return [m1, m2]

def setMotorDir(power):
	direction = 0
	oppDirection = 0
	if power < 0:
		direction = 1
		oppDirection = 2
	else:
		direction = 2
		oppDirection = 1
	return [direction, oppDirection]

def normalize(clockPow, counterPow):
	normClockPow = 0
	normCounterPow = 0
	if clockPow > 1 and counterPow > 1:
		if clockPow > counterPow:
			normCounterPow = counterPow / clockPow
			normClockPow = 1
		else:
			normClockPow = clockPow / counterPow
			normCounterPow = 1
	elif clockPow > 1:
		normCounterPow = counterPow / clockPow
		normClockPow = 1
	elif counterPow > 1:
		normClockPow = clockPow / counterPow
		normCounterPow = 1
	else:
		normClockPow = clockPow
		normCounterPow = counterPow
	return [normClockPow, normCounterPow]

def moveClaw():
	ser.write([HEADER_1, HEADER_2, PNEUMATIC_KEY, 0, 0])

# Return the latest image from the camera
def getImage():
	ret1, img1 = cam1.read()
	ret2, img2 = cam2.read()
	# Add images to blank image, puts 2 images onto 1 frame
	image[0 : IMAGE_SIZE[0], 0 : IMAGE_SIZE[1]] = image1
	image[0 : IMAGE_SIZE[0], IMAGE_SIZE[1] : IMAGE_SIZE[1] * 2] = image2
	return image

# Release the cameras being used
# Run once program ends
def releaseCamera():
	cam1.release()
	cam2.release()
	cv2.destroyAllWindows()

# Writes a special byte that should trigger the Arduino light
# to turn on. Use to test communication with the Arduino
def testComm():
	# Zeros are garbage data
	ser.write([HEADER_1, HEADER_2, COMM_KEY, 0, 0])

# Writes a special byte that should be returned by the Arduino.
# Use to test ping times to the Arduino
def testPing():
	# Zeros are garbage data
	ser.write([HEADER_1, HEADER_2, PING_KEY, 5, 0])

# Return the last recorded ping time
# -1 if no ping yet
def getPing():
	return pingTime

# Read a byte from serial, and return it.
def readByte(ser):
	return ord(ser.read())