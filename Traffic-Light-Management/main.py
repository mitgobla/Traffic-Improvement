import threading
import numpy as np
import os
import io

from flask import Flask, request, render_template, redirect, Response
from flask_classful import FlaskView, route

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.mlab import griddata
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate as interp

import traffic_simulator

CWD = os.path.dirname(os.path.realpath(__file__))

debug = True
app = Flask(__name__)
app.config.from_object(__name__)

class HomeView(FlaskView):
    route_base='/home'

    def index(self):
        return render_template("index.html")
    

class GetTimingView(FlaskView):
    route_base='/get-timings'

    def index(self):
        return render_template("env_setup.html")

class SimulateView(FlaskView):
    route_base='/simulate'

    @route('/submit', methods=['GET', 'POST'])
    def submit_simulation(self):
        self.distanceLtoL = float(request.form["distanceLtoL"])
        self.speedLimitLtoL = float(request.form["speedLimitLtoL"])
        self.timeUpQueue = float(request.form["timeUpQueue"])
        if "lightsDetectMovement" in request.form:
            self.lightsDetectMovement = True
        else:
            self.lightsDetectMovement = False
        self.simTime = int(request.form["simTime"])
        self.lightGreenTimesRange = [int(request.form["lightGreenTimeStart"]), int(request.form["lightGreenTimeEnd"])]
        self.roadUsagesRange = [float(request.form["roadUsageStart"]), float(request.form["roadUsageEnd"])]
        self.simulationThread = SimulationThread(self.distanceLtoL, self.speedLimitLtoL, self.timeUpQueue, self.lightsDetectMovement, self.simTime, self.lightGreenTimesRange, self.roadUsagesRange)
        self.simulationThread.name = "simThread"
        self.simulationThread.start()
        return redirect("/simulate/simulation-running")
    
    @route('/simulation-running')
    def running_simulation(self):
        response = Response(redirect('/simulate/simulation-results'))
        activeThreadNames = list(thread.name for thread in threading.enumerate())
        if "simThread" in activeThreadNames:
            simThread = threading.enumerate()[activeThreadNames.index("simThread")]
            return render_template('simulation_running.html', currentIteration=simThread.currentIteration, totalIterations=simThread.numberOfIterations, percentageDone=round((simThread.currentIteration/simThread.numberOfIterations) * 100), distanceLtoL=simThread.distanceLtoL, speedLimitLtoL=simThread.speedLimitLtoL, timeUpQueue=simThread.timeUpQueue, simTime=simThread.simTime, lightsDetectMovement=simThread.lightsDetectMovement)
        else:
            return redirect('/simulate/simulation-results')

    @route('/simulation-results')
    def finished_simulation(self):
        return render_template('simulation_results.html')


class SimulationThread(threading.Thread):
    def __init__(self, distanceLtoL, speedLimitLtoL, timeUpQueue, lightsDetectMovement, simTime, lightGreenTimesRange, roadUsagesRange):
        threading.Thread.__init__(self)
        self.distanceLtoL = distanceLtoL
        self.speedLimitLtoL = speedLimitLtoL
        self.timeUpQueue = timeUpQueue
        self.lightsDetectMovement = lightsDetectMovement
        self.simTime = simTime
        self.lightGreenTimesRange = lightGreenTimesRange
        self.roadUsageRange = roadUsagesRange
        self.timeGreenStep = 5
        self.roadUsageStep = 0.05

        self.numberOfIterations = round((((self.roadUsageRange[1]-self.roadUsageRange[0])/self.roadUsageStep)+2)*(((self.lightGreenTimesRange[1]-self.lightGreenTimesRange[0])/self.timeGreenStep)+2))
    
    def run(self):
        self.currentIteration = 0
        x = []
        y = []
        z = []
        for timeGreen in range(self.lightGreenTimesRange[0], self.lightGreenTimesRange[1]+self.timeGreenStep, self.timeGreenStep):
            for roadUsage in np.arange(self.roadUsageRange[0], self.roadUsageRange[1]+self.roadUsageStep, self.roadUsageStep):
                self.currentIteration += 1
                tenv = traffic_simulator.TrafficEnvironment()
                tenv.set_env_variables(self.distanceLtoL, self.speedLimitLtoL, self.timeUpQueue, self.lightsDetectMovement, self.simTime, timeGreen, roadUsage)

                tenv.start_simulation()
                if tenv.averageTimeStopped <= 60:
                    z.append(tenv.averageTimeStopped)
                else:
                    z.append(60)
                x.append(roadUsage)
                y.append(timeGreen)

        minimasx = []
        minimasy = []
        minimasz = []
        for roadUsage in np.arange(self.roadUsageRange[0], self.roadUsageRange[1]+self.roadUsageStep, self.roadUsageStep):
            indexesAtCurrentRoadUsage = []
            for index1 in range(len(x)):
                if x[index1] == roadUsage:
                    indexesAtCurrentRoadUsage.append(index1)
            tempZList = []
            tempYList = []
            for index2 in indexesAtCurrentRoadUsage:
                tempZList.append(z[index2])
                tempYList.append(y[index2])
            minIndex = np.argmin(tempZList)
            minimasx.append(roadUsage)
            minimasy.append(tempYList[minIndex])
            minimasz.append(tempZList[minIndex])

        plotx,ploty = np.meshgrid(np.linspace(np.min(x),np.max(x),50),\
                                np.linspace(np.min(y),np.max(y),50))
        plotz = interp.griddata((x,y),z,(plotx,ploty), method='linear')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(minimasx, minimasy, minimasz, '--k', label="Most Efficient")
        ax.legend()
        surf = ax.plot_surface(plotx,ploty,plotz,cstride=1,rstride=1,cmap=cm.jet)


        cbar = fig.colorbar(surf, shrink=0.5, aspect=10)
        ax.set_title("lightGreenTime vs. roadUsage")
        ax.set_xlabel('roadUsage') 
        ax.set_ylabel('lightGreenTime')
        ax.set_zlabel('averageTimeStopped')
        ax.view_init(elev=30, azim=-150)
        buf = io.BytesIO()
        with open(os.path.join(CWD, "static/images/tempGraph.svg"), "wb") as tempGraphFile:
            plt.savefig(tempGraphFile, format='svg')
        plt.close()
        plt_bytes = buf.getvalue()
        buf.close()
        self.graphImageBytes = plt_bytes


HomeView.register(app)
GetTimingView.register(app)
SimulateView.register(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=debug)