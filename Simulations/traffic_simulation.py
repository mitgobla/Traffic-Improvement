"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
        Edward Upton (engiego)        
"""

import simpy
import itertools
import random
import numpy as np
import math

class TrafficEnvironment(object):
    def __init__(self):
        """Configuration for environment
        """

        self.environment = simpy.Environment()      # Creating environment within the 'TrafficEnvironment' Class with 'Simpy'.

        # --- CONSTANTS FOR SIMULATION --- #
        self.weather = "clear"                      # clear, rain, snow. Affects human speed error and general speed limit
        self.rainSpeedReduction = (0, 4)
        self.snowSpeedReduction = (0, 8)

        self.distanceFromLightToStop = 1            # The Distance in units from the stop position of the car to the Traffic Light.
        self.timeFromAToB = 4                       # Time to traverse from Light 'A' to Light 'B'.
        self.timeToMoveUpQueue = 0.5                # Time it takes a vehicle to occupy the space in front within a queue.
        self.numVehiclesA = 1                       # Setting number of vehicles that will start on Light 'A'.
        self.numVehiclesB = 1                       # Setting number of vehicles that will start on Light 'B'.

        self.timePerVehicleGeneration = 1           # Units of time per generating Vehicle (used with probability)
        self.probabiliyNewVehiclePerUnitTime = 0.5  # Probability of adding Vehicle per "timePerVehicleGeneration"

        self.speedLimit = 30                        # Speed limit of the road (mph, automatically converted)
        self.humanSpeedError = 10                   # Range of human Error of reaching the correct speed limit (mph, automatically converted)
        self.humanReactionTime = 0.2                # Time it takes for a driver to react to a space being empty in front or the traffic light.
        self.humanDistractionChance = 0.25          # Chance for the driver to be distracted (causes them to take longer to move up queue)
        self.humanDistractionAmount = 2             # Scale of the normal distribution of time added from being distracted

        # --- VARIABLES TO SET UP SYSTEM -- #
        self.vehicleTypeDict = {
            "Car": {
                "length": (4.2, 4.8),
                "acceleration": (3, 4),
            },
            "Truck": {
                "length": (5.3, 6.2),
                "acceleration": (1.4, 2.5),
            },
            "LCV": {
                "length": (7.15, 7.82),
                "acceleration": (0.8, 1.4),
            },
            "Articulated HGV": {
                "length": (12.5, 16.5),
                "acceleration": (0.6, 0.8),
            },
            "Rigid HGV": {
                "length": (13.0, 15.5),
                "acceleration": (0.6, 0.8),
            },
            "Short Bus": {
                "length": (5.5, 9.0),
                "acceleration": (0.7, 1.2),
            },
            "Long Bus": {
                "length": (9.0, 15.0),
                "acceleration": (0.7, 1),
            },
            "Motorcycle": {
                "length": (1.8, 2.6),
                "acceleration": (3, 7),
            },
        }
        self.vehiclesList = []  # Stores all the vehicles that are in the environment
        self.lightsList = []    # Stores all the traffic lights that are in the environment
        
        # if self.weather == "rain":
        #     self.speedLimit -= 5
        #     self.humanSpeedError += 3
        # elif self.weather == "snow":
        #     self.speedLimit -= 10
        #     self.humanSpeedError -= 3
        self.speedLimit = self.speedLimit*0.44704
        self.humanSpeedError = self.humanSpeedError*0.44704

        # Array for light creation
        lightsToGenerate = [["A", [3,4]],
                            ["B", [12,3]]] 
        
        self.create_system(lightsToGenerate)    # Setup the Traffic System

        self.environment.run(until=100)    # Run the environment for ... units of time.

        # printing lights left at each Traffic Light
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
                i += 1
            yield self.environment.timeout(self.timePerVehicleGeneration)

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

        self.type = random.choice(list(self.tenv.vehicleTypeDict.keys()))
        self.length = round(random.uniform(self.tenv.vehicleTypeDict[self.type]["length"][0], self.tenv.vehicleTypeDict[self.type]["length"][1]), 2)
        self.acceleration = round(random.uniform(self.tenv.vehicleTypeDict[self.type]["acceleration"][0], self.tenv.vehicleTypeDict[self.type]["acceleration"][1]), 2)
        self.speed = round(np.random.normal(self.tenv.speedLimit, (self.tenv.humanSpeedError/2)), 2)
        
        if self.tenv.weather == 'rain':
            self.speed -= round(random.uniform(self.tenv.rainSpeedReduction[0], self.tenv.rainSpeedReduction[1]), 2)
        elif self.tenv.weather == 'snow':
            self.speed -= round(random.uniform(self.tenv.snowSpeedReduction[0], self.tenv.snowSpeedReduction[1]), 2)

        self.reactionTime = abs(round(np.random.normal(self.tenv.humanReactionTime, 1), 2))
        if random.random() < self.tenv.humanDistractionChance: # Distracted driver
            self.reactionTime += round(random.uniform(0.25, 1), 2)
            # self.reactionTime += self.tenv.humanReactionTime - abs(round(np.random.normal(self.tenv.humanReactionTime, self.tenv.humanDistractionAmount)))
        
        self.moved = self.tenv.environment.event()

        print(self.tenv.environment.now, ":","Created Vehicle --> Identity:", self.identity, "; Location:", self.location.identity)
        self.tenv.environment.process(self.run())
        
        
    def __str__(self):
        return self.identity

    def run(self):
        # while True:
        if self.location.vehiclesAtLight.index(self) == 0:
            yield self.location.lightGreenEvent
            # print(self.tenv.environment.now, ":","Traffic Light is --> State:", self.location.currentState, "; For Vehicle:", self.identity)
            yield self.tenv.environment.process(self.travel_between_lights())
            # print(self.tenv.environment.now, ":","Vehicle Has Gone Through Traffic Light --> Vehicle:", self.identity)
            # break
        elif self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1] == 'empty':
            print("Vehicle Starting to Move Up Queue Empty --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
            yield self.tenv.environment.timeout(self.reactionTime)
            yield self.tenv.environment.process(self.travel_up_queue())
        elif isinstance(self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1], Vehicle):
            vehicleInFront = self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1]
            yield vehicleInFront.moved
            yield self.tenv.environment.timeout(self.reactionTime)
            # if self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) -1] == 'empty':
            yield self.tenv.environment.process(self.travel_up_queue())

    def calculate_distance(self, V1, V2):
        vectorDifference = [abs(V2[0] - V1[0]), abs(V2[1] - V1[1])]
        return round(math.sqrt(vectorDifference[0]**2 + vectorDifference[1]**2), 2)
    
    def calculate_time(self, speed, distance, accelerate=True):
        if accelerate == 0:
            return (distance/speed)
        else:
            timeToAccelerate = speed/self.acceleration
            distanceToAccelerate = speed * timeToAccelerate
            distanceAtFinalSpeed = distance - 2*(distanceToAccelerate)
            if distanceToAccelerate > distance/2:
                timeToAccelerate = math.sqrt((distance/2)/self.acceleration)
                maxSpeedReached = self.acceleration*(timeToAccelerate**2)
                return round(2*timeToAccelerate, 2)
            else:
                timeAtFinalSpeed = distanceAtFinalSpeed/speed
                return round((2*timeToAccelerate + timeAtFinalSpeed), 2)



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
        print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", self.location.identity, "; Vehicles:", list(str(x) for x in self.location.vehiclesAtLight))
        print(self.tenv.environment.now, ":","Vehicle Moving Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        self.location.vehiclesAtLight.insert(self.location.vehiclesAtLight.index(self)+1, self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self)-1))
        yield self.tenv.environment.timeout(self.tenv.timeToMoveUpQueue)
       
        self.pop_spare_empty()
        self.moved.succeed()
        print(self.tenv.environment.now, ":","Vehicle Moved Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", self.location.identity, "; Vehicles:", list(str(x) for x in self.location.vehiclesAtLight))
        # yield self.tenv.environment.timeout(0.000001)
        self.moved = self.tenv.environment.event()
        self.tenv.environment.process(self.run())

    def pop_spare_empty(self):
        lastItemInTrafficLightList = self.location.vehiclesAtLight[-1]
        if lastItemInTrafficLightList == "empty":
            self.location.vehiclesAtLight.pop(-1)
        # try:
        #     if self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) + 2] == "empty":
        #         self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self) + 2)
        # except IndexError:
        #     pass


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