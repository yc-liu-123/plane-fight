import pygame
from pygame.locals import *
from numpy import random
from enemy import area

bomb_supply_image = '.\\images\\bomb_supply.png'
bullet_supply_image = '.\\images\\bullet_supply.png'

class Supply(object):

    cool_time = 2400
    
    def __init__(self):
        self.put_count = 0
        self.supply = [Bomb, Bullet]

    def drop(self):
        if self.put_count >= self.cool_time:
            self.put_count = 0
            supply = random.choice(self.supply)
            x = random.randint(0, 460)
            pygame.mixer.Sound('.\\sound\\supply.wav').play()
            return supply((x, 0))
        else:
            self.put_count += 1
            return None

class Bomb(object):
    
    def __init__(self, position):
        self.image = pygame.image.load(bomb_supply_image)
        self.position = position
        self.speed = 70
        self.get = False
        self.get_sound = pygame.mixer.Sound('.\\sound\\get_bomb.wav')

        w, h = self.image.get_size()
        x, y = self.position
        self.range = area((x-w/2, x+w/2), (y-h/2, y+h/2))

    def process(self, time):
        x, y = self.position
        new_y = y + self.speed * time
        w, h = self.image.get_size()
        self.position = (x, new_y)
        
        self.range = area((x-w/2, x+w/2), (new_y-h/2, new_y+h/2))

    def render(self, surface):
        x, y = self.position
        w, h = self.image.get_size()
        blit_x, blit_y = x-w/2, y-h/2
        surface.blit(self.image, (blit_x, blit_y))
        
class Bullet(Bomb):
    def __init__(self, position):
        self.image = pygame.image.load(bullet_supply_image)
        self.position = position
        self.speed = 70
        self.get = False
        self.get_sound = pygame.mixer.Sound('.\\sound\\get_bullet.wav')

        w, h = self.image.get_size()
        x, y = self.position
        self.range = area((x-w/2, x+w/2), (y-h/2, y+h/2))
