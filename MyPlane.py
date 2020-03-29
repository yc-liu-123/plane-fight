import pygame
from pygame.locals import *
import sys, os
import bullet
from enemy import area
from datetime import datetime, timedelta

my_plane_image1 = '.\\images\\me1.png'
my_plane_image2 = '.\\images\\me2.png'

me_down1 = '.\\images\\me_destroy_1.png'
me_down2= '.\\images\\me_destroy_2.png'
me_down3 = '.\\images\\me_destroy_3.png'
me_down4 = '.\\images\\me_destroy_4.png'

fire_sound = '.\\sound\\bullet.wav'
down_sound = '.\\sound\\me_down.wav'

class MyPlane(object):

    fire_cool = 5
    
    def __init__(self, world):
        self.score = 0
        self.life = 500
        self.bullet = bullet.bullet1
        self.position = (230, 500)
        self.image1 = pygame.image.load(my_plane_image1).convert_alpha()
        self.image2 = pygame.image.load(my_plane_image2).convert_alpha()
        self.image = self.image1
        self.world = world
        self.world.I_join_the_battle(self)
        self.alive = True
        self.fire_sound = pygame.mixer.Sound(fire_sound)
        self.down_sound = pygame.mixer.Sound(down_sound)

        w, h = self.image.get_size()
        x, y = self.position
        self.range = area((x-w/2, x+w/2), (y-h/2, y+h/2))

        down1 = pygame.image.load(me_down1).convert_alpha()
        down2 = pygame.image.load(me_down2).convert_alpha()
        down3 = pygame.image.load(me_down3).convert_alpha()
        down4 = pygame.image.load(me_down4).convert_alpha()
        self.down_order = (down1, down2, down3, down4)
        self.down_now = 0

        self.fire_count = 5

        self.bullet2_endure = 0

    def process(self, time):
        if self.life > 0:
            x, y = pygame.mouse.get_pos()
            new_x = x if 0 <= x <= self.world.size[0] else self.position[0]
            new_y = y if 0 <= y <= self.world.size[1] else self.position[1]
            self.position = (new_x, new_y)
            w, h = self.image.get_size()
            self.range = area((new_x-w/2, new_x+w/2), (new_y-h/2, new_y+h/2))
            if self.image == self.image1:
                self.image = self.image2
            else:
                self.image = self.image1
            self.fire()
            self.get_hit()
            self.get_supply()
            if type(self.bullet) != type:
                self.bullet2_endure += 1
                if self.bullet2_endure > 1200:
                    self.bullet = bullet.bullet1
                    self.bullet2_endure = 0
        else:
            if self.down_now == 0:
                self.down_sound.play()
            if self.down_now < len(self.down_order):
                self.image = self.down_order[self.down_now]
            else:
                self.alive = False
            self.down_now += 1

    def render(self, surface):
        x, y = self.position
        w, h = self.image.get_size()
        surface.blit(self.image, (x-w/2, y-h/2))

    def fire(self):
        if self.fire_count >= self.fire_cool:
            x, y = self.position
            w, h = self.image.get_size()
            head = y - h/2
            self.world.add_bullet(self.bullet((x, head)))
            self.fire_count = 0
            self.fire_sound.play()
        else:
            self.fire_count += 1

    def get_hit(self):
        x, y = self.position
        left, right = max(x-85, 0), min(x+85+1, 480+1)
        for p in self.world.map.Plane[left: right]:
            while p.next:
                p = p.next
                plane = p.value
                if self.range.if_over_stack(plane.range):
                    if plane.life > 0:
                        p_life = plane.life
                        plane.life -= self.life
                        self.life -= p_life
                        if p_life > 0 and plane.life <= 0:
                            self.world.score += plane.score                        

    def get_supply(self):
        if self.world.supplies:
            for supply in self.world.supplies:
                if self.range.if_over_stack(supply.range):
                    supply.get = True
                    supply.get_sound.play()

    def switch_bullet(self):
        #self.bullet2_endure = 0
        self.bullet = bullet.bullet2
