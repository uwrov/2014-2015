import cv2, math
import RobotSurfaceControl as rc
import pygame as pg
import numpy


pg.init()

# colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)

THRESHOLD = 0.15

camera_index = 0
camera=cv2.VideoCapture(camera_index)
camera.set(3, 480)
camera.set(4, 640)

SCREEN_SIZE = (1180, 520)
CAM_VIEW_SIZE = (320, 180)

x = 0;
y = 0;
z = 0;
speed = 0;
rotation = 0;

font = pg.font.SysFont(None, 20)


class GuiPrint(object):

    def __init__(self):
        self.reset()
        self.x_pos = 50
        self.y_pos = 50
        self.line_height = 15
        self.font = pg.font.Font(None, 20)
 
    def out(self, my_screen, text_string):
        """ Draw text onto the screen. """
        text_bitmap = self.font.render(text_string, True, BLACK)
        my_screen.blit(text_bitmap, [self.x_pos, self.y_pos])
        self.y_pos += self.line_height
		
    def reset(self):
        """ Reset text to the top of the screen. """
        self.x_pos = 700
        self.y_pos = 10
        self.line_height = 15


		
def joy_init():
    """Initializes pygame and the joystick, and returns the joystick to be
    used."""
    

    pg.joystick.init()
    if pg.joystick.get_count() == 0:
        print "joy_init: No joysticks connected"
        useJoy = False
        return
    joystick = pg.joystick.Joystick(0)
    joystick.init()

    return joystick


def update_values():
    global x, y, z, speed, rotation, joystickEnabled
    if pg.joystick.get_count() == 0:
        joystickEnabled = False
        x = float(pg.mouse.get_pos()[0]) / (SCREEN_SIZE[0]/2.0) - 1
        y = 1 - float(pg.mouse.get_pos()[1]) / (SCREEN_SIZE[1]/2.0)
    else:
        joystickEnabled = True
        x = joystick.get_axis(0)
        y = -joystick.get_axis(1)
        z = joystick.get_axis(2)
        rotation = joystick.get_axis(4)
        if (pow((pow(x,2) + pow(y,2)),0.5) < 1):
            speed = pow((pow(x,2) + pow(y,2)),0.5)
        else:
            speed = 1
        keepValuesAtZero()
       

def getCamFrame(camera):
    retval,frame=camera.read()
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    frame=numpy.rot90(frame)
    frame=pg.surfarray.make_surface(frame)
    return frame

def blitCamFrame(frame,screen):
    screen.blit(frame,(10,10))
    return screen

def getStringDir():
    global x, y
    if (x == 0):
        if (y > 0): return "N"
        else: return "S"
    elif (y == 0):
        if (x > 0): return "E"
        else: return "W"
    elif (x < 0):
        if (y > 0): return "NW"
        else: return "SW"
    elif (x > 0):
        if (y > 0): return "NE"
        else: return "SE"


def drawDirection(screen, origin_x, origin_y, radius):
    global x, y
    pg.draw.ellipse(screen, BLACK, [origin_x, origin_y, radius * 2, radius * 2], 5)
    normal = pow((pow(x,2) + pow(y,2)), 0.5)
    if (normal > THRESHOLD):
        pg.draw.line(screen, RED, [origin_x + radius, origin_y + radius], 
        [x/normal * radius + origin_x + radius, -y/normal * radius + origin_y + radius], 5)
        text = font.render(getStringDir(), True, BLACK)
        screen.blit(text, (origin_x + radius - text.get_rect().width/2, origin_y + radius - text.get_rect().height/2))
    

def drawDepth(screen, origin_x, origin_y, width, height):
    global z
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if (z < 0):
        pg.draw.rect(screen, RED, [origin_x, origin_y + height / 2, width, -z * (height / 2)])
    if (z > 0):
        pg.draw.rect(screen,RED, [origin_x, origin_y + height / 2 - (z * height / 2), width , z * height / 2])
    if (z != 0):
        text = font.render(str(int(z * 10)), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawDirModule(screen, origin_x, origin_y, size):
    drawDirection(screen, origin_x, origin_y, size)
    drawSpeed(screen, origin_x + size * 2.5, origin_y, size / 2, size * 2)

def drawRotation(screen, origin_x, origin_y, width, height):
    global rotation
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if(rotation < 0):
        pg.draw.rect(screen, GREEN, [origin_x + width / 2 + rotation * width / 2, origin_y, -rotation * width / 2, height])
    if(rotation > 0):
        pg.draw.rect(screen, GREEN, [origin_x + width / 2, origin_y, rotation * width / 2, height])
    if (rotation != 0):
        text = font.render(str(int(rotation * 10)), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawSpeed(screen, origin_x, origin_y, width, height):
    global speed, font
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 5)
    if (speed != 0):
        pg.draw.rect(screen,RED, [origin_x, origin_y + height - (speed * height), width, speed * height])
        text = font.render(str(int(speed * 10)), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))




def keepValuesAtZero():
    global x, y, z, speed, rotation
    if (abs(x) < THRESHOLD):
        x = 0
    if (abs(y) < THRESHOLD):
        y = 0
    if (abs(z) < THRESHOLD):
        z = 0
    if (abs(speed) < THRESHOLD):
        speed = 0
    if (abs(rotation) < THRESHOLD):
        rotation = 0
  
			
def main():
    global joystick, x, y, z, speed, rotation
    global SCREEN_SIZE
    joystick = joy_init()
    screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)
    pg.display.set_caption("Drive GUI")
    
    guiPrint = GuiPrint()
    clock = pg.time.Clock()
	
    done = False
	
    #rc.setup("")
    #cv2.imshow('frame', rc.getImage())

    while not done:
        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                SCREEN_SIZE = event.size
                screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)
            if event.type == pg.QUIT:
				done = True
            


        # limit to 30 fps
        clock.tick(30)

        guiPrint.reset()
        screen.fill(WHITE)
        
        update_values()
        """
        if joystickEnabled:
            guiPrint.out(screen, "Joystick Enabled")
        else: 
            guiPrint.out(screen, "Joystick Disabled")
       
        guiPrint.out(screen, "X value:{:>6.3f}".format(x))
        guiPrint.out(screen, "Y value:{:>6.3f}".format(y))
        guiPrint.out(screen, "Z value:{:>6.3f}".format(z))
        guiPrint.out(screen, "Speed: {:>6.3f}".format(speed))
        guiPrint.out(screen, "Rotation: {:>6.3f}".format(rotation))
        
        #rc.setMotors(x, y, z, rotation)
        
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[0]))
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[1]))
		"""
        #drawDirection(screen, 850, 150, 100)
        #drawSpeed(screen, 1075, 150, 50, 200)
        drawDirModule(screen, 700, 100, 100)
        drawDepth(screen, 1050, 100, 50, 350)
        drawRotation(screen, 700, 400, 300, 50)
       

        """
        buttons = joystick.get_numbuttons()
 
        for i in range(buttons):
            button = joystick.get_button(i)
            guiPrint.out(screen, "Button {:>2} value: {}".format(i, button))
        """
        frame=getCamFrame(camera)
        screen=blitCamFrame(frame,screen)
        pg.display.flip()

useJoy = False

main()

pg.quit()
