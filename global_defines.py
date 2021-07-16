import pygame


#Here, it should be possible to modify screen size and UI scale freely. However, this feature is experimental and isn't tested, things might be shifted or otherwise broken for some values.

#screen width and height in pixels.
g_screen_width = 1000
g_screen_height = 1000
g_texture_scale = 1.0

#offset on non-square screens. 
g_x_offset = max(0, g_screen_width - g_screen_height) // 2
g_y_offset = max(0, g_screen_height - g_screen_width) // 2


#convert world coordinates (0 - 1000 for both axes) to screen coordinates (0-screen_width/height)
def worldToScreenCoords(pos):
    return (int(g_x_offset + pos[0] * g_texture_scale), int(g_y_offset + pos[1] * g_texture_scale))

#convert screen coords to world coords
def screenToWorldCoords(scr_pos):
    return (int((scr_pos[0] - g_x_offset) / g_texture_scale), int((scr_pos[1] - g_y_offset) / g_texture_scale))

#get mouse world coordinates
def mouseWorldCoords():
    return screenToWorldCoords(pygame.mouse.get_pos())

#check whether button with given index is pressed
def mouseButtonPressed(b):
    return pygame.mouse.get_pressed()[b]

def mouseLeftButtonPressed():
    return mouseButtonPressed(0)

def mouseRightButtonPressed():
    return mouseButtonPressed(2)


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main