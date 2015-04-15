from serial import Serial
import numpy
import math
import cv2
from time import clock, sleep
from thread import start_new_thread

# Data Headers
HEADER_KEY_OUT_1 = 17
HEADER_KEY_OUT_2 = 151
HEADER_KEY_IN_1 = 74
HEADER_KEY_IN_2 = 225
HEADER_KEY_PNEUMATICS = 100
HEADER_KEY_LIGHT = 101
HEADER_KEY_PING = 102
HEADER_KEY_HOLD_ON = 103
HEADER_KEY_HOLD_OFF = 104

# Communication
ser = None
pingTime = -1
pingStartTime = 0

# Sensor values received from Arduino
sensor1Name = 0
sensor2Name = 1
sensors = {sensor1Name : 0, sensor2Name : 0}

# Motor values sent to Arduino
# Takes values between -255 and 255
motors = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

FORWARD = 3
BACKWARD = 2
ROTATION_SCALE = 0.5

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


# Set up serial communication and cameras, and start data reading thread
# Run this once program begins
# Returns 1 if an error occured during connect, 0 otherwise
def setup(serialPort):
	global ser

	ser = Serial(serialPort)
	if ser == None:
		print "Error: Did not connect"
		return 1

	cam1 = cv2.VideoCapture(0)
	cam2 = cv2.VideoCapture(1)
	cam1.set(3, IMAGE_SIZE[0])
	cam1.set(4, IMAGE_SIZE[1])
	cam2.set(3, IMAGE_SIZE[0])
	cam2.set(4, IMAGE_SIZE[1])

	start_new_thread(updateData, ())
	return 0


# Updates the sensor data and ping time from the Arduino. Runs on
# a separate thread after setup runs
def updateData():
	global sensors
	global pingTime
	global pingStartTime

	while True:
		sleep(0.1)

		# Write motor values to the Arduino
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 0, normClockPow, clockDir])
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 1, normCounterPow, counterDir])
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 2, normClockPow, oppClockDir])
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 3, normCounterPow, oppCounterDir])
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 4, zPow, zDir])
		# ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 5, zPow, zDir])

		# Packets should be received in sets of 4
		while ser.inWaiting() >= 4:
			sensorHeader1 = readByte(ser)
			while sensorHeader1 != HEADER_KEY_IN_1:
				sensorHeader1 = readByte(ser)

			sensorHeader2 = readByte(ser)
			if sensorHeader2 == HEADER_KEY_IN_2:
				sensorName = readByte(ser)
				sensorValue = readByte(ser)
				# Check if sent byte is returned ping
				if sensorName == HEADER_KEY_PING:
					pingEndTime = clock()
					pingTime = pingEndTime - pingStartTime
				else:
					sensors[sensorName] = sensorValue


# Set the motor speeds based on the given joystick values
# Joystick values range between -1 and 1
def setMotors(xSpeed, ySpeed, zSpeed, rotation):
	global motors

	setZ(zSpeed)
	setMotorTranslate(xSpeed, ySpeed)
	setMotorRotation(rotation)

	print motors


def setZ(zSpeed):
	global motors

	zPow = int(zSpeed * 255)
	motors[5] = zPow
	motors[6] = zPow


def setMotorTranslate(xSpeed, ySpeed):
	m1 = .5 * xSpeed + ySpeed / (2 * math.sqrt(3))
	m2 = -.5 * xSpeed + ySpeed / (2 * math.sqrt(3))

	if m1 == 0 and m2 == 0:
		motors[1] = motors[2] = motors[3] = motors[4] = 0
	else:
		m1_norm = m1 / abs(max(m1, m2)) * min(math.hypot(xSpeed, ySpeed), 1)
		m2_norm = m2 / abs(max(m1, m2)) *  min(math.hypot(xSpeed, ySpeed), 1)
		motors[1] = m1_norm
		motors[2] = m2_norm
		motors[3] = -m1_norm
		motors[4] = -m2_norm


def setMotorRotation(rotation):
	frontLeftPow = motors[1] + ROTATION_SCALE * rotation
	frontRightPow = motors[2] - ROTATION_SCALE * rotation
	backRightPow = motors[3] + ROTATION_SCALE * rotation
	backLeftPow = motors[4] - ROTATION_SCALE * rotation

	maxPow = max(frontLeftPow, frontRightPow, backRightPow, backLeftPow)
	if maxPow > 255:
		frontLeftPow /= maxPow
		frontRightPow /= maxPow
		backRightPow /= maxPow
		backLeftPow /= maxPow

	motors[1] = int(frontLeftPow * 255)
	motors[2] = int(frontRightPow * 255)
	motors[3] = int(backRightPow * 255)
	motors[4] = int(backLeftPow * 255)


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


# Change the state of the claw
# Switches between open and closed
def moveClaw():
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, HEADER_KEY_PNEUMATICS, 0, 0])


# Writes a special byte that should trigger the Arduino light
# to turn on. Use to test communication with the Arduino
def testComm():
	# Zeros are garbage data
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, HEADER_KEY_LIGHT, 0, 0])


# Writes a special byte that should be returned by the Arduino.
# Use to test ping times to the Arduino
def testPing():
	global pingStartTime

	pingStartTime = clock()
	# Zeros are garbage data
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, HEADER_KEY_PING, 0, 0])


# Return the last recorded ping time
# -1 if no ping yet
def getPing():
	return pingTime


# Read a byte from serial, and return it.
def readByte(ser):
	return ord(ser.read())