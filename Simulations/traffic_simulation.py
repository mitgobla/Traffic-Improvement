"""Traffic Light Simulation

Author: Ben Dodd (mitgobla)
        Edward Upton (engiego)        
"""

import simpy
import itertools
import random
import numpy as np
import math
import json
import matplotlib.pyplot as plt

class TrafficEnvironment(object):
    def __init__(self):
        """Configuration for environment
        """

        self.environment = simpy.Environment()      # Creating environment within the 'TrafficEnvironment' Class with 'Simpy'.

        # --- CONSTANTS FOR SIMULATION --- #
        self.weather = "clear"                      # clear, rain, snow. Affects human speed error and general speed limit
        self.rainSpeedReduction = (0, 4)            
        self.snowSpeedReduction = (0, 8)

        # self.timeFromAToB = 4                       # Time to traverse from Light 'A' to Light 'B'.
        self.timeToMoveUpQueue = 0.5                # Time it takes a vehicle to occupy the space in front within a queue.
        # self.numVehiclesA = 1                       # Setting number of vehicles that will start on Light 'A'.
        # self.numVehiclesB = 1                       # Setting number of vehicles that will start on Light 'B'.

        self.timePerVehicleGeneration = 1           # Units of time per generating Vehicle (used with probability)
        self.probabiliyNewVehiclePerUnitTime = 0.3 # Probability of adding Vehicle per "timePerVehicleGeneration"

        self.speedLimit = 30                        # Speed limit of the road (mph, automatically converted)
        self.humanSpeedError = 10                   # Range of human Error of reaching the correct speed limit (mph, automatically converted)
        self.humanReactionTime = 0.2                # Time it takes for a driver to react to a space being empty in front or the traffic light.
        self.humanDistractionChance = 0.25          # Chance for the driver to be distracted (causes them to take longer to move up queue)
        self.humanDistractionAmount = 2             # Scale of the normal distribution of time added from being distracted

        # --- VARIABLES TO SET UP SYSTEM -- #
        # Loading the vehilce type json file to a python dictionary
        with open("Simulations/vehicle_type_data.json", "r") as vehicleTypeDataFile:
            self.vehicleTypeDict = json.load(vehicleTypeDataFile)

        self.vehiclesList = []  # Stores all the vehicles that are in the environment
        self.lightsList = []    # Stores all the traffic lights that are in the environment

        # Converting speed from miles/hour to metres/second
        self.speedLimit = self.speedLimit*0.44704   
        self.humanSpeedError = self.humanSpeedError*0.44704

        self.standardGapQtoL = 3    # The Distance in units from the stop position of the car to the Traffic Light
        self.standardGapLtoONonClearance = 0    # The Distance in units from the light to the start of the obstruction
        self.standardGapLtoOWithClearance = 3   # The Distance in units from the light to the start of the obstruction to allow opposite driving cars past
        self.roadWidth = 6  # The distance in units of the road width.
        # STANDARD UNIQUE FOR LIGHT TYPE 3 and 4

        # Array for light creation
        
        self.create_system()    # Setup the Traffic System

        self.environment.run(until=1000)    # Run the environment for ... units of time.
        vectorListX = []
        # printing lights left at each Traffic Light
        for light in self.lightsList:
            vectorListX = vectorListX.append(light.)
            print("END -->", light.identity, "Has Vehicles", list(str(x) for x in light.vehiclesAtLight))
        

    def create_system(self):
        """Create Traffic Environment
        """
        lightsToGenerate = [["A", [3,4], 1],
                            ["B", [12,3], 2]] 
        
        self.intersectingPointVector = [7.5, 3.5]

        for light in lightsToGenerate:
            self.lightsList.append(TrafficLight(self, light[0], light[1], light[2]))
            
        self.roadBetweenLights = RoadBetweenLights(self)

        self.tmgmt = TrafficManagement(self)
        self.environment.process(self.generate_vehicles())
    
    def generate_vehicles(self):
        i = len(self.vehiclesList)
        while True:
            if random.random() < self.probabiliyNewVehiclePerUnitTime:
                self.vehiclesList.append(Vehicle(self, str(i), self.lightsList[random.randint(0, len(self.lightsList)-1)]))
                i += 1
            yield self.environment.timeout(self.timePerVehicleGeneration)

    def calculate_vector(self, v1, angle, distance):
        """Calculates a vector with an angle and distance from a current vector

        Arguments:
            v1 {array} -- Vector to take angle and distance from.
            angle {float} -- Angle in degrees from original vector.
            distance {float} -- Distance at angle from original vector.
        """
        return [(v1[0] + distance*math.sin(math.radians(angle))), (v1[1] + distance*math.cos(math.radians(angle)))]
    
    def calculate_angle_trig(self, v1, v2):
        x = v1[0] - v2[0]
        y = v1[1] - v2[1]
        angle = math.atan2(x, y)
        angle = math.degrees(angle)
        return angle


    def calculate_angle_trig_vector(self, v1, v2):
        angle = math.atan2(v2[0]-v1[0], v2[1]-v1[1])
        angle = math.degrees(angle)
        return angle

    def calculate_distance(self, x, y):
        return math.sqrt(x**2 + y**2)

    def calculate_distance_vectors(self, v1, v2):
        return math.sqrt((v1[0]-v2[0])**2 + (v1[1]-v2[1])**2)


