import math, os, string, sys
import cv2
import RobotSurfaceControl as rc
import pygame as pg


pg.init()

# colors
WHITE = (255, 255, 255)
BLACK = (0,0,0)
gray = (90, 90, 90)
red = (255, 0, 0)
light_blue = (100, 150, 255)
dark_blue = (20, 100, 195)

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
        self.x_pos = 10
        self.y_pos = 10
        self.line_height = 15


		
def joy_init():
    """Initializes pygame and the joystick, and returns the joystick to be
    used."""
    
    global use_joy

    pg.joystick.init()
    if pg.joystick.get_count() == 0:
        print "joy_init: No joysticks connected"
        return
    joystick = pg.joystick.Joystick(0)
    joystick.init()

    return joystick
	
	
			
def main():
    global joystick
    joystick = joy_init()
    screen = pg.display.set_mode((200, 300))
    pg.display.set_caption("Drive GUI")
    
    guiPrint = GuiPrint()
    clock = pg.time.Clock()
	
    done = False
	
    rc.setup("COM3")
    #cv2.imshow('frame', rc.getImage())

    while not done:
        for event in pg.event.get():
			if event.type == pg.QUIT:
				done = True
        # limit to 30 fps
        clock.tick(30)

        guiPrint.reset()
        screen.fill(WHITE)
        x = joystick.get_axis(0) 
        y = joystick.get_axis(1)
        speed = joystick.get_axis(3)
        rotation = joystick.get_axis(4)
        guiPrint.out(screen, "X value:{:>6.3f}".format(x))
        guiPrint.out(screen, "Y value:{:>6.3f}".format(y))
        guiPrint.out(screen, "Speed: {:>6.3f}".format(speed))
        guiPrint.out(screen, "Rotation: {:>6.3f}".format(rotation))
        
        #rc.setMotors(x, y, speed, rotation)
        
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[0]))
        guiPrint.out(screen, "Sensor: {}".format(rc.sensors[1]))
		
        buttons = joystick.get_numbuttons()
 
        for i in range(buttons):
            button = joystick.get_button(i)
            guiPrint.out(screen, "Button {:>2} value: {}".format(i, button))

		
        pg.display.flip()


main()

pg.quit()
