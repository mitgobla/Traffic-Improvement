import simpy
import random

class Environment():
    def __init__(self):
        self.environment = simpy.Environment()
        self.vehicleList = []
        self.environment.process(self.generate_vehicles())
        self.allowFrontCar = self.environment.event()
        self.environment.process(self.cycle())
        self.environment.run(until=100)

    def generate_vehicles(self):
        i = 0
        while True:
            if random.random() < 0.5:
                self.vehicleList.append(Vehicle(self, str(i)))
                i += 1
            yield self.environment.timeout(1)
        
    def cycle(self):
        while True:
            yield self.environment.timeout(2)
            self.allowFrontCar.succeed()
            yield self.environment.timeout(4)
            self.allowFrontCar = self.environment.event()


class Vehicle():
    def __init__(self, env, identity):
        self.env = env
        self.identity = identity
        self.moved = self.env.environment.event()
        self.position = 0
        self.env.environment.process(self.run())

    def run(self):
        if self.env.vehicleList.index(self) == 0:
            self.moved = self.env.environment.event()
            yield self.env.allowFrontCar
            yield self.env.environment.process(self.remove_car())
            print(self.env.environment.now, "Has Vehicles", list(x.identity for x in self.env.vehicleList))
        else:
            self.moved = self.env.environment.event()
            self.position = self.env.vehicleList.index(self)
            yield self.env.vehicleList[self.position - 1].moved
            yield self.env.environment.process(self.move_up_queue())
            print(self.env.environment.now, "Has Vehicles", list(x.identity for x in self.env.vehicleList))

    def remove_car(self):
        yield self.env.environment.timeout(1)
        self.env.vehicleList.pop(self.env.vehicleList.index(self))
        self.moved.succeed()
    
    def move_up_queue(self):
        yield self.env.environment.timeout(2)
        self.moved.succeed()
        self.env.environment.process(self.run())

ENV = Environment()