import cv2, math, os, sys
sys.path.insert(0, '../Surface Drive')
sys.path.insert(0, '../libraries')

import RobotSurfaceControl as rc
import pygame as pg
from pygame.locals import *
import numpy
import eztext

pg.init()



# colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)
GREEN    = (   0, 200,   0)
YELLOW   = ( 200, 200,   0)
RED      = ( 255,   0,   0)

PURPLE = (51, 0, 111)
GOLD = (145,123,76)
GREY = (216, 217, 218)
DARK_GREY = (153, 153, 153)

THRESHOLD = 0.15

ADJUSTMENT = 0.05

SCREEN_SIZE = (1280, 720)
DISPLAY_SIZE = (1280, 720)



### BUTTON DEFINITIONS ###

# A_BUTTON = 0
A_BUTTON = 11
B_BUTTON = 1
X_BUTTON = 2
# Y_BUTTON = 3
Y_BUTTON = 14
L_BUTTON = 4
R_BUTTON = 5
BACK_BUTTON = 6
START_BUTTON = 7


hasSignal = 0
numCams = 0
joyConnected = 0


x = 0;
y = 0;
z = 0;
speed = 0;
rotation = 0;

z_offset = 0;

joystickConnectButton = pg.Rect(0, 0, 0, 0)
arduinoConnectButton = pg.Rect(0, 0, 0, 0)
cameraConnectButton = pg.Rect(0, 0, 0, 0)



font = pg.font.SysFont("encodesansnormalblack",  DISPLAY_SIZE[0] / 60)

font_small = pg.font.SysFont("opensanssemibold", DISPLAY_SIZE[0] / 60)
font_panel = pg.font.SysFont("calibri", DISPLAY_SIZE[0] / 60)


# gets the size of the largest 19:9 rectangle that fits in the current window
def getEffectiveSize(current_size):
    multiplier = min(int(current_size[0] / 16), int(current_size[1] / 9))
    return (multiplier * 16, multiplier * 9)


# loads an image from file
def loadImage(name):
    path = os.path.join("images", name)
    try:
        image = pg.image.load(path)
    except pg.error, message:
        print "Cannot load image:", path
        raise SystemExit, message
    return image


# initializes pygame joysticks, and attempts to connect to the first joystick found. Sets
# joyConnected appropriately and returns the joystick to use
def joyInit():
    global joyConnected
    
    pg.joystick.quit()
    pg.joystick.init()
    if pg.joystick.get_count() == 0:
        print "joyInit: No joysticks connected"
        joyConnected = 0
    else:
        joyConnected = 1
        joystick = pg.joystick.Joystick(0)
        joystick.init()
        return joystick


# updates the global joystick values
def updateValues():
    global x, y, z, speed, rotation

    x = joystick.get_axis(0)
    y = -joystick.get_axis(1)
    z_value = joystick.get_axis(2)
    z_faster = 1 - z_offset
    z_slower = z_offset + 1
    if z_value > 0:
        z = z_value * z_faster + z_offset
    else:
        z = z_value * z_slower + z_offset
    z = max(min(z, 1), -1)
    rotation = joystick.get_axis(4)
    if x**2 + y**2 < 1:
        speed = pow(x**2 + y**2,0.5)
    else:
        speed = 1
    snapToZero()


# snaps small values to 0 to compensate for controller misalignment
def snapToZero():
    global x, y, z, speed, rotation

    if x**2 + y**2 < THRESHOLD**2:
        x = 0
        y = 0
    if abs(z - z_offset) < THRESHOLD:
        z = z_offset
    if abs(speed) < THRESHOLD:
        speed = 0
    if abs(rotation) < THRESHOLD:
        rotation = 0

# constrains value to the range [a, b]
def keepInRange(value, a, b):
    if value < a:
        return a
    if value > b:
        return b
    return value
       

# draw the no signal screen
def displayNoSignal(screen):
    pg.draw.rect(screen, BLACK, (DISPLAY_SIZE[0] / 40, DISPLAY_SIZE[1] / 5, DISPLAY_SIZE[0] * .67, DISPLAY_SIZE[1] * .67))
    text = font.render("No Signal", True, WHITE)
    screen.blit(text, (DISPLAY_SIZE[0] / 40 + DISPLAY_SIZE[0] / 3 - text.get_rect().width / 2, DISPLAY_SIZE[1] / 4 - text.get_rect().height / 2))


