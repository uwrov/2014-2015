from serial import Serial
ser = Serial("COM4")
while True:
	bit = input("Bit to send?: ")
	print "Sending..."
	ser.write(bit)
	print "Bit Sent."
	print "Bits in waiting: " + str(ser.inWaiting())
	while ser.inWaiting() != 0:
		print ord(ser.read()),