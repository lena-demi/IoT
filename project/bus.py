import paho.mqtt.client as mqtt
import json
import emulators
import time

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
        self.GPS = {"lat": 59.8461945595122, "lon": 30.1764661073685} # ЛЕНА поставь сюда координаты автопарка :)
        self.velocity = 0
        self.light = 110000 # [light]=[лк] = люкс 110000 - ясный день
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
        data["lat"] = str(self.GPS["lat"])
        data["lon"] = str(self.GPS["lon"])
        data["velocity"] = str(self.velocity)
        data["light"] = str(self.light)
        data["light_status"] = str(self.light_status)
        data["motor"] = str(self.motor)
        data = json.dumps(data)
        self.mqtt_client.publish(self.topic_info, data, retain=True)
        
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
    
mqtt_client = init("mqtt-lenademi52732-l4qj1i", clientUsername='123', clientPassword='123')
run(mqtt_client)
bus = Bus(mqtt_client)
dt = 2
light_time = 480 # Время для определения освещенности: при 480 освещенность соответствует освещенности в 8 утра
while True:
    bus.light = emulators.light_vary(light_time)
    bus.T_bus = emulators.temp_bus(bus.T_bus, bus.climat_control)
    bus.T_motor = emulators.temp_motor(dt, bus.T_motor, bus.motor)
    emulators.motion(dt, bus)
    bus.publish_data()
    light_time = light_time + dt
    time.sleep(dt)