import simpy

class Environment():
    def __init__(self):
        self.environment = simpy.Environment()
        self.vehicleList = []
        self.environment.process(self.generateVehicles())
        self.environment.run(until=100)
        self.allowFrontCar = self.environment.event()

    def generate_vehicles(self):
        i = 0
        while True:
            if random.random() < self.probabiliyNewVehiclePerUnitTime:
                self.vehiclesList.append(Vehicle(self, str(i)))
                i += 1
            yield self.environment.timeout(self.timePerVehicleGeneration)
        
    def cycle(self):
        while True:
            yield self.environment.timeout(2)
            self.allowFrontCar.succeed()
            yield self.environment.timout(4)
            self.allowFrontCar = self.environment.event()


class Vehicle():
    def __init__(self, env, identity):
        self.env = env
        self.identity = identity
        self.moved = self.env.environment.event()
        self.position = 0

    def run(self):
        if self.env.vehicleList.index(self) == 0:
            yield self.allowFrontCar
            yield self.env.process(self.removeCar())
        else:
            self.position = self.env.vehicleList.index(self)
            yield self.env.vehicleList[self.position - 1]
            yield self.env.process(self.moveUpList())

    def removeCar(self):
        yield self.env.environment.timeout(1)
        self.moved.succeed()
    
    def moveUpList(self):
       yield self.env.environment.timout(0.5)
       self.position = self.env.vehicleList.index(self)
        
