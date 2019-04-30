import salabim as sim
import time
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
import random
import numpy as np

VIEWPORT_RESOLUTION = [2560,1600]
PERCENTAGE_TIME_SAFETY_ADDITION = 0.2
STATE_COLOURS_DICT = {"states":[{"state":"red", "rgb":(255,0,0)},{"state":"redamber","rgb":(255,191,0)},{"state":"green", "rgb":(0,255,0)},{"state":"amber","rgb":(255,191,0)}]}

class VehicleSpawner(sim.Component):
    def setup(self, trafficEnv):
        self.trafficEnv = trafficEnv
        self.lightList = trafficEnv.lightList
        self.randomUniform = sim.Uniform(0,1)
        print(self.randomUniform.sample())
    def process(self):
        while True:
            for light in self.lightList:
                if light.busyness > self.randomUniform.sample():
                    Vehicle(light=light, trafficEnv=self.trafficEnv)
            yield self.hold(1)

class TrafficManagement(sim.Component):
    def setup(self, trafficEnv):
        self.trafficEnv = trafficEnv
        self.lightList = trafficEnv.lightList
        self.timeLightGreen = trafficEnv.timeLightGreen
        self.timeLtoLSafety = trafficEnv.timeLtoLSafety

    def process(self):
        while True:
            for light in self.lightList:
                yield self.hold(self.timeLtoLSafety)
                light.change_state(state='amber')
                yield self.hold(1)
                light.change_state(state='green')
                yield self.wait((light.movementState, 'none'), fail_delay=self.timeLightGreen)
                light.change_state(state='amber')
                yield self.hold(1)
                light.change_state(state='red')


class TrafficEnvironment():
    def __init__(self, envData, timeLightGreen):
        self.lightList = []
        for lightNum in range(2):
            self.lightList.append(Light(sensitivity=envData['lightData'][lightNum]['sensorSensitivity'], busyness=envData['lightData'][lightNum]['busyness']))
        self.roadBetween = RoadBetween()
        self.distanceLtoL = envData['lightDistance']
        self.speed = envData['speed'] / 2.237
        self.timeLtoL = self.distanceLtoL / self.speed
        self.timeLtoLSafety = self.timeLtoL * (1 + PERCENTAGE_TIME_SAFETY_ADDITION)
        self.timeLightGreen = timeLightGreen
        self.timeUpQueue = envData['timeUpQueue']

        self.vehicleSpawner = VehicleSpawner(trafficEnv=self)
        self.trafficManagement = TrafficManagement(trafficEnv=self)


class RoadBetween(sim.Component):
    def setup(self):
        self.vehiclesInBetweenBool = sim.State(
            self.name() + ".vehiclesPresentState", value=False)
        self.vehiclesQueue = sim.Queue(
            self.name() + ".vehiclesQueue")


class Light(sim.Component):
    def setup(self, sensitivity, busyness):
        self.state = sim.State((self.name() + ".state"), value="red")
        self.vehiclesQueue = sim.Queue(self.name() + ".queue")
        self.movementSensorSensitivity = sensitivity
        self.movementState = sim.State(self.name() + ".movementState", value='movement')
        self.busyness = busyness

    def process(self):
        while True:
            if self.movementSensorSensitivity == -1:
                pass
            else:
                if len(self.vehiclesQueue) == 0:
                    yield self.hold(self.movementSensorSensitivity)
                    if len(self.vehiclesQueue) == 0:
                        self.movementState.set('none')
                elif len(self.vehiclesQueue) > 0:
                    self.movementState.set('movement')
            yield self.hold(0.1)

    def change_state(self, state):
        self.state.set(state)


class Vehicle(sim.Component):
    def setup(self, light, trafficEnv):
        self.trafficEnv = trafficEnv
        self.roadBetween = trafficEnv.roadBetween
        self.atLight = light
        self.movedState = sim.State(self.name() + ".movedState")
        self.atLight.vehiclesQueue.add(self)

    def process(self):
        while True:
            if self.atLight.vehiclesQueue.index(self) == 0:
                yield self.wait((self.atLight.state, 'green'))
                # Travelling Between Lights
                self.roadBetween.vehiclesQueue.add(self)
                self.roadBetween.vehiclesInBetweenBool.set(True)
                self.atLight.vehiclesQueue.remove(self)
                self.movedState.set()
                yield self.hold(self.trafficEnv.timeLtoL)
                self.roadBetween.vehiclesQueue.remove(self)
                if len(self.roadBetween.vehiclesQueue) == 0:
                    self.roadBetween.vehiclesInBetweenBool.set(False)
            elif self not in self.atLight.vehiclesQueue:
                break
            else:
                vehicleInFront = self.atLight.vehiclesQueue[self.atLight.vehiclesQueue.index(self)-1]
                yield self.wait(vehicleInFront.movedState)
                # Moving Up Queue
                yield self.hold(self.trafficEnv.timeUpQueue)
                self.movedState.set()
                yield self.hold(0.01)
                self.movedState.set(False)
                self.process()

def run_optimisation(envData, optData):
    for lightGreenTime in range(int(optData['lightGreenTimeRange'][0]), int(optData['lightGreenTimeRange'][1]), int(optData['lightGreenTimeStep'])):
        runningAverageTotal = 0
        dataArray = []
        for iter in range(int(optData['iterationsPerSetting'])):
            averageWaitingTime = 0
            sim.random_seed = time.time()
            print(lightGreenTime)
            env = sim.Environment(trace=False, random_seed=time.time())
            env.animation_parameters(speed=10)
            trafficEnv = TrafficEnvironment(envData, lightGreenTime)
            env.run(int(optData['envTime']))
            averageWaitingTime = sum([trafficEnv.lightList[0].vehiclesQueue.length_of_stay.mean(), trafficEnv.lightList[1].vehiclesQueue.length_of_stay.mean()]) / 2
            runningAverageTotal += averageWaitingTime
            print(averageWaitingTime)
        dataArray.append([lightGreenTime, runningAverageTotal/20])

    x, y = zip(*dataArray)

    xnew = np.linspace(np.array(x).min(), np.array(x).max(), 300)

    spl = make_interp_spline(np.array(x), np.array(y), k=3)
    ynew = spl(xnew)


    plt.plot(xnew, ynew, color='g')
    plt.xlabel('Light Green Time')
    plt.ylabel('Average Waiting Time')
    plt.show()