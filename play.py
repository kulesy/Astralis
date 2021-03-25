import pygame 
import os
import time
import random
from scripts import text 
pygame.init()
clock = pygame.time.Clock()
FPS = 60
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
WIDTH, HEIGHT = 200, 200
WIN = pygame.display.set_mode((750, 750))
display = pygame.Surface((200, 200))
pygame.display.set_caption("Space Shooter Tutorial")
HS_FILE = "highscore.txt"


# Load image
RED_SPACE_SHIP = pygame.image.load(os.path.join("data", "assets", "enemy_red.png"))
RED_SPACE_SHIP.set_colorkey((BLACK))

#Player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("data", "assets", "player.png"))
YELLOW_SPACE_SHIP.set_colorkey((BLACK))
# Lasers 
RED_LASER = pygame.image.load(os.path.join("data", "assets", "laser_enemy.png"))
RED_LASER.set_colorkey((BLACK))
YELLOW_LASER = pygame.image.load(os.path.join("data", "assets", "laser_player.png"))
YELLOW_LASER.set_colorkey((BLACK))
# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("data", "assets", "background.png")), (200, 200))

# Lives
LIVES = pygame.image.load(os.path.join("data", "assets", "heart.png"))
LIVES.set_colorkey((BLACK))

# Font
font = pygame.image.load(os.path.join('data', 'font', 'small_font.png'))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) 
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return (self.y >= height or self.y <= -RED_LASER.get_width())
    
    def collision(self, obj):
        return game.collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y 
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 6, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=5):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP   
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.health_w = 60
        self.health_h = 3
        self.health_x = (WIDTH // 2) - (self.health_w // 2)
        self.health_y = 2

        self.ability_w = self.health_w // 2
        self.ability_h = 10

        self.score = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                   if laser.collision(obj):
                        if obj.color == "blue":
                            self.score += 20
                        elif obj.color == "green":
                            self.score += 40
                        elif obj.color == "red":
                            self.score += 60    
                        objs.remove(obj)

                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.HUD(window)

    def HUD(self, window):

        ability1 = pygame.Surface((self.ability_w, self.ability_h))
        ability1.set_alpha(128)
        ability1.fill((WHITE))

        ability2 = pygame.Surface((self.ability_w, self.ability_h))
        ability2.set_alpha(128)
        ability2.fill((0,0,255))
        
        pygame.draw.rect(window, (255,0,0), (self.health_x, self.health_y, self.health_w, self.health_h))
        pygame.draw.rect(window, (0,255,0), (self.health_x, self.health_y, self.health_w * (self.health/self.max_health), self.health_h))

        game.display.blit(ability1, (self.health_x, self.health_h + self.health_y))
        game.display.blit(ability2, ((WIDTH // 2), self.health_h + self.health_y))
    

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (RED_SPACE_SHIP, RED_LASER),
                "blue": (RED_SPACE_SHIP, RED_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.color = color
        self.clock = 0

    def move(self, vel):
        if self.clock > 0:
            self.y += vel
            self.clock = 0
        else:
            self.clock += 1

 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 6, self.y + 2, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Game:
    
    def __init__(self):
        self.run = True
        self.lost = False
       
        self.level = 0
        self.hearts = 5
        self.lives = self.hearts
        self.small_font = text.Font(os.path.join('data', 'font', 'small_font.png'), (WHITE))
        self.large_font = text.Font(os.path.join('data', 'font', 'large_font.png'), (WHITE))
        self.end_font = text.Font(os.path.join('data', 'font', 'large_font.png'), (11, 255, 230))
        self.end_font_back = text.Font(os.path.join('data', 'font', 'large_font.png'), (1, 136, 165))


        self.display = pygame.Surface((200,200))

        self.enemies = []
        self.wave_length = 5
        
        self.enemy_vel = 1
        self.player_vel = 2
        self.laser_vel = 2
        
        self.player = Player(WIDTH // 2 - (YELLOW_SPACE_SHIP.get_width() // 2), 175)
        
        self.clock = 0

        self.lost_count = 0

        self.score = 0

        self.W_KEY = False
        self.A_KEY = False
        self.S_KEY = False
        self.D_KEY = False
        self.SPACE_KEY = False
        self.START_KEY = False
        self.BACK_KEY = False
        self.load_data()
        
    def game_reset(self):
        self.run = True
        self.lost = False
        self.level = 0
        self.hearts = 5
        self.lives = self.hearts
        self.small_font = text.Font(os.path.join('data', 'font', 'small_font.png'), (WHITE))
        self.large_font = text.Font(os.path.join('data', 'font', 'large_font.png'), (WHITE))
        self.end_font = text.Font(os.path.join('data', 'font', 'large_font.png'), (11, 255, 230))
        self.end_font_back = text.Font(os.path.join('data', 'font', 'large_font.png'), (1, 136, 165))
        self.display = pygame.Surface((200, 200))
        self.enemies = []
        self.wave_length = 5
        self.enemy_vel = 1
        self.player_vel = 2
        self.laser_vel = 2
        self.player = player = Player(WIDTH // 2 - (YELLOW_SPACE_SHIP.get_width() // 2), 175)
        self.lost_count = 0
        self.score = 0
        self.reset_keys()

    def load_data(self):
        #load high score
        self.dir = os.path.dirname(__file__)
        try:
            #try to read the file
            with open(os.path.join(self.dir, HS_FILE), 'r+') as f:
                self.highscore = int(f.read())
        except:
            #create the file
            with open(os.path.join(self.dir, HS_FILE), 'w'):
                self.highscore = 0

    def collide(self, obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

    def redraw_window(self):
        self.display_window()
        WIN.blit(pygame.transform.scale(self.display, (750,750)), (0,0))
        pygame.display.update()
    
    def display_window(self):
        self.display.blit(BG, (0,0))
        # Draw text
        level_label = self.small_font.render(f"Level: {self.level}", self.display, (WIDTH - self.small_font.width(f"Level: {self.level}") - 10, 10))
        score_label = self.small_font.render(f"Score: {self.player.score}", self.display, (10, 10))
        
        for enemy in self.enemies:
            enemy.draw(self.display)

        self.player.draw(self.display)
        self.update_lives()

        if self.lost == True:
            scorew = (WIDTH//2 - (self.large_font.width(f"Score: {self.score}")//2))
            scoreh = HEIGHT/2 - 20
            if self.highscore > self.player.score:
                lost_label = self.end_font_back.render(f"Score: {self.player.score}", self.display, (scorew, scoreh))
                lost_label = self.end_font.render(f"Score: {self.player.score}", self.display, ((scorew) - 1, (scoreh) - 1))

            elif self.highscore <= self.player.score:
                self.highscore = self.player.score
                win_label = self.end_font_back.render(f"New Highscore! : {self.highscore}", self.display, ((WIDTH//2 - 60), (scoreh)))
                win_label = self.end_font.render(f"New Highscore! : {self.highscore}", self.display, ((WIDTH//2 - 60) - 1, (scoreh) - 1))
                with open(os.path.join(self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.player.score))

    def game_loop(self):
        while self.run:
            clock.tick(FPS)
            self.redraw_window()
            self.game_status()
            self.player_events()
            self.enemy_behaviour()
            self.player.move_lasers(self.laser_vel, self.enemies)
            self.reset_keys()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a: 
                    self.A_KEY = True
                if event.key == pygame.K_d: 
                    self.D_KEY = True
                if event.key == pygame.K_w: 
                    self.W_KEY = True
                if event.key == pygame.K_s: 
                    self.S_KEY = True
                if event.key == pygame.K_SPACE: 
                    self.SPACE_KEY = True
                if event.key == pygame.K_RETURN: 
                    self.START_KEY = True
                if event.key == pygame.K_ESCAPE: 
                    self.BACK_KEY = True


    def player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player.x - self.player_vel > 0: 
            self.player.x -= self.player_vel
        if keys[pygame.K_d] and self.player.x + self.player_vel + self.player.get_width() < WIDTH: 
            self.player.x += self.player_vel
        if keys[pygame.K_w] and self.player.y - self.player_vel > 0:
            self.player.y -= self.player_vel
        if keys[pygame.K_s] and self.player.y + self.player_vel + self.player.get_height() < HEIGHT:
            self.player.y += self.player_vel
        if keys[pygame.K_SPACE]:
            self.player.shoot()

    def game_status(self):
        if self.lives <= 0 or self.player.health <= 0:
            self.lost = True
        
        if self.lost:
            while self.lost_count < FPS * 3:
                clock.tick(FPS)
                self.redraw_window()
                self.lost_count += 1
            self.run = False
               
        if len(self.enemies) == 0: 
            self.level += 1
            self.wave_length += 5
            for i in range(self.wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                self.enemies.append(enemy)

    def enemy_behaviour(self):
        for enemy in self.enemies[:]:
            enemy.move(self.enemy_vel)
            enemy.move_lasers(self.laser_vel, self.player)

            if random.randrange(0, 3*60) == 1:
                enemy.shoot()

            if self.collide(enemy, self.player):
                self.player.health -= 10
                self.enemies.remove(enemy)
                
            elif enemy.y + enemy.get_height() > HEIGHT:
                self.lives -= 1
                self.enemies.remove(enemy)
    
    def reset_keys(self):
        self.W_KEY, self.A_KEY, self.S_KEY, self.D_KEY, self.SPACE_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False, False, False, False

    def text_3D(self, font1, font2, text, surf, loc):
        font1.render(text, surf, loc)
        coord = [pos - 1 for pos in loc]
        loc_new = (coord[0], coord[1])
        font2.render(text, surf, loc_new)

    def update_lives(self):
        offset = ((LIVES.get_width() / 2) - 3)
        for i in range(self.lives):
            self.display.blit(LIVES, (self.player.health_x + offset, (self.player.health_y + self.player.health_h + self.player.ability_h)))
            offset += self.player.health_w // self.hearts
game = Game()
