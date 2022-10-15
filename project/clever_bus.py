import sys # system params and function
import paho.mqtt.client as mqtt # mqtt paho
import json # json converter
import time # for sleep
from datetime import datetime, timedelta # for date

# Модель автобусной остановки
class Stop(ID=123, alarm=15, name="Тестовая остановка", bus = []):
    # Инициализация объекта
    def __init__(self, ID, mqtt_client, alarm, name, bus):
        
        # Конфигурационные параметры (не отправляются по mqtt)
        self.ID = ID # ID совпадает с ID в Rightech IoT Cloud
        self.name = name
        self.bus = bus
        self.deadline = None # Для блокировки кнопки тревоги на время реагирования
        
        # Параметры, отправляемые по mqtt
        self.T = 20 # [T]=[С]
        self.light = None # ЛЕНА ПОСМОТРИ ПАРАМЕТРЫ ОСВЕЩЕННОСТИ И ЕЕ НОРМЫ
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
        
    # Callbacks  ЛЕНА проверь, что  будет, если опустить часть аргументов? Я же их не использую
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
            self.deadline = datetime.now() + timedelta(minutes = self.alarm_duration)
            self.publish_data()
            
    
    def set_alarm_callback(self, client, userdata, message):
        print("Новое время реагирования на кнопку тревоги = %s минут" % str(message.payload))
        try:
            self.alarm_duration = int(message.payload)
        except:
            print("can't change duration to %s" % str(message.payload))
        self.publish_data()
        
    def bus_callback(self, client, userdata, message):
        msg = json.loads(message.payload)
        N = str(msg["N"])
        people = str(msg["people"])
        time = str(msg["time"])
        self.display = format("Автобус № %s будет %s, заполнен на %s %" % (N, time, people))
        self.publish_data()
        print(self.display)
    
    # Publish info via mqtt
    def publish_data(self):
        data = {}
        data["temperature"] = str(self.T)
        data["light"] = str(self.light)
        data["light_status"] = str(self.light_status)
        data["alarm"] = str(self.alarm)
        data["alarm_duration"] = str(self.alarm_duration)
        data["display"] = str(self.display)
        data = json.dumps(data)
        self.mqtt_client.publish(self.topic_info, data, retain=True)
    
    # Эмуляция данных для автобусной остановки (+ автоматическое включение ламп в темноте)
    # def temp_vary (self):
    #     self.T = 25
        
    def light_vary (self):
        self.light = 10

        
# Модель умного автобуса
class Bus(ID=456, N=1):
    def __init__(self, ID, mqtt_client, N):
        # Конфигурационные параметры (не отправляются по mqtt)
        self.ID = ID # ID совпадает с ID в Rightech IoT Cloud
        self.N  = N
        
        # Параметры, отправляемые по mqtt
        self.T_bus = 20
        self.T_motor = 20
        self.climat_control = 0 # 0 - выключено, 1 - обогрев, -1 - охлаждение
        self.people = 0 # ЕИ = [%]
        self.GPS = {"lon": 0, "lat": 0} # ЛЕНА поставь сюда координаты автопарка :)
        self.velocity = 0
        self.light = 0
        self.light_status = False
        self.motor = True
        
        # Топики и callbacks для MQTT
        self.mqtt_client = mqtt_client
        self.topic_info = "bus/info"
        self.topic_light = "stop/light"
        self.topic_motor = "bus/block"
        self.topic_heat = "bus/climat-control/heat"
        self.topic_cool = "bus/climat-control/cool"
        self.topic_climat = "bus/climat-control/off"
        self.topic_people = "bus/people"
        
        self.mqtt_client.subscribe(self.topic_light)
        self.mqtt_client.message_callback_add(self.topic_light, self.light_callback)
        self.mqtt_client.subscribe(self.topic_motor)
        self.mqtt_client.message_callback_add(self.topic_motor, self.motor_callback)
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
        print("Ручное включение/выключение освещения")
        if self.light_status == True:
            self.light_status = False
        else:
            self.light_status = True
        self.publish_data()
        
    def motor_callback(self, client, userdata, message):
        print("Выключение мотора")
        self.motor = False
        self.publish_data()
        
    def heat_callback(self, client, userdata, message):
        print("Ручное включение обогрева")
        self.climat_control = 1
        self.publish_data()
        
    def cool_callback(self, client, userdata, message):
        print("Ручное включение охлаждения")
        self.climat_control = -1
        self.publish_data()
        
    def climat_callback(self, client, userdata, message):
         print("Ручное выключение нагрева и охлаждения")
         self.climat_control = 0
         self.publish_data()
         
    def people_callback(self, client, userdata, message):
        try:
            people = int(message.payload)
            if people >= 0 and people <= 100:
                self.people = people
                print("Ручное изменение заполненности автобуса. Автобус заполнен на %s %" % str(message.payload))
        except:
            print("Невозможно изменитть заполненность автобуса на %s %" % str(message.payload))
        self.publish_data()
        
    # Publish info via mqtt
    def publish_data(self):     
        data = {}
        data["T_bus"] = str(self.T_bus)
        data["T_motor"] = str(self.T_motor)
        data["climat_control"] = str(self.climat_control)
        data["people"] = str(self.people)
        data["lon"] = str(self.GPS["lon"])
        data["lat"] = str(self.GPS["lat"])
        data["velocity"] = str(self.velocity)
        data["light"] = str(self.light)
        data["light_status"] = str(self.light_status)
        data["motor"] = str(self.motor)
        data = json.dumps(data)
        self.mqtt_client.publish(self.topic_info, data, retain=True)
        
    # Эмуляторы
    def temp_bus(self):
        self.T_bus = 20
        
    def temp_motor(self):
        self.T_motor = 20
        
    def light_vary(self):
        self.light = 0
        
    def motion(self):
        print("This is the most difficult part of the whole emulator :( ")