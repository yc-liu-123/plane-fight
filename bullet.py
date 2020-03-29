import pygame
from pygame.locals import *

bullet1_image = '.\\images\\bullet1.png'
bullet2_image = '.\\images\\bullet2.png'

class bullet1(object):
    damage = 30
    velocity = 200
    hit = False
    def __init__(self, initial_position):
        self.position = initial_position
        self.image = pygame.image.load(bullet1_image).convert_alpha()

    def process(self, time):
        x, y = self.position
        new_y = y - self.velocity * time
        self.position = (x, new_y)

    def render(self, surface):
        if not self.hit:
            x, y = self.position
            w, h = self.image.get_size()
            blit_x, blit_y = x-w/2, y
            surface.blit(self.image, (blit_x, blit_y))

class bullet2_single(bullet1):
    velocity = 250
    def __init__(self, initial_position):
        self.position = initial_position
        self.image = pygame.image.load(bullet2_image).convert_alpha()

def bullet2(position):
    x, y = position
    return (bullet2_single((x-15, y)), bullet2_single((x+15, y)))
