import math
import numpy
import cv2
from serial import Serial
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

WAIT_TIME = 0.1

# Sensor values received from Arduino
sensor1Name = 0
sensor2Name = 1
sensors = {sensor1Name : 0, sensor2Name : 0}

# Motor values sent to Arduino
# Stores values between -100 and 100
motors = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

ROTATION_SCALE = 0.5
MOTOR_REST_POSITION = 1475
MOTOR_VARIATION = 400
DISPLAY_SCALE = 4

# Image
IMAGE_SIZE = [480, 640]
image = numpy.zeros((IMAGE_SIZE[0] * 2, IMAGE_SIZE[1], 3), numpy.uint8)

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
# Returns 1 if an error occured during serial connection, 0 otherwise
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

	start_new_thread(__updateData__, ())
	return 0


# Updates the sensor data and ping time from the Arduino. Runs on
# a separate thread after setup runs
def __updateData__():
	global motors
	global sensors
	global pingTime
	global pingStartTime

	while True:
		sleep(WAIT_TIME)
		
		# Calculate motor/direction values for Arduino
		frontLeftPow = motors[1] * DISPLAY_SCALE + MOTOR_REST_POSITION
		frontRightPow = motors[2] * DISPLAY_SCALE + MOTOR_REST_POSITION
		backRightPow = motors[3] * DISPLAY_SCALE + MOTOR_REST_POSITION
		backLeftPow = motors[4] * DISPLAY_SCALE + MOTOR_REST_POSITION
		zFrontPow = motors[5] * DISPLAY_SCALE + MOTOR_REST_POSITION
		zBackPow = motors[6] * DISPLAY_SCALE + MOTOR_REST_POSITION

		# Write motor values to the Arduino
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 0,
			frontLeftPow, 0])
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 1,
			frontRightPow, 0])
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 2,
			backRightPow, 0])
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 3,
			backLeftPow, 0])
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 4,
			zFrontPow, 0])
		ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2, 5,
			zBackPow, 0])

		# Check for new packets from Arduino
		# Packets should be received in sets of 4
		while ser.inWaiting() >= 4:
			if __readByte__(ser) == HEADER_KEY_IN_1 and __readByte__(ser) == HEADER_KEY_IN_2:
				sensorName = __readByte__(ser)
				sensorValue = __readByte__(ser)
				# Check if sent packet is returned ping
				if sensorName == HEADER_KEY_PING:
					pingEndTime = clock()
					pingTime = pingEndTime - pingStartTime
				else:
					sensors[sensorName] = sensorValue


# Set the motor speeds based on the given joystick values
# Joystick values range between -1 and 1
def setMotors(xSpeed, ySpeed, zSpeed, rotation):
	global motors

	__setZ__(zSpeed)
	__setMotorTranslate__(xSpeed, ySpeed)
	__setMotorRotation__(rotation)

	print motors


# Set the speed of the z direction (up/down) motors
def __setZ__(zSpeed):
	global motors

	zPow = int(zSpeed * MOTOR_VARIATION / DISPLAY_SCALE)
	motors[5] = zPow
	motors[6] = zPow


# Set the speed of the x/y direction (up/down/left/right) motors
def __setMotorTranslate__(xSpeed, ySpeed):
	# Translate x/y coordinate values to motor coordinate values
	m1 = .5 * xSpeed + ySpeed / (2 * math.sqrt(3))
	m2 = -.5 * xSpeed + ySpeed / (2 * math.sqrt(3))

	# Don't normalize values if both are 0
	if m1 == 0 and m2 == 0:
		motors[1] = motors[2] = motors[3] = motors[4] = 0
	else:
		m1_norm = m1 / abs(max(m1, m2)) * min(math.hypot(xSpeed, ySpeed), 1)
		m2_norm = m2 / abs(max(m1, m2)) *  min(math.hypot(xSpeed, ySpeed), 1)
		motors[1] = -m1_norm
		motors[2] = -m2_norm
		motors[3] = m1_norm
		motors[4] = m2_norm


# Add the speed of rotation to the motor speeds
def __setMotorRotation__(rotation):
	frontLeftPow = motors[1] - ROTATION_SCALE * rotation
	frontRightPow = motors[2] + ROTATION_SCALE * rotation
	backRightPow = motors[3] - ROTATION_SCALE * rotation
	backLeftPow = motors[4] + ROTATION_SCALE * rotation

	# Normalize the values if greater than 1
	maxPow = max(abs(frontLeftPow), abs(frontRightPow),
		abs(backRightPow), abs(backLeftPow))
	if maxPow > 1:
		frontLeftPow /= maxPow
		frontRightPow /= maxPow
		backRightPow /= maxPow
		backLeftPow /= maxPow

	motors[1] = int(frontLeftPow * MOTOR_VARIATION / DISPLAY_SCALE)
	motors[2] = int(frontRightPow * MOTOR_VARIATION / DISPLAY_SCALE)
	motors[3] = int(backRightPow * MOTOR_VARIATION / DISPLAY_SCALE)
	motors[4] = int(backLeftPow * MOTOR_VARIATION / DISPLAY_SCALE)


# Return the latest image from the camera
def getImage():
	ret1, img1 = cam1.read()
	ret2, img2 = cam2.read()

	# Add images to blank image, puts 2 images onto 1 frame
	image[0 : IMAGE_SIZE[0], 0 : IMAGE_SIZE[1]] = image1
	image[IMAGE_SIZE[0] : IMAGE_SIZE[0] * 2, 0 : IMAGE_SIZE[1]] = image2
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
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2,
		HEADER_KEY_PNEUMATICS, 0, 0])


# Writes a special byte that should trigger the Arduino light
# to turn on. Use to test communication with the Arduino
def testComm():
	# Zeros are garbage data
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2,
		HEADER_KEY_LIGHT, 0, 0])


# Writes a special byte that should be returned by the Arduino.
# Use to test ping times to the Arduino
def testPing():
	global pingStartTime

	pingStartTime = clock()
	# Zeros are garbage data
	ser.write([HEADER_KEY_OUT_1, HEADER_KEY_OUT_2,
		HEADER_KEY_PING, 0, 0])


# Return the last recorded ping time
# -1 if no ping recorded yet
def getPing():
	return pingTime


# Read a byte from serial, and return the value.
def __readByte__(ser):
	return ord(ser.read())