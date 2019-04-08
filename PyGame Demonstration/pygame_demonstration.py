import pygame
import sys, os, traceback, random, itertools

if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Vehicle(pygame.sprite.Sprite):

    def __init__(self, group, direction):
        pygame.sprite.DirtySprite.__init__(self)

        self.group = group

        self.image = pygame.Surface([16, 16])
        col = random.choice([(50, 50,  random.uniform(100, 255)), (50, random.uniform(100, 255), 50), (random.uniform(100, 255), 50, 50)])
        self.image.fill(col)
        # self.image.set_colorkey((0, 0, 0))

        self.direction = direction
        #self.direction = random.choice(["northbound", "southbound"])

        if self.direction == "northbound":
            self.rect = pygame.draw.rect(self.image, (0, 0, 0), [64, 512, 16, 16])
        elif self.direction == "southbound":
            self.rect = pygame.draw.rect(self.image, (0, 0, 0), [80, 0, 16, -16])

        
    def update(self):
        self.move()
        if (self.rect.y < -16 and self.direction == "northbound") or (self.rect.y > 576 and self.direction == "southbound"):
            # print("removed")
            self.group.remove(self)

    def move(self):
        if self.direction == "northbound":
            # self.rect.y -= 1
            if self.rect.y <= 311 and self.rect.y >= 304:
                self.rect.move_ip(2, 0)
            if self.rect.y <= 223 and self.rect.y >= 216:
                self.rect.move_ip(-2, 0)
            self.rect.move_ip(0, -1)
        elif self.direction == "southbound":
            # self.rect.y += 1
            self.rect.move_ip(0, 1)

class TrafficLight(pygame.sprite.Sprite):

    def __init__(self, direction):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([16, 16])

        self.colours = itertools.cycle([(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 255, 0)])
        self.c_col = next(self.colours)

        if direction == "northbound":
            self.c_col = next(self.colours)
            self.c_col = next(self.colours)
            self.image.fill(self.c_col)
            self.rect = pygame.draw.rect(self.image, self.c_col, [48, 304, 16, 16])
        else:
            self.image.fill(self.c_col)
            self.rect = pygame.draw.rect(self.image, self.c_col, [96, 224, 16, 16])


        self.frame = 0
    
    def update(self):
        self.frame += 1
        if self.frame == 128:
            self.c_col = next(self.colours)
            self.image.fill(self.c_col)
            self.frame = 0
    

    

class SimulationGame:

    screen_size = [512, 512]

    def __init__(self):
        self.surface = pygame.display.set_mode(SimulationGame.screen_size)
        self.running = True

        self.sprites = pygame.sprite.Group()
        self.traffic_lights = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

        

        trafficLightNorth = TrafficLight("northbound")
        trafficLightSouth = TrafficLight("southbound")
        self.traffic_lights.add(trafficLightNorth)
        self.traffic_lights.add(trafficLightSouth)
    
        # self.sprites.add(self.car)
    
    def run(self):
        self.surface.fill((100, 230, 100))
        pygame.display.flip()
        canSpawnNorthbound = 0
        canSpawnSouthbound = 0
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.sprites.update()
            self.traffic_lights.update()

            if random.choice(["northbound", "southbound"]) == "northbound":
                if random.random() < 0.05 and canSpawnNorthbound == 0:
                        self.sprites.add(Vehicle(self.sprites, "northbound")) 
                        canSpawnNorthbound = 9
            else:
                if random.random() < 0.01 and canSpawnSouthbound == 0:
                        self.sprites.add(Vehicle(self.sprites, "southbound")) 
                        canSpawnSouthbound = 9

            
            if canSpawnNorthbound:
                canSpawnNorthbound -= 1
            
            if canSpawnSouthbound:
                canSpawnSouthbound -= 1

            
            
            self.sprites.update()


            pygame.draw.rect(self.surface, (20, 20, 20), [64, 0, 32, 512])
            pygame.draw.rect(self.surface, (120, 120, 20), [64, 240, 16, 64])
            self.sprites.draw(self.surface)
            self.traffic_lights.draw(self.surface)
            pygame.draw.line(self.surface, (255, 255, 255), [80, 0], [80, 512], 1)
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 0, 40, 16])
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 496, 40, 16])
            # pygame.display.update(rects)
            pygame.display.flip()
    
GAME = SimulationGame()
GAME.run()





    

