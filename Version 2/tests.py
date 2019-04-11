import salabim as sim

sim.random_seed = None

for i in range(100):
    print(sim.Uniform(1,10).sample())