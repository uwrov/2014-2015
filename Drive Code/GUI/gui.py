import cv2, math, os
import RobotSurfaceControl as rc
#import os
#os.environ['PYGAME_FREETYPE'] = '1'
import pygame as pg
import numpy




pg.init()

# colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)

PURPLE = (51, 0, 111)
GOLD = (145,123,76)
GREY = (216, 217, 218)

THRESHOLD = 0.15

ADJUSTMENT = 0.05

hasSignal = False

emergency = False

camera_index = 3
camera=cv2.VideoCapture(camera_index)
if(camera.isOpened()):  
    hasSignal = True
    print "Camera connected "

camera.set(3, 480)
camera.set(4, 640)

SCREEN_SIZE = (1180, 520)
CAM_VIEW_SIZE = (320, 180)

x = 0;
y = 0;
z = 0;
speed = 0;
rotation = 0;

x_offset = 0;
y_offset = 0;
z_offset = 0;
rotation_offset = 0;

A_BUTTON = 0
B_BUTTON = 1
X_BUTTON = 2
Y_BUTTON = 3
L_BUTTON = 4
R_BUTTON = 5
BACK_BUTTON = 6
START_BUTTON = 7

font = pg.font.SysFont("encodesansnormalblack",  SCREEN_SIZE[0] / 50)

font_small = pg.font.SysFont("opensanssemibold", SCREEN_SIZE[0] / 50)
#font_small = pg.font.SysFont("opensans", SCREEN_SIZE[0] / 50)


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

def load_image(name):
    path = os.path.join("images", name)
    try:
        image = pg.image.load(path)
    except pg.error, message:
        print "Cannot load image:", path
        raise SystemExit, message
    return image
		
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
        x = joystick.get_axis(0) + x_offset
        y = -joystick.get_axis(1) + y_offset
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

def displayNoSignal(screen):
    pg.draw.rect(screen, BLACK, [SCREEN_SIZE[0] / 40, SCREEN_SIZE[1] / 5, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2])
    text = font.render("No Signal", True, WHITE)
    screen.blit(text, (SCREEN_SIZE[0]/4  - text.get_rect().width/2, SCREEN_SIZE[1]/4 - text.get_rect().height/2))

def setCamDimensions():
    camera.set(3, SCREEN_SIZE[0]/2)
    camera.set(4, SCREEN_SIZE[1]/2)

def blitCamFrame(frame,screen):
    screen.blit(frame,([SCREEN_SIZE[0] / 40, SCREEN_SIZE[1] / 5, SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2]))
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
    text = font.render("Direction", True, BLACK)
    screen.blit(text, (origin_x + radius  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - radius / 4))
    pg.draw.ellipse(screen, BLACK, [origin_x, origin_y, radius * 2, radius * 2], 3)
    normal = pow((pow(x,2) + pow(y,2)), 0.5)
    if (normal > THRESHOLD):
        pg.draw.line(screen, PURPLE, [origin_x + radius, origin_y + radius],
        [x/normal * radius + origin_x + radius, -y/normal * radius + origin_y + radius], 5)
        text = font.render(getStringDir(), True, BLACK)
        screen.blit(text, (origin_x + radius - text.get_rect().width/2, origin_y + radius - text.get_rect().height/2))
    

