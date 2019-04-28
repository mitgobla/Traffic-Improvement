import os
from flask import Flask, request, render_template, redirect, Response
from flask_classful import FlaskView, route
import threading
import pickle

import traffic_env_optimising
import traffic_env_running

CWD = os.path.dirname(os.path.realpath(__file__))

debug = True
app = Flask(__name__)
app.config.from_object(__name__)

LIGHT_SENSOR_SENSITIVITY = 2

class HomeView(FlaskView):
    route_base='/home'

    def index(self):
        return render_template("home.html")

class GetTimingsView(FlaskView):
    route_base='/get-timings'

    def index(self):
        return render_template("get-timings.html")

    @route('/submit', methods=['GET', 'POST'])
    def submit(self):
        self.lightDistance = float(request.form["distanceBetweenLightsRange"])
        self.speed = float(request.form["speedRange"])
        self.timeUpQueue = float(request.form["queueTimeRange"])
        self.light1Busyness = float(request.form["busyness1Range"])
        self.light2Busyness = float(request.form["busyness2Range"])
        if "sensor1Check" in request.form:
            self.light1SensorSensitivity = LIGHT_SENSOR_SENSITIVITY
        else:
            self.light1SensorSensitivity = -1

        if "sensor2Check" in request.form:
            self.light2SensorSensitivity = LIGHT_SENSOR_SENSITIVITY
        else:
            self.light2SensorSensitivity = -1

        self.envTime = float(request.form["envTime"])
        self.greenTimeRange = [float(request.form.getlist('greenTimeRange')[0]), float(request.form.getlist('greenTimeRange')[1])]
        self.greenTimeStep = float(request.form["greenTimeStep"])

        self.environmentData = {'lightDistance':self.lightDistance,
                                'speed':self.speed,
                                'timeUpQueue':self.timeUpQueue,
                                'lightData':[{'busyness':self.light1Busyness,
                                                'sensorSensitivity':self.light1SensorSensitivity},
                                                {'busyness':self.light2Busyness,
                                                'sensorSensitivity':self.light2SensorSensitivity}]}
        self.optimisationData = {'envTime':self.envTime,
                                'lightGreenTimeRange':self.greenTimeRange,
                                'lightGreenTimeStep':self.greenTimeStep,
                                'iterationsPerSetting':5}

        self.simulationThread = OptimisationThread(self.environmentData, self.optimisationData)
        self.simulationThread.name = "optThread"
        self.simulationThread.start()
        return redirect("/get-timings/optimisation-running")

    @route('/optimisation-running')
    def running_optimisation(self):
        activeThreadNames = list(thread.name for thread in threading.enumerate())
        if "optThread" in activeThreadNames:
            simThread = threading.enumerate()[activeThreadNames.index("optThread")]
            return render_template('optimisation-running.html', envData = simThread.envData, optData = simThread.optData)
        else:
            return redirect('/get-timings/results')
    
    @route('/results')
    def finished_optimising(self):
        with open(os.path.join(CWD, 'TempData', 'optimisationResults.pkl'), 'rb') as tempData:
            optResults = pickle.load(tempData)
        bestLightGreenTime = optResults['optimalGreenTime']
        lowestWaitingTime = optResults['averageWaitingTime']
        graphFileName = optResults['graphFileName']
        return render_template('optimisation-results.html', bestTiming = str(bestLightGreenTime), leastWaitingTime = str(round(lowestWaitingTime, 1)), graphName = graphFileName)

class SimulationView(FlaskView):
    route_base='/use-timings'

    @route('/simulation', methods=['POST','GET'])
    def index(self):
        with open(os.path.join(CWD, 'TempData', 'optimisationResults.pkl'), 'rb') as tempData:
            optResults = pickle.load(tempData)
        self.simThread = SimulationThread(optResults)
        self.simThread.start()
        return render_template('simulation.html')

class OptimisationThread(threading.Thread):
    def __init__(self, envData, optData):
        threading.Thread.__init__(self)
        self.envData = envData
        self.optData = optData
    def run(self):
        traffic_env_optimising.run_optimisation(self.envData, self.optData)

class SimulationThread(threading.Thread):
    def __init__(self, resData):
        threading.Thread.__init__(self)
        self.resData = resData
    
    def run(self):
        traffic_env_running.run_simulation(self.resData)

HomeView.register(app)
GetTimingsView.register(app)
SimulationView.register(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=debug)
