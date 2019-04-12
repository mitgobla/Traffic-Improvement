import time

with open('Simulations//output.log') as simulation_file:
    simulation_data = simulation_file.read()

simulation_data = simulation_data.split('\n')
simulation_data.pop(-1)

simulation_time = []
simulation_events = []
for event in simulation_data:
    event_data = event.split(' ')
    if not event_data[0] in simulation_time:
        simulation_time.append(event_data[0])
        simulation_events.append([])
    event_data.pop(0)
    simulation_events[-1].append(event_data)

print(simulation_events)
