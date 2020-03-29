import pygame
from pygame.locals import *
import sys, os
from random import choice

identities = 0

def distance(point1, point2):
    return ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5

class area(object):
    def __init__(self, x_range, y_range):
        self.left = x_range[0]
        self.right = x_range[1]
        self.top = y_range[0]
        self.down = y_range[1]
        self.center = (sum(x_range)/len(x_range), sum(y_range)/len(y_range))

    def if_touch(self, point):
        x, y = point
        if self.left <= x <=self.right:
            if self.top <= y <= self.down:
                return True
        return False

    def if_over_stack(self, others):
        gap = distance(self.center, others.center)
        d1 = min(self.right-self.left, self.down-self.top)
        d2 = min(others.right-others.left, others.down-others.top)
        return gap < d1/2 + d2/2

class enemy1(object):

    health = 100
    enemy_image = '.\\images\\enemy1.png'
    velocity = 50
    score = 100
    get_hit_image = '.\\images\\enemy1.png'
    down1 = '.\\images\\enemy1_down1.png'
    down2 = '.\\images\\enemy1_down2.png'
    down3 = '.\\images\\enemy1_down3.png'
    down4 = '.\\images\\enemy1_down4.png'
    down_sound = '.\\sound\\enemy1_down.wav'
    get_hit = False
    
    def __init__(self, position, world):
        self.life = self.health
        self.position = position
        self.normal_img = pygame.image.load(self.enemy_image).convert_alpha()
        self.image = self.normal_img
        w, h = self.image.get_size()
        x, y = self.position
        self.range = area((x-w/2, x+w/2), (y-h/2, y+h/2))
        self.world = world

        self.down_order = (self.down1, self.down2, self.down3, self.down4)
        self.down_now = 0

        self.down_sound = pygame.mixer.Sound(self.down_sound)

        global identities
        self.identity = identities
        identities += 1

    def process(self, time):
        if self.life > 0:
            self.deal_hit()
            self.normal_act(time)
        else:
            self.fall()

    def fall(self):
        if self.down_now == 0:
            self.down_sound.play()
        if self.down_now < len(self.down_order):
            self.image = pygame.image.load(self.down_order[self.down_now]).convert_alpha()
        self.down_now += 1

    def normal_act(self, time):
        x, y = self.position
        new_y = y + self.velocity * time
        w, h = self.image.get_size()
        self.position = (x, new_y)
        self.range = area((x-w/2, x+w/2), (new_y-h/2, new_y+h/2))

    def deal_hit(self):
        if self.get_hit:
            self.image = pygame.image.load(self.get_hit_image).convert_alpha()
            self.get_hit = False
        else:
            self.image = self.normal_img

    def render(self, surface):
        x, y = self.position
        w, h = self.image.get_size()
        blit_x, blit_y = x-w/2, y-h/2
        surface.blit(self.image, (blit_x, blit_y))

class enemy2(enemy1):

    health = 500
    enemy_image = '.\\images\\enemy2.png'
    velocity = 30
    score = 300
    get_hit_image = '.\\images\\enemy2_hit.png'
    down1 = '.\\images\\enemy2_down1.png'
    down2 = '.\\images\\enemy2_down2.png'
    down3 = '.\\images\\enemy2_down3.png'
    down4 = '.\\images\\enemy2_down4.png'
    down_sound = '.\\sound\\enemy2_down.wav'

class enemy3(enemy1):

    health = 1000
    enemy_image1 = '.\\images\\enemy3_n1.png'
    enemy_image2 = '.\\images\\enemy3_n2.png'
    velocity = 20
    score = 600
    get_hit_image = '.\\images\\enemy3_hit.png'
    down1 = '.\\images\\enemy3_down1.png'
    down2 = '.\\images\\enemy3_down2.png'
    down3 = '.\\images\\enemy3_down3.png'
    down4 = '.\\images\\enemy3_down4.png'
    down_sound = '.\\sound\\enemy3_down.wav'
    fly_sound = '.\\sound\\enemy3_flying.wav'

    def __init__(self, position, world):
        self.life = self.health
        self.position = position
        self.normal_image1 = pygame.image.load(self.enemy_image1).convert_alpha()
        self.normal_image2 = pygame.image.load(self.enemy_image2).convert_alpha()
        self.image = self.normal_image1
        w, h = self.image.get_size()
        x, y = self.position
        self.range = area((x-w/2, x+w/2), (y-h/2, y+h/2))
        self.world = world

        self.down_order = (self.down1, self.down2, self.down3, self.down4)
        self.down_now = 0

        self.down_sound = pygame.mixer.Sound(self.down_sound)
        self.fly_sound = pygame.mixer.Sound(self.fly_sound)

        global identities
        self.identity = identities
        identities += 1

    def deal_hit(self):
        if self.get_hit:
            self.image = pygame.image.load(self.get_hit_image).convert_alpha()
            self.get_hit = False
        else:
            self.image = choice([self.normal_image1, self.normal_image2])
