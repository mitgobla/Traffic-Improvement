import pylab
#from scipy.interpolate import interp1d

with open('Simulations//output.log') as simulation_file:
    simulation_data = simulation_file.read()

simulation_data = simulation_data.split('\n')
simulation_data.pop(-1)

carsleft = simulation_data[::2]
carsright = simulation_data[::-2]
carsright.reverse()

t = pylab.arange(0, len(carsleft), 1)

for index, item in enumerate(carsleft):
    carsleft[index] = int(item)

for index, item in enumerate(carsright):
    carsright[index] = int(item)

pylab.plot(t, carsleft)
pylab.plot(t, carsright)
pylab.legend(['Left', 'Right'])
pylab.xlabel('Time')
pylab.ylabel('Cars')
pylab.title('Cars waiting at traffic light')
pylab.show()
