from global_defines import *
from game_defines import *
from random import randint
import threading
import pygame
from piece_moves import EmptyMove

#Player abstract base class
class Player:
    color = None
    game = None
    next_move = None
    def __init__(self, color, game = None):
        self.color = color
        self.game = game
    
    def setGame(self, game):
        self.game = game

    def draw(self, surf, time):
        pass

    def drawAfterPieces(self, surf, time):
        pass

    def shouldPlay(self):
        return self.game.isTurnOf(self.color)


#Manages one human player
class HumanPlayer(Player):
    #currently selected moves
    current_moves = []
    def __init__(self, color, game = None):
        super().__init__(color, game)
        self.current_moves = []

    def draw(self, surf, time):
        #if the player should play(it's his turn)
        if self.shouldPlay():
            #remove all recorded moves when he presses the right button
            if mouseRightButtonPressed():
                self.current_moves = []

            #if any moves were selected already
            if self.current_moves:
                #next moves is an array of moves that can be played next
                next_moves = self.current_moves[-1].getNextMoves()
                #if there are no next moves, a move was selected whole - play it
                if not next_moves:
                    self.game.playTurn(self.current_moves)
                    #reset current moves array and return
                    self.current_moves = []
                    return
            else:
                #update next moves
                next_moves = self.game.getPossibleMoves(self.color)
            
            #draw a dark red square for every already selected move
            for move in self.current_moves:
                drawBoardSquare(surf, (64, 0, 0), move.getEndPos())

            #coords of square, in which the mouse is
            mouse_pos = worldToSquareCoords(mouseWorldCoords())
            #go over next moves
            for next_move in next_moves:
                move_pos = next_move.getEndPos()
                mouse_inside = positionsEqual(move_pos, mouse_pos)
                #draw a dark green square for every next move, a bit brighter if mouse is inside the next move
                drawBoardSquare(surf, (0, 96 if mouse_inside else 64, 0), move_pos)
                #if mouse is inside next move and is pressed, add next move to the list of moves to play
                if mouse_inside and mouseLeftButtonPressed():
                    self.current_moves.append(next_move)
            
    #draw move hints over pieces
    def drawAfterPieces(self, surf, time):
        #if there are any moves to draw
        if self.current_moves:
            red = (255, 0, 0); green = (0, 255, 0)
            #draw the first move(tree root)
            self.current_moves[0].draw(surf, red)
            #go through the rest of the moves, draw each one
            for i in range(1, len(self.current_moves)):
                self.current_moves[i].draw(surf, self.current_moves[i-1].getEndPos(), green, red, red)

            #draw a line if there is a next move to the square being hovered
            mouse_pos = worldToSquareCoords(mouseWorldCoords())
            #go over all next moves
            for next_move in self.current_moves[-1].getNextMoves():
                #if mouse is inside the next move, draw the line
                if positionsEqual(next_move.getEndPos(), mouse_pos):
                    next_move.draw(surf, self.current_moves[-1].getEndPos(), green, red, red)


#Go through all possible move combinations, used for AI
def iterateAllPossibleMoves(possible_moves):
    if not possible_moves:
        yield [EmptyMove()]
        return
    for mv in possible_moves:
        yield from iterateOverMoves([mv])

#Iterate through one move tree, preorder
def iterateOverMoves(current_moves):
    #if there are no next moves, yield current move array
    next_moves = current_moves[-1].getNextMoves()
    if len(next_moves) == 0: yield current_moves
    #if there are next moves, go through all of them
    for move in next_moves:
        #add current move to the array
        current_moves.append(move)
        #iterate over all of it's child moves
        yield from iterateOverMoves(current_moves)
        #remove current move from the array
        current_moves.pop()



