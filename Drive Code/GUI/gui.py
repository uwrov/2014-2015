import cv2
import RobotSurfaceControl as rc
import pygame as pg
import numpy


pg.init()

# colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)

camera_index = 0
camera=cv2.VideoCapture(camera_index)

SCREEN_SIZE = (1080, 520)
CAM_VIEW_SIZE = (320, 180)

x = 0;
y = 0;
speed = 0;
rotation = 0;


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
    global x, y, speed, rotation, joystickEnabled
    if pg.joystick.get_count() == 0:
        joystickEnabled = False
        x = (pg.mouse.get_pos()[0] - SCREEN_SIZE[0]/2.0) / (SCREEN_SIZE[0] / 2.0)
        y = -((-(pg.mouse.get_pos()[1] - SCREEN_SIZE[1])/2.0) / (SCREEN_SIZE[1] / 2.0))
    else:
        joystickEnabled = True
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        speed = joystick.get_axis(2)
        rotation = joystick.get_axis(3)
       

def getCamFrame(camera):
    retval,frame=camera.read()
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    frame=numpy.rot90(frame)
    frame=pg.surfarray.make_surface(frame)
    return frame

def blitCamFrame(frame,screen):
    screen.blit(frame,(10,10))
    return screen
			
def main():
    global joystick
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

        if joystickEnabled:
            guiPrint.out(screen, "Joystick Enabled")
        else: 
            guiPrint.out(screen, "Joystick Disabled")
       
        guiPrint.out(screen, "X value:{:>6.3f}".format(x))
        guiPrint.out(screen, "Y value:{:>6.3f}".format(y))
        guiPrint.out(screen, "Speed: {:>6.3f}".format(speed))
        guiPrint.out(screen, "Rotation: {:>6.3f}".format(rotation))
        
        #rc.setMotors(x, y, speed, rotation)
        
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[0]))
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[1]))
		
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
