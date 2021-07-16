from game_defines import *
from random import randint



#Simulates a number of particles. Particles move in a line, and when they leave at the right/bottom end of screen, they come back from left/top
class ParticleAnimation:    
    particle_count = 100
    particle_radius = 3
    particle_velocity_min = 100
    particle_velocity_max = 300
    particle_color = (64, 64, 64)

    render_width = 0
    render_height = 0
    surface_alpha_overlay = None
    surface_render = None
    particle_velocities = []
    def __init__(self, render_width, render_height, pcolor, bgcolor, pcount = 100):
        #render width, height are sizes of texture to render into
        self.render_width  = render_width
        self.render_height = render_height
        self.particle_count = pcount
        self.particle_color = pcolor
        
        #surface alpha overlay has target background color but alpha channel = 1. Drawing this over the whole screen causes a neat disappearing effect after particles.
        self.surface_alpha_overlay = pygame.Surface((self.render_width, self.render_height), pygame.SRCALPHA)
        self.surface_alpha_overlay.fill(list(bgcolor) + [1])
        
        #prepare surface to render into, fill it with background color
        self.surface_render = pygame.Surface((self.render_width, self.render_height))
        self.surface_render.fill(bgcolor)

        #create particles and assign them random velocities
        self.particle_velocities = [[randint(self.particle_velocity_min, self.particle_velocity_max) for j in range(2)] for i in range(self.particle_count)]

    def update(self, time):
        #go through all particles
        for v in self.particle_velocities:
            #compute current particle position - time * v is distance traveled, modulo makes it seem like particles disappear on one side of screen and come back from the other
            x = int(time * v[0] % (self.render_width  + 2*self.particle_radius) - self.particle_radius) 
            y = int(time * v[1] % (self.render_height + 2*self.particle_radius) - self.particle_radius)
            #draw current particle
            pygame.draw.circle(self.surface_render, self.particle_color, (x, y), self.particle_radius)
        #draw alpha overlay - responsible for fading particle tails
        self.surface_render.blit(self.surface_alpha_overlay, (0, 0))

    #get rendered surface
    def getRender(self):
        return self.surface_render
        

    


#Particle effect on the background of black fields. To use less performance that will be used for AI/..., there is only one particle animation, into which there are multiple viewports.
class BlackTileAnimation(ParticleAnimation):
    #how much does viewport shift when moving one field
    shift_x = 25
    shift_y = 25

    def __init__(self):
        #compute render width and height from viewport shift and tile radius
        self.width  = gm_tile_width  + gm_board_size_x * self.shift_x
        self.height = gm_tile_height + gm_board_size_y * self.shift_y
        super().__init__(self.width, self.height, (64, 64, 64), (0, 0, 0))

    #draw one square with given pos
    def draw(self, surf, time, sqr_pos):
        dist = worldToScreenCoords(squareToWorldCoords(sqr_pos))
        circle_x = self.shift_x * sqr_pos[0]
        circle_y = self.shift_y * sqr_pos[1]
        surf.blit(self.getRender(), dist, pygame.Rect(circle_x, circle_y, gm_tile_width, gm_tile_height), pygame.BLEND_MAX)  



#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main