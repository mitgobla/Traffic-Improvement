import salabim as sim
import time
import itertools

sim.random_seed = 123
VIEWPORT_RESOLUTION = [2560,1600]
STATE_COLOURS_DICT = {"states":[{"state":"red", "rgb":(255,0,0)},{"state":"green", "rgb":(0,255,0)}]}

class TrafficEnvironment():
    def __init__(self):
        self.lightList = []
        for lightNum in range(2):
            self.lightList.append(Light())
        self.roadBetween = RoadBetween()
        self.timeLtoL = 10
        self.timeLtoLSafety = 20
        self.timeLightGreen = 40
        self.timeUpQueue = 2
        self.vehicleGenerateChance = 0.3
        self.vehicleMeanPeriod = 1/self.vehicleGenerateChance

class VehicleGenerator(sim.Component):
    def setup(self, trafficEnv):
        self.trafficEnv = trafficEnv
        self.lightList = trafficEnv.lightList
        self.vehicleGenerateChance = trafficEnv.vehicleGenerateChance
    def process(self):
        while True:
            if sim.IntUniform(1,2).sample() == 1:
                Vehicle(light=self.lightList[0], trafficEnv=trafficEnv)
            else:
                Vehicle(light=self.lightList[1], trafficEnv=trafficEnv)
            yield self.hold(sim.Uniform(self.trafficEnv.vehicleMeanPeriod-2, self.trafficEnv.vehicleMeanPeriod+2).sample())

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
                light.change_state(state='green')
                yield self.hold(self.timeLightGreen)
                light.change_state(state='red')


class RoadBetween(sim.Component):
    def setup(self):
        self.vehiclesInBetweenBool = sim.State(
            self.name() + ".vehiclesPresentState", value=False)
        self.vehiclesQueue = sim.Queue(
            self.name() + ".vehiclesQueue")


class Light(sim.Component):
    def setup(self):
        self.state = sim.State((self.name() + ".state"), value="red")
        self.vehiclesQueue = sim.Queue(self.name() + ".queue")

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


time0 = time.time()
env = sim.Environment(trace=False)
trafficEnv = TrafficEnvironment()
trafficManagement = TrafficManagement(trafficEnv=trafficEnv)
VehicleGenerator = VehicleGenerator(trafficEnv=trafficEnv)

def check_light_state(light, state):
    if light.state.value() == state:
        for stateDict in STATE_COLOURS_DICT["states"]:
            if stateDict["state"] == state:
                return stateDict["rgb"]+tuple([255])
    else:
        for stateDict in STATE_COLOURS_DICT["states"]:
            if stateDict["state"] == state:
                return stateDict["rgb"]+tuple([60])
    
        

numberOfLights = len(trafficEnv.lightList)
sim.AnimateText(text="Traffic Environment Simulation", x=10, y=728, textcolor='20%gray', fontsize=30)
sim.AnimateText(text="Light A", x=10, y=700, textcolor='20%gray', fontsize=20)
sim.AnimateRectangle(spec=(10, 530, 70, 690), fillcolor='black')
sim.AnimateCircle(radius=20, x=40, y=660, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'red'))
sim.AnimateCircle(radius=20, x=40, y=610, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'red'))
sim.AnimateCircle(radius=20, x=40, y=560, fillcolor=lambda: check_light_state(trafficEnv.lightList[0], 'green'))
sim.AnimateRectangle(spec=(83,650,786,714), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
sim.AnimateQueue(trafficEnv.lightList[0].vehiclesQueue, x=110, y=674, title='Queue', direction='e', max_length=14)
sim.AnimateRectangle(spec=(83,525,786,646), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
sim.AnimateMonitor(trafficEnv.lightList[0].vehiclesQueue.length_of_stay, title="Waiting Time", x=90, y=530, width=689, height=100, horizontal_scale=2, vertical_scale=1)

sim.AnimateText(text="Light B", x=10, y=450, textcolor='20%gray', fontsize=20)
sim.AnimateRectangle(spec=(10, 280, 70, 440), fillcolor='black')
sim.AnimateCircle(radius=20, x=40, y=410, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'red'))
sim.AnimateCircle(radius=20, x=40, y=360, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'red'))
sim.AnimateCircle(radius=20, x=40, y=310, fillcolor=lambda: check_light_state(trafficEnv.lightList[1], 'green'))
sim.AnimateRectangle(spec=(83,400,786,464), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
sim.AnimateQueue(trafficEnv.lightList[1].vehiclesQueue, x=110, y=424, title='Queue', direction='e', max_length=14)
sim.AnimateRectangle(spec=(83,275,786,396), linecolor='90%gray', linewidth=2, fillcolor='whitesmoke')
sim.AnimateMonitor(trafficEnv.lightList[1].vehiclesQueue.length_of_stay, title="Waiting Time", x=90, y=280, width=689, height=100, horizontal_scale=2, vertical_scale=1)


env.background_color('90%gray')
env.animate(True)
env.animation_parameters(speed=50)
env.run()
print("Time to run:", time.time() - time0)
for light in trafficEnv.lightList:
    light.vehiclesQueue.print_statistics()
    print(len(light.vehiclesQueue))

