import paho.mqtt.client as mqtt # mqtt paho
import json # json converter
from datetime import datetime, timedelta # for date

# Модель автобусной остановки
class Stop():
    # Инициализация объекта
    def __init__(self, mqtt_client, ID = 123, alarm = 15, name = "Тестовая остановка", bus = [1]):
        
        # Конфигурационные параметры (не отправляются по mqtt)
        self.ID = ID # ID совпадает с ID в Rightech IoT Cloud
        self.name = name
        self.bus = bus
        self.deadline = None # Для блокировки кнопки тревоги на время реагирования
        
        # Параметры, отправляемые по mqtt
        self.T = 20 # [T]=[С]
        self.light = 110000 # [light]=[лк] = люкс 110000 - ясный день
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
            self.deadline = datetime.now() + timedelta(seconds = self.alarm_duration)
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