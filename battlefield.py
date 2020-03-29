import pygame
import MyPlane, enemy, supply
#from time import sleep
from numpy import random
from pygame.locals import *
from threading import Thread, Lock

# 加载背景音乐，背景画面，字体以及其他图片音乐
background_music_file = '.\\sound\\game_music.ogg'
background_image_file = '.\\images\\background.png'

bomb_image = '.\\images\\bomb.png'
again_image = '.\\images\\again.png'
pause_image = '.\\images\\pause_nor.png'
resume_image = '.\\images\\resume_nor.png'
gameover_image = '.\\images\\gameover.png'

use_bomb_sound = '.\\sound\\use_bomb.wav'

font_file = '.\\font\\font.ttf'

class process(Thread):
    '''过程线程，计算各飞机、子弹与补给的新位置'''
    def __init__(self, world, time):
        super().__init__()
        self._world = world
        self._time = time/1000

    def run(self):
        if self._world.me.alive:
            falling_supply = self._world.supply_dropper.drop()
            if falling_supply:
                self._world.add_supply(falling_supply)
            self._world.me.process(self._time)
            self._world.map.process_plane(self._time)
            self._world.map.process_bullet(self._time)
            for supply in self._world.supplies:
                supply.process(self._time)
        else:
            self._world.gameover = True

class render(Thread):
    '''显示线程，刷新各元素画面'''
    def __init__(self, world, surface):
        super().__init__()
        self._world = world
        self._surface = surface

    def run(self):
        self._surface.blit(self._world.background, (0, 0))
        if self._world.me.alive:
            self._world.pause.render(self._surface)
            self._world.bomb.render(self._surface)
            font = pygame.font.Font(font_file, 32)
            text = font.render('{0}'.format(str(self._world.bomb_num)), True, (0, 0, 0))
            self._surface.blit(text, (73, 640))
            self._world.me.render(self._surface)
            self._world.map.render_bullet(self._surface)
            self._world.map.render_plane(self._surface)
            for supply in self._world.supplies:
                supply.render(self._surface)
        #else:
        #    self._world.gameover = True
        #    self._world.overgame.render(self._surface)
        #    self._world.again.render(self._surface)
        #    pygame.mouse.set_visible(True)

class lockDecorator():
    '''锁类装饰器，包括飞机锁，子弹锁与补给锁'''
    planeLock = Lock()
    bulletLock = Lock()
    supplyLock = Lock()
    def sync(self, *args):
        locks = args
        def Lock(func):
            def wrapper(*args, **kwargs):
                for lock in locks:
                    lock.acquire()
                res = None
                try:
                    res = func(*args, **kwargs)
                finally:
                    for lock in locks:
                        lock.release()
                return res
            return wrapper
        return Lock

    def mlock(self, fn):
        return self.sync(self.planeLock, self.bulletLock)(fn)

    def plock(self, fn):
        return self.sync(self.planeLock)(fn)

    def block(self, fn):
        return self.sync(self.bulletLock)(fn)
    
    def slock(self, fn):
        return self.sync(self.supplyLock)(fn)

# 实例化锁类
d = lockDecorator()

class link():
    '''链表类，飞机地图与子弹地图的基础'''
    def __init__(self, value, prev=None, next=None):
        self.value = value
        self.prev = prev
        self.next = next

    def __repr__(self):
        return str((self.value, self.next))

    def insert(self, new_link):
        next_link = self
        while next_link.next:
            next_link = next_link.next
        next_link.next = new_link
        new_link.prev = next_link

    def delete(self):
        if self.prev is not None:
            self.prev.next = self.next
        if self.next is not None:
            self.next.prev = self.prev

