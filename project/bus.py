import paho.mqtt.client as mqtt # mqtt paho
import json # json converter

class Bus():
    def __init__(self, mqtt_client, ID = 456, N = 1):
        # Конфигурационные параметры (не отправляются по mqtt)
        self.ID = ID # ID совпадает с ID в Rightech IoT Cloud
        self.N  = N
        self.motor_time = 0 # время работы/простоя мотора, [мин]
        
        # Параметры, отправляемые по mqtt
        self.T_bus = 20
        self.T_motor = 20
        self.climat_control = 0 # 0 - выключено, 1 - обогрев, -1 - охлаждение
        self.people = 0 # ЕИ = [%]
        self.GPS = {"lon": 0, "lat": 0} # ЛЕНА поставь сюда координаты автопарка :)
        self.velocity = 0
        self.light = 55000
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