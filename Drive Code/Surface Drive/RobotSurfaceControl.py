import serial
import numpy
import cv2

ser = serial.Serial("COM5")

cam1 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)
cam1.set(3, 480)
cam1.set(4, 640)
cam2.set(3, 480)
cam2.set(4, 640)
image = numpy.zeros((960,1280,3), numpy.uint8)
MOTOR_HEADER_1 = 17
MOTOR_HEADER_2 = 151
EXPECTED_SENSOR_HEADER_1 = 74
EXPECTED_SENSOR_HEADER_1 = 225

# Returns the latest sensor values
def readSensors():
	while ser.inWaiting() >= 4:
		sensorHeader1 = ser.read()
		while sensorHeader1 != EXPECTED_SENSOR_HEADER_1 and ser.inWaiting() >= 3:
			sensorHeader1 = ser.read()
		sensorHeader2 = ser.read()
		if sensorHeader2 == EXPECTED_SENSOR_HEADER_2:
			sensor1 = ser.read()
			sensor2 = ser.read()
	return [sensor1, sensor2]

# Set the motor speeds based on the given directions
def setMotors(xSpeed, ySpeed, zSpeed, rotation):
	return

# Return the latest image from the camera
def getImage():
	ret1, img1 = cam1.read()
	ret2, img2 = cam2.read()
	x_offset = 0
	y_offset = 0
	image[y_offset:y_offset+image1.shape[0], x_offset:x_offset+image1.shape[1]] = image1
	x_offset = image1.shape[1]
	image[y_offset:y_offset+image2.shape[0], x_offset:x_offset+image2.shape[1]] = image2
	return image

# Release the cameras being used
# Run once program ends
def releaseCamera():
	cam1.release()
	cam2.release()
	cv2.destroyAllWindows()