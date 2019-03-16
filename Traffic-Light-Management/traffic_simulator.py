import itertools
import json
import math
import os
import random
import time

import numpy as np
import simpy

class TrafficEnvironment(object):
    def __init__(self):
        self.environment = simpy.Environment()
        self.trafficLightsToCreate = [["A"],["B"]]

        self.vehiclesList = []
        self.trafficLightsList = []
    
    def set_env_variables(self, distanceLtoL, speedLimitLtoL, timeUpQueue, trafficLightDetectMovement, simTime, timeGreen, roadUsage):
        """Set Environment Variables
        
        Keyword Arguments:
        distanceLtoL -- The distance between the two lights
        speedLimitLtoL -- The speed limit (mph) between the two lights
        timeUpQueue -- Time it takes a vehicle to move up the queue
        trafficLightDetectMovement -- Can the traffic light detect if no vehicles are moving
        simTime -- How long to simulate this iteration form
        timeGreen -- How long is each traffic light green
        roadusage -- How many vehicles are added per second
        """
        
        self.timeLtoL = distanceLtoL / (speedLimitLtoL * 0.44704)
        self.timeUpQueue = timeUpQueue
        self.trafficLightDetectMovement = trafficLightDetectMovement
        self.simTime = simTime
        self.timeGreen = timeGreen
        self.roadUsage = roadUsage


    def start_simulation(self):
        self.create_system()

        self.environment.run(until=self.simTime)

        # print(len(self.trafficLightsList[0].vehiclesAtLight))
        # print(len(self.trafficLightsList[1].vehiclesAtLight))

        totalTimeStopped = 0
        vehicleCount = 0
        for vehicle in self.vehiclesList:
            if hasattr(vehicle, "timeStopped"):
                totalTimeStopped += vehicle.timeStopped
                vehicleCount += 1
        self.averageTimeStopped = totalTimeStopped / vehicleCount
        # print("Average Time Stopped:", (totalTimeStopped/vehicleCount))

    def create_system(self):
        for trafficLight in self.trafficLightsToCreate:
            
            self.trafficLightsList.append(TrafficLight(self, trafficLight[0]))

        self.roadBetweenLights = RoadBetweenLights(self)

        self.tmgmt = TrafficManagement(self)
        self.environment.process(self.generate_vehicles())

    def generate_vehicles(self):
        i = len(self.vehiclesList)
        while True:
            if random.random() < self.roadUsage:
                self.vehiclesList.append(Vehicle(self, str(i), self.trafficLightsList[random.randint(0, len(self.trafficLightsList)-1)]))
                i += 1
            yield self.environment.timeout(1)

class TrafficManagement:
    def __init__(self, tenv):
        self.tenv = tenv
        self.tenv.environment.process(self.cycle_light_states())
    
    def cycle_light_states(self):
        while True:
            for light in self.tenv.trafficLightsList:
                yield self.tenv.roadBetweenLights.isEmpty
                yield self.tenv.environment.timeout(1)
                light.change_light_state()
                light.checkForMovement = True
                self.tenv.environment.process(light.no_movement_detection())
                yield self.tenv.environment.any_of([self.tenv.environment.timeout(self.tenv.timeGreen)])
                light.checkForMovement = False
                light.change_light_state()

    



class TrafficLight:
    def __init__(self, tenv, identity):
        self.tenv = tenv
        self.identity = identity
        self.vehiclesAtLight = []
        self.states = itertools.cycle(['red', 'green'])
        self.currentState = next(self.states)
        self.lightGreenEvent = self.tenv.environment.event()
        self.lightRedEvent = self.tenv.environment.event()
        self.noMovementEvent = self.tenv.environment.event()
        self.checkForMovement = False

    def change_light_state(self):
        self.currentState = next(self.states)
        if self.currentState == 'green':
            self.lightGreenEvent.succeed()
            self.lightRedEvent = self.tenv.environment.event()
        if self.currentState == 'red':
            self.lightRedEvent.succeed()
            self.lightGreenEvent = self.tenv.environment.event()

    def no_movement_detection(self):
        if self.tenv.trafficLightDetectMovement:
            while self.checkForMovement == True:
                if len(self.vehiclesAtLight) == 0:
                    yield self.tenv.environment.timeout(1)
                    if len(self.vehiclesAtLight) == 0:
                        self.noMovementEvent.succeed() 
                yield self.tenv.environment.timeout(1)
                self.noMovementEvent = self.tenv.environment.event()

class Vehicle:
    def __init__(self, tenv, identity, location):
        self.tenv = tenv
        self.identity = identity
        self.location = location
        self.location.vehiclesAtLight.append(self)
        self.tenv.environment.process(self.run())
        self.timeWhenStopped = self.tenv.environment.now

    def run(self):
        if self.location.vehiclesAtLight.index(self) == 0:
            self.moved = self.tenv.environment.event()
            yield self.location.lightGreenEvent            
            yield self.tenv.environment.process(self.travel_between_lights())            
        else: 
            self.moved = self.tenv.environment.event()
            yield self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) - 1].moved
            yield self.tenv.environment.process(self.travel_up_queue())

    def travel_between_lights(self):
        # print("Car", self.identity, "is moving between lights from", self.location.identity)
        self.tenv.roadBetweenLights.add_vehicle(self)
        self.moved.succeed()
        self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self))
        self.timeStopped = self.tenv.environment.now - self.timeWhenStopped
        # print(self.timeStopped)
        yield self.tenv.environment.timeout(self.tenv.timeLtoL)
        self.tenv.roadBetweenLights.remove_vehicle(self)
    
    def travel_up_queue(self):
        # # print("Car", self.identity, "is moving up queue", self.location.identity)
        yield self.tenv.environment.timeout(0.5)
        yield self.tenv.environment.timeout(self.tenv.timeUpQueue)
        self.moved.succeed()
        self.tenv.environment.process(self.run())

class RoadBetweenLights:
    def __init__(self, tenv):
        self.tenv = tenv
        self.vehiclesBetweenLights = []
        self.isEmpty = self.tenv.environment.event()
        self.isEmpty.succeed()
    
    def add_vehicle(self, vehicle):
        self.isEmpty = self.tenv.environment.event()
        self.vehiclesBetweenLights.append(vehicle)

    def remove_vehicle(self, vehicle):
        self.vehiclesBetweenLights.pop(self.tenv.roadBetweenLights.vehiclesBetweenLights.index(vehicle))
        if len(self.vehiclesBetweenLights) == 0:
            # print("Allowing Lights to change")
            self.isEmpty.succeed()