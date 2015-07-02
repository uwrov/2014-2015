import pygame as pg
from pygame.locals import *
import math, numpy, os, sys
sys.path.insert(0, 'libraries')
import button
import eztext


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (220, 160, 40)

pg.init()

font = pg.font.SysFont('monospace', 24)


class IncLine:

    TO_START = 0
    TO_FIRST_CLICK = 1
    TO_SECOND_CLICK = 2
    FINISHED = 3

    def __init__(self, color):
        self.start = None
        self.end = None
        self.state = IncLine.TO_START
        self.color = color

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def init(self):
        self.state = IncLine.TO_FIRST_CLICK

    def nextState(self):
        self.state += 1

    def reset(self):
        self.state = IncLine.TO_START

    def setColor(self, color):
        self.color = color

    def click(self, pos):
        if self.state == IncLine.TO_FIRST_CLICK:
            self.start = pos
            self.end = pos
            self.nextState()
        elif self.state == IncLine.TO_SECOND_CLICK:
            self.end = pos
            self.nextState()

    def len(self):
        if self.start != None and self.end != None:
            return math.sqrt((self.start[0]-self.end[0])**2 + (self.start[1]-self.end[1])**2)
        else:
            return 0

    def vec(self):
        if self.start != None and self.end != None:
            return (self.end[0] - self.start[0], self.end[1] - self.start[1])
        else:
            return (0, 0)

    def slope(self):
        v = self.vec()
        if v != (0, 0) and v[0] != 0:
            return v[1] / v[0]
        else:
            return None


following = IncLine(BLACK)
base = IncLine(RED)
var = IncLine(GREEN)

stupidRules = False




screen = pg.display.set_mode((1200, 800), pg.RESIZABLE)
pg.display.set_caption("Length Analysis")

image_base = pg.image.load("ocean.jpg")



def aspect_scale(image, (width, height)):
    sx, sy = image.get_size()
    scale_x = float(width) / sx
    scale_y = float(height) / sy

    if scale_x > scale_y:
        return pg.transform.scale(image, (int(scale_y * sx), height))
    else:
        return pg.transform.scale(image, (width, int(scale_x * sy)))

def drawFollowingLine(screen, events):
    if following.state == IncLine.TO_SECOND_CLICK:
        for event in events:
            if event.type == MOUSEMOTION:
                following.setEnd(event.pos)
        pg.draw.line(screen, following.color, following.start, following.end)

def drawFinishedLines(screen):
    if base.state == IncLine.FINISHED:
        pg.draw.line(screen, base.color, base.start, base.end)
    if var.state == IncLine.FINISHED:
        pg.draw.line(screen, var.color, var.start, var.end)

def getUnknownSize():
    if base.state == IncLine.FINISHED and var.state == IncLine.FINISHED:
        baseLen = base.len()
        varLen = var.len()
        if baseLen != 0 and varLen != 0:
            try:
                baseSize = float(lengthInput.get_text())
                return round(varLen / baseLen * baseSize, 3)
            except (ValueError):
                pass
    return 0

def getAngle():
    if var.state == IncLine.FINISHED:
        varVec = var.vec()
        if varVec != (0, 0):
            angle = math.acos(numpy.dot((1, 0), varVec) / (1 * var.len())) * 180 / math.pi
            return round(min(angle, 180 - angle), 2)
    return -1

def getBase():
    if base.state == IncLine.FINISHED and var.state == IncLine.FINISHED:
        baseLen = base.len()
        varVec = var.vec()
        if varVec != (0, 0):
            if var.start[1] < var.end[1]:
                topPoint = var.start
                bottomPoint = var.end
            else:
                topPoint = var.end
                bottomPoint = var.start
        varLen = abs(topPoint[0] - bottomPoint[0])
        if baseLen != 0 and varLen != 0:
            try:
                baseSize = float(lengthInput.get_text())
                return round(varLen / baseLen * baseSize, 3)
            except (ValueError):
                pass
    return 0

def getHeight():
    if base.state == IncLine.FINISHED and var.state == IncLine.FINISHED:
        baseLen = base.len()
        varVec = var.vec()
        if varVec != (0, 0):
            if var.start[1] < var.end[1]:
                topPoint = var.start
                bottomPoint = var.end
            else:
                topPoint = var.end
                bottomPoint = var.start
        varLen = abs(topPoint[1] - bottomPoint[1])
        if baseLen != 0 and varLen != 0:
            try:
                baseSize = float(lengthInput.get_text())
                return round(varLen / baseLen * baseSize, 3)
            except (ValueError):
                pass
    return 0


