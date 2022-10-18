import json
import math
import random
#import bus # ЛЕНА, попробуй убрать этот модуль и посмотреть, будет ли работать итоговый код?
import paho.mqtt.client as mqtt # mqtt paho

# Изменение температуры на улице
def T_vary():
    T = random.randint(0,30)
    return T

# Изменение освещенности
def light_vary(t):
    light = 55000*math.cos((2*math.pi/1440)*t-math.pi)+55000
    return light

# Изменение температуры под капотом автобуса
def temp_motor(dt, temp, motor):
    if motor == True:
        T = temp + dt/2
    else:
        T = temp - dt/2
    return (T)

# Изменение температуры в салоне автобуса
def temp_bus(temp, climat_control):
    if climat_control == 0:
        T = temp + random.randint(-0.5,0.5)
    elif climat_control == 1:
        T = temp + 1
    else:
        T = temp - 1
    return (T)

# Получить координаты маршрута на основе JSON выгруженного из Rightech:
# Маршрут пройден ботом со скоростью 60 км/ч
def track(path="./track.json"):
    f = open(path, 'r')
    file = f.read()
    track = json.loads(file)
    f.close()
    lat = []
    lon = []
    for i in range (len(track)):
        data = track[i]
        if data["topic"] =="lat":
            lat.append(data["lat"])
        elif data["topic"] =="lon":
            lon.append(data["lon"])
    lat.pop(834)
    return(lat, lon)

# Эмулятор движения автобуса
def motion(dt, bus, path_to_track_file = "./track.json"):
    track_lat, track_lon = track(path_to_track_file)
    bus.t_move = bus.t_move  + dt
    t = bus.t_move
    if bus.motor == True:
        bus.velocity =round((30*math.cos((2*math.pi/120)*t-math.pi)+30), 2)
    else:
        bus.velocity = 0
    if bus.velocity < 2:
        bus.people = random.randint(0, 100)
    else:
        dj = int((bus.velocity/60)*dt)
        i = bus.j+dj
        bus.j = i
        bus.GPS["lat"] = track_lat[i]
        bus.GPS["lon"] = track_lon[i]
    if bus.GPS["lat"] == 59.8461945595122 and bus.GPS["lon"] == 30.1764661073685:
        bus.t_move = 0
    #return (bus)