#A thread used for AI player to not stop the game completely when the AI is computing its' next move.
class AIPlayerThread:
    #thread handle
    thread = None
    #how large a part of the computation was finished already, in percent
    compute_progress = 0.0
    def __init__(self, color, game_state, depth):
        #create a new thread
        self.thread = threading.Thread(target=self.start, args=(color, game_state, depth))
        #result to be computed by the thread
        self.result = None
        #start the computation
        self.thread.start()

    def start(self, color, game_state, depth):
        #compute optimal move
        self.result = self.findOptimalMove(color, game_state, depth)

    def findOptimalMove(self, color, game_state, depth):
        possible_moves = None
        try:
            #find possible moves for current game
            must_jump, possible_moves = game_state.findPossibleMovesForPlayerOfColor(color)
            #find how good each of previously found moves is
            weights = self.findMoveWeights(color, game_state, depth)
            #weights are done from the viewpoint of white -> larger numbers are good for him. Select min/max number based on player color
            target = max(weights) if color == COLOR_WHITE else min(weights)
            
            #how many weights are there with the same value as target, then select a random move. This is done to prevent AI from looping the same move over and over again.
            count = sum([1 if abs(target-w) < 1e-10 else 0 for w in weights])
            #index of the move to select
            a = randint(0, count - 1)
            
            a_i = 0
            i = 0
            #go through all possible moves, select the one with the correct index
            for moves in iterateAllPossibleMoves(possible_moves):
                if abs(weights[i] - target) < 1e-10:
                    if a_i == a:
                        return moves
                    a_i += 1
                i += 1
            print("Move with correct index not found.")
            #return first available move
            for moves in iterateAllPossibleMoves(possible_moves):
                return moves
        #If AI crashes for any reason, return first possible move, better than having the game freeze.
        except:
            for moves in iterateAllPossibleMoves(possible_moves):
                return moves

        
    def findMoveWeights(self, player_color, game_state, depth, progress = 0.0, importance_mult = 1.0):
        #progress bar explanation - progress marks the part of bar done already, importance mult is the change, which will occur after this instance of the function finishes running
        #Since this function can be split into multiple parts(total mark_c), one for each move, progress bar can be updated once per each part completion

        #how good is each individual move for the white player
        move_weights = []
        #find all possible moves
        must_jump, possible_moves = game_state.findPossibleMovesForPlayerOfColor(player_color)
        #how large a part was done already, used for progress bar
        done_c = 0
        #how many parts there are in total
        move_c = sum(1 for m in iterateAllPossibleMoves(possible_moves))
        #go over all possible moves
        for moves in iterateAllPossibleMoves(possible_moves):
            #create new game state, then execute moves on it
            new_game_state = game_state.copy()
            for i in range(1, len(moves)):
                moves[i].execute(new_game_state, moves[i-1].getEndPos())
            #depth specifies how many moves should be predicted in advance. If no more should be predicted, assess game state
            if depth == 0:
                #count pieces
                w, b = new_game_state.countPieces()
                #value on each side, queen is equal to three normal pieces
                val_w = w[0] + 3*w[1]; val_b = b[0] + 3*b[1]
                #assess how good the position is for the white player - ratio of white to black pieces
                ratio_w = float("inf") if val_b == 0 else val_w / val_b
                #append computed weight to the list
                move_weights.append(ratio_w)
            else:
                #find weights for the next set of moves
                weights = self.findMoveWeights(invertColor(player_color), new_game_state, depth-1, self.compute_progress, importance_mult / move_c)
                #if current player is black, the next one is white -> he will chose the best move for himself, or the largest value. Black will chose the smallest one.
                if player_color == COLOR_BLACK:
                    move_weights.append(max(weights))
                else:
                    move_weights.append(min(weights))
            #increase amount of done sections
            done_c += 1
            #udpdate progress bar
            self.compute_progress = progress + done_c * importance_mult / move_c
        return move_weights

    #get computed result, or none if there isn't one yet
    def getResult(self):
        return self.result

    #whether the thread is still running
    def isAlive(self):
        return self.thread.is_alive()

    #how large a part was done already, in percent
    def getProgress(self):
        return self.compute_progress


#AI player
class AIPlayer(Player):
    compute_thread = None
    #difficulty - amount of moves predicted in advance
    def __init__(self, color, difficulty, game = None):
        super().__init__(color, game)
        self.difficulty = difficulty

    def draw(self, surf, time):
        #if AI should play
        if self.shouldPlay():
            #if there isn't a compute thread for this move yet, create one
            if self.compute_thread == None:
                self.compute_thread = AIPlayerThread(self.color, self.game.getGameState().copy(), self.difficulty)
            #draw progress bar for the computation
            #select y value - progress bar is over the board for white or under for black
            y = 45 if self.color == COLOR_WHITE else 925
            #draw gray background
            pygame.draw.rect(surf, (128, 128, 128), (worldToScreenCoords((100, y)), (int(800*g_texture_scale), int(30*g_texture_scale))))
            #draw part progressed - white for white, dark gray for black
            pygame.draw.rect(surf, 
                (255, 255, 255) if self.color == COLOR_WHITE else (64, 64, 64),\
                (worldToScreenCoords((103, y+3)),\
                (int(794 * self.compute_thread.getProgress()*g_texture_scale), int(24 * g_texture_scale))))
            #try getting the result
            result = self.compute_thread.getResult()
            #if there is a result and the thread has finished running, play turn and discard thread handle
            if not self.compute_thread.isAlive() and result:
                self.game.playTurn(result)
                self.compute_thread = None
            

   



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main