def drawStupidRules(screen, image):
    if var.state == IncLine.FINISHED:
        varVec = var.vec()
        if varVec != (0, 0):
            if var.start[1] < var.end[1]:
                topPoint = var.start
                bottomPoint = var.end
            else:
                topPoint = var.end
                bottomPoint = var.start
            pg.draw.line(screen, ORANGE, (topPoint[0], 0), (topPoint[0], image.get_height()))
            pg.draw.line(screen, ORANGE, (0, bottomPoint[1]), (image.get_width(), bottomPoint[1]))







def defineBaseClick():
    base.init()
    following.init()
    following.setColor(base.color)

def defineVarClick():
    var.init()
    following.init()
    following.setColor(var.color)

def loadImageClick():
    global image_base
    try:
        num = imgNum.get_text()
    except (ValueError):
        return

    if os.path.isfile(os.path.join("..", "screenshots", str(num) + ".png")):
        image_base = pg.image.load(os.path.join("..", "screenshots", str(num) + ".png"))

def toggleStupidRules():
    global stupidRules
    stupidRules = not stupidRules

defineBaseButton = button.Button("Define Base", (0, 0), (160, 60), defineBaseClick, [], backgroundColor=RED)
defineVarButton = button.Button("Define Var", (0, 0), (160, 60), defineVarClick, [], backgroundColor=GREEN)
loadImageButton = button.Button("Load Image", (0, 0), (160, 60), loadImageClick, [], backgroundColor=(20,70,220))
stupidRulesButton = button.Button("Overlay", (0, 0), (160, 60), toggleStupidRules, [], backgroundColor=(162,158,20))


lengthInput = eztext.Input(max_length=10, font=font, input_width=140, default_text="length", restricted="0123456789.")
lengthOutput = eztext.Input(max_length=10, font=font, input_width=140)
lengthOutput.lock()
angleOutput = eztext.Input(max_length=10, font=font, input_width=140, default_text="angle")
angleOutput.lock()
imgNum = eztext.Input(max_length=10, font=font, input_width=140, default_text="image num", restricted="0123456789")
baseOutput = eztext.Input(max_length=10, font=font, input_width=140, default_text="base")
baseOutput.lock()
heightOutput = eztext.Input(max_length=10, font=font, input_width=140, default_text="height")
heightOutput.lock()


done = False
while not done:
    events = pg.event.get()
    for event in events:
        if event.type == MOUSEBUTTONDOWN:
            following.click(event.pos)
            base.click(event.pos)
            var.click(event.pos)
        if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode(event.size, pg.RESIZABLE)
        if event.type == pg.QUIT:
            done = True

    image = aspect_scale(image_base, numpy.subtract(screen.get_size(), (200, 0)))
    screen.fill(WHITE)
    screen.blit(image, (0, 0))

    defineBaseButton.setPos((screen.get_width() - 180, 20))
    defineBaseButton.update(events)
    defineBaseButton.draw(screen)

    defineVarButton.setPos((screen.get_width() - 180, 100))
    defineVarButton.update(events)
    defineVarButton.draw(screen)

    lengthInput.set_pos(screen.get_width() - 180, 180)
    lengthInput.update(events)
    lengthInput.draw(screen)

    lengthOutput.set_pos(screen.get_width() - 180, 220)
    lengthOutput.update(events)
    lengthOutput.draw(screen)

    angleOutput.set_pos(screen.get_width() - 180, 260)
    angleOutput.update(events)
    angleOutput.draw(screen)

    imgNum.set_pos(screen.get_width() - 180, 340)
    imgNum.update(events)
    imgNum.draw(screen)

    loadImageButton.setPos((screen.get_width() - 180, 380))
    loadImageButton.update(events)
    loadImageButton.draw(screen)

    stupidRulesButton.setPos((screen.get_width() - 180, 460))
    stupidRulesButton.update(events)
    stupidRulesButton.draw(screen)

    baseOutput.set_pos(screen.get_width() - 180, 540)
    baseOutput.update(events)
    baseOutput.draw(screen)

    heightOutput.set_pos(screen.get_width() - 180, 580)
    heightOutput.update(events)
    heightOutput.draw(screen)

    drawFollowingLine(screen, events)
    drawFinishedLines(screen)

    usize = getUnknownSize()
    if usize > 0:
        lengthOutput.set_text(str(usize))
    else:
        lengthOutput.set_text("")

    angle = getAngle()
    if angle != -1:
        angleOutput.set_text(str(angle) + " deg")
    else:
        angleOutput.set_text("")

    wbase = getBase()
    if wbase != 0:
        baseOutput.set_text("b: " + str(wbase))
    else:
        baseOutput.set_text("")

    height = getHeight()
    if height != 0:
        heightOutput.set_text("h: " + str(height))
    else:
        heightOutput.set_text("")

    if stupidRules:
        drawStupidRules(screen, image)

    pg.display.flip()
