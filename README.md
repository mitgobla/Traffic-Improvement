# Traffic-Improvement

Sixth Form Raspberry Pi Project for PAConsulting.com

## Summary

Traffic-Improvement is software used to reduce waiting times at a traffic light system by comparing many factors that affect traffic flow, and then calculating the most efficient traffic light cycle timings to use. The Raspberry Pi is used to control the traffic lights, and runs a web interface that allows an engineer to change variables for that traffic system. 

The inspiration for the project originated from the number of traffic lights at roadworks in our area. We noticed that drivers would be waiting for extended periods of time at lights, and in some cases just to have no cars going past before the lights would change. 

This project aims to reduce the waiting time for drivers at traffic lights by using the optimum timings on the traffic light depending on the conditions. As a result, drivers will feel more positive when travelling and it will reduce traffic build-up at roadworks. 

Firstly, we gathered information on current traffic statistics in the UK, from government sources. Furthermore, we researched into other factors that affect traffic flow, such as:

- human reaction time
- distraction chance
- weather effects
- probability of traffic

By combining these factors, we could determine the average waiting time of vehicles in the system for different road usages and traffic light timings. The first part of the software simulates the traffic system with these variables to return an average waiting for all the vehicles. We then plot these on a 3D graph which would then reveal the most efficient timings for different traffic levels for the fastest experience.

_Write about flask app here_

_Write about improvements here_

## Software & Hardware

**Software Used:** All software listed is free.
- Visual Studio Code.
    - Python 3.6
        - Flask module for Web Interface.
        - Simpy and other modules for simulation.
        - MatPlotLib module for graphs.
    - HTML + CSS for Web Interface.
- PuTTY (for SSH connection to Raspberry Pi).

**Hardware Used:**
- Raspberry Pi Model 3 B

## Instructions

1. Setup the Raspberry Pi in headless mode. _Follow this guide [here](https://caffinc.github.io/2016/12/raspberry-pi-3-headless/)._
2. Connect to the Raspberry Pi using PuTTY or any other SSH software.
3. Install `git`,`python3`,`python3-pip`:
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git python3 python3-pip
```
4. Clone this repository:
```bash
git clone https://github.com/mitgobla/Traffic-Improvement TrafficImprovement
cd TrafficImprovement
```
5. Install the required Python modules in `requirements.txt`:
```bash
cd Traffic-Light-Timer-Optimiser
sudo python3 -m pip install -r requirements.txt
```

