import math
import random

VIntersection = [random.randint(-10,10), random.randint(-10,10)]
VLight = [random.randint(-10,10), random.randint(-10,10)]

def calculate_angle_to_verticle(VIntersection, VLight):
    if VLight[0] > VIntersection[0] and VLight[1] > VIntersection[1]:   # Traffic Light NorthEast to Intersection Point
        return math.degrees(math.atan((VLight[0]-VIntersection[0])/(VLight[1]-VIntersection[1])))
    elif VLight[0] > VIntersection[0] and VLight[1] == VIntersection[1]:   # Traffic Light East to Intersection Point
        return 90.0
    elif VLight[0] > VIntersection[0] and VIntersection[1] > VLight[1]:   # Traffic Light SouthEast to Intersetcion Point
        return 180.0 + math.degrees(math.atan((VLight[0]-VIntersection[0])/(VLight[1]-VIntersection[1])))
    elif VLight[0] == VIntersection[0] and VIntersection[1] > VLight[1]:   # Traffic Light South to Intersection Point
        return 180.0
    elif VIntersection[0] > VLight[0] and VIntersection[1] > VLight[1]:   # Traffic Light SouthWest to Intersection Point
        return math.degrees(math.atan((VLight[0]-VIntersection[0])/(VLight[1]-VIntersection[1]))) - 180.0
    elif VIntersection[0] > VLight[0] and VLight[1] == VIntersection[1]:  # Traffic Light West to Intersection Point
        return 270.0
    elif VIntersection[0] > VLight[0] and VLight[1] > VIntersection[1]:   # Traffic Light NorthWest to Intersection Point
        return math.degrees(math.atan((VLight[0]-VIntersection[0])/(VLight[1]-VIntersection[1])))
    elif VLight[0] == VIntersection[0] and VLight[1] > VIntersection[1]:    # Traffic Light North to Intersection Point
        return 0.0

print(VIntersection, VLight, calculate_angle_to_verticle(VIntersection, VLight)) 