"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
        Edward Upton (engiego)        
"""



import simpy
import math
import random
import itertools
import logging
import threading
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
        self.timeTillNextCar = 1                

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
        self.create_system()

    def create_system(self):
        # print("---Traffic Simulation Setup ---")
        # print("Raining:", "Yes" if self.raining else "No")
        # print("---                         ---")

        self.vehiclesInTransit = []            
        self.trafficLights = []        
        self.trafficLights.append(TrafficLight(self, 0, [0, 0]))
        self.trafficLights.append(TrafficLight(self, 1, [15, 0]))

        self.vehicles = []
        self.environment.process(self.generate_cars())
        self.environment.process(self.cycle_light_state())
        self.environment.run(until=500)

    def generate_cars(self):
        while True:
            if random.random() < self.probabilityOfCar:
                location = random.choice(self.trafficLights)
                position = len(location.vehiclesAtLight)
                nextvehicle = Vehicle(self, len(self.vehicles), location, position)
                self.vehicles.append(nextvehicle)
                self.environment.process(self.vehicles[-1].run())
            yield self.environment.timeout(self.timeTillNextCar)

    def any_in_transit(self):
        while len(self.vehiclesInTransit) > 0:
            yield self.environment.timeout(0)

    def cycle_light_state(self):
        while True:
            for light in self.trafficLights:
                # yield self.environment.process(self.any_in_transit())
                yield self.environment.timeout(5)
                light.change_state() # Go redamber
                yield self.environment.timeout(5)
                light.change_state() # Go Green
                yield self.environment.timeout(15)
                light.change_state() # Go greenamber
                yield self.environment.timeout(5)
                light.change_state() # Go Red

class TrafficLight(object):
    def __init__(self, tenv: TrafficEnvironment, identity, vector):
        self.tenv = tenv
        self.identity = identity
        self.vector = vector
        self.vehiclesAtLight = []

        self.green_event = self.tenv.environment.event()
        # self.states = itertools.cycle(['red', 'redamber', 'green', 'greenamber'])
        self.states = itertools.cycle(['red', 'redamber', 'green', 'greenamber'])
        self.currentState = next(self.states)

    def change_state(self):
        print("Traffic Light", self.identity, "is changing state")
        self.green_event = self.tenv.environment.event() # Resetting Green Event 
        self.currentState = next(self.states)
        if self.currentState == 'green':
            self.green_event.succeed()
            print("Changed", self.identity, "event to green")
        print(self.identity, "light is now", self.currentState)
        


class Vehicle(object):
    def __init__(self, tenv: TrafficEnvironment, identity, location, position):
        self.tenv = tenv
        self.identity = identity
        self.location = location

        self.location.vehiclesAtLight.append(self)

        self.inTransit = self.tenv.environment.event()
        self.vehicleMoved = self.tenv.environment.event()

        print("Created vehicle", identity, "at", self.location.identity, "in position", position)

        self.humanReaction = round(random.uniform(self.tenv.humanReactionTime[0], self.tenv.humanReactionTime[1]), 2)
        self.humanAcceleration = random.uniform(self.tenv.avgAcceleration[0], self.tenv.avgAcceleration[1])
        self.selfRainSpeedReduction = random.randint(self.tenv.rainSpeedReduction[0], self.tenv.rainSpeedReduction[1])

        self.calculate()
        #self.action = self.tenv.environment.process(self.run())

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

    def check_light(self):
        yield self.location.green_event

    def run(self):
        running = True
        while running:
            if self.location.vehiclesAtLight.index(self) == 0:
                print("Vehicle", self.identity, "waiting for light", self.location.identity, "to turn green.")
                yield self.tenv.environment.process(self.check_light())
                # Wait until light is green
                print("Vehicle", self.identity, "sees green")
                yield self.tenv.environment.process(self.transit())
                running = False
                # self.action.interrupt()
            else:
                # print("Vehicle", self.identity, "is going to check to move forward.")
                # print(self.location.identity, "cars:", list(x.identity for x in self.location.vehiclesAtLight))
                carInFront = self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self)-1]
                if carInFront != 'empty' and carInFront != self.location.vehiclesAtLight[-1]: # Has to be a car in front
                    yield carInFront.vehicleMoved
                    yield self.tenv.environment.timeout(1)
                    yield self.tenv.environment.process(self.move_in_queue())
                

    def transit(self):
        self.inTransit.succeed()
        print("Vehicle", self.identity, "starting transit at", self.location.identity)
        yield self.tenv.environment.timeout(self.timeToPerformCToT)
        print("Vehicle", self.identity, "in transit")
        self.location.vehiclesAtLight[0] = 'empty'
        self.vehicleMoved.succeed()
        print("Successfully moved")
        self.tenv.vehiclesInTransit.append(self)
        yield self.tenv.environment.timeout(self.timeToPerformTransit)
        print("Vehicle", self.identity, "attempting removal")
        del self.tenv.vehiclesInTransit[self.tenv.vehiclesInTransit.index(self)]
        print("Vehicle", self.identity, "left transit (removed from system)")        



    def move_in_queue(self):
        # 
        print("Vehicle", self.identity, "is moving in the queue at", self.location.identity)
        yield self.tenv.environment.timeout(self.timeToPerformCToT)
        # print("Vehicle", self.identity, "has moved in the queue at", self.location.identity)
        self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self) - 1)
        self.location.vehiclesAtLight.insert([self.location.vehiclesAtLight.index(self) + 1], 'empty')
        self.vehicleMoved.succeed()
        self.vehicleMoved = self.tenv.environment.event()

    # def move_in_queue(self):
    #     movingInQueue = True
    #     while movingInQueue:
    #         yield self.tenv.environment.timeout(self.humanReaction)
    #         yield self.tenv.environment.timeout(self.timeToPerformCToT)
    #         self.position = self.location.vehiclesAtLight.index(self)
    #         # print("Vehicle", self.identity, "has moved position in queue at", self.location.identity)
    #         movingInQueue = False

TENV = TrafficEnvironment()

