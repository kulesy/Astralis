import pygame 
import os
import time
import random
from scripts import text 
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
FPS = 30
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
WIDTH, HEIGHT = 200, 200
WIN = pygame.display.set_mode((750, 750))
display = pygame.Surface((200, 200))
HS_FILE = "highscore.txt"

# Load image
RED_SPACE_SHIP = pygame.image.load(os.path.join( "data", "assets", "enemy_red.png"))
RED_SPACE_SHIP.set_colorkey((BLACK))
# Player 
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join( "data", "assets", "player.png"))
YELLOW_SPACE_SHIP.set_colorkey((BLACK))
# Lasers 
RED_LASER = pygame.image.load(os.path.join( "data", "assets", "laser_enemy.png"))
RED_LASER.set_colorkey((BLACK))
YELLOW_LASER = pygame.image.load(os.path.join( "data", "assets", "laser_player.png"))
YELLOW_LASER.set_colorkey((BLACK))
LASER1 = pygame.mixer.Sound(os.path.join( "data", "sounds", "shoot1.wav"))
LASER2 = pygame.mixer.Sound(os.path.join( "data", "sounds", "shoot2.wav"))
# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join( "data", "assets", "background.png")), (200, 200))
# Lives
LIVES = pygame.image.load(os.path.join( "data", "assets", "heart.png"))
LIVES.set_colorkey((BLACK))
# Font
font = pygame.image.load(os.path.join( 'data', 'font', 'small_font.png'))

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
    COOLDOWN = 20
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y 
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        # Display the player ship to the window
        window.blit(self.ship_img, (self.x, self.y))
        # Draw each laser in the list to the screen
        for laser in self.lasers:
            if not laser.off_screen(HEIGHT):
                laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        # Move each laser & check its collisions with the player
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser) 
            if laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        # Wait for cooldown before shooting next laser
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            LASER1.play()
            laser = Laser(self.x + 6, self.y, self.laser_img)
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
        self.health_w = 60
        self.health_h = 3
        self.health_x = (WIDTH // 2) - (self.health_w // 2)
        self.health_y = 10
        self.score = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        # Move each laser & check enemy collisions
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
        # Draw the display and HUD to the window
        super().draw(window)
        self.HUD(window)

    def HUD(self, window):      
        # Display the healthbar
        pygame.draw.rect(window, (255,0,0), (self.health_x, self.health_y, self.health_w, self.health_h))
        pygame.draw.rect(window, (0,255,0), (self.health_x, self.health_y, self.health_w * (self.health/self.max_health), self.health_h))   

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

    def move(self, vel):
        # Move enemy down
        self.y += 1

    def shoot(self):
        # Shoot the enemy laser if the cooldown is zero and the enemy is not offscreen
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 6, self.y + 2, self.laser_img)
            if not laser.off_screen(HEIGHT):
                LASER2.play()
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Game:
    
    def __init__(self):
        self.run = True
        self.lost = False
       
        self.level = 0
        self.hearts = 5
        self.lives = self.hearts
        self.small_font = text.Font(os.path.join( 'data', 'font', 'small_font.png'), (WHITE))
        self.large_font = text.Font(os.path.join( 'data', 'font', 'large_font.png'), (WHITE))
        self.end_font = text.Font(os.path.join( 'data', 'font', 'large_font.png'), (11, 255, 230))
        self.end_font_back = text.Font(os.path.join( 'data', 'font', 'large_font.png'), (1, 136, 165))


        self.display = pygame.Surface((200,200))

        self.enemies = []
        self.wave_length = 5
        
        self.enemy_vel = 1
        self.player_vel = 4
        self.laser_vel = 8
        
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
        #Reset the game from scratch
        self.__init__()

    def load_data(self):
        #Load high score file from directory
        self.dir = os.path.dirname(__file__)
        try:
            #try to read the file
            with open(os.path.join( self.dir, HS_FILE), 'r+') as f:
                self.highscore = int(f.read())
        except:
            #create the file
            with open(os.path.join( self.dir, HS_FILE), 'w'):
                self.highscore = 0

    def collide(self, obj1, obj2):
        # Take the difference of two obj
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        # Check if objects overlap with each other, if they do return true, if not return false
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

    def redraw_window(self):
        self.display_window()
        # Rescale display to window
        WIN.blit(pygame.transform.scale(self.display, (750,750)), (0,0))
        pygame.display.update()
    
    def display_window(self):
        self.display.blit(BG, (0,0))
        # Display each enemy om the enemies list
        for enemy in self.enemies:
            enemy.draw(self.display)
        # Display player
        self.player.draw(self.display)
        # Draw level and score HUD to display
        self.small_font.render(f"Level: {self.level}", self.display, (WIDTH - self.small_font.width(f"Level: {self.level}") - 10, self.player.health_y))
        self.small_font.render(f"Score: {self.player.score}", self.display, (10, self.player.health_y))
        self.update_lives()
        # If you lose, show your score
        if self.lost == True:
            scorew = (WIDTH - (self.large_font.width(f"Score: {self.score}")))//2
            scoreh = HEIGHT/2 - 20
            # If score is less than highscore, no highscore
            if self.highscore > self.player.score:
                self.text_3D(self.end_font_back, self.end_font, f"Score: {self.player.score}", self.display, (scorew, scoreh))
             # If score is more than highscore, you have the highscore
            elif self.highscore <= self.player.score:
                self.highscore = self.player.score
                self.text_3D(self.end_font_back, self.end_font, f"New Highscore! : {self.highscore}", self.display, ((WIDTH//2 - 60), (scoreh)))
                with open(os.path.join( self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.player.score))

    def game_loop(self):
        while self.run:
            # Lock FPS
            clock.tick(FPS)
            self.redraw_window()
            # Check events
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
                if event.key == pygame.K_a: # A key Pressed
                    self.A_KEY = True
                if event.key == pygame.K_d: # D key Pressed
                    self.D_KEY = True
                if event.key == pygame.K_w: # W key Pressed
                    self.W_KEY = True
                if event.key == pygame.K_s: # S key Pressed
                    self.S_KEY = True
                if event.key == pygame.K_SPACE: # Space key Pressed
                    self.SPACE_KEY = True
                if event.key == pygame.K_RETURN: # Start key Pressed
                    self.START_KEY = True
                if event.key == pygame.K_ESCAPE: # Back key Pressed
                    self.BACK_KEY = True

    def player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player.x - self.player_vel > 0: # Move player left
            self.player.x -= self.player_vel
        if keys[pygame.K_d] and self.player.x + self.player_vel + self.player.get_width() < WIDTH: # Move player right
            self.player.x += self.player_vel
        if keys[pygame.K_w] and self.player.y - self.player_vel > 0: # Move player up
            self.player.y -= self.player_vel
        if keys[pygame.K_s] and self.player.y + self.player_vel + self.player.get_height() < HEIGHT: # Move player down
            self.player.y += self.player_vel
        if keys[pygame.K_SPACE]: # Player shoot 
            self.player.shoot()

    def game_status(self):
        if self.lives <= 0 or self.player.health <= 0: # Player lost
            self.lost = True
        
        if self.lost:
            while self.lost_count < FPS * 3: # Wait 3 Sec until displaying endmenu
                clock.tick(FPS)
                self.redraw_window()
                self.lost_count += 1
            self.run = False
               
        if len(self.enemies) == 0: # New Wave
            self.level += 1
            self.wave_length += 5
            for i in range(self.wave_length): # Set enemies for current wave
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-500, -100), random.choice(["red", "blue", "green"]))
                self.enemies.append(enemy)

    def enemy_behaviour(self):
        for enemy in self.enemies[:]: # Move enemies and lasers in the list of enemies
            enemy.move(self.enemy_vel)
            enemy.move_lasers(self.laser_vel, self.player)

            if random.randrange(0, 3*FPS) == 1: # Enemies shooting set to a random timer
                enemy.shoot()

            if self.collide(enemy, self.player): # Enemy collisions with player
                self.player.health -= 10
                self.enemies.remove(enemy)
                
            elif enemy.y + enemy.get_height() > HEIGHT: # Enemies getting past player line
                self.lives -= 1
                self.enemies.remove(enemy)
    
    def reset_keys(self): #Reset keys to false
        self.W_KEY, self.A_KEY, self.S_KEY, self.D_KEY, self.SPACE_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False, False, False, False 

    def text_3D(self, font1, font2, text, surf, loc): #Draw 3D effect text to screen
        font1.render(text, surf, loc)
        coord = [pos - 1 for pos in loc]
        loc_new = (coord[0], coord[1])
        font2.render(text, surf, loc_new)

    def update_lives(self): #Update the amount of lives you have
        offset = ((LIVES.get_width() / 2) - 3)
        for i in range(self.lives):
            self.display.blit(LIVES, (self.player.health_x + offset, (self.player.health_y + self.player.health_h + 2)))
            offset += self.player.health_w // self.hearts

game = Game() #Instantiate game

# Credit to framework of my game https://www.youtube.com/watch?v=Q-__8Xw9KTM Tech With Tim