# displays the camera image on the screen
def blitCamFrame(frame, screen):
    screen.blit(frame,((DISPLAY_SIZE[0] / 10, DISPLAY_SIZE[1] / 5, DISPLAY_SIZE[0] * .67, DISPLAY_SIZE[1] * .67)))
    return screen

# draws the current direction of movement
def drawDirection(screen, origin_x, origin_y, radius):
    global x, y

    text = font.render("Horizontal vector", True, BLACK)
    screen.blit(text, (origin_x + radius  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - radius / 4))
    pg.draw.ellipse(screen, BLACK, [origin_x, origin_y, radius * 2, radius * 2], 3)
    normal = pow(x**2 + y**2, 0.5)
    if normal > 0:
        pg.draw.line(screen, GOLD, [origin_x + radius, origin_y + radius],
        [x/normal * radius + origin_x + radius, -y/normal * radius + origin_y + radius], 5)
    

def drawDepth(screen, origin_x, origin_y, width, height):
    global z
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    text = font.render("Depth", True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - width / 2))
    if (z < 0):
        pg.draw.rect(screen, GOLD, [origin_x, origin_y + height / 2 - (-z * height / 2), width , -z * height / 2])
    if (z > 0):
        pg.draw.rect(screen, PURPLE, [origin_x, origin_y + height / 2, width, z * (height / 2)])
    if (z != 0):
        text = font.render(str(int(round(-z * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

def drawDirModule(screen, origin_x, origin_y, size):
    drawDirection(screen, origin_x, origin_y, size)
    drawSpeed(screen, origin_x + size * 2.5, origin_y, size / 2, size * 2)
    drawVerticalBar(screen, origin_x + size * 2.5, origin_y + size * 2.5, size / 2, size * 2, z, "Vertical vector")

def drawInputs(screen):
    global joystickConnectButton, arduinoConnectButton, cameraConnectButton

    local_x_origin = DISPLAY_SIZE[0] / 40
    local_y_origin = DISPLAY_SIZE[1] - DISPLAY_SIZE[1] / 10
    local_width = DISPLAY_SIZE[0] / 8
    local_height = DISPLAY_SIZE[1] / 12
    drawConnections(screen, local_x_origin, local_y_origin, local_width, local_height, joyConnected, 1, "Joystick")
    drawConnections(screen, local_x_origin + local_width  * 1.5, local_y_origin, local_width, local_height, hasSignal, 1, "Arduino")
    drawConnections(screen, local_x_origin + local_width  * 3, local_y_origin, local_width, local_height, numCams, 2, "Camera")
    joystickConnectButton = pg.Rect(local_x_origin, local_y_origin, local_width, local_height)
    arduinoConnectButton = pg.Rect(local_x_origin + local_width  * 1.5, local_y_origin, local_width, local_height)
    cameraConnectButton = pg.Rect(local_x_origin + local_width  * 3, local_y_origin, local_width, local_height)


 
def drawRotation(screen, origin_x, origin_y, width, height):
    global rotation
    text = font.render("Rotation", True, BLACK)
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - height / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)
    if(rotation < 0):
        pg.draw.rect(screen, PURPLE, [origin_x + width / 2 + rotation * width / 2, origin_y, -rotation * width / 2, height])
    if(rotation > 0):
        pg.draw.rect(screen, GOLD, [origin_x + width / 2, origin_y, rotation * width / 2, height])
    if (rotation != 0):
        text = font.render(str(int(round(rotation * 10))), True, BLACK)
        screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))


# value in [-1, 1]
def drawHorizontalBar(screen, origin_x, origin_y, width, height, value, text):
    text = font_small.render(text, True, BLACK)
    value = round(value, 2)
    if value == 0: # prevent it from displaying -0.0
        value = 0
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - height / 2))
    pg.draw.rect(screen, BLACK, [origin_x - 2, origin_y, width + 4, height], 2)
    if(value < 0):
        pg.draw.rect(screen, PURPLE, [origin_x + width / 2 + value * width / 2, origin_y + 2, -value * width / 2, height - 3])
    if(value > 0):
        pg.draw.rect(screen, GOLD, [origin_x + width / 2, origin_y + 2, value * width / 2, height - 3])

    text = font_small.render(str(round(value * 10, 1)), True, BLACK)
    screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))

