import pygame 
import os
import time
import random
pygame.init()

FPS = 60
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Load image
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
        self.y += vel

    def off_screen(self, height):
        return not(self.y < height and self.y >= 0)
    
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
            laser = Laser(self.x, self.y, self.laser_img)
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
        pygame.draw.rect(window, (255,0,0), (WIDTH / 2, 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (WIDTH / 2, 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

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
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Game:
    
    def __init__(self):
        self.run = True
        self.lost = False
       
        self.level = 0
        self.lives = 5
        self.main_font = pygame.font.SysFont("comicsans", 50)
        self.lost_font = pygame.font.SysFont("comicsans", 60)

        self.display = pygame.Surface((WIDTH, HEIGHT))

        self.enemies = []
        self.wave_length = 5
        
        self.enemy_vel = 1
        self.player_vel = 7
        self.laser_vel = 8
        
        self.mainmenu = MainMenu()
        self.endmenu = EndMenu()
        self.player = Player(300, 630)
        self.clock = pygame.time.Clock()

        self.lost_count = 0

        self.W_KEY = False
        self.A_KEY = False
        self.S_KEY = False
        self.D_KEY = False
        self.SPACE_KEY = False
        self.START_KEY = False
        self.BACK_KEY = False
    
    def game_reset(self):
        self.run = True
        self.lost = False
        self.level = 0
        self.lives = 5
        self.main_font = pygame.font.SysFont("comicsans", 50)
        self.lost_font = pygame.font.SysFont("comicsans", 60)
        self.display = pygame.Surface((WIDTH, HEIGHT))
        self.enemies = []
        self.wave_length = 5
        self.enemy_vel = 1
        self.player_vel = 7
        self.laser_vel = 8
        self.mainmenu = MainMenu()
        self.endmenu = EndMenu()
        self.player = player = Player(300, 630)
        self.clock = pygame.time.Clock()
        self.lost_count = 0
        self.reset_keys()

    
    def collide(self, obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

    def redraw_window(self):
        WIN.blit(BG, (0,0))
        # Draw text
        level_label = self.main_font.render(f"Level: {self.level}", 1, (255,255,255))

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
            self.clock.tick(FPS)
            if self.mainmenu.run_display == True:
                self.mainmenu.display_menu()
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
            self.lost_count += 1
        
        if self.lost:
            if self.lost_count > FPS * 3:
                self.run = False
                self.endmenu.display_menu()
            else:
                self.game_loop()
               
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

    def draw_text(self, text, size, x, y ):
        font = pygame.font.SysFont("comicsans", size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)

class Menu:
    def __init__(self):
        self.mid_w, self.mid_h = WIDTH / 2, HEIGHT / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 100

    def draw_cursor(self):
        game.draw_text('*', 70, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        WIN.blit(game.display, (0, 0))
        pygame.display.update()
        game.reset_keys()
    
# class HUD:
#     def __init__(self):
#         self.image = 

class MainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 30
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 70
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 110
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
    
    def display_menu(self):
        self.run_display = True
        while self.run_display:
            game.clock.tick(FPS)
            game.check_events()
            self.check_input()
            game.display.fill(BLACK)
            game.draw_text('Main Menu', 100, WIDTH / 2, HEIGHT / 2 - 100)
            game.draw_text('Start Game', 50, self.startx, self.starty)
            game.draw_text('Options', 50, self.optionsx, self.optionsy)
            game.draw_text('Credits', 50, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self): 
        if game.S_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy + 10)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy + 10)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
        elif game.W_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy + 10)
                self.state = 'Credits'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy + 10)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if game.START_KEY:
            if self.state == 'Start':
                game.playing = True
            # if self.state == 'Options':
            #     pass
            # if self.state == 'Credits':
            #     pass
            self.run_display = False

class EndMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h
        self.exitx, self.exity = self.mid_w, self.mid_h + 30
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
    
    def display_menu(self):
        self.run_display = True
        while self.run_display:
            game.clock.tick(FPS)
            game.check_events()
            self.check_input()
            game.display.fill(BLACK)
            game.draw_text('Play Again', 50, self.startx, self.starty)
            game.draw_text('Exit', 50, self.exitx, self.exity)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self): 
        if game.S_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity + 10)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
        elif game.W_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity + 10)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
    def check_input(self):
        self.move_cursor()
        if game.START_KEY:
            if self.state == 'Start':
                game.game_reset()
                game.game_loop()
            if self.state == 'Exit':
                pass
            self.run_display = False

game = Game()
game.game_loop()

