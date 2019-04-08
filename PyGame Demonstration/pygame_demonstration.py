import itertools
import os
import random
import sys
import traceback

import pygame

class Environment:

    def __init__(self):
        self.vehicles = {
            "northbound": [],
            "southbound": []
        }

        self.traffic_lights = {
            "northbound": [],
            "southbound": []
        }

        self.vehicle_group = pygame.sprite.Group()

        self.traffic_light_group = pygame.sprite.Group()
        self.traffic_lights["northbound"].append(TrafficLight("northbound"))
        self.traffic_lights["southbound"].append(TrafficLight("southbound"))

        self.canSpawn = {
            "northbound": 0,
            "southbound": 0
        }

    def generate(self):
        if self.canSpawn["northbound"] == 0:
            vehicle = Vehicle(self, "northbound")
            self.vehicle_group.add(vehicle)
            self.vehicles["northbound"].append(vehicle)
            self.canSpawn["northbound"] = 16

        self.canSpawn["northbound"] -= 1



class Vehicle(pygame.sprite.Sprite):

    def __init__(self, env: Environment, direction: str):
        super().__init__()
        self.image = pygame.Surface([16, 16])
        self.colour = random.choice([(50, 50,  random.uniform(100, 255)), (50, random.uniform(100, 255), 50), (random.uniform(100, 255), 50, 50)])
        self.image.fill(self.colour)

        self.env = env
        self.direction = direction
        self.stopped = False

        if self.direction == "northbound":
            self.rect = pygame.draw.ellipse(self.image, (0, 0, 0), [64, 512, 16, 16])
        elif self.direction == "southbound":
            self.rect = pygame.draw.ellipse(self.image, (0, 0, 0), [80, 0, 16, 16])

    def update(self):
        if self.direction == "northbound":
            if self.rect.y < -15:
                self.env.vehicle_group.remove(self)
                return

            # if at traffic light and it is green, then move to right lane and forward
            if self.rect.y <= 320:
                if self.env.traffic_lights[self.direction][0].current_colour == (0, 255, 0):
                    self.rect.move_ip(16, 1)
                    print("yup")
                    self.env.vehicles[self.direction].pop()
                    self.stopped = False
                else:
                    self.stopped = True

            # if out of traffic system, then move to left lane
            if self.rect.y == 224:
                self.rect.move_ip(-16, 0)

            if self.rect.y > 320:
                if self.env.vehicles[self.direction][0] != self:
                    if self.env.vehicles[self.direction][self.env.vehicles[self.direction].index(self)-1].stopped:
                        if self.rect.y != (self.env.vehicles[self.direction][self.env.vehicles[self.direction].index(self)-1].rect.y - 17):
                            self.rect.move_ip(0, -1)
            else:
                self.rect.move_ip(0, -1)

            if not self.stopped:
                self.rect.move_ip(0, -1)
            # if not self.stopped:
            #     if self.env.vehicles[self.direction][0] != self:
            #         if self.rect.y > (self.env.vehicles[self.direction][self.env.vehicles[self.direction].index(self)-1].rect.y - 17):
            #             self.rect.move_ip(0, -1)
            #         else:
            #             self.stopped = True



class TrafficLight(pygame.sprite.Sprite):

    def __init__(self, direction):
        super().__init__()

        self.image = pygame.Surface([16, 16])

        self.direction = direction
        self.colours = itertools.cycle([(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 255, 0)])
        self.current_colour = next(self.colours)

        self.frame = 0

        self.setup()

    def setup(self):
        if self.direction == "northbound":
            self.current_colour = next(self.colours)
            self.current_colour = next(self.colours)
            self.image.fill(self.current_colour)
            self.rect = pygame.draw.rect(self.image, self.current_colour, [48, 304, 16, 16])
        elif self.direction == "southbound":
            self.image.fill(self.current_colour)
            self.rect = pygame.draw.rect(self.image, self.current_colour, [96, 224, 16, 16])

    def update(self):
        self.frame += 1
        if self.frame == 128:
            self.current_colour = next(self.colours)
            self.image.fill(self.current_colour)
            self.frame = 0

class SimulationGame:

    def __init__(self):
        self.surface = pygame.display.set_mode([512, 512])
        self.running = True

        self.env = Environment()

        self.clock = pygame.time.Clock()

    def run(self):
        self.surface.fill((100, 230, 100))
        pygame.display.flip()
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False

            self.env.vehicle_group.update()
            self.env.traffic_light_group.update()
            self.env.generate()
            # Road
            pygame.draw.rect(self.surface, (20, 20, 20), [64, 0, 32, 512])

            # Roadworks
            pygame.draw.rect(self.surface, (120, 120, 20), [64, 240, 16, 64])

            # Update vehicles and traffic lights
            self.env.vehicle_group.draw(self.surface)
            self.env.traffic_light_group.draw(self.surface)

            # Tunnels and road line
            pygame.draw.line(self.surface, (255, 255, 255), [80, 0], [80, 512], 1)
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 0, 40, 16])
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 496, 40, 16])

            pygame.display.flip()

GAME = SimulationGame()

if __name__ == "__main__":
    GAME.run()
    pygame.quit()

