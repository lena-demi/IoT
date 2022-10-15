import math
import random

# Изменение температуры на улице
def T_vary():
    T = random.random(0,30)
    return T

# Изменение освещенности
def light_vary(t):
    light = 55000*math.cos((2*math.pi/1440)*t-math.pi)+55000
    return light