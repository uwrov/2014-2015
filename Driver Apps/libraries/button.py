import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Button:

    def __init__(self, text, (x, y), (width, height), onclick, args, backgroundColor=WHITE, textColor=BLACK,
                 borderColor=BLACK, borderWidth=1):
        self.text = text
        self.shape = pygame.Rect(x, y, width, height)
        self.onclick = onclick
        self.args = args
        self.backgroundColor = backgroundColor
        self.textColor = textColor
        self.borderColor = borderColor
        self.borderWidth = borderWidth
        self.font = pygame.font.Font(None, 32)
        self.locked = False

    def setText(self, text):
        self.text = text

    def setSize(self, (width, height)):
        self.shape.size = (width, height)

    def setPos(self, (x, y)):
        self.shape.topleft = (x, y)

    def setOnclick(self, onclick):
        self.onclick = onclick

    def setFont(self, font):
        self.font = font

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def toggle_lock(self):
        self.locked = not self.locked

    def draw(self, surface):
        pygame.draw.rect(surface, self.backgroundColor, self.shape)
        pygame.draw.rect(surface, self.borderColor, self.shape, self.borderWidth)

        text = self.font.render(self.text, 1, self.textColor)
        surface.blit(text, (self.shape.centerx - text.get_width() / 2, self.shape.centery - text.get_height() / 2))

    def update(self, events):
        if not self.locked:
            for event in events:
                if event.type == MOUSEBUTTONDOWN:
                    if self.shape.collidepoint(event.pos):
                        self.onclick(*self.args)