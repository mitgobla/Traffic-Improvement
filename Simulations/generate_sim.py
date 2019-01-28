import simpy
import random
import threading
import itertools
import logging

logging.basicConfig(filename='Simulations//output.log', filemode='w', format='%(message)s', level=logging.DEBUG)

class TrafficLight(object):

    def __init__(self, env: simpy.Environment):
        self.coloursleft = itertools.cycle(['red', 'amber', 'green', 'amber'])
        self.coloursright = itertools.cycle(['green', 'amber', 'red', 'amber'])
        self.currentColourLeft = None
        self.currentColourRight = None
        self.env = env

        self.cars_left = []
        self.cars_right = []

        #self.thread = threading.Thread(target=self.cyclelight)

    def cycle_light(self):
        while True:
            #logging.info(str(self.env.now)+" Light "+self.currentColour)
            self.currentColourLeft = next(self.coloursleft)
            self.currentColourRight = next(self.coloursright)
            if self.currentColourLeft == 'red':
                for car in range(20):
                    try:
                        self.remove_car_right()
                    except IndexError:
                        pass
                        ##logging.info(str(self.env.now)+": No Cars Waiting")
                    logging.info(str(len(self.cars_left)))
                    logging.info(str(len(self.cars_right)))
                    yield self.env.timeout(1)
            elif self.currentColourLeft == 'amber':
                for waiting in range(2):
                    logging.info(str(len(self.cars_left)))
                    logging.info(str(len(self.cars_right)))
                    yield self.env.timeout(1)
            elif self.currentColourLeft == 'green':
                for car in range(20):
                    try:
                        self.remove_car_left()
                    except IndexError:
                        pass
                        ##logging.info(str(self.env.now)+": No Cars Waiting")
                    logging.info(str(len(self.cars_left)))
                    logging.info(str(len(self.cars_right)))
                    yield self.env.timeout(1)
    
    def current_left(self):
        return self.currentColourLeft

    def current_right(self):
        return self.currentColourRight
    
    def add_car_left(self, car):
        self.cars_left.append(car)
    
    def add_car_right(self, car):
        self.cars_right.append(car)

    def remove_car_left(self):
        self.cars_left.pop(0)

    def remove_car_right(self):
        self.cars_right.pop(0)

class Car(object):

    def __init__(self, name, env: simpy.Environment, light: TrafficLight):
        self.name = str(name)
        self.env = env
        self.light = light

    def run(self):
        direction = random.randint(0, 1)
        if direction:
            self.light.add_car_left(self)
        else:
            self.light.add_car_right(self)
        #logging.info(str(self.env.now)+" Car "+self.name+" Arrive")
        while self in self.light.cars_left or self in self.light.cars_right:
            yield env.timeout(1)
        #logging.info(str(self.env.now)+" Car "+self.name+" Leave")


class Environment(object):

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.env.process(self.setup())
    
    def setup(self):
        light = TrafficLight(self.env)
        self.env.process(light.cycle_light())
        i = 1
        # for i in range(4):
        #     car = Car(i,self.env, light)
        #     self.env.process(car.run())
        
        while True:
            yield self.env.timeout(random.randint(1, 2))
            i += 1
            car = Car(i, self.env, light)
            self.env.process(car.run())
        
random.seed()
env = simpy.Environment()
trafficEnvironment = Environment(env)
#trafficEnvironment.setup()
env.run(until=2000)