class Map():
    '''地图类，包含飞机地图与子弹地图，
       方法包括元素加入、伤害判定、元素过程以及元素显示'''
    def __init__(self):
        self.Plane = tuple(link('head') for _ in range(480+1))
        self.Bullet = tuple(link('head') for _ in range(480+1))
        
    @d.plock
    def add_plane(self, plane):
        x, y = plane.position
        self.Plane[x].insert(link(plane))

    @d.block
    def add_bullet(self, bullet):
        bullets = bullet if type(bullet) == tuple else (bullet, )
        for bullet in bullets:
            x, y = bullet.position
            if 0 <= x <= 480:
                self.Bullet[x].insert(link(bullet))

    @d.mlock
    def update(self):
        '''判定伤害与删除飞出画面的飞机子弹'''
        score = 0
        for x, bq in enumerate(self.Bullet):
            left, right = max(x-85, 0), min(x+85+1, 480+1) # 最宽敌机宽度约170
            head_bullet = bq
            while head_bullet.next:
                head_bullet = head_bullet.next
                bullet = head_bullet.value
                for q in range(left, right):
                    if bullet.hit: break
                    head_plane = self.Plane[q]
                    while head_plane.next:
                        head_plane = head_plane.next
                        plane = head_plane.value
                        prev = plane.life
                        if plane.range.if_touch(bullet.position):
                            plane.life -= bullet.damage
                            bullet.hit = True
                            plane.get_hit = True
                        if plane.life <= 0 and prev > 0:
                            score += plane.score
                if bullet.hit or bullet.position[1] < 0:
                    head_bullet.delete()
        for head in self.Plane:
            while head.next and head.next.value.position[1] > 960:
                head.next.delete()
        return score

    @d.block
    def render_bullet(self, surface):
        for b in self.Bullet:
            while b.next:
                b = b.next
                bullet = b.value
                bullet.render(surface)

    @d.plock
    def render_plane(self, surface):
        for p in self.Plane:
            while p.next:
                p = p.next
                plane = p.value
                plane.render(surface)

    @d.block
    def process_bullet(self, time):
        for b in self.Bullet:
            while b.next:
                b = b.next
                bullet = b.value
                bullet.process(time)

    @d.plock
    def process_plane(self, time):
        for p in self.Plane:
            while p.next:
                p = p.next
                plane = p.value
                if plane.life <= 0 and plane.down_now >= len(plane.down_order):
                    p.delete()
                else:
                    plane.process(time)

class BattleField(object):
    '''控制台，控制所有飞机，子弹，补给以及使用炸弹等元素与事件，判断游戏暂停与结束'''
    def __init__(self, surface_size):
        self.map = Map()
        self.background = pygame.image.load(background_image_file).convert()
        self.sound = pygame.mixer.music.load(background_music_file)
        self.size = surface_size
        self.score = 0
        self.me = None
        self.gameover = False
        self.overgame = GameOver()
        self.again = Again()
        self.pause = Button()
        self.bomb = Bomb()
        self.bomb_num = 0
        self.supplies = []
        self.supply_dropper = supply.Supply()
        self.use_bomb_sound = pygame.mixer.Sound(use_bomb_sound)

    def I_join_the_battle(self, plane):
        self.me = plane
    
    def add_plane(self, plane):
        self.map.add_plane(plane)

    def add_bullet(self, bullet):
        self.map.add_bullet(bullet)

    @d.slock
    def add_supply(self, supply):
        self.supplies += [supply]

    @d.slock
    def update_supplies(self, new_supplies):
        self.supplies = new_supplies

    def check(self):
        self.score += self.map.update()

        new_supplies = []
        for supply0 in self.supplies:
            if not supply0.get:
                if supply0.position[1] < 700:
                    new_supplies += [supply0]
            else:
                if type(supply0) == supply.Bomb:
                    self.bomb_num += 1
                else:
                    self.me.switch_bullet()
        self.update_supplies(new_supplies)

    @d.plock
    def use_bomb(self):
        if self.bomb_num > 0:
            self.use_bomb_sound.play()
            self.bomb_num -= 1
            for p in self.map.Plane:
                while p.next:
                    p = p.next
                    plane = p.value
                    plane.life = 0
                    self.score += plane.score
        else:
            print('No Bomb')

class Button(object):
    '''按键类，父类为暂停键，子类包括重新开始、结束游戏、按下炸弹'''
    def __init__(self):
        self.position = (25, 25)
        self.image_pause = pygame.image.load(pause_image)
        self.image_resume = pygame.image.load(resume_image)
        self.image_current = self.image_pause
        self.playing = True

    def render(self, surface):
        x, y = self.position
        w, h = self.image_current.get_size()
        x -= w/2
        y -= h/2
        surface.blit(self.image_current, (x, y))

    def is_click(self, point):
        point_x, point_y = point
        x, y = self.position
        w, h = self.image_current.get_size()
        x -= w/2
        y -= h/2
        in_x = point_x >= x and point_x < x + w
        in_y = point_y >= y and point_y < y + h
        if in_x and in_y:
            if self.image_current == self.image_pause:
                self.image_current = self.image_resume
                self.playing = False
            else:
                self.image_current = self.image_pause
                self.playing = True
            return True
        return False

class GameOver(Button):
    def __init__(self):
        self.position = (240, 300)
        self.image_current = pygame.image.load(gameover_image)

    def is_click(self, point):
        point_x, point_y = point
        x, y = self.position
        w, h = self.image_current.get_size()
        x -= w/2
        y -= h/2
        in_x = point_x >= x and point_x < x + w
        in_y = point_y >= y and point_y < y + h
        if in_x and in_y:
            return True
        return False

