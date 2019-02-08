V1 = [2,2]
V2 = [4,4]
import math


def calculate_time(speed, distance, acceleration, accelerate=True):
    if accelerate == 0:
        return (distance/speed)
    else:
        timeToAccelerate = speed/acceleration
        print("Time To Accelerate to Max Speed:", timeToAccelerate)
        distanceToAccelerate = speed * timeToAccelerate
        print("Distance to Accelerate to Max Speed:", distanceToAccelerate)
        distanceAtFinalSpeed = distance - 2*(distanceToAccelerate)
        print("Distance at Max Speed:", distanceAtFinalSpeed)
        if distanceToAccelerate > distance/2:
            timeToAccelerate = math.sqrt((distance/2)/acceleration)
            print("Time to Accelerate to largest possible speed:", timeToAccelerate)
            maxSpeedReached = acceleration*(timeToAccelerate**2)
            print("Max Speed Reached at middle of journey:", maxSpeedReached)
            return 2*timeToAccelerate
        else:
            timeAtFinalSpeed = distanceAtFinalSpeed/speed
            print("Time at Final Speed:", timeAtFinalSpeed)
            return round((2*timeToAccelerate + timeAtFinalSpeed), 2)

speed = 30
distance = 70
acceleration = 20

print(calculate_time(speed, distance, acceleration))
