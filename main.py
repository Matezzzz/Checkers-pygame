import pygame

import layouts
import game
from global_defines import *



class Application:
    #currently active layout
    active_layout = None

    #layouts for game settings, active game and victory screen
    game_settings_layout = None
    game_layout = None
    victory_screen_layout = None

    #screen surface to draw into
    screen_surface = None

    #whether app should exit - True if ESC or cross button was pressed
    should_exit = False
    def __init__(self):
        #create all layouts
        self.game_settings_layout = layouts.NewGameSettings(self)
        self.game_layout = game.ActiveGame(self)
        self.victory_screen_layout = layouts.VictoryScreen(self)

        #set active layout as new game settings
        self.active_layout = self.game_settings_layout
        #create pygame window and save surface
        self.screen_surface = pygame.display.set_mode((g_screen_width, g_screen_height))

    #is called when start game button is pressed, start new game with given players
    def startGame(self, white_player, black_player):
        #set active layout to game
        self.setLayout(self.game_layout)
        #reset game state and set players
        self.game_layout.resetGame()
        self.game_layout.setPlayers(white_player, black_player)

    #is called when somebody wins
    def endGame(self, status):
        #swap to victory screen
        self.setLayout(self.victory_screen_layout)
        #tell the victory screen who won
        self.victory_screen_layout.setStatus(status)

    def exit(self):
        self.should_exit = True

    #check events
    def pollEvents(self):
        #exit if user pressed the X button
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                self.exit()
        #pump events - if not called window can stop responding
        pygame.event.pump()

    def draw(self, time):
        self.pollEvents()
        #fill screen with pitch black
        self.screen_surface.fill((0, 0, 0))
        #draw current layout
        self.active_layout.draw(self.screen_surface, time)

    #checked in main game loop
    def running(self):
        return not self.should_exit

    #change active layout
    def setLayout(self, target):
        self.active_layout = target



#Main game loop
pygame.init()
game = Application()
t = 0.0
#clock for limiting FPS to 60
clock = pygame.time.Clock()
while game.running():
    #increase time by a small bit every frame
    t += 0.005
    #draw everything
    game.draw(t)
    pygame.display.flip()
    #limit FPS to 60
    clock.tick_busy_loop(60)

