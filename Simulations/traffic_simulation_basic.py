"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
        Edward Upton (engiego)        
"""

import simpy
import itertools
import random
import numpy as np

class TrafficEnvironment(object):
    def __init__(self):
        """Configuration for environment
        """

        self.environment = simpy.Environment()  # Creating environment within the 'TrafficEnvironment' Class with 'Simpy'.

        # --- CONSTANTS FOR SIMULATION --- #
        self.distanceFromLightToStop = 1    # The Distance in units from the stop position of the car to the Traffic Light.
        self.timeFromAToB = 4   # Time to traverse from Light 'A' to Light 'B'.
        self.timeToMoveUpQueue = 0.5    # Time it takes a vehicle to occupy the space in front within a queue.
        self.humanReactionTime = 0.2    # Time it takes for a driver to react to a space being empty in front or the traffic light.
        self.numVehiclesA = 1    # Setting number of vehicles that will start on Light 'A'.
        self.numVehiclesB = 1    # Setting number of vehicles that will start on Light 'B'.
        self.timePerVehicleGeneration = 1   # Units of time per generating Vehicle (used with probability)
        self.probabiliyNewVehiclePerUnitTime = 0.2  # Probability of adding Vehicle per "timePerVehicleGeneration"

        # --- VARIABLES TO SET UP SYSTEM -- #
        self.vehiclesList = []  # Stores all the vehicles that are in the environment
        self.lightsList = []    # Stores all the traffic lights that are in the environment

        # Array for light creation
        lightsToGenerate = [["A", [3,4]],
                            ["B", [12,3]]] 
        
        self.create_system(lightsToGenerate)    # Setup the Traffic System

        self.environment.run(until=1000)    # Run the environment for ... units of time.

        # Printing lights left at each Traffic Light
        for light in self.lightsList:
            print("END -->", light.identity, "Has Vehicles", list(str(x) for x in light.vehiclesAtLight))

    def create_system(self, lightsToGenerate):
        """Create Traffic Environment
        """
        for light in lightsToGenerate:
            self.lightsList.append(TrafficLight(self, light[0], light[1]))
            
        self.roadBetweenLight = RoadBetweenLights(self)

        self.tmgmt = TrafficManagment(self)
        self.environment.process(self.generate_vehicles())
    
    def generate_vehicles(self):
        # while True:
        #     if np.random.choice([True, False], p=[self.probabiliyAddingVehiclePerTimeDelay, 1-self.probabiliyAddingVehiclePerTimeDelay]):
        #         numVehicles = len(self.vehiclesList)
        #         self.vehiclesList.append(Vehicle(self, str(numVehicles), self.lightsList[random.randint(0, 1)]))
        #         yield self.environment.timeout(self.timeDelayAddingVehicles)
        i = len(self.vehiclesList)
        while True:
            if random.random() < self.probabiliyNewVehiclePerUnitTime:
                self.vehiclesList.append(Vehicle(self, str(i), self.lightsList[random.randint(0, 1)]))
            yield self.environment.timeout(self.timePerVehicleGeneration)
            i += 1

class TrafficManagment:
    def __init__(self, tenv):
        self.tenv = tenv
        self.tenv.environment.process(self.cycle_light_states())
        # self.tenv.environment.process(self.tenv.roadBetweenLight.until_empty())       
    
    def cycle_light_states(self):
        while True:
            for light in self.tenv.lightsList:
                yield self.tenv.roadBetweenLight.isEmpty
                yield self.tenv.environment.timeout(2)
                light.change_state() # Go redamber
                yield self.tenv.environment.timeout(1)
                print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", light.identity, "; Vehicles:", list(str(x) for x in light.vehiclesAtLight))
                light.change_state() # Go Green
                yield self.tenv.environment.timeout(5)
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

        print(self.tenv.environment.now, ":","Created Vehicle --> Identity:", self.identity, "; Location:", self.location.identity)
        self.tenv.environment.process(self.run())
        
    def __str__(self):
        return self.identity

    def run(self):
        # while True:
        if self.location.vehiclesAtLight.index(self) == 0:
            yield self.location.lightGreenEvent
            print(self.tenv.environment.now, ":","Traffic Light is --> State:", self.location.currentState, "; For Vehicle:", self.identity)
            yield self.tenv.environment.process(self.travel_between_lights())
            print(self.tenv.environment.now, ":","Vehicle Has Gone Through Traffic Light --> Vehicle:", self.identity)
            # break
        elif isinstance(self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1], Vehicle):
            vehicleInFront = self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1]
            yield vehicleInFront.moved
            yield self.tenv.environment.timeout(self.tenv.humanReactionTime)
            # if self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1] == 'empty':
            yield self.tenv.environment.process(self.travel_up_queue())
        elif self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1] == 'empty':
            print("Vehicle Starting to Move Up Queue Empty --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
            yield self.tenv.environment.timeout(self.tenv.humanReactionTime)
            yield self.tenv.environment.process(self.travel_up_queue())


    def travel_between_lights(self):
        self.tenv.roadBetweenLight.add_vehicle(self)
        if len(self.location.vehiclesAtLight) == 1 and self.location.vehiclesAtLight[0] == self:
            self.location.vehiclesAtLight.pop(0)
        else:
            self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self)] = 'empty'
        self.moved.succeed()
        print(self.tenv.environment.now, ":","Vehicle is Travelling Between Lights --> Identity:", self.identity)
        yield self.tenv.environment.timeout(self.tenv.timeFromAToB)
        self.tenv.roadBetweenLight.remove_vehicle(self)

    def travel_up_queue(self):
        print(self.tenv.environment.now, ":","Vehicle Moving Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        yield self.tenv.environment.timeout(self.tenv.timeToMoveUpQueue)
        self.location.vehiclesAtLight.insert(self.location.vehiclesAtLight.index(self)+1, self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self)-1))
        self.pop_last_empty()
        print(self.tenv.environment.now, ":","Vehicle Moved Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", self.location.identity, "; Vehicles:", list(str(x) for x in self.location.vehiclesAtLight))
        self.moved.succeed()
        # yield self.tenv.environment.timeout(0)
        self.moved = self.tenv.environment.event()
        self.tenv.environment.process(self.run())

    def pop_last_empty(self):
        lastItemInTrafficLightList = self.location.vehiclesAtLight[-1]
        if lastItemInTrafficLightList == "empty":
            self.location.vehiclesAtLight.pop(-1)


class TrafficLight(object):
    def __init__(self, tenv, identity, vector):
        self.tenv = tenv
        
        self.identity = identity
        self.vector = vector
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