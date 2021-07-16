from global_defines import *


#board size should match textures
gm_board_width = 800
gm_board_height = 800
gm_board_size_x = 8
gm_board_size_y = 8
#is 1000 and not screen width/height to match world coords size
gm_board_offset_x = (1000 - gm_board_width) // 2
gm_board_offset_y = (1000 - gm_board_height) // 2
gm_tile_width = gm_board_width // gm_board_size_x
gm_tile_height = gm_board_height // gm_board_size_y


#These values are only used to convert ID based representation of game state to an array of SquareStates
#None = white board spot, no tokens will ever move here
#Empty = tokens can move here, but none are present right now
CREATE_PIECE_NONE = 0
CREATE_PIECE_EMPTY = 1
CREATE_PIECE_WHITE_NORMAL = 2
CREATE_PIECE_WHITE_QUEEN = 3
CREATE_PIECE_BLACK_NORMAL = 4
CREATE_PIECE_BLACK_QUEEN = 5

#Enum of all player and token colors
COLOR_NONE = 0
COLOR_EMPTY = 1
COLOR_WHITE = 2
COLOR_BLACK = 3

#Enum of all piece types
PIECE_TYPE_NONE = 0
PIECE_TYPE_NORMAL = 1
PIECE_TYPE_QUEEN = 2

#Enum of all possible game states
GAME_STATE_UNDECIDED = 0
GAME_STATE_DRAW = 1
GAME_STATE_WHITE_WON = 2
GAME_STATE_BLACK_WON = 3


#Return a generator over all board positions
def allBoardPositions():
    for x in range(gm_board_size_x):
        for y in range(gm_board_size_y):
            yield (x, y)

#draw board square with given color and coordinates
def drawBoardSquare(surf, color, sqr_pos, border = 0):
    pygame.draw.rect(surf, color, pygame.Rect(*getSquareRect(sqr_pos, border)))

#compare two sets of coordinates, return true if they are equal
def positionsEqual(pos1, pos2):
    return (pos1[0] == pos2[0] and pos1[1] == pos2[1])

#convert square coordinates to world coordinates of squares' upper left corner
def squareToWorldCoords(sqr_pos):
    return (sqr_pos[0] * gm_tile_width + gm_board_offset_x, sqr_pos[1] * gm_tile_height + gm_board_offset_y)

#convert world coords to square ones
def worldToSquareCoords(pos):
    return ((pos[0] - gm_board_offset_x) // gm_tile_width, (pos[1] - gm_board_offset_y) // gm_tile_height)

#return square center in screen coordinates
def squareCenterToScreenCoords(sqr_pos):
    return worldToScreenCoords(squareToWorldCoords([sqr_pos[0] + 0.5, sqr_pos[1]+0.5]))

#return rectangle describing square at given pos. Boundary width is size of border around square, square will be smaller by this value
def getSquareRect(sqr_pos, boundary_width = 0):
    s_x, s_y = worldToScreenCoords(squareToWorldCoords(sqr_pos))
    w, h = (gm_tile_width, gm_tile_height)
    if boundary_width:
        s_x += boundary_width / 2; s_y += boundary_width / 2
        w -= boundary_width; h -= boundary_width
    return ((s_x, s_y), (g_texture_scale*w, g_texture_scale*h))

#check whether square position is in board bounds
def squareInBounds(sqr_pos):
    return (0 <= sqr_pos[0] < gm_board_size_x and 0 <= sqr_pos[1] < gm_board_size_y)

#Assumes default square pattern
def isValidSquare(sqr_pos):
    return (squareInBounds(sqr_pos) and (sqr_pos[0] - sqr_pos[1]) % 2)

#invert given color
def invertColor(color):
    if color == COLOR_WHITE: return COLOR_BLACK
    if color == COLOR_BLACK: return COLOR_WHITE
    return COLOR_NONE


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main