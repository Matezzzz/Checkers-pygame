from game_defines import *
from piece_moves import PieceMove, PieceJump, PieceMoveTreeBase
from copy import deepcopy

FLAG_MOVES_NORMAL = 1
FLAG_MOVES_JUMPS = 2


#Square state - Holds state of one board square
class SquareState:
    #piece color - NONE/EMPTY/BLACK/WHITE
    color = COLOR_NONE
    #piece type - NONE/NORMAL/QUEEN
    p_type = PIECE_TYPE_NORMAL
    def __init__(self, piece_id):
        #convert piece id to color & piece type
        self.color = COLOR_BLACK if (piece_id == CREATE_PIECE_BLACK_NORMAL or piece_id == CREATE_PIECE_BLACK_QUEEN) else\
                    (COLOR_WHITE if (piece_id == CREATE_PIECE_WHITE_NORMAL or piece_id == CREATE_PIECE_WHITE_QUEEN) else
                    (COLOR_EMPTY if (piece_id == COLOR_EMPTY) else\
                     COLOR_NONE))
        self.p_type = PIECE_TYPE_NORMAL if (piece_id == CREATE_PIECE_WHITE_NORMAL or piece_id == CREATE_PIECE_BLACK_NORMAL) else (PIECE_TYPE_QUEEN if (piece_id == CREATE_PIECE_WHITE_QUEEN or piece_id == CREATE_PIECE_BLACK_QUEEN) else PIECE_TYPE_NONE)
    
    def isEmpty(self):
        return self.color == COLOR_EMPTY
    def isWhite(self):
        return self.color == COLOR_WHITE
    def isBlack(self):
        return self.color == COLOR_BLACK
    def isOfColor(self, color):
        return self.color == color
    def isNormal(self):
        return self.p_type == PIECE_TYPE_NORMAL
    def isQueen(self):
        return self.p_type == PIECE_TYPE_QUEEN
    def isValid(self):
        return self.color != COLOR_NONE
    def isEnemyOf(self, target):
        return self.color != target.color and target.color != COLOR_EMPTY and target.color != COLOR_NONE
    def upgradeToQueen(self):
        self.p_type = PIECE_TYPE_QUEEN

    #move set is specified by an array a- a[0] represents distance that the piece can travel, a[1] is a list of all supported directions 
    def getMoveSet(self):
        if self.isNormal():
            #select different direction (up/down) based on piece color
            dy = 1 if self.isOfColor(COLOR_WHITE) else -1
            return (1, [[-1, dy], [1, dy]])
        #if queen, all directions are enabled, distance enables travel to any distance
        elif self.isQueen():
            return (max(gm_board_size_x, gm_board_size_y), [[-1, -1], [-1, 1], [1, 1], [1, -1]])
    
    #convert self to string. Uses unicode chess piece characters.
    def __str__(self):
        if self.isWhite():
            return "\u2655" if self.isQueen() else "\u2659"
        elif self.isBlack():
            return "\u265B" if self.isQueen() else "\u265F"
        else:
            return " "





#Makes sure infinite recursion doesn't occur when searching for jumps. Holds 
#   O
#  O O      -E.g. in this case, Q is white queen, O are black pieces - as pieces are not removed during searching, the queen would be able to jump any number of times in the circle, this would crash the program
#   O
#  Q
DEPTH_A_LOT = 100
class DepthArray:
    a = []
    def __init__(self, w, h):
        self.a = [[False for x in range(w)] for y in range(h)]
    def jumpedAt(self, pos):
        return self.a[pos[1]][pos[0]]
    def jumpAt(self, pos):
        self.a[pos[1]][pos[0]] = True
    def unjumpAt(self, pos):
        self.a[pos[1]][pos[0]] = False
    def reset(self):
        self.__init__(len(self.a[0]), len(self.a))



