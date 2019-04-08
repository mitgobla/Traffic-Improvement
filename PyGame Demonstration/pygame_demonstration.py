import pygame
import sys, os, traceback

if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Vehicle(pygame.sprite.Sprite):

    def __init__(self, group, direction="northbound"):
        pygame.sprite.DirtySprite.__init__(self)

        self.group = group

        self.image = pygame.Surface([16, 16])
        self.image.fill((255, 0, 0))
        # self.image.set_colorkey((0, 0, 0))

        if direction == "northbound":
            self.rect = pygame.draw.rect(self.image, (255, 0, 0), [64, 496, 16, 16])
        elif direction == "southbound":
            self.rect = pygame.draw.rect(self.image, (255, 0, 0), [80, 0, 16, 16])

        self.direction = direction
        
    def update(self):
        if (self.rect.y < -16 and self.direction == "northbound") or (self.rect.y > 576 and self.direction == "southbound"):
            print("removed")
            self.group.remove(self)

    def move(self):
        if self.direction == "northbound":
            # self.rect.y -= 1
            self.rect.move_ip(0, -1)
        elif self.direction == "southbound":
            # self.rect.y += 1
            self.rect.move_ip(0, 1)


    

class SimulationGame:

    screen_size = [512, 512]

    def __init__(self):
        self.surface = pygame.display.set_mode(SimulationGame.screen_size)
        self.running = True

        self.sprites = pygame.sprite.Group()
        self.clock = pygame.time.Clock()

        self.car = Vehicle(self.sprites)

        self.sprites.add(self.car)
    
    def run(self):
        self.surface.fill((100, 230, 100))
        pygame.display.flip()
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.sprites.update()
            self.car.move()
            pygame.draw.rect(self.surface, (20, 20, 20), [64, 0, 32, 512])
            pygame.draw.line(self.surface, (255, 255, 255), [80, 0], [80, 512], 1)
            rects = self.sprites.draw(self.surface)
            # pygame.display.update(rects)
            pygame.display.flip()
    
GAME = SimulationGame()
GAME.run()





    

