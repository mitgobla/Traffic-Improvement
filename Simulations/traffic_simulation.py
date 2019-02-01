"""Traffic Light Simulation 

Author: Ben Dodd (mitgobla)
"""

import simpy
import math
import random
import itertools
import logging

logging.basicConfig(filename='Simulations//output.log',
                    filemode='w', format='%(message)s', level=logging.DEBUG)


class TrafficEnvironment(object):

    def __init__(self):
        # C -> distanceFromA -> A                        B
        #                      <- Distance between AB  -> <- distanceFromB <- C

        # --- Traffic Setup ---
        # Probability a car appears from the left every second
        self.probabilityLeft = 0.5
        # Probability a car appears from the right every second
        self.probabilityRight = 0.5

        # --- Traffic Lights Setup ---
        # Distance of car from left traffic light in metres
        self.distanceFromA = 2.0
        # Distance of car from right traffic light in metres
        self.distanceFromB = 4.0
        # Distance AB in metres
        self.distanceAToB = 30.0
        # Width of road in metres
        self.roadWidth = 6.0
        # Speed limit inbetween AB (miles per hour)
        self.speedLimit = 20

        # --- Car Setup ---
        # Average Car Acceleration (metres per second squared)
        self.avgAcceleration = 3.5

        # --- Other ---
        self.environment = simpy.Environment()

    def calculate(self):
        diagonalDistance = math.sqrt(
            self.distanceFromA**2+(self.roadWidth/2)**2)
        timeToPerformCToA = math.sqrt(
            (2*diagonalDistance)/self.avgAcceleration)
        timeToPerformCToB = math.sqrt(
            (2*self.distanceFromB)/self.avgAcceleration)

        # milePerHour = 0.44704 metres per second
        metresPerSecond = self.speedLimit*0.44704

        timeToPerformAToB = self.distanceAToB / metresPerSecond

        self.timeToPerformLeft = 2*(timeToPerformCToA) + timeToPerformAToB
        self.timeToPerformRight = 2*(timeToPerformCToA) + timeToPerformAToB


class TrafficLight(object):
    def __init__(self, name):
        self.colours = itertools.cycle(['red', 'amber1', 'green', 'amber2'])
        self.currentColour = next(self.colours)
        self.name = name

    def next_colour(self):
        self.currentColour = next(self.colours)
        print("TrafficLight", self.name, 'is currently', self.currentColour)


class TrafficLightManagement(object):
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.trafficLights = []
        self.vehicles = []

    def run(self):
        while True:
            for light in self.trafficLights:
                # Light is Red
                yield self.env.timeout(10)  # Stay red for 10 seconds
                light.next_colour()
                yield self.env.timeout(5)  # Stay amber1 for 5 seconds
                light.next_colour()
                yield self.env.timeout(10)  # Stay green for 10 seconds
                light.next_colour()
                yield self.env.timeout(5)  # Stay amber2 for 5 seconds
                light.next_colour()
                yield self.env.timeout(5)  # All lights stay red for 5 seconds

    def add_light(self, traffic_light: TrafficLight):
        self.trafficLights.append(traffic_light)
        self.vehicles.append(list())
    
    def add_vehicle(self, light, vehicle):
        self.vehicles[self.trafficLights.index(light)].append(vehicle)


class Vehicle(object):

    def __init__(self, name, traffic_system: TrafficLightManagement):
        self.traffic_system = traffic_system
        self.name = name
        self.source = None
        self.destination = None

        self.setup()

    def setup(self):
        self.source = random.choice(self.traffic_system.trafficLights)
        self.traffic_system.add_vehicle(self.source, self)
        self.destination = self.source
        while self.destination == self.source:
            self.destination = random.choice(self.traffic_system.trafficLights)
        print(self.source.name, "-> Car", self.name, "->", self.destination.name)

TENV = TrafficEnvironment()
TENV.calculate()

TMGMT = TrafficLightManagement(TENV.environment)

for i in range(2):
    light = TrafficLight(str(i))
    TMGMT.add_light(light)

for i in range(10):
    vehicle = Vehicle(i, TMGMT)

TENV.environment.process(TMGMT.run())
TENV.environment.run(until=5000)
