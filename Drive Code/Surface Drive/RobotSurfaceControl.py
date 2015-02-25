import time
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
blank_image = np.zeros((960,1280,3), np.uint8)

while running:
	time.sleep(5)

	e = pygame.event.pump()
	power = joy.get_axis(0)
	running = joy.get_button(0)
	direction = 0
	if (power < 0):
		direction = 2
	else:
		direction = 1
	power = abs(power)
	if power > 255:
		power = 255
	ser.write([0, power, direction])

	ret1, img1 = cam1.read()
	ret2, img2 = cam2.read()
	x_offset = 0
	y_offset = 0
	blank_image[y_offset:y_offset+image1.shape[0], x_offset:x_offset+image1.shape[1]] = image1
	x_offset = image1.shape[1]
	blank_image[y_offset:y_offset+image2.shape[0], x_offset:x_offset+image2.shape[1]] = image2
	
	sensorData = ser.read()

cam1.release()
cam2.release()
cv2.destroyAllWindows()