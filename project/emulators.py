import math
import random
import bus # ЛЕНА, попробуй убрать этот модуль и посмотреть, будет ли работать итоговый код?
import paho.mqtt.client as mqtt # mqtt paho

# Изменение температуры на улице
def T_vary():
    T = random.random(0,30)
    return T

# Изменение освещенности
def light_vary(t):
    light = 55000*math.cos((2*math.pi/1440)*t-math.pi)+55000
    return light

# Изменение температуры под капотом автобуса
def temp_motor(dt, motor, temp):
    if motor == True:
        T = temp + dt
    else:
        T = temp - dt
    return (T)

# Изменение температуры в салоне автобуса
def temp_bus(temp, climat_control):
    if climat_control == 0:
        T = temp + random.random(-0.5,0.5)
    elif climat_control == 1:
        T = temp + 1
    else:
        T = temp - 1
    return (T)

# Эмулятор движения автобуса
def motion(t, bus):
    return (bus.N)

# Отладка    
mqtt_client = mqtt.Client("123_client_id")
t = 15
b = bus.Bus(mqtt_client)
print(t, motion(b))
    