#Holds current game state. Is responsible for searching for available moves
class GameState:
    state = None
    jump_depths = None
    def __init__(self, state):
        #create SquareState for every field
        self.state = [[SquareState(e) for e in r] for r in state]
        #initialize jump depths array
        self.jump_depths = DepthArray(gm_board_size_x, gm_board_size_y)

    def at(self, pos):
        return self.state[pos[1]][pos[0]]
    
    def setAt(self, pos, new):
        self.state[pos[1]][pos[0]] = new

    #destroy piece at given position
    def killAt(self, pos):
        self.setAt(pos, SquareState(CREATE_PIECE_EMPTY))

    def upgradeAt(self, pos):
        self.at(pos).upgradeToQueen()

    #move piece from given pos to new one. Now, is used only for computing AI, as normal moves are done using animations.
    def move(self, pos_from, pos_to):
        a = self.at(pos_to)
        self.setAt(pos_to, self.at(pos_from))
        self.setAt(pos_from, a)

    #count pieces of all types. Return a tuple ((w_n, w_q), (b_n, b_q)) - w_n is count of white normal pieces, w_q of white queens. Same for black.
    def countPieces(self):
        #same as wn, wq, bn, bq
        w0 = 0; w1 = 0; b0 = 0; b1 = 0
        for pos in allBoardPositions():
            p = self.at(pos)
            if p.isWhite():
                if p.isNormal(): w0 += 1
                else: w1 += 1
            if p.isBlack():
                if p.isNormal(): b0 += 1
                else: b1 += 1
        return (w0, w1), (b0, b1)
    
    #identify current game status. Can be - UNDECIDED/WHITE_WON/BLACK_WON/DRAW
    def checkGameStatus(self):
        wh, bl = self.countPieces()
        #count white and black piece count
        wh = sum(wh); bl = sum(bl)
        #if there aren't any white pieces
        if wh == 0:
            #if there aren't any black pieces either - this, well, cannot happen in normal version of the game. The game would end in a draw.
            if bl == 0:
                return GAME_STATE_DRAW
            #if black has pieces and white doesn't, black wins
            return GAME_STATE_BLACK_WON
        #if there aren't any black pieces, white wins
        if bl == 0:
            return GAME_STATE_WHITE_WON
        #if neither of the above is true, the game hasn't been decided yet
        return GAME_STATE_UNDECIDED

    #find normal moves for all pieces of given color
    def findAllMoves(self, player_color):
        moves = []
        #iterate over all pieces of player
        for pos, player_piece in self.iterOverAllPlayerPieces(player_color):
            #find all available moves for current piece, append them to the array if any are available
            cur_moves = self.findMoves(player_piece, pos)
            if cur_moves: moves.append(PieceMoveTreeBase(pos, cur_moves))
        return moves

    #find jumps for all pieces of given color
    def findAllJumps(self, player_color):
        jumps = []
        #iterate over all pieces of player
        for pos, player_piece in self.iterOverAllPlayerPieces(player_color):
            #find all jumps for current piece, append them if any were found
            cur_jumps = self.findJumps(player_piece, pos)
            if cur_jumps: jumps.append(PieceMoveTreeBase(pos, cur_jumps))
        return jumps

    #generator for all pieces of given player
    def iterOverAllPlayerPieces(self, player_color):
        #go over all board positions
        for pos in allBoardPositions():
            piece = self.at(pos)
            #if piece is of player color, yield it
            if piece.isOfColor(player_color):
                yield pos, piece
            
    #find all normal moves for a given piece
    def findMoves(self, piece, pos):
        targets = []
        #get all available directions and max dist the piece can travel
        max_dist, moves = piece.getMoveSet()
        #iterate over all directions
        for dx, dy in moves:
            #iterate over all distances
            for dist in range(1, max_dist + 1):
                #the pos the piece would arrive at
                pos_target = (pos[0] + dist * dx, pos[1] + dist * dy)
                #if not in bounds, search the next direction
                if not squareInBounds(pos_target): break
                #the position the piece would arrive at
                target = self.at(pos_target)
                #if target isn't empty, it blocks current piece from travelling further in this direction, search the next direction
                if not target.isEmpty(): break
                #else, piece can move to the target spot. Save the move.
                targets.append(PieceMove(pos_target))
        return targets

    #find all jumps for a given piece
    def findJumps(self, piece, pos):
        targets = []
        #get all available directions and max dist the piece can travel
        max_dist, moves = piece.getMoveSet()
        #iterate over all directions
        for dx, dy in moves:
            #iterate over all distances
            for dist in range(1, max_dist + 1):
                #current position being iterated is the position of enemy to jump
                pos_enemy = (pos[0] + dist * dx, pos[1] + dist * dy)
                #if pos is out of bounds, continue to next direction
                if not squareInBounds(pos_enemy): break
                #get token at enemy pos
                enemy = self.at(pos_enemy)
                #if the spot isn't empty
                if not enemy.isEmpty():
                    #the jump depth at the position of enemy being jumped
                    #if the target token is an enemy and it hasn't been jumped by this token before
                    if enemy.isEnemyOf(piece) and not self.jump_depths.jumpedAt(pos_enemy):
                        #compute the pos the jumping token would end at if it were to jump the enemy
                        pos_end = (pos_enemy[0] + dx, pos_enemy[1] + dy)
                        #if it's in bounds
                        if squareInBounds(pos_end):
                            #if the end spot is empty, this jump is valid, save it. Also, try searching for next jumps from target position.
                            end = self.at(pos_end)
                            if end.isEmpty():
                                #set mark token at the position of enemy as jumped
                                self.jump_depths.jumpAt(pos_enemy)
                                #search for next jumps with new depth set
                                targets.append(PieceJump(pos_enemy, pos_end, self.findJumps(piece, pos_end)))
                                #make enemy not jumped anymore
                                self.jump_depths.unjumpAt(pos_enemy)
                    #if spot wasn't empty, break
                    break
        return targets

    #find all moves for a player of given color
    def findPossibleMovesForPlayerOfColor(self, player_color):
        #try finding all jumps
        moves = self.findAllJumps(player_color)
        #if there are any, return them, with must_jump flag set to True
        if moves: return (True, moves)
        #otherwise, return all normal moves, must_jump flag is False
        return (False, self.findAllMoves(player_color))

    #return a copy of game state - is used for AI player
    def copy(self):
        return deepcopy(self)

    #upgrade all viable pieces to queens
    def upgradeAllViableToQueens(self, game_manager):
        #go over all black fields at ends of board, upgrade all viable pieces to queens
        for i in range(4):
            pos = (2*i+1, 0)
            piece = self.at(pos)
            if piece.isBlack() and piece.isNormal():
                game_manager.upgradeQueenAt(pos)
                return True
            pos = (2*i, gm_board_size_y - 1)
            piece = self.at(pos)
            if piece.isWhite() and piece.isNormal():
                game_manager.upgradeQueenAt(pos)
                return True
        return False

    #convert game state to string - was used for a while for debugging
    def __str__(self):
        s = ""
        for y in range(gm_board_size_y):
            for x in range(gm_board_size_x):
                s += str(self.state[y][x]) + " "
            s += "\n"
        return s


#starting game state
#0 = none, 1 = empty, 2 = white, 3 = white queen, 4 = black, 5 = black queen, same as CREATE_PIECE_*** from game_defines.py, is kept like this to be easier to read and write
class DefaultGameState(GameState):
    def __init__(self):
        super().__init__([
            [0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 2, 0, 2, 0, 2, 0],
            [0, 2, 0, 2, 0, 2, 0, 2],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [4, 0, 4, 0, 4, 0, 4, 0],
            [0, 4, 0, 4, 0, 4, 0, 4],
            [4, 0, 4, 0, 4, 0, 4, 0]
        ])

#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main