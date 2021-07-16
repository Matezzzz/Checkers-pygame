from texture import DebugTexture
from collisions import RectangleCollisionDetector
from global_defines import *



class PygameObject:
    #Object texture
    texture = None
    def __init__(self, tex):
        self.texture = tex

    #draw object, when provided surface, position and current time
    def draw(self, surf, screen_pos, time):
        surf.blit(self.texture.get(time), screen_pos)

    #change set texture
    def setTexture(self, texture):
        self.texture = texture


#Same as pygame object, but with the same position
class StaticObject(PygameObject):
    pos = (0, 0)
    
    #create object with texture and given pos
    def __init__(self, tex, x, y):
        #call parent constructor
        super().__init__(tex)
        #save position in screen coords
        self.pos = worldToScreenCoords((x, y))
    
    def draw(self, surf, time):
        #draw object with given pos
        super().draw(surf, self.pos, time)



#UI element responds to being hovered by swapping to a different texture
class UIElement(StaticObject):
    #used to detect being hovered by mouse
    collision_detector = None
    #texture when not hovered
    normal_tex = None
    #texture when hovered
    hover_tex = None
    #function that will be called when this object is pressed(with left button)
    pressed_func = None
    #parameters to pass to pressed function
    pressed_func_params = None
    #last time of being pressed - so that one press doesn't create multiple events
    last_pressed = 0.0

    def __init__(self, tex, hover_tex, x, y, collision_detector, pressed_func, pressed_func_params = ()):
        #init parent static object
        super().__init__(tex, x, y)
        #save all given data
        self.normal_tex = tex
        self.hover_tex = hover_tex
        self.collision_detector = collision_detector
        self.pressed_func = pressed_func
        self.pressed_func_params = pressed_func_params

    def draw(self, surf, time):
        #if mouse is inside, set texture to hovered
        if self.mouseInside():
            self.setTexture(self.hover_tex)
            #if is pressed and last press was a long ago
            if mouseLeftButtonPressed() and time - self.last_pressed > 0.1:
                #call pressed func with params
                self.pressed_func(*self.pressed_func_params)
                #save current time as last pressed time
                self.last_pressed = time
        else:
            #set texture to normal if not hovered
            self.setTexture(self.normal_tex)
        #draw object
        super().draw(surf, time)
        
    def mouseInside(self):
        #check with collision detector to find out whether mouse is inside
        return self.collision_detector.pointInside(mouseWorldCoords())



#Same as UI element above, but for rectangular buttons - Collision detector derived from texture size2
class RectangleUIElement(UIElement):
    def __init__(self, x, y, tex, hover_tex, pressed_func, pressed_func_params = ()):
        #Call parent init func. Collision detector will simply check whether mouse is inside of texture rectangle
        super().__init__(tex, hover_tex, x, y,
            RectangleCollisionDetector(x, y, tex.width() / g_texture_scale, tex.height() / g_texture_scale),
            pressed_func, pressed_func_params
        )


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main