# value in [-1, 1]
def drawVerticalBar(screen, origin_x, origin_y, width, height, value, text):
    text = font.render(text, True, BLACK)
    value = round(value, 2)
    if value == 0: # prevent it from displaying -0.0
        value = 0
    screen.blit(text, (origin_x + width/2  - text.get_rect().width/2, origin_y - text.get_rect().height/2 - width / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y - 2, width, height + 4], 2)
    if(value < 0):
        pg.draw.rect(screen, PURPLE, [origin_x + 2, origin_y + height / 2 - value * height / 2, width - 3, value * height / 2])
    if(value > 0):
        pg.draw.rect(screen, GOLD, [origin_x + 2, origin_y + height / 2 - value * height / 2, width - 3, value * height / 2])

    text = font.render(str(round(value * 10, 1)), True, BLACK)
    screen.blit(text, (origin_x + width / 2 - text.get_rect().width/2, origin_y + height / 2 - text.get_rect().height/2))


def drawSpeed(screen, origin_x, origin_y, width, height):
    text = font.render("Speed", True, BLACK)
    screen.blit(text, (origin_x + width / 2  - text.get_rect().width / 2, origin_y - text.get_rect().height / 2 - width / 2))
    pg.draw.rect(screen, BLACK, [origin_x, origin_y - 2, width, height + 2], 2)

    if speed != 0:
        pg.draw.rect(screen, GOLD, [origin_x + 2, origin_y + height - (speed * height), width - 3, speed * height])
    text = font.render(str(round(speed * 10, 1)), True, BLACK)
    screen.blit(text, (origin_x + width / 2 - text.get_rect().width / 2, origin_y + height / 2 - text.get_rect().height / 2))

def drawGraphics(screen):
    banner = loadImage("uwrovlogo.png").convert()
    size = banner.get_rect().size
    banner = pg.transform.scale(banner, (size[0] * DISPLAY_SIZE[0] / 3000 , size[1] * DISPLAY_SIZE[0] / 3000))
    screen.blit(banner, (0, 0))


def exectueEmergency(screen):
    pg.draw.rect(screen, RED, [10, 10, DISPLAY_SIZE[0] - 10, DISPLAY_SIZE[1] - 10])
    text = font.render("EMERGENCY STOP", True, BLACK)
    screen.blit(text, (DISPLAY_SIZE[0] / 2  - text.get_rect().width / 2, DISPLAY_SIZE[1] / 2 - text.get_rect().height / 2))

def drawConnections(screen, origin_x, origin_y, width, height, value, max_value, text):
    pg.draw.rect(screen, BLACK, [origin_x, origin_y, width, height], 2)

    percent = 100 * value / max_value
    if percent == 0:
        color = DARK_GREY
    elif percent <= 50:
        color = YELLOW
    else:
        color = GREEN

    pg.draw.ellipse(screen, color, [origin_x + width - width / 3, origin_y + height / 8, height * 0.75,  height * 0.75])
    text = font_panel.render(text, True, BLACK)
    screen.blit(text, (origin_x + width / 16, origin_y + height / 2 - text.get_rect().height / 2))



def getSerialPorts():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        print "Unsupported platform"
        return []

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

  
            
