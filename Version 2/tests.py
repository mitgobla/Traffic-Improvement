import salabim as sim

class Light(sim.Component):
    def setup(self, lightName):
        self.lightName = lightName
        self.vehiclesQueue = sim.Queue(self.lightName)

env = sim.Environment(trace=True)
lightList = []
lightList.append(Light(lightName="light0"))
lightList.append(Light(lightName="light1"))
env.run(till=500)
for light in lightList:
    print(light.vehiclesQueue.name())