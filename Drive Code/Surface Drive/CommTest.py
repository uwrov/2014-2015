from time import sleep
import thread
import RobotSurfaceControl as rsc

ping = -1

rsc.setup("COM3")
while True:
	raw_input()
	rsc.testComm()
	print rsc.readSensors()
	rsc.testPing()
	raw_input()
	ping = rsc.getPing()
	print ping