class TrafficManagement:
    def __init__(self, tenv):
        self.tenv = tenv
        self.tenv.environment.process(self.cycle_light_states())
    
    def cycle_light_states(self):
        while True:
            for light in self.tenv.lightsList:
                yield self.tenv.roadBetweenLights.isEmpty
                yield self.tenv.environment.timeout(1)
                light.change_light_state() # Go redamber
                yield self.tenv.environment.timeout(1)
                print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", light.identity, "; Vehicles:", list(str(x) for x in light.vehiclesAtLight))
                light.change_light_state() # Go Green
                yield self.tenv.environment.timeout(15)
                light.change_light_state() # Go greenamber
                yield self.tenv.environment.timeout(1)
                light.change_light_state() # Go Red
                

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
        self.position = 0
        self.location.vehiclesAtLight.append(self)
        self.moved = self.tenv.environment.event()

        self.type = random.choice(list(self.tenv.vehicleTypeDict.keys()))
        self.length = round(random.uniform(self.tenv.vehicleTypeDict[self.type]["length"][0], self.tenv.vehicleTypeDict[self.type]["length"][1]), 2)
        self.acceleration = round(random.uniform(self.tenv.vehicleTypeDict[self.type]["acceleration"][0], self.tenv.vehicleTypeDict[self.type]["acceleration"][1]), 2)
        self.speed = round(np.random.normal(self.tenv.speedLimit, (self.tenv.humanSpeedError/2)), 2)
        self.gapDistance = round((1.5 + np.random.normal(1, 3)), 2)
        self.update_vehicle_vector

        print(self.gapDistance)
        if self.tenv.weather == 'rain':
            self.speed -= round(random.uniform(self.tenv.rainSpeedReduction[0], self.tenv.rainSpeedReduction[1]), 2)
        elif self.tenv.weather == 'snow':
            self.speed -= round(random.uniform(self.tenv.snowSpeedReduction[0], self.tenv.snowSpeedReduction[1]), 2)

        self.reactionTime = abs(round(np.random.normal(self.tenv.humanReactionTime, 1), 2))
        if random.random() < self.tenv.humanDistractionChance: # Distracted driver
            self.reactionTime += round(random.uniform(0.25, 1), 2)
            # self.reactionTime += self.tenv.humanReactionTime - abs(round(np.random.normal(self.tenv.humanReactionTime, self.tenv.humanDistractionAmount)))
        

        print(self.tenv.environment.now, ":","Created Vehicle --> Identity:", self.identity, "; Location:", self.location.identity)
        self.tenv.environment.process(self.run())

    def __str__(self):
        return self.identity

    def run(self):
        if self.location.vehiclesAtLight.index(self) == 0:
            self.moved = self.tenv.environment.event()
            yield self.location.lightGreenEvent
            # print(self.tenv.environment.now, ":","Traffic Light is --> State:", self.location.currentState, "; For Vehicle:", self.identity)
            yield self.tenv.environment.process(self.travel_between_lights())
            # print(self.tenv.environment.now, ":","Vehicle Has Gone Through Traffic Light --> Vehicle:", self.identity)
        else: 
            self.moved = self.tenv.environment.event()
            self.position = self.location.vehiclesAtLight.index(self)
            yield self.location.vehiclesAtLight[self.position - 1].moved
            yield self.tenv.environment.process(self.travel_up_queue())
    
    def calculate_time(self, speed, distance, accelerate=True, deccelerate=True):
        if accelerate == False and deccelerate == False:
            return (distance/speed)
        elif accelerate == True and deccelerate == True:
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
        elif (accelerate == True and deccelerate == False) or (accelerate == False and deccelerate == True):
            timeToAccelerate = speed/self.acceleration
            distanceToAccelerate = speed * timeToAccelerate
            distanceAtFinalSpeed = distance - distanceToAccelerate
            if distanceToAccelerate > distance:
                timeToAccelerate = math.sqrt(distance/self.acceleration)
                maxSpeedReached = self.acceleration*(timeToAccelerate**2)
                return round(timeToAccelerate, 2)
            else:
                timeAtFinalSpeed = distanceAtFinalSpeed/speed
                return round((timeToAccelerate + timeAtFinalSpeed), 2)

    def update_vehicle_vector(self):
        if self.location.vehiclesAtLight.index(self) == 0:
            self.vector = self.location.vectorQ
        else:
            vectorDelta = [math.sin(self.location.bearingFacing) * self.gapDistance, math.cos(self.location.bearingFacing) * self.gapDistance]
            vehicleInFront = self.location.vehiclesAtLight[self.location.vehiclesAtLight.index(self) - 1]
            vectorDeltaVehicleInFrontLength = [math.sin(self.location.bearingFacing) * vehicleInFront.length, math.cos(self.location.bearingFacing) * vehicleInFront.length]
            vector = [vehicleInFront.vector[0] +  vectorDeltaVehicleInFrontLength[0] + vectorDelta[0], vehicleInFront.vector[1] +  vectorDeltaVehicleInFrontLength[1] + vectorDelta[1]]
            self.vector = list(map(lambda x: round(x, 2), vector))
        

    def travel_between_lights(self):
        self.tenv.roadBetweenLights.add_vehicle(self)
        yield self.tenv.environment.timeout(self.calculate_time(self.speed, self.location.distanceQtoPL, deccelerate=False)) # Time to leave queue and enter road between traffic light
        self.location.vehiclesAtLight.pop(self.location.vehiclesAtLight.index(self))
        self.vector = self.location.vectorPL
        self.moved.succeed()
        print(self.tenv.environment.now, ":","Vehicle is Travelling Between Lights --> Identity:", self.identity)
        yield self.tenv.environment.timeout(self.calculate_time(self.speed, self.location.distancePLtoPO, accelerate=False, deccelerate=False))
        self.vector = self.location.vectorPO
        yield self.tenv.environment.timeout(self.calculate_time(self.speed, self.tenv.calculate_distance_vectors(self.tenv.lightsList[0].vectorPosition, self.tenv.lightsList[1].vectorPosition), accelerate=False, deccelerate=False))
        self.tenv.roadBetweenLights.remove_vehicle(self)
        print(self.tenv.environment.now, ":", "Vehicle has Travelled Through Lights --> Identity:", self.identity)

    def travel_up_queue(self):
        print(self.tenv.environment.now, ":","Vehicle Moving Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        yield self.tenv.environment.timeout(self.tenv.timeToMoveUpQueue)
        self.moved.succeed()
        self.update_vehicle_vector()
        print(self.tenv.environment.now, ":","Vehicle Moved Up Queue --> Vehicle:", self.identity, "Traffic Light:", self.location.identity)
        print(self.tenv.environment.now, ":","Vehicles at Traffic Light --> Identity:", self.location.identity, "; Vehicles:", list(str(x) for x in self.location.vehiclesAtLight))
        self.tenv.environment.process(self.run())

class TrafficLight(object):
    def __init__(self, tenv, identity, vector, lightType):
        """Creates a Traffic Light
        
        Arguments:
            tenv {TrafficEnvironment} -- Traffic Environment. Used to access configured variables.
            identity {str} -- Name of light.
            position {vector} -- Vector position of where it is in the environment.
            lightType {int} -- One of 4 different layouts for traffic  lights.
        """
        self.tenv = tenv

        self.identity = identity
        self.vectorPosition = vector
        self.bearingFacing = self.tenv.calculate_angle_trig(self.vectorPosition, self.tenv.intersectingPointVector)
        self.vehiclesAtLight = []
        self.states = itertools.cycle(['red', 'redamber', 'green', 'greenamber'])
        self.currentState = next(self.states)
        self.lightGreenEvent = self.tenv.environment.event()
        self.ligthsRedEvent = self.tenv.environment.event()

        self.lightType = lightType
        self.gapQtoL = self.tenv.standardGapQtoL
        if self.lightType == 1:
            self.gapLtoO = self.tenv.standardGapLtoONonClearance
            self.vectorPL = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing-90, self.tenv.roadWidth/2)
            self.vectorQ = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing, self.gapQtoL)
            self.vectorPQ = self.tenv.calculate_vector(self.vectorQ, self.bearingFacing, self.tenv.roadWidth/2)
            self.vectorO = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing+180, self.gapLtoO)
            self.vectorPO = self.tenv.calculate_vector(self.vectorO, self.bearingFacing-90, self.tenv.roadWidth/2)
        elif self.lightType == 2:
            self.gapLtoO = self.tenv.standardGapLtoOWithClearance
            self.vectorPL = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing-90, self.tenv.roadWidth/2)
            self.vectorQ = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing, self.gapQtoL)
            self.vectorPQ = self.tenv.calculate_vector(self.vectorQ, self.bearingFacing, self.tenv.roadWidth/2)
            self.vectorO = self.tenv.calculate_vector(self.vectorPL, self.bearingFacing+180, self.gapLtoO)
            self.vectorPO = self.tenv.calculate_vector(self.vectorO, self.bearingFacing+90, self.tenv.roadWidth/2)
        elif self.lightType == 3:
            self.gapLtoO = self.tenv.standardGapLtoOWithClearance
            self.vectorPL = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing+90, self.tenv.roadWidth/2)
            self.vectorQ = self.tenv.calculate_vector(self.vectorPL, self.bearingFacing, self.gapQtoL)
            self.vectorPQ = self.tenv.calculate_vector(self.vectorQ, self.bearingFacing, self.tenv.roadWidth/2)
            self.vectorO = self.tenv.calculate_vector(self.vectorPL, self.bearingFacing+180, self.gapLtoO)
            self.vectorPO = self.tenv.calculate_vector(self.vectorO, self.bearingFacing-90, self.tenv.roadWidth/2)
        elif self.lightType == 4:
            self.gapLtoO = self.tenv.standardGapLtoONonClearance
            self.vectorPL = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing+90, self.tenv.roadWidth/2)
            self.vectorQ = self.tenv.calculate_vector(self.vectorPL, self.bearingFacing, self.gapQtoL)
            self.vectorPQ = self.tenv.calculate_vector(self.vectorQ, self.bearingFacing, self.tenv.roadWidth/2)
            self.vectorO = self.tenv.calculate_vector(self.vectorPosition, self.bearingFacing+180, self.gapLtoO)
            self.vectorPO = self.tenv.calculate_vector(self.vectorO, self.bearingFacing+90, self.tenv.roadWidth/2)
        
        self.distanceQtoPL = self.tenv.calculate_distance_vectors(self.vectorQ, self.vectorPL)
        self.distancePLtoPO = self.tenv.calculate_distance_vectors(self.vectorPL, self.vectorPO)

    def change_light_state(self):
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
        self.vehiclesBetweenLights.pop(self.tenv.roadBetweenLights.vehiclesBetweenLights.index(vehicle))
        if len(self.vehiclesBetweenLights) == 0:
            self.isEmpty.succeed()

TENV = TrafficEnvironment()