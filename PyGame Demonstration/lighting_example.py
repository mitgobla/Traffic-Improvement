import pygame
# from pygame.locals import *
import sys, os, traceback

import PAdLib

if sys.platform in ["win32", "win64"]: os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class SimulationGame:

    screen_size = [512, 512]

    def __init__(self):
        # Stores the lighting information
        self.surface = pygame.display.set_mode(SimulationGame.screen_size)
        self.surf_lighting = pygame.Surface(SimulationGame.screen_size)

        # Shadow object
        self.shadow = PAdLib.shadow.Shadow()

        # Background
        self.surf_bg = pygame.image.load(os.path.join(SCRIPT_DIR, "bg.png")).convert()

        # Occulders are objects that block light.
        self.occulders = []

        self.with_background = True
        self.with_falloff = True

        self.setup()

    def setup(self):
        for y in range(self.surf_bg.get_height()):
            for x in range(self.surf_bg.get_width()):
                color = self.surf_bg.get_at((x, y))
                if color == (0, 0, 0, 255):
                    # Creates an occulder object with dimensions X1 Y1, X2, Y2 based on the black pixels
                    self.occulders.append(PAdLib.occluder.Occluder([[x*16,y*16],[x*16,y*16+16],[x*16+16,y*16+16],[x*16+16,y*16]]))

        self.shadow.set_occluders(self.occulders)
        self.shadow.set_radius(100.0)

        self.surf_bg = pygame.transform.scale(self.surf_bg, SimulationGame.screen_size)
        self.surf_bg.convert()

        self.surf_falloff = pygame.image.load(os.path.join(SCRIPT_DIR, "light_falloff_car.png")).convert()

    def get_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return False
                elif event.key == pygame.locals.K_f:
                    self.with_falloff = not self.with_falloff
                elif event.key == pygame.locals.K_b:
                    self.with_background = not self.with_background
        self.shadow.set_light_position(mouse_pos)
        return True

    def draw(self):
        # First compute lighting information
        mask, draw_pos = self.shadow.get_mask_and_position(False)

        if self.with_falloff:
            mask.blit(self.surf_falloff, (0,0), special_flags=pygame.locals.BLEND_MULT)

        self.surf_lighting.fill((190, 190, 190)) # Ambient Light
        self.surf_lighting.blit(mask, draw_pos, special_flags=pygame.locals.BLEND_MAX)

        if self.with_background:
            self.surface.blit(self.surf_bg, (0, 0))
        else:
            self.surface.fill((255, 0, 0))

        self.surface.blit(self.surf_lighting, (0, 0), special_flags=pygame.locals.BLEND_MULT)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            if not self.get_input():
                break
            self.draw()
            clock.tick(60)
        pygame.quit()

GAME = SimulationGame()

if __name__ == "__main__":
    try:
        GAME.run()
    except:
        traceback.print_exc()
        pygame.quit()
        sys.exit()
