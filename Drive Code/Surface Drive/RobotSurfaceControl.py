from serial import Serial
import numpy
import cv2
from time import clock, sleep

HEADER_1 = 17
HEADER_2 = 151
EXPECTED_SENSOR_HEADER_1 = 74
EXPECTED_SENSOR_HEADER_2 = 225
sensor1Name = 0
sensor2Name = 1
sensors = {sensor1Name : 0, sensor2Name : 0}

IMAGE_SIZE = [480, 640]
image = numpy.zeros((IMAGE_SIZE[0], IMAGE_SIZE[1] * 2, 3), numpy.uint8)

# Set up serial communication and cameras
# Run once program begins
def setup(serialPort):
	ser = Serial(serialPort)
	cam1 = cv2.VideoCapture(0)
	cam2 = cv2.VideoCapture(1)
	cam1.set(3, IMAGE_SIZE[0])
	cam1.set(4, IMAGE_SIZE[1])
	cam2.set(3, IMAGE_SIZE[0])
	cam2.set(4, IMAGE_SIZE[1])
	clock()

# Return the latest sensor values
def readSensors():
	while ser.inWaiting() >= 4:
		sensorHeader1 = ser.read()
		while sensorHeader1 != EXPECTED_SENSOR_HEADER_1 and ser.inWaiting() >= 3:
			sensorHeader1 = ser.read()
		sensorHeader2 = ser.read()
		if sensorHeader2 == EXPECTED_SENSOR_HEADER_2:
			sensorName = ser.read()
			sensorValue = ser.read()
			sensors[sensorName] = sensorValue
	return [sensors[sensor1Name], sensors[sensor2Name]]

# Set the motor speeds based on the given directions
def setMotors(xSpeed, ySpeed, zSpeed, rotation):
	direction = 0
	if zSpeed < 0:
		direction = 1
	else:
		direction = 2
	zSpeed = abs(zSpeed)
	if zSpeed > 255:
		zSpeed = 255
	ser.write([HEADER_1, HEADER_2, 4, zSpeed, direction])
	ser.write([HEADER_1, HEADER_2, 5, zSpeed, direction])

# Return the latest image from the camera
def getImage():
	ret1, img1 = cam1.read()
	ret2, img2 = cam2.read()
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
# to turn on
def testComm():
	ser.write([HEADER_1, HEADER_2, 101, 0, 0])

# Writes a special byte that should be returned by the Arduino. Returns
# the time it took to receive
def testPing():
	startTime = clock()
	ser.write([HEADER_1, HEADER_2, 102, 0, 0])
	while ser.inWaiting == 0:
		wait(0.001)
	while ser.inWaiting >= 4:
		sensorHeader1 = ser.read()
		while sensorHeader1 != EXPECTED_SENSOR_HEADER_1 and ser.inWaiting >= 3:
			sensorHeader1 = ser.read()
		sensorHeader2 = ser.read()
		if sensorHeader2 == EXPECTED_SENSOR_HEADER_2:
			key = ser.read()
			if key == 102:
				endTime = clock()
				totalTime = endTime - startTime
				return totalTime
	return -1