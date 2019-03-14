import time
import sys
import threading
import os

import traffic_flow_sim

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.mlab import griddata
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.mplot3d import Axes3D
import scipy.interpolate as interp
import numpy as np
import flask
from flask import request

CWD = os.path.dirname(os.path.realpath(__file__))
print(CWD)

# FLASK INITIALISATION
DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)


@APP.route('/', methods=['GET', 'POST'])
def index():
    # Home Page
    return flask.render_template("env_creation.html")

@APP.route('/simulate', methods=['GET', 'POST'])
def simulate():
    if request.method == 'POST':
        print(request.method)
        timeLtoL = int(request.form["timeLtoL"])
        timeUpQueue = int(request.form["timeUpQueue"])
        if "lightDetectMovement" in request.form:
            lightsDetectMovement = True
        else:
            lightsDetectMovement = False
        simTime = int(request.form["simTime"])
        lightGreenTimeRange = [int(request.form["lightGreenTimeStart"]), int(request.form["lightGreenTimeEnd"])]
        chanceVehicleAddedRange = [int(float(request.form["chanceVehicleAddedStart"])*100), int(float(request.form["chanceVehicleAddedEnd"])*100)]

        simulationThread = SimulationThread(timeLtoL, timeUpQueue, lightsDetectMovement, simTime, lightGreenTimeRange, chanceVehicleAddedRange)
        simulationThread.run()

        return flask.render_template("finishedSimulation.html", graphPlot="static/images/graph_image.png")

class SimulationThread():
    def __init__(self, timeLtoL, timeUpQueue, lightsDetectMovement, simTime, lightGreenTimeRange, chanceVehicleAddedRange):
        self.timeLtoL = timeLtoL
        self.timeUpQueue = timeUpQueue
        self.lightDetectMovement = lightsDetectMovement
        self.simTime = simTime
        self.lightGreenTimeRange = lightGreenTimeRange
        self.chanceVehicleAddedRange = chanceVehicleAddedRange
    
    def run(self):
        print("Running Thread")
        x = []
        y = []
        z = []
        for lightGreenTime in range(self.lightGreenTimeRange[0], self.lightGreenTimeRange[1], 2):
            for roadUsage in range(self.chanceVehicleAddedRange[0], self.chanceVehicleAddedRange[1], 2):
                print(roadUsage, lightGreenTime)
                
                tenv = traffic_flow_sim.TrafficEnvironment()
                tenv.timeGreen = lightGreenTime
                tenv.chanceVehicleSpawnPerUnitTime = roadUsage * 0.01
                tenv.simTime = self.simTime
                tenv.trafficLightDetectMovement = self.lightDetectMovement
                tenv.timeLtoL = self.timeLtoL
                tenv.timeUpQueue = self.timeUpQueue

                tenv.start_simulation()
                if tenv.averageTimeStopped <= 60:
                    z.append(tenv.averageTimeStopped)
                else:
                    z.append(60)
                x.append(roadUsage * 0.01)
                y.append(lightGreenTime)

        minimasx = []
        minimasy = []
        minimasz = []
        for roadUsage in range(self.chanceVehicleAddedRange[0], self.chanceVehicleAddedRange[1], 2):
            indexesAtCurrentRoadUsage = []
            for index1 in range(len(x)):
                if x[index1] == roadUsage * 0.01:
                    indexesAtCurrentRoadUsage.append(index1)
            tempZList = []
            tempYList = []
            for index2 in indexesAtCurrentRoadUsage:
                tempZList.append(z[index2])
                tempYList.append(y[index2])

            print(tempZList)
            minIndex = np.argmin(tempZList)
            minimasx.append(roadUsage * 0.01)
            minimasy.append(tempYList[minIndex])
            minimasz.append(tempZList[minIndex])
        print(minimasx)
        print(minimasy)
        print(minimasz)

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
        with open(os.path.join(CWD, "static/images/graph_image.png"), "wb") as imageFile:
            plt.savefig(imageFile)


if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=80, debug=DEBUG)