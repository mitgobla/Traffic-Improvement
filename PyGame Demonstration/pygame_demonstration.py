"""PyGame Demo for simulation results

Author: Edward Upton (engiego)
        Ben Dodd (mitgobla)
"""

import itertools
import os
import random
import sys
import traceback
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

pygame.init()
pygame.font.init()
pygame.display.set_caption("Traffic Light Management Demo")

SCALE = 8 # Modify the traffic light timings

class Environment:
    """Class for the traffic environment.
    Stores vehicles and traffic lights, and controls the current viewmode.
    """

    def __init__(self):
        """Class for the traffic environment.
        Stores vehicles and traffic lights, and controls the current viewmode.
        """

        self.viewmodes = itertools.cycle(["colours", "waiting"])
        self.current_viewmode = next(self.viewmodes)

        self.vehicles = {
            "northbound": [],
            "southbound": []
        }

        self.traffic_lights = {
            "northbound": [],
            "southbound": []
        }

    def remove_vehicle(self, direction):
        """Remove a vehicle from the environment.
        
        Arguments:
            direction {str} -- Direction of travel of the vehicle to remove.
        """

        del self.vehicles[direction][0]

    def remove_last_vehicle(self, direction):
        """Remove the last vehicle from the environment.
        
        Arguments:
            direction {str} -- Direction of travel of the vehicle to remove.
        """

        del self.vehicles[direction][-1]

    def add_vehicle(self, vehicle, direction):
        """Add a vehicle to the environment.
        
        Arguments:
            vehicle {Vehicle} -- Vehicle object to add.
            direction {str} -- Direction of travel of the vehicle to add.
        """

        data = dict(name=vehicle.name, vehicle_obj=vehicle, direction=direction, rect=vehicle.rect)
        self.vehicles[direction].append(data)

    def add_traffic_light(self, light, direction):
        """Add a traffic light to the environment.
        
        Arguments:
            light {TrafficLight} -- TrafficLight object to add.
            direction {str} -- Direction of travel the TrafficLight object will control.
        """

        self.traffic_lights[direction].append(light)



class TrafficLight(pygame.sprite.DirtySprite):
    """Traffic Light object & sprite.
    
    Arguments:
        DirtySprite {pygame.sprite.DirtySprite} -- Parent class.
    """

    def __init__(self, env: Environment, group: pygame.sprite.Group, direction: str):
        """Traffic light object & sprite.
        
        Arguments:
            env {Environment} -- Traffic Environment.
            group {pygame.sprite.Group} -- Sprite group.
            direction {str} -- Direction of travel this traffic light controls.
        """

        pygame.sprite.DirtySprite.__init__(self)

        self.env = env
        self.image = pygame.Surface([16, 16])
        self.image.fill((0, 0, 0))
        # self.image.set_colorkey((0, 0, 0))
        # self.colours = itertools.cycle(
        #     [(255, 0, 0), (255, 155, 0), (255, 0, 0), (255, 0, 0), (255, 155, 0), (0, 255, 0)])
        # self.colours = itertools.cycle(
        #     [(255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0)])
        # colour_cycle = [(255, 0, 0), (255, 155, 0), (0, 255, 0), (255, 155, 0), (255, 0, 0)]
        colour_cycle = []
        colour_cycle.extend(((255, 0, 0),)*SCALE)
        colour_cycle.append((255, 155, 0))
        colour_cycle.extend(((0, 255, 0),)*SCALE)
        colour_cycle.append((255, 155, 0))
        colour_cycle.extend(((255, 0, 0),)*SCALE)
        self.colours = itertools.cycle(colour_cycle)
        self.current_colour = next(self.colours)

        self.frame = 0

        self.font = pygame.font.SysFont("Arial", 10)
        self.text_surf = self.font.render("0", 1, (255, 255, 255), self.current_colour)

        self.text_w, self.text_h = self.text_surf.get_width(), self.text_surf.get_height()
        self.direction = direction
        if self.direction == "northbound":
            self.current_colour = [next(self.colours) for _ in range(2*SCALE)][-1]
            # self.current_colour = next(self.colours)
            self.rect = pygame.draw.ellipse(
                self.image, self.current_colour, [0, 0, 16, 16])
            self.rect = self.rect.move(48, 304)
        elif self.direction == "southbound":
            self.rect = pygame.draw.ellipse(
                self.image, self.current_colour, [0, 0, 16, 16])
            self.rect = self.rect.move(96, 224)

        self.image.blit(self.text_surf, [8 - self.text_w/2, 8 - self.text_h/2])

    def update(self):
        """Update traffic light state. Automatically done by PyGame.
        """
        self.frame += 1
        if self.frame == 15:
            self.current_colour = next(self.colours)
            # self.image.fill(self.current_colour, rect=self.rect)
            self.frame = 0
        self.rect = pygame.draw.ellipse(
            self.image, self.current_colour, [0, 0, 16, 16])
        if self.direction == "northbound":
            self.rect = self.rect.move(48, 304)
        elif self.direction == "southbound":
            self.rect = self.rect.move(96, 224)
        # self.text_surf = self.font.render(str(len(self.env.vehicles[self.direction])), 1, (255, 255, 255, 255), self.current_colour+(0,))
        self.text_surf = self.font.render(str(self.frame), 1, (255, 255, 255, 255), self.current_colour+(0,))
        self.text_w, self.text_h = self.text_surf.get_width(), self.text_surf.get_height()
        self.image.blit(self.text_surf, [8 - self.text_w/2, 8 - self.text_h/2])
        # self.text_surf = self.font.render(str(self.frame), 1, (255, 255, 255, 255), self.current_colour+(0,))


