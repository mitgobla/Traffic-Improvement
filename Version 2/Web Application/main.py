import os
from flask import Flask, request, render_template, redirect, Response
from flask_classful import FlaskView, route
import threading

import traffic_env_optimising

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

        self.simulationThread = SimulationThread(self.environmentData, self.optimisationData)
        self.simulationThread.name = "simThread"
        self.simulationThread.start()
        return redirect("/get-timings/optimisation-running")

    @route('/optimisation-running')
    def running_optimisation(self):
        activeThreadNames = list(thread.name for thread in threading.enumerate())
        if "simThread" in activeThreadNames:
            simThread = threading.enumerate()[activeThreadNames.index("simThread")]
            return render_template('optimisation-running.html', envData = simThread.envData, optData = simThread.optData)
        else:
            return redirect('/get-timings/results')
    
    @route('/results')
    def finished_optimising(self):
        with open(os.path.join(CWD, 'TempData', 'tempOptimisationData.txt'), 'r') as tempData:
            dataString = tempData.read()
        bestLightGreenTime = float(dataString.split(',')[0])
        lowestWaitingTime = float(dataString.split(',')[1])
        graphFileName = dataString.split(',')[2]
        return render_template('optimisation-results.html', bestTiming = str(bestLightGreenTime), leastWaitingTime = str(round(lowestWaitingTime, 1)), graphName = graphFileName)

class SimulationThread(threading.Thread):
    def __init__(self, envData, optData):
        threading.Thread.__init__(self)
        self.envData = envData
        self.optData = optData
    def run(self):
        self.optimisationResults = traffic_env_optimising.run_optimisation(self.envData, self.optData)

HomeView.register(app)
GetTimingsView.register(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=debug)