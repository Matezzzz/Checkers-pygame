from objects import RectangleUIElement, StaticObject, UIElement
from texture_loader import textures
from player import HumanPlayer, AIPlayer
from global_defines import *
from game_defines import GAME_STATE_WHITE_WON, COLOR_BLACK, COLOR_WHITE
from particle_anim import ParticleAnimation


#Layout holds UI objects and draws them
class Layout:
    app = None
    elements = []
    def __init__(self, app):
        self.app = app
        self.elements = []

    #add given object to this layout. It will be drawn every frame.
    def add(self, element):
        self.elements.append(element)

    #draw all objects
    def draw(self, surf, time):
        for e in self.elements:
            e.draw(surf, time)


#Layout for modifying new game settings, then starting the game - Select player types and bot difficulty
class NewGameSettings(Layout):
    def __init__(self, app):
        super().__init__(app)
        #whether given player is played by human or by AI
        self.white_human = True
        self.black_human = False

        #default bot difficulty for each player. Doesn't apply to humans. 
        self.white_difficulty = 2
        self.black_difficulty = 2
        #get textures for each of 4 levels of difficulty
        self.difficulties = [textures.get("difficulty " + str(i)) for i in range(1, 5)]

        #get textures for human, easy bot and hard bot
        self.human_tex = textures.get("human")
        self.easy_bot_tex = textures.get("bot easy")
        self.hard_bot_tex = textures.get("bot supreme")
        
        #get textures for all buttons. Up on end = texture isn't being hovered.
        tex_add_up = textures.get("button add up"); tex_add_down = textures.get("button add down")
        tex_sub_up = textures.get("button sub up"); tex_sub_down = textures.get("button sub down")
        tex_swp_up = textures.get("button swap player type up"); tex_swp_down = textures.get("button swap player type down")

        #white bot difficulty object, texture updated each frame based on selected difficulty
        self.white_bot_diff = StaticObject(None, 100, 200)
        #button for adding white bot difficulty
        self.white_bot_add = RectangleUIElement(100, 125, tex_add_up, tex_add_down, self.changeWhiteDifficulty, [ 1])
        #button for subtracting white bot difficulty
        self.white_bot_sub = RectangleUIElement(100, 350, tex_sub_up, tex_sub_down, self.changeWhiteDifficulty, [-1])
        #white player profile pic - either human, bot easy or bot hard
        self.white_avatar = StaticObject(None, 300, 200)
        #white piece object - is above player pic to signal that they will be playing as white
        self.add(StaticObject(textures.get("piece white"), 325, 100))
        #button to swap between human and bot for white player
        self.add(RectangleUIElement(300, 350, tex_swp_up, tex_swp_down, self.swapWhitePlayer))

        
        #same objects for black as they were for white
        self.black_bot_diff = StaticObject(None, 750, 200)
        self.black_bot_add = RectangleUIElement(750, 125, tex_add_up, tex_add_down, self.changeBlackDifficulty, [ 1])
        self.black_bot_sub = RectangleUIElement(750, 350, tex_sub_up, tex_sub_down, self.changeBlackDifficulty, [-1])
        self.black_avatar = StaticObject(None, 550, 200)
        self.add(StaticObject(textures.get("piece black"), 575, 100))
        self.add(RectangleUIElement(550, 350, tex_swp_up, tex_swp_down, self.swapBlackPlayer))
    
        #small vs. text between players
        self.add(StaticObject(textures.get("versus"), 475, 250))

        #start game button
        self.add(RectangleUIElement(150, 775, textures.get("button up"), textures.get("button down"), self.startGame))
    

    def draw(self, surf, time):
        #draw all unconditional UI elements
        super().draw(surf, time)
        #if white is human, set his texture as such
        if self.white_human:
            self.white_avatar.setTexture(self.human_tex)
        else:
            #if white is bot, set his texture based on difficulty(easy/hard)
            self.white_avatar.setTexture(self.hard_bot_tex if self.white_difficulty == 3 else self.easy_bot_tex)
            #update bot difficulty texture
            self.white_bot_diff.setTexture(self.difficulties[self.white_difficulty])
            #draw bot difficulty, and buttons to increase/decrease it
            self.white_bot_diff.draw(surf, time)
            self.white_bot_add.draw(surf, time)
            self.white_bot_sub.draw(surf, time)
        #draw white avatar
        self.white_avatar.draw(surf, time)

        #functions for black are same as they are for white
        if self.black_human:
            self.black_avatar.setTexture(self.human_tex)
        else:
            self.black_avatar.setTexture(self.hard_bot_tex if self.black_difficulty == 3 else self.easy_bot_tex)
            self.black_bot_diff.setTexture(self.difficulties[self.black_difficulty])
            self.black_bot_diff.draw(surf, time)
            self.black_bot_add.draw(surf, time)
            self.black_bot_sub.draw(surf, time)
        self.black_avatar.draw(surf, time)
            
    #change white difficulty by the given constant. Difficulty is clamped to max 3(or 4 in textures)
    def changeWhiteDifficulty(self, dif):
        self.white_difficulty = min(max(self.white_difficulty + dif, 0), 3)

    #change black difficulty by the given constant. Difficulty is clamped to max 3(or 4 in textures)
    def changeBlackDifficulty(self, dif):
        self.black_difficulty = min(max(self.black_difficulty + dif, 0), 3)

    #swap white from human to AI or vice-versa
    def swapWhitePlayer(self):
        self.white_human = not self.white_human

    #swap black from human to AI or vice-versa
    def swapBlackPlayer(self):
        self.black_human = not self.black_human

    #start game
    def startGame(self):
        #create a Player object for black and white based on their respective settings
        w = HumanPlayer(COLOR_WHITE) if self.white_human else AIPlayer(COLOR_WHITE, self.white_difficulty + 2)
        b = HumanPlayer(COLOR_BLACK) if self.black_human else AIPlayer(COLOR_BLACK, self.black_difficulty + 2)
        #start game with created players
        self.app.startGame(w, b)


#Layout for victory screen
class VictoryScreen(Layout):
    #who actually won
    status = None
    def __init__(self, app):
        super().__init__(app)
        #get both win textures
        self.white_win_tex = textures.get("white win"); self.black_win_tex = textures.get("black win")
        #prepare object for win message
        self.win_message = StaticObject(None, 100, 400)


    def draw(self, surf, time):
        #update particle effect
        self.animation.update(time)
        #draw particle effect as background
        surf.blit(self.animation.getRender(), (0, 0))
        #draw win message
        self.win_message.draw(surf, time)

    #has to be called when switching to this layout, specifies who won
    def setStatus(self, status):
        #save status
        self.status = status
        #choose colors for particle effect based on the victor. Meaning - particle color, background color, particle count
        pc, bg, n = ((255, 255, 255), (50, 50, 50), 400) if status == GAME_STATE_WHITE_WON else ((0, 0, 0), (150, 150, 150), 1000)
        #create particle effect with params above
        self.animation = ParticleAnimation(g_screen_width, g_screen_height, pc, bg, n)
        #set win message texture
        self.win_message.setTexture(self.white_win_tex if self.status == GAME_STATE_WHITE_WON else self.black_win_tex)



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main

        