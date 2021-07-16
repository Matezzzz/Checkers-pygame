from global_defines import *
from game_defines import *

from layouts import Layout
from objects import StaticObject
from texture_loader import textures
from game_state import DefaultGameState
from particle_anim import BlackTileAnimation
from game_manager import GameManager




#Manages Active game and players
class ActiveGame(Layout):    
    game_manager = None
    tile_animation = None
    
    white_player = None
    black_player = None

    def __init__(self, app):
        #initialize layout
        super().__init__(app)
        #add static object to layout - this draws game board each frame
        self.add(StaticObject(textures.get("game board"), 100, 100))

        #game and players will be initialized later, when swapped to this layout using the setPlayers and resetGame functions
        self.game_manager = None
        self.white_player = None
        self.black_player = None

        #initialize tile animation - this is responsible for cool effect on black fields
        self.tile_animation = BlackTileAnimation()

    #initialize players
    def setPlayers(self, white_player, black_player):
        #set game reference for both players, then save them. Game reference is used for getting moves, checking whether player should play, etc.
        white_player.setGame(self)
        self.white_player = white_player
        black_player.setGame(self)
        self.black_player = black_player

    #reset game back to default state
    def resetGame(self):
        self.game_manager = GameManager(self.app, DefaultGameState())

    
    def draw(self, surf, time):
        #update black tile animation
        self.tile_animation.update(time)
        
        #draw and update both players - draw move hints for humans, draw compute progress bar for AI
        self.white_player.draw(surf, time)
        self.black_player.draw(surf, time)

        #call parent draw, this updates layout and draws board
        super().draw(surf, time)

        #draw all black squares with animation
        for sqr_pos in allBoardPositions():
            if isValidSquare(sqr_pos):
                self.tile_animation.draw(surf, time, sqr_pos)
        
        #draw all pieces and animations
        self.game_manager.draw(surf, time)

        #draw lines showing currently selected move, these are drawn separately, over pieces
        self.white_player.drawAfterPieces(surf, time)
        self.black_player.drawAfterPieces(surf, time)
    
    #play and animate given moves    
    def playTurn(self, moves):
        self.game_manager.playTurn(moves)

    #get possible moves for current player
    def getPossibleMoves(self, player_color):
        return self.game_manager.getPossibleMoves(player_color)

    #check whether player with given color should play
    def isTurnOf(self, player_color):
        return self.game_manager.isTurnOf(player_color)

    def getGameState(self):
        return self.game_manager.getGameState()



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main