def main():
    global joystick, x, y, z, speed, rotation, z_offset, font, screen
    global hasSignal, numCams
    global DISPLAY_SIZE, SCREEN_SIZE

    screen = pg.display.set_mode(DISPLAY_SIZE, pg.RESIZABLE)
    pg.display.set_caption("Drive GUI")

    joystick = joyInit()
    numCams = rc.cameraSetup()

    port_input = eztext.Input(max_length=40, font=pg.font.SysFont('monospace', 24), input_width=560, default_text="port name")
    cam1_input = eztext.Input(max_length=2, font=pg.font.SysFont('monospace', 24), input_width=28, default_text="C1", restricted="0123456789")
    cam2_input = eztext.Input(max_length=2, font=pg.font.SysFont('monospace', 24), input_width=28, default_text="C2", restricted="0123456789")
    
    clock = pg.time.Clock()
    
    done = False
    emergency = False
    camView = 1
    saveNextImage = False
    imageNum = 0

    while not done:

        events = pg.event.get()

        # process events
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if joyConnected == 0 and joystickConnectButton.collidepoint(event.pos): # click the joystick connect
                    print "attempting joystick connect"
                    joystick = joyInit()
                elif hasSignal == 0 and arduinoConnectButton.collidepoint(event.pos): # click the arduino connect
                    hasSignal = rc.arduinoSetup(port_input.get_text())
                    if hasSignal != 0:
                        port_input.lock()
                elif cameraConnectButton.collidepoint(event.pos): # click the camera connect
                    numCams = rc.cameraSetup(cam1_input.get_text(), cam2_input.get_text())
            elif event.type == pg.VIDEORESIZE:
                DISPLAY_SIZE = getEffectiveSize(event.size)
                SCREEN_SIZE = event.size
                screen = pg.display.set_mode(SCREEN_SIZE, pg.RESIZABLE)
                font = pg.font.SysFont("encodesansnormalblack",  DISPLAY_SIZE[0] / 50)
                font_small = pg.font.SysFont(None, DISPLAY_SIZE[0] / 50)
            elif joyConnected != 0:
                if event.type == pg.JOYBUTTONDOWN:
                    if event.dict['button'] == X_BUTTON:
                        camView = 3 - camView
                    elif event.dict['button'] == B_BUTTON:
                        print "B pressed"
                    elif event.dict['button'] == Y_BUTTON:
                        z_offset += ADJUSTMENT
                        z_offset = keepInRange(z_offset, -1, 1)
                    elif event.dict['button'] == A_BUTTON:
                        z_offset -= ADJUSTMENT
                        z_offset = keepInRange(z_offset, -1, 1)
                    elif event.dict['button'] == START_BUTTON:
                        saveNextImage = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    saveNextImage = True

            if event.type == pg.QUIT:
                done = True
        
        """
        if (joystick.get_button(BACK_BUTTON) and joystick.get_button(START_BUTTON)):
            done = True 
            emergency = True
        """
        
        if (emergency == True):
            exectueEmergency(screen)



        if joyConnected != 0:
            updateValues()
        rc.setMotors(x, y, z, rotation) 

        screen.fill(GREY)
        drawGraphics(screen)
        drawDirModule(screen, int(DISPLAY_SIZE[0] * .75), int(DISPLAY_SIZE[1] / 9), int(DISPLAY_SIZE[0] / 16))
        drawInputs(screen)

        port_input.set_pos(DISPLAY_SIZE[0] / 40 + DISPLAY_SIZE[0] / 8 * 4.5, DISPLAY_SIZE[1] * .9)
        port_input.update(events)
        port_input.draw(screen)

        cam1_input.set_pos(DISPLAY_SIZE[0] / 40 + DISPLAY_SIZE[0] / 8 * 4.5, DISPLAY_SIZE[1] * .95)
        cam1_input.update(events)
        cam1_input.draw(screen)

        cam2_input.set_pos(DISPLAY_SIZE[0] / 40 + DISPLAY_SIZE[0] / 8 * 4.5 + 100, DISPLAY_SIZE[1] * .95)
        cam2_input.update(events)
        cam2_input.draw(screen)

        
        if numCams != 0:
            frame = rc.getImage(camView)

            if frame == None:
                displayNoSignal(screen)
            else:
                frame = pg.surfarray.make_surface(frame)
                screen = blitCamFrame(frame, screen)

                if saveNextImage:
                    out = pg.surfarray.array3d(frame)
                    out = numpy.rot90(out)
                    out = out[::-1, :,]
                    out[:,:,[0,2]] = out[:,:,[2, 0]]
                    while os.path.isfile(os.path.join("..", "..", "screenshots", str(imageNum) + ".png")):
                        imageNum += 1
                    cv2.imwrite(os.path.join("..", "..", "screenshots", str(imageNum) + ".png"), out)
                    saveNextImage = False
        else:
            displayNoSignal(screen)

        pg.display.flip()

        # limit to 30 fps
        clock.tick(30)


main()

rc.close()
pg.quit()
