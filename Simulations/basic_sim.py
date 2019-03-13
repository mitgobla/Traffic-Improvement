import itertools
import json
import math
import os
import random
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interp
import simpy
from matplotlib import cm
from matplotlib.mlab import griddata
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image, ImageDraw

class TrafficEnvironment(object):
    def __init__(self):
        self.environment = simpy.Environment()

        self.timeLtoL = 5
        self.timeUpQueue = 2
        
        self.vehiclesList = []
        self.trafficLightsList = []

        self.timeGreen = 15
        self.chanceVehicleSpawnPerUnitTime = 0.2

    def start_simulation(self):
        self.create_system()

        self.environment.run(until=5000)

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
        self.trafficLightsList.append(TrafficLight(self, "A"))
        self.trafficLightsList.append(TrafficLight(self, "B"))

        self.roadBetweenLights = RoadBetweenLights(self)

        self.tmgmt = TrafficManagement(self)
        self.environment.process(self.generate_vehicles())

    def generate_vehicles(self):
        i = len(self.vehiclesList)
        while True:
            if random.random() < self.chanceVehicleSpawnPerUnitTime:
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
                yield self.tenv.environment.timeout(self.tenv.timeGreen)
                yield self.tenv.environment.timeout(1)
                light.change_light_state()



class TrafficLight:
    def __init__(self, tenv, identity):
        self.tenv = tenv
        self.identity = identity
        self.vehiclesAtLight = []
        self.states = itertools.cycle(['red', 'green'])
        self.currentState = next(self.states)
        self.lightGreenEvent = self.tenv.environment.event()
        self.ligthsRedEvent = self.tenv.environment.event()

    def change_light_state(self):
        self.currentState = next(self.states)
        if self.currentState == 'green':
            self.lightGreenEvent.succeed()
            self.lightRedEvent = self.tenv.environment.event()
        if self.currentState == 'red':
            self.lightRedEvent.succeed()
            self.lightGreenEvent = self.tenv.environment.event()

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

x = []
y = []
z = []
START = time.clock()
for lightGreenTime in range(5, 90, 2):
    for roadUsage in range(5, 35, 2):
        print(roadUsage, lightGreenTime)
        tenv = TrafficEnvironment()
        tenv.timeGreen = lightGreenTime
        tenv.chanceVehicleSpawnPerUnitTime = roadUsage * 0.01
        tenv.start_simulation()
        if tenv.averageTimeStopped <= 60:
            z.append(tenv.averageTimeStopped)
        else:
            z.append(60)
        x.append(roadUsage * 0.01)
        y.append(lightGreenTime)

minimasx = []
minimasy = []
minimasz = []
for roadUsage in range(5, 35, 2):
    indexesAtCurrentRoadUsage = []
    for index1 in range(len(x)):
        if x[index1] == roadUsage * 0.01:
            indexesAtCurrentRoadUsage.append(index1)
    tempZList = []
    tempYList = []
    for index2 in indexesAtCurrentRoadUsage:
        tempZList.append(z[index2])
        tempYList.append(y[index2])
    minIndex = np.argmin(tempZList)
    minimasx.append(roadUsage * 0.01)
    minimasy.append(tempYList[minIndex])
    minimasz.append(tempZList[minIndex])

print(minimasx)
print(minimasy)
print(minimasz)

plotx,ploty = np.meshgrid(np.linspace(np.min(x),np.max(x),50),\
                           np.linspace(np.min(y),np.max(y),50))
plotz = interp.griddata((x,y),z,(plotx,ploty), method='linear')

# lobf = np.polyfit(plotx, ploty, 1, full=True)
# lobf = interp.griddata()

# linex = plotx.argsort()[:50]
# liney = ploty.argsort()[:50]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(minimasx, minimasy, minimasz, '--k', label="Most Efficient")
ax.legend()
surf = ax.plot_surface(plotx,ploty,plotz,cstride=1,rstride=1,cmap=cm.jet)


cbar = fig.colorbar(surf, shrink=0.5, aspect=10)
#ax.figure.legend((1), ("Line"), loc=0, fancybox=True)
ax.set_title("lightGreenTime vs. roadUsage")
ax.set_xlabel('roadUsage') 
ax.set_ylabel('lightGreenTime')
ax.set_zlabel('averageTimeStopped')
END = time.clock()
plt.show()
print("Execution time:", (END - START))
