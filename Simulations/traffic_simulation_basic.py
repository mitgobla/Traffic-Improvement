"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
        Edward Upton (engiego)        
"""

import simpy
import itertools
import random
import numpy as np

class TrafficEnvironment:
    def __init__(self):
        """Configuration for environment
        """



        self.timeFromAToB = 15   # Time to traverse from Light 'A' to Light 'B'.
        self.timeToMoveUpQueue = 0.5 
        self.numVehiclesA = 1    # Setting number of vehicles that will start on Light 'A'.
        self.numVehiclesB = 1    # Setting number of vehicles that will start on Light 'B'.
        self.timeDelayAddingCars = 1
        self.probabiliyAddingCarPerTimeDelay = 0.001
        self.trafficLightCarGenerateWeighting = [0.4,0.6]


        # --- Other ---
        self.vehiclesList = [] # Stores all the vehicles that are in the environment
        self.lightsList = [] # Stores all the traffic lights that are in the environmen
        self.environment = simpy.Environment()  # Creating environment within the 'TrafficEnvironment' Class with 'Simpy'.
        self.create_system() # Setup the Traffic System

    def create_system(self):    # Creates the overall traffic environment.
        """Create Traffic Environment
        """

        self.lightsList.append(TrafficLight(self, "A"))
        self.lightsList.append(TrafficLight(self, "B"))
        
        # self.vehiclesList.append(Vehicle(self, "2", self.lightsList[1]))
        # self.vehiclesList.append(Vehicle(self, "3", self.lightsList[0]))
        # self.vehiclesList.append(Vehicle(self, "4", self.lightsList[1]))
        # self.vehiclesList.append(Vehicle(self, "5", self.lightsList[0]))
        # self.vehiclesList.append(Vehicle(self, "6", self.lightsList[1]))
        # self.vehiclesList.append(Vehicle(self, "7", self.lightsList[0]))
        # self.vehiclesList.append(Vehicle(self, "8", self.lightsList[1]))
        # self.vehiclesList.append(Vehicle(self, "9", self.lightsList[0]))
        # self.vehiclesList.append(Vehicle(self, "10", self.lightsList[1]))
        # self.vehiclesList.append(Vehicle(self, "11", self.lightsList[0]))
        # self.vehiclesList.append(Vehicle(self, "12", self.lightsList[1]))
        self.roadBetweenLight = RoadBetweenLights(self)

        self.tmgmt = TrafficManagment(self)
        self.environment.process(self.generate_vehicles())

        self.environment.run(until=50)
    
    def generate_vehicles(self):
        while True:
            if np.random.choice([True, False], p=[self.probabiliyAddingCarPerTimeDelay, 1-self.probabiliyAddingCarPerTimeDelay]):
                numVehicles = len(self.vehiclesList)
                self.vehiclesList.append(Vehicle(self, str(numVehicles), self.lightsList[random.randint(0, 1)]))
                yield self.environment.timeout(self.timeDelayAddingCars)

class TrafficManagment:
    def __init__(self, tenv):
        self.tenv = tenv
        self.tenv.environment.process(self.cycle_light_states())
        # self.tenv.environment.process(self.tenv.roadBetweenLight.until_empty())       
    
    def cycle_light_states(self):
        while True:
            for light in self.tenv.lightsList:
                yield self.tenv.roadBetweenLight.isEmpty
                yield self.tenv.environment.timeout(5)
                light.change_state() # Go redamber
                yield self.tenv.environment.timeout(1)
                print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", light.identity, "; Vehicles:", list(str(x) for x in light.vehiclesAtLight))
                light.change_state() # Go Green
                yield self.tenv.environment.timeout(1)
                light.change_state() # Go greenamber
                yield self.tenv.environment.timeout(1)
                light.change_state() # Go Red
                

class Vehicle:
    def __init__(self, tenv, identity, location):
        """Create a vehicle
        
        Arguments:
            tenv {TrafficEnvironment} -- Traffic Environment. Used to access configured variables.
            identity {str} -- Name of vehicle
            location {TrafficLight} -- Traffic Light object to start at
        """

        self.tenv = tenv

        self.identity = identity
        self.location = location
        self.location.vehiclesAtLight.append(self)

        self.moved = self.tenv.environment.event()

        print(self.tenv.environment.now, ":","Created Car --> Identity:", self.identity, "; Location:", self.location.identity)
        self.tenv.environment.process(self.run())
        
    def __str__(self):
        return self.identity

    def run(self):
        # while True:
        print(self.identity, self.location.vehiclesAtLight)
        if self.location.vehiclesAtLight.index(self) == 0:
            yield self.location.lightGreenEvent
            print(self.tenv.environment.now, ":","Traffic Light is --> State:", self.location.currentState, "; For Vehicle:", self.identity)
            yield self.tenv.environment.process(self.travel_between_lights())
            print(self.tenv.environment.now, ":","Car Has Gone Through Traffic Light --> Vehicle:", self.identity)
            # break
        elif isinstance(self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1], Vehicle):
            carInFront = self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1]
            yield carInFront.moved
            yield self.tenv.environment.process(self.travel_up_queue())
        elif self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1] == 'empty':
            yield self.tenv.environment.process(self.travel_up_queue())


    def travel_between_lights(self):
        self.tenv.roadBetweenLight.add_vehicle(self)
        if len(self.location.vehiclesAtLight) == 1 and self.location.vehiclesAtLight[0] == self:
            self.location.vehiclesAtLight.pop(0.1)
        else:
            self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self)] = 'empty'
        self.moved.succeed()
        print(self.tenv.environment.now, ":","Car is Travelling Between Lights --> Identity:", self.identity)
        yield self.tenv.environment.timeout(self.tenv.timeFromAToB)
        self.tenv.roadBetweenLight.remove_vehicle(self)

    def travel_up_queue(self):
        oldPos = self.location.vehiclesAtLight.index(self)
        self.location.vehiclesAtLight[oldPos - 1] = self
        if oldPos != len(self.location.vehiclesAtLight) - 1:
            self.location.vehiclesAtLight[oldPos] = 'empty'
        else:
            self.location.vehiclesAtLight.pop(oldPos)
        # if self.location.vehiclesAtLight[-1] == 'empty':
        #     self.location.vehiclesAtLight.pop(-1)
        # self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self)] = 'empty'
        print(self.tenv.environment.now, ":","Car Moving Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        yield self.tenv.environment.timeout(self.tenv.timeToMoveUpQueue)
        print(self.tenv.environment.now, ":","Car Moved Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", self.location.identity, "; Vehicles:", list(str(x) for x in self.location.vehiclesAtLight))
        self.moved.succeed()
        yield self.tenv.environment.timeout(0.1)
        self.moved = self.tenv.environment.event()
        self.tenv.environment.process(self.run())

class TrafficLight(object):
    def __init__(self, tenv, identity):
        self.tenv = tenv

        self.identity = identity
        self.vehiclesAtLight = []
        self.states = itertools.cycle(['red', 'redamber', 'green', 'greenamber'])
        self.currentState = next(self.states)

        self.lightGreenEvent = self.tenv.environment.event()
        self.lightRedEvent = self.tenv.environment.event()
        print(self.tenv.environment.now, ":","Created Traffic Light --> Identity:", self.identity)
    
    def change_state(self):
        self.currentState = next(self.states)
        if self.currentState == 'green':
            self.lightGreenEvent.succeed()
            self.lightRedEvent = self.tenv.environment.event()
        if self.currentState == 'red':
            self.lightRedEvent.succeed()
            self.lightGreenEvent = self.tenv.environment.event()
        print(self.tenv.environment.now, ":","Traffic Light Changed --> Identity:", self.identity, "; State:", self.currentState)

class RoadBetweenLights(object):
    def __init__(self, tenv):
        self.tenv = tenv
        self.vehiclesBetweenLights = []
        self.isEmpty = self.tenv.environment.event()
        self.isEmpty.succeed()
    
    def add_vehicle(self, vehicle):
        self.isEmpty = self.tenv.environment.event()
        self.vehiclesBetweenLights.append(vehicle)

    def remove_vehicle(self, vehicle):
        self.vehiclesBetweenLights.pop(self.tenv.roadBetweenLight.vehiclesBetweenLights.index(vehicle))
        if len(self.vehiclesBetweenLights) == 0:
            self.isEmpty.succeed()

TENV = TrafficEnvironment()