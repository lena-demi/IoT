import paho.mqtt.client as mqtt
import json
import time
import math
import random

class Bus():
    def __init__(self, mqtt_client, N = 1):
        # Конфигурационные параметры (не отправляются по mqtt)
        self.N  = N
        self.t_move = 0 # время на маршруте [мин]
        self.j = 0 # индекс актуальной координаты из массива координат
        
        # Параметры, отправляемые по mqtt
        self.T_bus = 20
        self.T_motor = 20
        self.climat_control = 0 # 0 - выключено, 1 - обогрев, -1 - охлаждение
        self.people = 0 # ЕИ = [%]
        self.GPS = {"lat": 59.8461945595122, "lon": 30.1764661073685}
        self.velocity = 0
        self.light = 5000 # [light]=[лк] = люкс 5000 лк - дневной свет
        self.light_status = False
        self.motor = True
        
        # Топики и callbacks для MQTT
        self.mqtt_client = mqtt_client
        self.topic_info = "bus/info"
        self.topic_light = "bus/light"
        self.topic_motor_off = "bus/block"
        self.topic_motor_on = "bus/run"
        self.topic_heat = "bus/climat-control/heat"
        self.topic_cool = "bus/climat-control/cool"
        self.topic_climat = "bus/climat-control/off"
        self.topic_people = "bus/people"
        
        self.mqtt_client.subscribe(self.topic_light)
        self.mqtt_client.message_callback_add(self.topic_light, self.light_callback)
        self.mqtt_client.subscribe(self.topic_motor_off)
        self.mqtt_client.message_callback_add(self.topic_motor_off, self.motor_off_callback)
        self.mqtt_client.subscribe(self.topic_motor_on)
        self.mqtt_client.message_callback_add(self.topic_motor_on, self.motor_on_callback)
        self.mqtt_client.subscribe(self.topic_heat)
        self.mqtt_client.message_callback_add(self.topic_heat, self.heat_callback)
        self.mqtt_client.subscribe(self.topic_cool)
        self.mqtt_client.message_callback_add(self.topic_cool, self.cool_callback)
        self.mqtt_client.subscribe(self.topic_climat)
        self.mqtt_client.message_callback_add(self.topic_climat, self.climat_callback)
        self.mqtt_client.subscribe(self.topic_people)
        self.mqtt_client.message_callback_add(self.topic_people, self.people_callback)
        
    # Callbacks
    def light_callback(self, client, userdata, message):
        print("Включение/выключение освещения")
        if self.light_status == True:
            self.light_status = False
        else:
            self.light_status = True
        self.publish_data()
        
    def motor_off_callback(self, client, userdata, message):
        print("Блокировка мотора")
        self.motor = False
        self.publish_data()
        
    def motor_on_callback(self, client, userdata, message):
        print("Разблокировка мотора")
        self.motor = True
        self.publish_data()
    
    def heat_callback(self, client, userdata, message):
        print("Включение обогрева")
        self.climat_control = 1
        self.publish_data()
        
    def cool_callback(self, client, userdata, message):
        print("Включение охлаждения")
        self.climat_control = -1
        self.publish_data()
        
    def climat_callback(self, client, userdata, message):
         print("Выключение нагрева и охлаждения")
         self.climat_control = 0
         self.publish_data()
         
    def people_callback(self, client, userdata, message):
        try:
            people = int(message.payload)
            if people >= 0 and people <= 100:
                self.people = people
                print("Ручное изменение заполненности автобуса. Автобус заполнен на %s" % str(message.payload))
        except:
            print("Невозможно изменитть заполненность автобуса на %s" % str(message.payload))
        self.publish_data()
    
    # Publish info via mqtt
    def publish_data(self):     
        data = {}
        data["T_bus"] = str(self.T_bus)
        data["T_motor"] = str(self.T_motor)
        data["climat_control"] = str(self.climat_control)
        data["people"] = str(self.people)
        data["lat"] = str(self.GPS["lat"])
        data["lon"] = str(self.GPS["lon"])
        data["velocity"] = str(self.velocity)
        data["light"] = str(self.light)
        data["light_status"] = str(self.light_status)
        data["motor"] = str(self.motor)
        data["N"] = str(self.N)
        data = json.dumps(data)
        self.mqtt_client.publish(self.topic_info, data, retain=True)
        
# Изменение освещенности
def light_vary(t):
    light = round(2500*math.cos((2*math.pi/1440)*t-math.pi)+2500)
    return light

# Изменение температуры под капотом автобуса
def temp_motor(dt, temp, motor):
    if motor == True:
        T = temp + dt/4
    else:
        if temp > 20:
            T = temp - dt*2
        else:
            T = temp
    return (T)

# Изменение температуры в салоне автобуса
def temp_bus(temp, climat_control):
    if climat_control == 0:
        T = round(temp + random.uniform(-0.5,0.5), 2)
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
    if bus.motor == True:
        bus.t_move = bus.t_move  + dt
        t = bus.t_move
        bus.velocity =round((30*math.cos((2*math.pi/240)*t-math.pi)+30), 2)
        if bus.velocity < 0.5:
            bus.people = random.randint(0, 100)
        else:
            
            dj = int((bus.velocity/60)*dt)
            i = bus.j+dj
            bus.j = i
            bus.GPS["lat"] = track_lat[i]
            bus.GPS["lon"] = track_lon[i]
            if bus.GPS["lat"] == 59.8461945595122 and bus.GPS["lon"] == 30.1764661073685 and bus.t_move > 60:
                bus.t_move = 0
                bus.j = 0
    else:
        bus.velocity = 0
    return (bus)

# init mqtt
def init(clientid, clientUsername="", clientPassword=""):
    client = mqtt.Client(client_id=clientid)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username = clientUsername, password = clientPassword)
    return client

# connect reaction
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        isConnect = 1
        client.publish("connect", "true", 1)
    if rc == 5:
        print("Authorization error")

# default message reaction
def on_message(client, userdata, message):
     print("Some message received topic: %s, payload: %s" % (str(message.topic), str(message.payload)))

# mqtt connection
def run(client, host="dev.rightech.io", port=1883):
    client.connect(host, port, 60)
    client.loop_start()
    
mqtt_client = init("mqtt-lenademi52732-fecf7e", clientUsername='', clientPassword='')
run(mqtt_client)
bus = Bus(mqtt_client)
dt = 2
light_time = 480 # Время для определения освещенности: при 480 освещенность соответствует освещенности в 8 утра
while True:
    bus.light =light_vary(light_time)
    bus.T_bus = temp_bus(bus.T_bus, bus.climat_control)
    bus.T_motor = temp_motor(dt, bus.T_motor, bus.motor)
    bus = motion(dt, bus)
    bus.publish_data()
    light_time = light_time + dt
    time.sleep(dt)