def drawDepth(screen, origin_x, origin_y, width, height):
    global z
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    text = font.render("Depth", True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - width / 2))
    if (z < 0):
        pg.draw.rect(screen, GOLD, [origin_x, origin_y + height / 2, width, -z * (height / 2)])
    if (z > 0):
        pg.draw.rect(screen, PURPLE, [origin_x, origin_y + height / 2 - (z * height / 2), width , z * height / 2])
    if (z != 0):
        text = font.render(str(int(round(z * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawDirModule(screen, origin_x, origin_y, size):
    global x_offset, y_offset, z_offset, rotation_offset
    drawDirection(screen, origin_x, origin_y, size)
    drawSpeed(screen, origin_x + size * 2.5, origin_y, size / 2, size * 2)
    drawDepth(screen, origin_x + size * 3.5, origin_y, size / 2, size * 3.5)
    drawRotation(screen, origin_x, origin_y + size * 3, size * 3, size / 2)
    drawHorizontalBar(screen, origin_x, origin_y + size * 4.0, size * 2, size / 3, x_offset, "X Offset")
    drawHorizontalBar(screen, origin_x, origin_y + size * 4.75, size * 2, size / 3, y_offset, "Y Offset")
    drawHorizontalBar(screen, origin_x, origin_y + size * 5.5, size * 2, size / 3, z_offset, "Z Offset")
    drawHorizontalBar(screen, origin_x, origin_y + size * 6.25, size * 2, size / 3, rotation_offset, "Rotation Offset")

 
def drawRotation(screen, origin_x, origin_y, width, height):
    global rotation
    text = font.render("Rotation", True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - height / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if(rotation < 0):
        pg.draw.rect(screen, GOLD, [origin_x + width / 2 + rotation * width / 2, origin_y, -rotation * width / 2, height])
    if(rotation > 0):
        pg.draw.rect(screen, PURPLE, [origin_x + width / 2, origin_y, rotation * width / 2, height])
    if (rotation != 0):
        text = font.render(str(int(round(rotation * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawHorizontalBar(screen, origin_x, origin_y, width, height, value, text):
    text = font_small.render(text, True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - height / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if(value < 0):
        pg.draw.rect(screen, GOLD, [origin_x + width / 2 + value * width / 2, origin_y, -value * width / 2, height])
    if(value > 0):
        pg.draw.rect(screen, PURPLE, [origin_x + width / 2, origin_y, value * width / 2, height])
    if (value != 0):
        text = font_small.render(str(int(round(value * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))


def drawSpeed(screen, origin_x, origin_y, width, height):
    global speed, font
    text = font.render("Speed", True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - width / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if (speed != 0):
        pg.draw.rect(screen, PURPLE, [origin_x, origin_y + height - (speed * height), width, speed * height])
        text = font.render(str(int(round(speed * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawGraphics(screen):
    banner = load_image("boundlessband.png").convert()
    size = banner.get_rect().size
    banner = pg.transform.scale(banner, (size[0] * SCREEN_SIZE[0] / 2000 , size[1] * SCREEN_SIZE[0] / 2000))
    screen.blit(banner, (0, 0))


def exectueEmergency(screen):
    pg.draw.rect(screen, RED, [10, 10, SCREEN_SIZE[0]-10, SCREEN_SIZE[1]-10])
    text = font.render("EMERGENCY STOP", True, BLACK)
    screen.blit(text, (SCREEN_SIZE[0]/2  - text.get_rect().width/2, SCREEN_SIZE[1]/2 - text.get_rect().height/2))

def drawConnections(screen, origin_x, origin_y, width, height, value, text):
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    text = font_small.render(text, True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - height / 2))



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
    global joystick, x, y, z, speed, rotation, x_offset, y_offset, z_offset, font, emergency, screen
    global SCREEN_SIZE
    joystick = joy_init()
    screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)
    pg.display.set_caption("Drive GUI")
    
    guiPrint = GuiPrint()
    clock = pg.time.Clock()
	
    done = False
	
    #rc.setup("COM4")
    #cv2.imshow('frame', rc.getImage())


    while not done:
        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                SCREEN_SIZE = event.size
                screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)
                setCamDimensions()
                font = pg.font.SysFont("encodesansnormalblack",  SCREEN_SIZE[0] / 50)
                font_small = pg.font.SysFont(None, SCREEN_SIZE[0] / 50)
            if event.type == pg.JOYHATMOTION:
                coord = event.dict['value']
                if (coord[0] > 0): x_offset += ADJUSTMENT
                if (coord[0] < 0): x_offset -= ADJUSTMENT
                if (coord[1] > 0): y_offset += ADJUSTMENT
                if (coord[1] < 0): y_offset -= ADJUSTMENT
            if event.type == pg.JOYBUTTONDOWN:
                if event.dict['button'] == L_BUTTON:
                    z_offset += ADJUSTMENT
                if event.dict['button'] == R_BUTTON:
                    z_offset -= ADJUSTMENT
                if event.dict['button'] == X_BUTTON:
                    print ""
                if event.dict['button'] == Y_BUTTON:
                    print ""
                #text = font.render(str(event.__dict__), True, BLACK)
                #screen.blit(text, (0,0))

            if event.type == pg.QUIT:
				done = True
        
        if (joystick.get_button(BACK_BUTTON) == True and joystick.get_button(START_BUTTON) == True):
            done = True
            emergency = True
        
        if (emergency == True):
            exectueEmergency(screen)


        # limit to 30 fps
        clock.tick(30)

        guiPrint.reset()
        screen.fill(GREY)
        
        update_values()

        #rc.setMotors(x, y, z, rotation)

        #drawDirection(screen, 850, 150, 100)
        #drawSpeed(screen, 1075, 150, 50, 200)
        #drawDirModule(screen, 700, 100, 100)
        drawGraphics(screen)
        drawDirModule(screen, SCREEN_SIZE[0] / 1.5, SCREEN_SIZE[1] / 10, SCREEN_SIZE[0] / 15)
        #drawDepth(screen, 1050, 100, 50, 350)
        #drawRotation(screen, 700, 400, 300, 50)


        """
        buttons = joystick.get_numbuttons()
 
        for i in range(buttons):
            button = joystick.get_button(i)
            guiPrint.out(screen, "Button {:>2} value: {}".format(i, button))
        """
        if (hasSignal):
            frame=getCamFrame(camera)
            screen=blitCamFrame(frame,screen)
        else:
            displayNoSignal(screen)
        pg.display.flip()

useJoy = False

main()


pg.quit()
