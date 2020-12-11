import salabim as sim
import time
import random
import numpy as np
import uuid
import os
import pickle
import time
from sys import platform as _platform

if 'debian' in _platform:
    runningOnPi = True
    os.system('sudo pigpiod')
    import pigpio
    controller = pigpio.pi()
else:
    runningOnPi = False

if runningOnPi:
    red = controller.set_PWM_dutycycle(17,0)
    amber = controller.set_PWM_dutycycle(27,0)
    greeen = controller.set_PWM_dutycycle(22,0)

CWD = os.path.dirname(os.path.realpath(__file__))

VIEWPORT_RESOLUTION = [2560,1600]
PERCENTAGE_TIME_SAFETY_ADDITION = 0.2
STATE_COLOURS_DICT = {"states":[{"state":"red", "rgb":(255,0,0), "pin":[17]},{"state":"redamber","rgb":(255,191,0), "pin":[17, 27]},{"state":"green", "rgb":(0,255,0), "pin":[22]},{"state":"amber","rgb":(255,191,0), "pin":[27]}]}

class VehicleSpawner(sim.Component):
    def setup(self, trafficEnv):
        self.trafficEnv = trafficEnv
        self.lightList = trafficEnv.lightList
        self.randomUniform = sim.Uniform(0,1)
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
        print('car created')
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
                yield self.hold(self.trafficEnv.timeLtoLSafety)
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


def check_light_state(light, state, updateRealLight):
    if light.state.value() == state:
        for stateDict in STATE_COLOURS_DICT["states"]:
            if stateDict["state"] == state:
                if runningOnPi:
                    if updateRealLight:
                        for pin in stateDict["pin"]:
                            controller.set_PWM_dutycycle(pin,255)
                return stateDict["rgb"]+tuple([255])
    else:
        for stateDict in STATE_COLOURS_DICT["states"]:
            if stateDict["state"] == state:
                if runningOnPi:
                    if updateRealLight:
                        for pin in stateDict["pin"]:
                            controller.set_PWM_dutycycle(pin,0)
                return stateDict["rgb"]+tuple([60])

def setup_animation_window(trafficEnv, env):
    # env.background_color('90%gray')
    sim.AnimateText(text="Traffic Environment Simulation", x=10, y=728, textcolor='20%gray', fontsize=30)

    # Animation setup for Light A
    sim.AnimateText(text="Light A", x=10, y=700, textcolor='20%gray', fontsize=20)
    sim.AnimateRectangle(spec=(10, 530, 70, 690), fillcolor='black')
    sim.AnimateCircle(radius=20, x=40, y=660, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'red', True))
    sim.AnimateCircle(radius=20, x=40, y=610, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'amber', True))
    sim.AnimateCircle(radius=20, x=40, y=560, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'green', True))
    sim.AnimateRectangle(spec=(83,650,786,714), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
    sim.AnimateQueue(trafficEnv.lightList[0].vehiclesQueue, x=110, y=674, title='Queue', direction='e', max_length=14)
    sim.AnimateRectangle(spec=(83,525,786,646), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
    sim.AnimateMonitor(trafficEnv.lightList[0].vehiclesQueue.length_of_stay, title="Waiting Time", x=90, y=530, width=689, height=100, horizontal_scale=2, vertical_scale=1)
    sim.AnimateRectangle(spec=(790,525,1024,714), fillcolor='whitesmoke')
    sim.AnimateText(text=lambda: "Queue Length: " + str(len(trafficEnv.lightList[0].vehiclesQueue)), x=795, y=694, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Queue Length Mean: " + str(round(trafficEnv.lightList[0].vehiclesQueue.length.mean(), 1)), x=795, y=679, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Queue Length Maximum: " + str(round(trafficEnv.lightList[0].vehiclesQueue.length.maximum(), 1)), x=795, y=664, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Waiting Time Mean: " + str(round(trafficEnv.lightList[0].vehiclesQueue.length_of_stay.mean(), 1)), x=795, y=634, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Waiting Time Maximum: " + str(round(trafficEnv.lightList[0].vehiclesQueue.length_of_stay.maximum(), 1)), x=795, y=619, fontsize=15, textcolor='20%gray')

    # Animation setup for Light B.
    sim.AnimateText(text="Light B", x=10, y=450, textcolor='20%gray', fontsize=20)
    sim.AnimateRectangle(spec=(10, 280, 70, 440), fillcolor='black')
    sim.AnimateCircle(radius=20, x=40, y=410, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'red', False))
    sim.AnimateCircle(radius=20, x=40, y=360, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'amber', False))
    sim.AnimateCircle(radius=20, x=40, y=310, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'green', False))
    sim.AnimateRectangle(spec=(83,400,786,464), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
    sim.AnimateQueue(trafficEnv.lightList[1].vehiclesQueue, x=110, y=424, title='Queue', direction='e', max_length=14)
    sim.AnimateRectangle(spec=(83,275,786,396), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
    sim.AnimateMonitor(trafficEnv.lightList[1].vehiclesQueue.length_of_stay, title="Waiting Time", x=90, y=280, width=689, height=100, horizontal_scale=2, vertical_scale=1)
    sim.AnimateRectangle(spec=(790,275,1024,464), fillcolor='whitesmoke')
    sim.AnimateText(text=lambda: "Queue Length: " + str(len(trafficEnv.lightList[1].vehiclesQueue)), x=795, y=444, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Queue Length Mean: " + str(round(trafficEnv.lightList[1].vehiclesQueue.length.mean(), 1)), x=795, y=429, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Queue Length Maximum: " + str(round(trafficEnv.lightList[1].vehiclesQueue.length.maximum(), 1)), x=795, y=414, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Waiting Time Mean: " + str(round(trafficEnv.lightList[1].vehiclesQueue.length_of_stay.mean(), 1)), x=795, y=384, fontsize=15, textcolor='20%gray')
    sim.AnimateText(text=lambda: "Waiting Time Maximum: " + str(round(trafficEnv.lightList[1].vehiclesQueue.length_of_stay.maximum(), 1)), x=795, y=369, fontsize=15, textcolor='20%gray')

def run_simulation(resData):
    print('1')
    env = sim.Environment(trace=False, random_seed=time.time())
    env.animate(True)
    print('2')
    env.animation_parameters(speed=3)
    print('3')
    trafficEnv = TrafficEnvironment(resData, resData['optimalGreenTime'])
    print('4')
    setup_animation_window(trafficEnv, env)
    
    print('5')
    env.run(5000)
