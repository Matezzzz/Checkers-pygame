from game_defines import *
import pygame

#animation class - a common base for moving animations
class Animation:
    #time of animation start
    start_time = 0.0
    #how long should the animation last
    duration = 0.0
    
    def __init__(self, duration):
        self.duration = duration

    def start(self, time):
        self.start_time = time

    #returns a value between 0 and 1 based on what part of animation is done already
    def percentDone(self, time):
        return min(1.0, (time - self.start_time) / self.duration)

    #returns true if animation has finished
    def isDone(self, time):
        return (time - self.start_time) >= self.duration

    def reset(self, time):
        self.start_time = time
    
    def update(self, time, game_manager):
        pass

    def end(self, time, game_manager):
        pass


#A simple move animation from one place to another
class MoveAnimation(Animation):
    def __init__(self, duration, p_from, p_to):
        super().__init__(duration)
        self.p_from = p_from
        self.p_to = p_to
    
    #get position in screen coords
    def getPos(self, time):
        t = self.percentDone(time)
        #linear interpolation between start and end based on t
        p = [self.p_from[0] + (self.p_to[0] - self.p_from[0]) * t, self.p_from[1] + (self.p_to[1] - self.p_from[1]) * t]
        return worldToScreenCoords(squareToWorldCoords(p))


#The following are animations with negative duration - they represent an action, done immediately

#Place given token at given position
class PlaceTokenCommand(Animation):
    def __init__(self, pos, token):
        super().__init__(-1)
        self.pos = pos
        self.token = token

    #place token
    def end(self, time, game_manager):
        game_manager.getGameState().setAt(self.pos, self.token)

#Destroy token at given
class DestroyTokenCommand(Animation):
    def __init__(self, pos):
        super().__init__(-1)
        self.pos = pos

    #destroy token
    def end(self, time, game_manager):
        game_manager.getGameState().killAt(self.pos)

#End move command - then, upgrading to queens or passing turn commences
class EndMoveCommand(Animation):
    def __init__(self):
        super().__init__(-1)
    
    def end(self, time, game_manager):
        game_manager.endMove()


#Pass turn to the next player
class PassTurnCommand(Animation):
    def __init__(self):
        super().__init__(-1)
    
    def end(self, time, game_manager):
        game_manager.passTurn()


#Wait for the given time at a given position
class WaitAnimation(Animation):
    def __init__(self, duration, pos):
        super().__init__(duration)
        self.pos = worldToScreenCoords(squareToWorldCoords(pos))
    def getPos(self, time):
        return self.pos


#Upgrade piece at a given position
class UpgradePieceCommand(Animation):
    def __init__(self, pos):
        super().__init__(-1)
        self.pos = pos

    def end(self, time, game_manager):
        game_manager.getGameState().upgradeAt(self.pos)


#abstract base class for all piece move tree objects
class PieceMoveTreeNode:
    #get next moves the piece can do in the same turn, e.g. more jumps in a row
    def getNextMoves(self):
        return []

    #draw the move
    def draw(self, surf, point_color):
        pass

    #create animations for moving the piece
    def createAnimations(self, pos_from):
        return []

    #execute this move - modify game state as if it had happened
    def execute(self, game_state, pos_from):
        pass

    #return move end pos
    def getEndPos(self):
        print ("Get pos not implemented. Error.")


#Moves are represented as a tree - This class forms the root, PieceMove/PieceJump form the rest
class PieceMoveTreeBase(PieceMoveTreeNode):
    #where does the move start
    move_from = [0, 0]
    #what moves can be done next
    next_moves = []

    #save from pos and next set of moves
    def __init__(self, from_pos, next_moves):
        self.move_from = from_pos
        self.next_moves = next_moves
 
    def getEndPos(self):
        #this node only represents beginning of movement, end pos is just move_from
        return self.move_from

    def getNextMoves(self):
        return self.next_moves


#Moves piece from one spot to another
class PieceMove(PieceMoveTreeNode):
    move_to = [0, 0]
    def __init__(self, m_to):
        self.move_to = m_to

    def getEndPos(self):
        return self.move_to

    def draw(self, surf, move_from, line_color, cross_color, point_color):
        #p1 - move start, p2 - move end
        p1 = squareCenterToScreenCoords(move_from)
        p2 = squareCenterToScreenCoords(self.move_to)
        #draw a line between start and end point
        pygame.draw.line(surf, line_color, p1, p2, 2)
        #move circle on end point
        pygame.draw.circle(surf, point_color, p2, 5)

    #move token from first to second pos
    def createAnimations(self, pos_from):
        return [MoveAnimation(0.15, pos_from, self.move_to)]

    #move token in game state
    def execute(self, game_state, from_pos):
        game_state.move(from_pos, self.move_to)


#Move piece from one spot to another, destroy token in between them. Can continue with more jumps
class PieceJump(PieceMove):
    move_over = [0, 0]
    next_jumps = []
    def __init__(self, m_over, m_to, next_jumps):
        super().__init__(m_to)
        self.move_over = m_over
        self.next_jumps = next_jumps

    def getNextMoves(self):
        return self.next_jumps

    def draw(self, surf, move_from, line_color, cross_color, point_color):
        #draw line between start and end points, same as for PieceMove
        super().draw(surf, move_from, line_color, cross_color, point_color)
        #draw a cross over the token to destroy
        p2 = squareCenterToScreenCoords(self.move_over)
        pygame.draw.line(surf, cross_color, (p2[0] - 5, p2[1] - 5), (p2[0] + 5, p2[1] + 5), 3)
        pygame.draw.line(surf, cross_color, (p2[0] - 5, p2[1] + 5), (p2[0] + 5, p2[1] - 5), 3)

    #create animations - move to the token to jump over, destroy it, then continue move to target square
    def createAnimations(self, pos_from):
        return [MoveAnimation(0.1, pos_from, self.move_over), DestroyTokenCommand(self.move_over), MoveAnimation(0.1, self.move_over, self.move_to)]

    
    def execute(self, game_state, from_pos):
        #execute move normally
        super().execute(game_state, from_pos)
        #destroy the token jumped over
        game_state.killAt(self.move_over)


class EmptyMove(PieceMoveTreeNode):
    pass


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main