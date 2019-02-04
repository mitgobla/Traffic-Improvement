"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
"""

import simpy
import math
import random
import itertools
import logging

class TrafficEnvironment(object):

    def __init__(self):
        # C -> distanceFromA -> A                        B
        #                      <- Distance between AB  -> <- distanceFromB <- C

        # --- Traffic Setup ---
        # Probability a car appears from the left every second
        self.probabilityLeft = 0.05
        # Probability a car appears from the right every second
        self.probabilityRight = 0.05

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
        self.timeToPerformCToA = math.sqrt(
            (2*diagonalDistance)/self.avgAcceleration)
        self.timeToPerformCToB = math.sqrt(
            (2*self.distanceFromB)/self.avgAcceleration)

        # milePerHour = 0.44704 metres per second
        metresPerSecond = self.speedLimit*0.44704

        timeToPerformAToB = self.distanceAToB / metresPerSecond

        self.timeToPerformLeft = 2*(self.timeToPerformCToA) + timeToPerformAToB
        self.timeToPerformRight = 2*(self.timeToPerformCToB) + timeToPerformAToB


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
        self.create_light(0, [0,0])
        self.create_light(1, [15,0])
    
    def create_light(self, identity, vector):
        self.trafficLights.append(TrafficLight(self.tenv, identity, vector))
        print("Created Light:", identity, "at", vector)
    
    def run(self):
        for light in self.trafficLights:
            anyTransit = True
            while anyTransit:
                for vehicles                             
            yield self.tenv.environment.timeout(5)
            light.change_state()
            yield self.tenv.environment.timeout(5)
            light.change_state()
            yield self.tenv.environment.timeout(5)
            light.change_state()
            yield self.tenv.environment.timeout(5)
            light.change_state()


class Controller(object):
    def __init__(self, tenv: TrafficEnvironment):
        self.tmgmt = TrafficManagment(tenv)    
        self.tenv = tenv
    
    def run(self):
        self.tenv.environment.process(self.tmgmt.run())
        self.tenv.environment.run(until=100)

TENV = TrafficEnvironment()
CTRL = Controller(TENV)
CTRL.run()
