import salabim as sim
import time
import itertools

# sim.random_seed = 123

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
env.run(till=5000)
print("Time to run:", time.time() - time0)
for light in trafficEnv.lightList:
    light.vehiclesQueue.print_statistics()
    print(len(light.vehiclesQueue))

