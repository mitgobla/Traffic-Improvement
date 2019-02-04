"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
"""

import simpy
import math
import random
import itertools
import logging
import numpy

class TrafficEnvironment(object):

    def __init__(self):
        # C -> distanceFromA -> A                        B
        #                      <- Distance between AB  -> <- distanceFromB <- C

        # Environment Setup
        self.raining = random.random() < 0.05
        self.rainSpeedReduction = (2, 7)

        # --- Traffic Setup ---
        # Probability a car appears from the left every second
        # self.probabilityLeft = 0.05
        # Probability a car appears from the right every second
        # self.probabilityRight = 0.05
        self.probabilityOfCar = 0.05

        # --- Traffic Lights Setup ---
        # Distance of car from left traffic light in metres
        self.distanceFromA = 4.0
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
        self.avgAcceleration = (2, 4.5)
        # Random Human Reaction # random.uniform(humanReaction, 2) 
        self.humanReactionTime = (0.75, 2)
        # Normal Distribution of human speed error (higher = more random error)
        self.humanSpeedScale = 10
        # Chance of being distracted
        self.humanDistractionChance = 0.25
        self.humanDistractionDelay = 2
        
        # --- Other ---
        self.environment = simpy.Environment()
        self.output()

    def output(self):
        print("---Traffic Simulation Setup ---")
        print("Raining:", "Yes" if self.raining else "No")
        print("---                         ---")


class TrafficLight(object):
    def __init__(self, tenv: TrafficEnvironment, identity, vector):
        self.tenv = tenv
        self.identity = identity
        self.vector = vector

        self.states = itertools.cycle(['red', 'redamber', 'green', 'greenamber'])
        self.currentState = next(self.states)
    
    def change_state(self):
        self.currentState = next(self.states)
        print(self.identity, "light is now", self.currentState)

class TrafficManagment(object):
    def __init__(self, tenv: TrafficEnvironment):
        self.tenv = tenv

        self.trafficLights = []
        self.vehicles = []
        self.carsInTransit = []
        self.scan = True
    
    def create_light(self, identity, vector):
        self.trafficLights.append(TrafficLight(self.tenv, identity, vector))
        print("Created Light:", identity, "at", vector)
    
    def vehicle_creation(self, numVehicles):

        for identity in range(len(self.vehicles), len(self.vehicles) + numVehicles):
            location = random.choice(self.trafficLights)
            position = 0
            for vehicle in self.vehicles:
                if vehicle.location == location:
                    if position <= vehicle.position:
                        position = vehicle.position + 1
            self.vehicles.append(Vehicle(self.tenv, self, identity, location, position))

    def generate_cars(self):
        while True:
            if random.random() < self.tenv.probabilityOfCar:
                location = random.choice(self.trafficLights)
                position = 0
                for vehicle in self.vehicles:
                    if vehicle.location == location:
                        if position <= vehicle.position:
                            position = vehicle.position + 1
                self.vehicles.append(Vehicle(self.tenv, self, len(self.vehicles), location, position))
            yield self.tenv.environment.timeout(1)

    def cycle_light_states(self):
        while True:
            for light in self.trafficLights:
                while self.intransit_scan():
                    pass
                yield self.tenv.environment.timeout(5)
                light.change_state() # Go redamber
                yield self.tenv.environment.timeout(5)
                light.change_state() # Go Green
                yield self.tenv.environment.timeout(15)
                light.change_state() # Go greenamber
                yield self.tenv.environment.timeout(5)
                light.change_state() # Go Red
    
    def intransit_scan(self):
        self.carsInTransit = []
        for vehicle in self.vehicles:
            if vehicle.location == -1:
                self.carsInTransit.append(vehicle)
            else:
                if vehicle in self.carsInTransit:
                    self.carsInTransit.pop(self.carsInTransit.index(vehicle))
        return self.carsInTransit

class Vehicle(object):
    def __init__(self, tenv: TrafficEnvironment, tmgmt: TrafficManagment, identity, location, position):
        self.tenv = tenv
        self.tmgmt = tmgmt
        self.identity = identity
        self.location = location
        self.position = position

        print("Created vehicle", identity, "at", location.identity, "in position", position)
        self.humanReaction = round(random.uniform(self.tenv.humanReactionTime[0], self.tenv.humanReactionTime[1]), 2)
        self.humanAcceleration = random.uniform(self.tenv.avgAcceleration[0], self.tenv.avgAcceleration[1])
        self.selfRainSpeedReduction = random.randint(self.tenv.rainSpeedReduction[0], self.tenv.rainSpeedReduction[1])

        self.calculate()
        
    def calculate(self):
        if self.tenv.raining:
            self.tenv.speedLimit -= self.selfRainSpeedReduction
        self.timeToPerformCToT = round(math.sqrt(
            (2*self.tenv.distanceFromA)/self.humanAcceleration),2)
        # milePerHour = 0.44704 metres per second
        self.metresPerSecond = round((numpy.random.normal(loc=self.tenv.speedLimit, scale=self.tenv.humanSpeedScale)*0.44704), 2)

        self.timeToPerformTransit = (self.tenv.distanceAToB / self.metresPerSecond) + self.timeToPerformCToT

        if random.random() < self.tenv.humanDistractionChance:
            self.timeToPerformCToT += self.tenv.humanDistractionDelay

    def run(self):
        while True:
            if self.position == 0:
                if self.location.currentState == "green":
                    self.transit()
            elif self.position > 0:
                tempVehiclePos = []
                for vehicle in self.tmgmt.vehicles:
                    if vehicle.location == self.location:
                        tempVehiclePos.append(vehicle.position)
                if (self.location - 1) in tempVehiclePos:
                    self.move_in_queue()
                        

    def transit(self):
        yield self.tenv.environment.timeout(self.timeToPerformCToT)
        self.location = -1
        self.position = 0
        if self.tmgmt.carsInTransit:
            self.position = len(self.tmgmt.intransit_scan) - 1
        print("Vehicle", self.identity, "is in transit")
        yield self.tenv.environment.timeout(self.timeToPerformTransit)
        self.location = -2
        self.position = -1
        print("Vehicle", self.identity, "is out of transit")


    def move_in_queue(self):
        yield self.tenv.environment.timeout(self.humanReaction)
        yield self.tenv.environment.timeout(self.timeToPerformCToT)
        self.position -= self.position
        print("Vehicle", self.identity, "has moved position in queue at", self.location.identity)


class Controller(object):
    def __init__(self, tenv: TrafficEnvironment):
        self.tmgmt = TrafficManagment(tenv)    
        self.tenv = tenv
    
    def run(self):
        self.tmgmt.create_light(0, [0,0])
        self.tmgmt.create_light(1, [15,0])
        # self.tmgmt.vehicle_creation(20)
        self.tmgmt.vehicle_creation(10)
        self.tenv.environment.process(self.tmgmt.generate_cars())
        # self.tenv.environment.event(self.tmgmt.intransit_scan())
        self.tenv.environment.process(self.tmgmt.cycle_light_states())
        self.tenv.environment.run(until=200)

TENV = TrafficEnvironment()
CTRL = Controller(TENV)
CTRL.run()
