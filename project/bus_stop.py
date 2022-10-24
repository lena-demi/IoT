# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
from datetime import datetime, timedelta
import time
import random
import math

# Модель автобусной остановки
class Stop():
    # Инициализация объекта
    def __init__(self, mqtt_client, alarm = 15, name = "Тестовая остановка", bus = [1]):
        
        # Конфигурационные параметры (не отправляются по mqtt)
        self.name = name
        self.bus = bus
        self.deadline = None # Для блокировки кнопки тревоги на время реагирования
        
        # Параметры, отправляемые по mqtt
        self.T = 20 # [T]=[С]
        self.light = 5000 # [light]=[лк] = люкс 5000 - дневной свет
        self.light_status = False
        self.alarm = False
        self.alarm_duration = alarm # [t]=[мин]
        
        # Параметры, получаемые по mqtt
        self.display = "Информация о прибывающих автобусах пока неизвестна"
        
        # Топики и callbacks для MQTT
        self.mqtt_client = mqtt_client
        self.topic_info = "stop/info"
        self.topic_light = "stop/light"
        self.topic_send_alarm = "stop/alarm"
        self.topic_set_alarm = "stop/alarm/time"
        self.topic_bus = "stop/bus"
        
        self.mqtt_client.subscribe(self.topic_light)
        self.mqtt_client.message_callback_add(self.topic_light, self.light_callback)
        self.mqtt_client.subscribe(self.topic_send_alarm)
        self.mqtt_client.message_callback_add(self.topic_send_alarm, self.send_alarm_callback)       
        self.mqtt_client.subscribe(self.topic_set_alarm)
        self.mqtt_client.message_callback_add(self.topic_set_alarm, self.set_alarm_callback)
        self.mqtt_client.subscribe(self.topic_bus)
        self.mqtt_client.message_callback_add(self.topic_bus, self.bus_callback)
        
    # Callbacks
    def light_callback(self, client, userdata, message):
        print("Ручное включение/выключение освещения" )
        if self.light_status == True:
            self.light_status = False
        else:
            self.light_status = True
        self.publish_data()
        
    def send_alarm_callback(self, client, userdaata, message):
        if self.alarm == False:
            print("Тревога! Послан сигнал вызова полиции.")
            self.alarm = True
            self.deadline = datetime.now() + timedelta(seconds = self.alarm_duration)
            self.publish_data()
            
    
    def set_alarm_callback(self, client, userdata, message):
        print("Новое время реагирования на кнопку тревоги = %s минут" % str(message.payload))
        try:
            if int(message.payload) >= 0:
                self.alarm_duration = int(message.payload)
            else: print("Невозможно установить время реагирования: %s" % str(message.payload))
        except:
            print("Невозможно установить время реагирования: %s" % str(message.payload))
        self.publish_data()
        
    def bus_callback(self, client, userdata, message):
        msg = message.payload
        self.display = msg.decode("utf-8", errors="replace")
        print(self.display)
    
    # Publish info via mqtt
    def publish_data(self):
        data = {}
        data["name"] = str(self.name)
        data["temperature"] = str(self.T)
        data["light"] = str(self.light)
        data["light_status"] = str(self.light_status)
        data["alarm"] = str(self.alarm)
        data["alarm_duration"] = str(self.alarm_duration)
        data = json.dumps(data)
        self.mqtt_client.publish(self.topic_info, data, retain=True)
        
# Изменение температуры на улице
def T_vary():
    T = random.randint(0,30)
    return T

# Изменение освещенности
def light_vary(t):
    light = round(2500*math.cos((2*math.pi/1440)*t-math.pi)+2500)
    return light

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
    
mqtt_client = init("mqtt-lenademi52732-w9110v", clientUsername='', clientPassword='')
run(mqtt_client)
stop = Stop(mqtt_client, name="Улица Лёни Голикова")
dt = 2
light_time = 480
while True:
    if stop.alarm == True and datetime.now() >= stop.deadline:
        stop.alarm = False
    stop.light = light_vary(light_time)
    stop.T = T_vary()
    stop.publish_data()
    light_time = light_time + dt
    time.sleep(dt)