import pygame

#abstract base class for all textures
class Texture:
    def get(self, time):
        print ("Get not implemented in derived class.")


#Basic, 1-surface texture
class BasicTexture(Texture):
    surface = None
    def __init__(self, surface):
        self.surface = surface
    def get(self, time):
        return self.surface
    #smoothscale the texture to the new size
    def rescale(self, new_width, new_height):
        self.surface = pygame.transform.smoothscale(self.surface, (new_width, new_height))
    #width in pixels
    def width(self):
        return self.surface.get_width()
    #height in pixels
    def height(self):
        return self.surface.get_height()


#Load a texture of the given name from file
class FileTexture(BasicTexture):
    def __init__(self, filename):
        try:
            super().__init__(pygame.image.load(filename))
        except FileNotFoundError:
            print ("File couldn't be found:", filename)


#just a rectangle filled with one color
class DebugTexture(BasicTexture):
    def __init__(self, w, h, color):
        surf = pygame.Surface((w, h))
        surf.fill(color)
        super().__init__(surf)


#Texture changing with time, not finished yet
class AnimatedTexture(Texture):
    textures = []
    time_per_surface = 0.0
    start_t = 0.0
    def __init__(self, sub_textures, time_per_surface):
        self.textures = sub_textures
        self.time_per_surface = time_per_surface

    def start(self, time):
        self.start_t = time

    def get(self, time):
        i = int((time - self.start_t) // self.time_per_surface)
        return self.textures[min(i, len(self.textures)-1)].get(time)



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main