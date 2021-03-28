import pygame 
import os
import time
import play
from scripts import text 
pygame.init()
clock = pygame.time.Clock()
FPS = 60
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
WIDTH, HEIGHT = 200, 200
WIN = pygame.display.set_mode((750, 750))
pygame.display.set_caption("Astralis")

# Icon
LOGO = pygame.image.load(os.path.join('data', 'assets', 'logo.png'))
pygame.display.set_icon(LOGO)

# Menu
MAIN_MENU = pygame.image.load(os.path.join('data', 'assets', 'Main_Menu.png'))
MAIN_MENU.set_colorkey((BLACK))

# Cursor
CURSOR = pygame.image.load(os.path.join('data', 'assets', 'cursor.png'))
CURSOR.set_colorkey((BLACK))


class Menu:
    def __init__(self):
        self.mid_w, self.mid_h = (WIDTH - game.large_font.width(f'Highscore: {str(game.highscore)}')) / 2, (HEIGHT / 2) + 10
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = 0
        self.menu_font = text.Font(os.path.join('data', 'font', 'large_font.png'), (11, 255, 230))
        self.menu_font_back = text.Font(os.path.join('data', 'font', 'large_font.png'), (1, 136, 165))

    def draw_cursor(self):
        # Display cursor
        game.display.blit(CURSOR, (self.cursor_rect.x, self.cursor_rect.y - 7))

    def update_display(self):
        # Rescale display to window
        WIN.blit(pygame.transform.scale((game.display), (750, 750)), (0,0))
        pygame.display.update()
        game.reset_keys()

class MainMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.state = "Start"
        self.startx, self.starty = self.mid_w , self.mid_h + 10
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 30
        self.quitx, self.quity = self.mid_w , self.mid_h + 50
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
        self.back_offset = 1

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            # Lock FPS
            clock.tick(FPS)
            game.check_events()
            self.check_input()
            # Display menu
            game.display.blit(MAIN_MENU, (0,0))
            # Draw text
            game.text_3D(self.menu_font_back, self.menu_font, f'Highscore: {str(game.highscore)}', game.display, ((WIDTH - game.large_font.width(f'Highscore: {str(game.highscore)}') + 2) / 2, 10 + self.back_offset))
            game.text_3D(self.menu_font_back, self.menu_font,'Start Game', game.display, (((WIDTH  + 2 - self.menu_font.width('Start Game'))/ 2) , self.starty + self.back_offset))
            game.text_3D(self.menu_font_back, self.menu_font, 'Options', game.display, ((WIDTH + self.back_offset - self.menu_font.width('Options')) / 2 , self.optionsy + self.back_offset))
            game.text_3D(self.menu_font_back, self.menu_font, 'Quit', game.display, ((WIDTH + self.back_offset - self.menu_font.width('Quit'))/ 2, self.quity + self.back_offset))
            self.draw_cursor()
            self.update_display()

    def move_cursor(self): 
        # Cursor Down
        if game.S_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy + 10)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity + 10)
                self.state = 'Quit'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
        # Cursor Up
        elif game.W_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity + 10)
                self.state = 'Quit'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Start'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy + 10)
                self.state = 'Options'

    def check_input(self):
        self.move_cursor()
        if game.START_KEY:
            if self.state == 'Start':
                game.playing = True
            # if self.state == 'Options':
            #     pass
            if self.state == 'Quit':
                game.run = False
            self.run_display = False

class EndMenu(Menu):
    def __init__(self):
        Menu.__init__(self)
        self.state = "Play Again?"
        self.startx, self.starty = self.mid_w, self.mid_h - 15
        self.exitx, self.exity = self.mid_w, self.mid_h + 5
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            # Lock FPS
            clock.tick(FPS)
            game.check_events()
            self.check_input() 
            game.display_window()
            # Draw text
            game.text_3D(self.menu_font_back, self.menu_font, 'Play Again?', game.display, (((WIDTH - self.menu_font.width('Play Again?')) / 2) + 1, self.starty + 1))
            game.text_3D(self.menu_font_back, self.menu_font, 'Exit', game.display, (((WIDTH - self.menu_font.width('Exit')) / 2) + 1, self.exity + 1))
            self.draw_cursor()
            self.update_display()

    def move_cursor(self): 
        # Cursor Down
        if game.S_KEY:
            if self.state == 'Play Again?':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity + 10)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Play Again?'
        # Cursor Up
        elif game.W_KEY:
            if self.state == 'Play Again?':
                self.cursor_rect.midtop = (self.exitx + self.offset, self.exity + 10)
                self.state = 'Exit'
            elif self.state == 'Exit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty + 10)
                self.state = 'Play Again?'

    def check_input(self):
        self.move_cursor()
        if game.START_KEY:
            if self.state == 'Play Again?':
                game.game_reset()
            if self.state == 'Exit':
                pass
            self.run_display = False

# Making classes more accesible    
game = play.Game()
mainmenu = MainMenu()
endmenu = EndMenu()
    
# Running game
def run():
    mainmenu.display_menu()
    while game.run:
        game.game_loop()
        endmenu.display_menu()
run()

