import math
import random

v1 = [2,2]
v2 = [1,3]
distance = 5
angle = 135

def calculate_vector(v2, distance, angle):
    v2 = [(v1[0] + distance*math.sin(math.radians(angle))), (v1[1] + distance*math.cos(math.radians(angle)))]
    return v2

# print(calculate_vector(v1, distance, angle))

def calculate_angle_trig(v1, v2):
    angle = math.atan2(v2[0]-v1[0], v2[1]-v1[1])
    angle = math.degrees(angle)
    return angle