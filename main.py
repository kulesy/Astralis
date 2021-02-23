import pygame 
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers 
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img) 
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x -= vel

    def off_screen(self, width):
        return (self.x > width or self.x <= -50)
    
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
            if laser.off_screen(WIDTH):
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
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP   
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                   if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x -= vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Game:
    
    def __init__(self):
        self.run = True
        self.lost = False
       
        self.FPS = 60
        self.level = 0
        self.lives = 5
        self.main_font = pygame.font.SysFont("comicsans", 50)
        self.lost_font = pygame.font.SysFont("comicsans", 60)

        self.enemies = []
        self.wave_length = 5
        
        self.enemy_vel = 1
        self.player_vel = 7
        self.laser_vel = 8

        self.player = Player(100, 300)

        self.clock = pygame.time.Clock()

        self.lost_count = 0
    
    def collide(self, obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

    def redraw_window(self):
        WIN.blit(BG, (0,0))
        # Draw text
        lives_label = self.main_font.render(f"Lives: {self.lives}", 1, (255,255,255))
        level_label = self.main_font.render(f"Level: {self.level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
        for enemy in self.enemies:
            enemy.draw(WIN)

        self.player.draw(WIN)

        if self.lost == True:
            lost_label = self.lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    def game_loop(self):
        while self.run:
            self.clock.tick(self.FPS)
            self.redraw_window()
            self.game_status()
            self.check_events()
            self.enemy_behaviour()
            self.player.move_lasers(self.laser_vel, self.enemies)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player.x - self.player_vel > 0: # Left
            self.player.x -= self.player_vel
        if keys[pygame.K_d] and self.player.x + self.player_vel + self.player.get_width() < WIDTH: # Right
            self.player.x += self.player_vel
        if keys[pygame.K_w] and self.player.y - self.player_vel > 0: # Up
            self.player.y -= self.player_vel
        if keys[pygame.K_s] and self.player.y + self.player_vel + self.player.get_height() < HEIGHT: # Down
            self.player.y += self.player_vel
        if keys[pygame.K_SPACE]: # Shoot
            self.player.shoot()

    def game_status(self):
        if self.lives <= 0 or self.player.health <= 0:
            self.lost = True
            self.lost_count += 1
        
        if self.lost:
            if self.lost_count > self.FPS * 3:
                self.run = False
            else:
                self.game_loop()
        if len(self.enemies) == 0: 
            self.level += 1
            self.wave_length += 5
            for i in range(self.wave_length):
                enemy = Enemy(random.randrange(WIDTH, WIDTH + 1000), random.randrange(100, HEIGHT - 100), random.choice(["red", "blue", "green"]))
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
                
            elif enemy.x - enemy.get_width() < -50:
                self.lives -= 1
                self.enemies.remove(enemy)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game = Game()
                game.game_loop()
    pygame.quit()

game = Game()
main_menu()        

