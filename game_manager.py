from texture_loader import textures
from game_defines import *
from objects import PygameObject
from piece_moves import DestroyTokenCommand, EndMoveCommand, PassTurnCommand, PlaceTokenCommand, UpgradePieceCommand, WaitAnimation



#abstract base class for animations
class GameManagerAnimation:
    #currently running animation
    anim_i = 0
    #list of all animations and commands (e.g. for one JUMP would be [MOVE_TO_PLACE_OF_KILL, DESTROY_ENEMY_TOKEN, MOVE_TO_END_FIELD])
    animations = []
    #piece object to animate
    piece = None
    #whether animation has finished yet
    is_running = True
    #last position where token was present, used for drawing after animation is finished
    last_pos = (0, 0)

    is_started = False
    def __init__(self, piece, anims):
        self.animations = anims
        #save piece object
        self.piece = piece
        #reset last pos
        self.last_pos = (0, 0)

    def draw(self, surf, time, game_manager):
        if not self.is_started:
            self.animations[0].start(time)
            self.is_started = True
        #iterate over all finished animations
        if self.anim_i < len(self.animations):
            while self.animations[self.anim_i].isDone(time):
                #end finished animation
                self.animations[self.anim_i].end(time, game_manager)
                self.anim_i += 1
                #if there are more animations that should run
                if self.anim_i < len(self.animations):
                    #increase animation index and start next animation
                    self.animations[self.anim_i].start(time)
                #if all animations are finished, proclaim whole move as finished
                else:
                    self.is_running = False
                    #draw piece one last time, prevents token from going missing for one frame
                    self.piece.draw(surf, self.last_pos, time)
                    return
        #if animation is running, update last pos and draw token
        if self.is_running:
            self.last_pos = self.animations[self.anim_i].getPos(time)
            self.piece.draw(surf, self.last_pos, time)
    
    def isDone(self):
        return not self.is_running


#Animates piece movement
class PieceMoveAnimation(GameManagerAnimation):
    def __init__(self, moves, piece, game_manager):
        
        p = moves[0].getEndPos()
        animations = []
        #start move by destroying token on board
        animations.append(DestroyTokenCommand(p))
        #do all move animations, these are created from given moves
        for i in range(1, len(moves)):
            animations = animations + moves[i].createAnimations(moves[i-1].getEndPos())
        #end move by putting token back to the board
        animations.append(PlaceTokenCommand(moves[-1].getEndPos(), game_manager.getGameState().at(p)))
        #pass turn to the other player
        animations.append(EndMoveCommand())

        super().__init__(piece, animations)
    
    


#Animates upgrading to queen
class QueenUpgradeAnimation(GameManagerAnimation):
    def __init__(self, pos):
        #get animated texture
        self.tex = textures.get("queen animation")
        #create object for animated texture
        piece = PygameObject(self.tex)
        #init parent object with animations - first wait for the animation to finish, then upgrade the piece in game state, then pass the turn
        super().__init__(piece, [WaitAnimation(34*0.01, pos), UpgradePieceCommand(pos), PassTurnCommand()])
        #whether texture animation has started already
        self.started = False

    def draw(self, surf, time, game_manager):
        #start texture animation if it hasn't been done before
        if not self.started:
            self.tex.start(time)
            self.started = True
        #draw the piece
        super().draw(surf, time, game_manager)




class GameManager:
    #Objects for drawing all piece types
    white_piece_tex = None
    black_piece_tex = None
    white_queen_tex = None
    black_queen_tex = None

    #all animations running at the present moment
    running_animations = []

    #currently playing player
    active_player_color = COLOR_WHITE
    active_player_has_to_jump = False
    #tree of moves available to current player
    active_player_possible_moves = None

    #current game state - positions of all tokens
    game_state = None

    #reference to application class, used to swap to victory screen when somebody has won
    app = None
    def __init__(self, app, game_state):
        #initialize all piece objects
        self.white_piece = PygameObject(textures.get("piece white"))
        self.black_piece = PygameObject(textures.get("piece black"))
        self.white_queen = PygameObject(textures.get("queen white"))
        self.black_queen = PygameObject(textures.get("queen black"))
        #initialize game state
        self.game_state = game_state
        self.running_animations = []
        self.active_player_color = COLOR_WHITE
        #find moves available to current player
        self.updateActivePlayerMoves()
        self.app = app

    def draw(self, surf, time):
        #iterate over all board positions, draw all pieces
        for sqr_pos in allBoardPositions():
            piece_obj = self.getPieceObjectAt(sqr_pos)
            #if there is a piece on current field
            if piece_obj:
                piece_obj.draw(surf, worldToScreenCoords(squareToWorldCoords(sqr_pos)), time)
        #are there any animations left running
        anims_running = False
        for anim in self.running_animations:
            #draw animation
            anim.draw(surf, time, self)
            #set bool if anim is still running
            if not anim.isDone(): anims_running = True
        #if no animations are running, empty the list, this is a simple version of removing redundant, finished animations
        if anims_running == False:
            self.running_animations = []

    #Play turn as current player
    def playTurn(self, moves):
        #create animation from current moves, remove all possible moves
        self.running_animations.append(PieceMoveAnimation(moves, self.getPieceObjectAt(moves[0].getEndPos()), self))
        self.active_player_possible_moves = []

    #get all possible moves for player of given color
    def getPossibleMoves(self, player_color):
        #if it's the turn of given player, return his moves
        if self.active_player_color == player_color:
            return self.active_player_possible_moves
        #otherwise, he has no available moves at all
        else:
            return []
    
    
    #end move and try promoting to queens, pass turn if no promotion happens
    def endMove(self):
        #upgrade all tokens on end fields to queens, if there were no upgrades, pass turn immediately
        if not self.game_state.upgradeAllViableToQueens(self):
            self.passTurn()

    #pass turn to next player
    def passTurn(self):
        #check whether somebody has won
        game_status = self.game_state.checkGameStatus()
        #if somebody did, end game and announce winner
        if game_status != GAME_STATE_UNDECIDED:
            self.app.endGame(game_status)

        #transfer turn to other player
        self.transferTurn()
        #find out next set of possible moves
        self.updateActivePlayerMoves()
        #if there are no moves available for the next player, just skip his turn
        if self.active_player_possible_moves == []:
            self.passTurn()

    def upgradeQueenAt(self, pos):
        self.running_animations.append(QueenUpgradeAnimation(pos))

    #get piece object at given position
    def getPieceObjectAt(self, pos):
        piece = self.game_state.at(pos)
        #return one of four piece objects based on piece type at given pos
        if piece.isWhite():
            return self.white_piece if piece.isNormal() else self.white_queen
        elif piece.isBlack():
            return self.black_piece if piece.isNormal() else self.black_queen
        return None

    #update active player moves
    def updateActivePlayerMoves(self):
        self.active_player_has_to_jump, self.active_player_possible_moves = self.game_state.findPossibleMovesForPlayerOfColor(self.active_player_color)

    #swap player color
    def transferTurn(self):
        self.active_player_color = invertColor(self.active_player_color)

    def getGameState(self):
        return self.game_state
    
    #all animations must be finished before a player can play
    def isTurnOf(self, player_color):
        return (self.active_player_color == player_color) and len(self.running_animations) == 0


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main