class Vehicle(pygame.sprite.DirtySprite):
    """Vehicle object & sprite.
    
    Arguments:
        DirtySprite {pygame.sprite.DirtySprite} -- Parent class.
    """

    def __init__(self, env: Environment, group: pygame.sprite.Group, name, direction: str):
        """Vehicle object & sprite.
        
        Arguments:
            env {Environment} -- Traffic Environment.
            group {pygame.sprite.Group} -- Sprite group.
            direction {str} -- Direction of travel this traffic light controls.
        """

        pygame.sprite.DirtySprite.__init__(self)

        self.env = env
        self.group = group
        self.name = str(name)
        self.frame = 0

        self.image = pygame.Surface((16, 16))
        self.car_colour = random.choice([(50, 50,  random.uniform(100, 255)), (50, random.uniform(100, 255), 50), (random.uniform(100, 255), 50, 50)])
        self.colour = (0, 255, 0)
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        self.dirty = 1
        self.direction = direction
        self.stopped = False

        if self.env.current_viewmode == "waiting":
            self.colour = (0, 255, 0)
        elif self.env.current_viewmode == "colours":
            self.colour = self.car_colour

        if self.direction == "northbound":
            # self.rect = pygame.draw.rect(self.image, self.colour, [64, 512, 16, 16])
            self.rect = pygame.draw.ellipse(
                self.image, self.colour[:3], [0, 0, 16, 16])
            if len(self.env.vehicles[self.direction]) <= 11:
                self.rect = self.rect.move(64, 512)
            else:
                self.rect = self.rect.move(64, (514 + 16*(len(self.env.vehicles[self.direction])-10)))
        elif self.direction == "southbound":
            # self.rect = pygame.draw.rect(self.image, self.colour, [80, 0, 16, 16])
            self.rect = pygame.draw.ellipse(
                self.image, self.colour[:3], [0, 0, 16, 16])
            if len(self.env.vehicles[self.direction]) <= 14:
                self.rect = self.rect.move(80, 0)
        pygame.draw.ellipse(self.image, (255, 255, 255), [0, 0, 16, 16], 2)

        self.x, self.y = self.rect.x, self.rect.y
            # else:
            #     # self.rect = self.rect.move(80, (-2 - 16*(len(self.env.vehicles[self.direction])-12)))
            #     del self.env.vehicles[self.direction][-1]
            #     self.group.remove(self)
        # self.image.fill(self.colour, rect=self.rect)

    def vehicle_property(self):
        """Get vehicle data.
        
        Returns:
            dict -- Dictionary of Vehicle sprite rectangle, name, and direction.
        """
        return dict(rect=self.rect, name=self.name, direction=self.direction)

    def update(self):
        """Update vehicle state. Automatically done by PyGame.
        """
        self.x, self.y = self.rect.x, self.rect.y
        if self.env.current_viewmode == "waiting":
            if self.stopped and self.frame < 253:
                self.frame += 2
            # elif not self.stopped and self.frame > 1:
            #     self.frame -= 2

            # if self.frame > 255:
            #     self.frame = 255
            self.colour = (self.frame, 255-self.frame, 0)
        elif self.env.current_viewmode == "colours":
            self.colour = self.car_colour
        # self.image.fill(self.colour, self.rect)
        self.rect = pygame.draw.ellipse(self.image, self.colour, [0, 0, 16, 16])
        self.rect = self.rect.move(self.x, self.y)
        pygame.draw.ellipse(self.image, (255, 255, 255), [0, 0, 16, 16], 2)
        self.move()
        if (self.rect.y < -16 and self.direction == "northbound") or (self.rect.y > 576 and self.direction == "southbound"):
            self.group.remove(self)
            self.dirty = 1

    def move(self):
        """Intelligently move the vehicle based on its direction of travel.
        """
        if self.direction == "northbound":

            try:
                vehicle_pos = self.env.vehicles["northbound"].index(next(item for item in self.env.vehicles["northbound"] if item["name"] == self.name))*16
                if self.rect.y == (320 + vehicle_pos) and self.env.traffic_lights["northbound"][0].current_colour in [(255, 0, 0), (255, 155, 0)]:
                    self.stopped = True
                elif self.rect.y >= (320 + vehicle_pos) and self.env.traffic_lights["northbound"][0].current_colour in [(0, 255, 0)]:
                    self.stopped = False
            except StopIteration:
                pass

            if self.rect.y == 320 and self.env.traffic_lights["northbound"][0].current_colour in [(0, 255, 0)]:
                self.rect.move_ip(16, -2)
                self.env.remove_vehicle(self.direction)
                self.stopped = False
            elif self.rect.y == 320:
                self.stopped = True

            if self.rect.y < 224 and self.rect.x == 80:
                self.rect.move_ip(-16, 0)
                self.stopped = False

            if self.rect.y > 320:
                if not self.stopped:
                    self.rect.move_ip(0, -2)
                    self.stopped = False

            if self.rect.y < 320 and not self.stopped:
                self.rect.move_ip(0, -2)
                self.stopped = False

            self.dirty = 1

        elif self.direction == "southbound":

            try:
                vehicle_pos = self.env.vehicles["southbound"].index(next(item for item in self.env.vehicles["southbound"] if item["name"] == self.name))*16
                if self.rect.y <= (208 - vehicle_pos) and self.env.traffic_lights["southbound"][0].current_colour in [(0, 255, 0)]:
                    self.stopped = False
                elif self.rect.y == (208 - vehicle_pos) and self.env.traffic_lights["southbound"][0].current_colour in [(255, 0, 0), (255, 155, 0)]:
                    self.stopped = True
            except StopIteration:
                pass

            if self.rect.y == 208 and self.env.traffic_lights["southbound"][0].current_colour in [(0, 255, 0)]:
                self.stopped = False
                self.env.remove_vehicle(self.direction)
                self.rect.move_ip(0, 2)
            elif self.rect.y == 208:
                self.stopped = True

            if self.rect.y < 208 and not self.stopped:
                self.rect.move_ip(0, 2)
                self.stopped = False

            if self.rect.y > 208:
                self.rect.move_ip(0, 2)
                self.stopped = False

            self.dirty = 1


