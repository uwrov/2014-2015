import sys
import RobotSurfaceControl as rc

x = float(sys.argv[1])
y = float(sys.argv[2])
z = float(sys.argv[3])
r = float(sys.argv[4])
rc.setMotors(x, y, z, r)