class Again(GameOver):
    def __init__(self):
        self.position = (240, 400)
        self.image_current = pygame.image.load(again_image)

class Bomb(GameOver):
    def __init__(self):
        self.position = (35, 655)
        self.image_current = pygame.image.load(bomb_image)

class Strategy(object):
    '''策略类，负责敌机的生成'''
    def __init__(self, world):
        self.world = world
        self.enemy1 = enemy1_strategy(self.world)
        self.enemy2 = enemy2_strategy(self.world)
        self.enemy3 = enemy3_strategy(self.world)

    def generate_enemy(self):
        self.enemy1.difficulty()
        self.enemy2.difficulty()
        self.enemy3.difficulty()

class enemy1_strategy(object):
    '''生成一类敌机'''
    cool_time = 60
    plane = enemy.enemy1
    def __init__(self, world):
        self.world = world       
        self.count = self.cool_time

    def difficulty(self):
        '''根据当前分数决定生成的数量'''
        if self.world.score > 10000:
            self.cool_time = 30
            self.generate()
        elif self.world.score > 5000:
            self.cool_time = 40
            self.generate()
        elif self.world.score > 2000:
            self.cool_time = 50
            self.generate()
        elif self.world.score >= 0:
            self.generate()

    def generate(self):
        '''插入敌机的具体方法'''
        if self.count >= self.cool_time:
            for _ in range(1):
                x = random.randint(0, 480)
                self.world.add_plane(self.plane((x, 0), self.world))
            self.count = 0
        else:
            self.count += 1

class enemy2_strategy(enemy1_strategy):
    cool_time = 300
    plane = enemy.enemy2
    def difficulty(self):
        if self.world.score > 10000:
            self.cool_time = 100
            self.generate()
        elif self.world.score > 5000:
            self.cool_time = 200
            self.generate()
        elif self.world.score > 1000:
            self.generate()

class enemy3_strategy(enemy1_strategy):
    cool_time = 1000
    plane = enemy.enemy3
    def difficulty(self):
        if self.world.score > 30000:
            self.cool_time = 500
            self.generate()
        elif self.world.score > 20000:
            self.cool_time = 700
            self.generate()
        elif self.world.score > 10000:
            self.generate()

# 游戏主函数
def run():
    # pygame初始化
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.set_num_channels(8)
    MUSIC_END = USEREVENT+1
    pygame.mixer.music.set_endevent(MUSIC_END)
    SCREEN_SIZE = (480, 700)
    w, h = SCREEN_SIZE
    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)
    font = pygame.font.Font(font_file, 32)
    font_length = font.size('Score: 0')[0]
    pygame.display.set_caption("Plane Fight")
    clock = pygame.time.Clock()

    play = True
    while play:
        battlefield = BattleField(SCREEN_SIZE)
        myplane = MyPlane.MyPlane(battlefield)
        strategy = Strategy(battlefield)
    
        pygame.mouse.set_visible(False)

        pygame.mixer.music.play()

        # 主循环
        while not battlefield.gameover:
            # 获取pygame事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                if event.type == MUSIC_END:
                    pygame.mixer.music.play()
                if event.type == MOUSEBUTTONDOWN:
                    battlefield.pause.is_click(event.pos)
                if event.type == KEYDOWN:
                    if event.key == K_p:
                        battlefield.pause.is_click((25, 25))
                    if event.key == K_a:
                        battlefield.use_bomb()
        
            score_text = font.render('Score: {0}'.format(str(battlefield.score)), True, (0, 0, 0))
                
            time_passed = clock.tick(60)

            processing = process(battlefield, time_passed)
            rendering = render(battlefield, screen)
        
            rendering.start()

            if battlefield.pause.playing:
                strategy.generate_enemy()
                processing.start()
                battlefield.check()
                processing.join()
        
            rendering.join()
            screen.blit(score_text, ((w - font_length)/2, 0))
    
            pygame.display.update()

        pygame.mouse.set_visible(True)
        notdecide = True
        # 等待按键
        while notdecide:
            battlefield.overgame.render(screen)
            battlefield.again.render(screen)
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    if battlefield.overgame.is_click(event.pos):
                        play = False
                        notdecide = False
                    elif battlefield.again.is_click(event.pos):
                        play = True
                        notdecide = False
                else:
                    continue
            pygame.display.update()
    pygame.quit()

if __name__ == '__main__':
    run()