class SimulationGame:
    """Game Class
    """

    def __init__(self):
        """Game class.
        Initialize game environment variables.
        """
        self.surface = pygame.display.set_mode([512, 512])
        self.running = True

        self.vehicle_group = pygame.sprite.Group()
        self.traffic_light_group = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

        self.env = Environment()

        self.northbound_light = TrafficLight(
            self.env, self.traffic_light_group, "northbound")
        self.southbound_light = TrafficLight(
            self.env, self.traffic_light_group, "southbound")

        self.traffic_light_group.add(
            self.northbound_light, self.southbound_light)
        self.env.add_traffic_light(self.northbound_light, "northbound")
        self.env.add_traffic_light(self.southbound_light, "southbound")

        self.secure_random = random.SystemRandom()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)

    def run(self):
        """PyGame mainloop.
        """
        self.surface.fill((100, 230, 100))
        pygame.display.flip()

        can_spawn_northbound = 0
        can_spawn_southbound = 0
        spawn_northbound_chance = 0.0
        spawn_southbound_chance = 0.0

        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # print(event.key, pygame.K_a)
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        self.env.current_viewmode = next(self.env.viewmodes)
                    if event.key == pygame.K_q:
                        if spawn_northbound_chance < 1:
                            spawn_northbound_chance += 0.005
                    if event.key == pygame.K_a:
                        if spawn_northbound_chance > 0:
                            spawn_northbound_chance -= 0.005
                            # print(spawn_northbound_chance)
                    if event.key == pygame.K_w:
                        if spawn_southbound_chance < 1:
                            spawn_southbound_chance += 0.005
                    if event.key == pygame.K_s:
                        if spawn_southbound_chance > 0:
                            spawn_southbound_chance -= 0.005
                            

            if random.choice(["northbound", "southbound"]) == "northbound":
                if random.random() < spawn_northbound_chance and can_spawn_northbound == 0:
                    vehicle = Vehicle(self.env, self.vehicle_group,
                                      self.secure_random.random(), "northbound")
                    self.vehicle_group.add(vehicle)
                    self.env.add_vehicle(vehicle, "northbound")
                    can_spawn_northbound = 16
            else:
                if random.random() < spawn_southbound_chance and can_spawn_southbound == 0 and len(self.env.vehicles["southbound"]) <= 13:
                    vehicle = Vehicle(self.env, self.vehicle_group,
                                      self.secure_random.random(), "southbound")
                    self.vehicle_group.add(vehicle)
                    self.env.add_vehicle(vehicle, "southbound")
                    can_spawn_southbound = 16

            if can_spawn_northbound:
                can_spawn_northbound -= 1

            if can_spawn_southbound:
                can_spawn_southbound -= 1

            self.vehicle_group.update()
            self.traffic_light_group.update()

            self.surface.fill((100, 230, 100))
            textsurface = self.font.render('(W+, S-) Southbound Busyness: '+str(round(spawn_southbound_chance, 4)), False, (255, 55, 55))
            self.surface.blit(textsurface, (110, 0))
            textsurface = self.font.render('(Q+, A-) Northbound Busyness: '+str(round(spawn_northbound_chance, 4)), False, (255, 55, 55))
            self.surface.blit(textsurface, (110, 490))
            pygame.draw.rect(self.surface, (20, 20, 20), [64, 0, 32, 512])
            pygame.draw.rect(self.surface, (120, 120, 20), [64, 240, 16, 64])
            self.vehicle_group.draw(self.surface)
            self.traffic_light_group.draw(self.surface)
            pygame.draw.line(self.surface, (255, 255, 255),
                             [80, 0], [80, 512], 1)
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 0, 40, 16])
            pygame.draw.rect(self.surface, (60, 20, 20), [60, 496, 40, 16])
            # pygame.display.update(rects)
            pygame.display.flip()


GAME = SimulationGame()

if __name__ == "__main__":
    GAME.run()
