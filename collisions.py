from global_defines import *

#checks whether the mouse is inside a rectangle
class RectangleCollisionDetector:
    #rectangle parameters
    x = 0
    y = 0
    width = 0
    height = 0
    def __init__(self, x_pos, y_pos, width, height):
        self.x = x_pos
        self.y = y_pos
        self.width = width
        self.height = height

    def pointInside(self, pos):
        x, y = pos
        #return true if pos is inside of rect, false othewise
        return (x >= self.x and x < self.x + self.width and y >= self.y and y < self.y + self.height)



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main