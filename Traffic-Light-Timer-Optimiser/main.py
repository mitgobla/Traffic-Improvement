import time
import sys

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

# FLASK INITIALISATION
DEBUG = True
APP = flask.Flask(__name__, root_path='Web-Interface')
APP.config.from_object(__name__)


@APP.route('/', methods=['GET', 'POST'])
def index():
    # Home Page
    return flask.render_template("index.html")


# x = []
# y = []
# z = []
# START = time.clock()
# for lightGreenTime in range(1, 90, 2):
#     for roadUsage in range(5, 35, 2):
#         print(roadUsage, lightGreenTime)
        
#         tenv = traffic_flow_sim.TrafficEnvironment()
#         tenv.timeGreen = lightGreenTime
#         tenv.chanceVehicleSpawnPerUnitTime = roadUsage * 0.01
#         tenv.start_simulation()
#         if tenv.averageTimeStopped <= 60:
#             z.append(tenv.averageTimeStopped)
#         else:
#             z.append(60)
#         x.append(roadUsage * 0.01)
#         y.append(lightGreenTime)

# minimasx = []
# minimasy = []
# minimasz = []
# for roadUsage in range(5, 35, 2):
#     indexesAtCurrentRoadUsage = []
#     for index1 in range(len(x)):
#         if x[index1] == roadUsage * 0.01:
#             indexesAtCurrentRoadUsage.append(index1)
#     tempZList = []
#     tempYList = []
#     for index2 in indexesAtCurrentRoadUsage:
#         tempZList.append(z[index2])
#         tempYList.append(y[index2])
#     minIndex = np.argmin(tempZList)
#     minimasx.append(roadUsage * 0.01)
#     minimasy.append(tempYList[minIndex])
#     minimasz.append(tempZList[minIndex])

# print(minimasx)
# print(minimasy)
# print(minimasz)

# plotx,ploty = np.meshgrid(np.linspace(np.min(x),np.max(x),50),\
#                            np.linspace(np.min(y),np.max(y),50))
# plotz = interp.griddata((x,y),z,(plotx,ploty), method='linear')

# # lobf = np.polyfit(plotx, ploty, 1, full=True)
# # lobf = interp.griddata()

# # linex = plotx.argsort()[:50]
# # liney = ploty.argsort()[:50]

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(minimasx, minimasy, minimasz, '--k', label="Most Efficient")
# ax.legend()
# surf = ax.plot_surface(plotx,ploty,plotz,cstride=1,rstride=1,cmap=cm.jet)


# cbar = fig.colorbar(surf, shrink=0.5, aspect=10)
# #ax.figure.legend((1), ("Line"), loc=0, fancybox=True)
# ax.set_title("lightGreenTime vs. roadUsage")
# ax.set_xlabel('roadUsage') 
# ax.set_ylabel('lightGreenTime')
# ax.set_zlabel('averageTimeStopped')
# END = time.clock()
# plt.show()
# print("Execution time:", (END - START))
# sys.exit(0)

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=80, debug=DEBUG)