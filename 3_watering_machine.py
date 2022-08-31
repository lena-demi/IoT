# -*- coding: utf-8 -*-
import sys # system params and function
import paho.mqtt.client as mqtt # mqtt paho
import json # json converter
import time # for sleep
from datetime import datetime # for date
dt = 2 # check watering machine and update system every dt seconds

### machine and logic
class watering_machine():
    def __init__(self, mqtt_client, crit_moisture = 30, duration = 15, water_level = 100):  
        # Can be changed by user
        self.crit_moisture = crit_moisture        
        self.duration = duration
        self.water_level = water_level
        
        # Changed on working or via config (not by mqtt)
        self.status = "off"
        self.moisture = 40
        self.last_watering = None
        self.Q = 0.07 # water consumption on watering [l/sec]
        self.mode = 0 # 0 - emulator mode, 1 - manual water on/off
        
        self.mqtt_client = mqtt_client
        self.topic_state = "watering_machine/state"
        self.topic_errors = "watering_machine/errors"
        self.topic_water = "command/water"
        self.topic_add_water = "command/fulfill"
        self.topic_change_crit_moisture = "command/set/moisture"
        self.topic_change_duration = "command/set/duration"
        
        self.mqtt_client.subscribe(self.topic_water)
        self.mqtt_client.message_callback_add(self.topic_water, self.water_callback)
        self.mqtt_client.subscribe(self.topic_add_water)
        self.mqtt_client.message_callback_add(self.topic_add_water, self.add_water)
        self.mqtt_client.subscribe(self.topic_change_duration)
        self.mqtt_client.message_callback_add(self.topic_change_duration, self.set_duration)
        self.mqtt_client.subscribe(self.topic_change_crit_moisture)
        self.mqtt_client.message_callback_add(self.topic_change_crit_moisture, self.set_moisture)
        
    # Variation of moisture (assumed that it dries with rate 2% per dt and moisturizes with rate 3% per dt)
    def moisture_vary (self):
        if self.status == "off":
            self.moisture = self.moisture - dt*2
        else:
            self.moisture = self.moisture + dt*3
        return (self.moisture)

    # Water amount
    def consumption (self):
        if self.water_level<=1:
            print("run out of water, please fulfill the storage tank")
            print("To do so it is necessary to publish messsage with topic '%s', payload = water volume in liters \n" % self.topic_add_water)
            self.mqtt_client.publish(self.topic_errors, "run out of water, please fulfill the storage tank")
        else:
            self.water_level=round(self.water_level-dt*self.Q, 2)
        return (self.water_level)
        
    # Process of watering
    def watering(self):
        self.status = "on"
        self.last_watering = datetime.now()
        self.update_config()
        self.log()
        print("%s water on" % str(self.last_watering))
        for t in range(0, self.duration, dt):
            if self.status == "off":
                break
            self.moisture=self.moisture_vary()
            self.water_level=self.consumption()
            self.publish_data()
            self.update_config()
            time.sleep(dt)
        self.status="off"
        print(" %s water off" % str(datetime.now()))
        self.publish_data()
        self.update_config()
        self.log()
        
    # To write config (all actual parameters)   
    def update_config(self):
        try:
            f = open('./config.txt', 'r')
            file = f.read()
            config = json.loads(file)
            f.close()
        except:
            config = {}
        f = open('./config.txt', 'w')
        config["water_level"] = str(self.water_level)
        config["last_watering"] = str(self.last_watering)
        config["crit_moisture"] = str(self.crit_moisture)
        config["duration"] = str(self.duration)
        config["consumption"] = str(self.Q)
        config = json.dumps(config)
        f.write("%s" % config)
        f.close()
        
   # To write log (when machine starts and stops watering)
    def log(self):
        path_to_log = sys.argv[1] if len(sys.argv) > 1 else "./log.txt"
        f = open(path_to_log, 'a')
        f.write("%s machine %s, moisture = %s \n" % (str(datetime.now()), str(self.status), str(self.moisture)))
        f.close()
    
    # To publish data
    def publish_data(self):
        config = {}
        config["status"] = str(self.status)
        config["moisture"] = str(self.moisture)
        config["water_level"] = str(self.water_level)
        config["last_watering"] = str(self.last_watering)
        config["crit_moisture"] = str(self.crit_moisture)
        config["duration"] = str(self.duration)
        config = json.dumps(config)
        self.mqtt_client.publish(self.topic_state, config)
        
    # Callbacks
    def add_water(self, client, userdata, message):
        print("Command: add water, now water level = %s" % str(message.payload))
        try:
            water = float(message.payload)
            self.water_level = self.water_level + water
            if self.water_level > 100:
                self.water_level = 100
        except:
            self.water_level = 100
        self.publish_data()
        
    def set_duration(self, client, userdata, message):
        print("command: change watering duration, new duration: %s" % str(message.payload))
        try:
            self.duration = int(message.payload)
        except:
            print("can't change duration to %s" % str(message.payload))
        self.publish_data()
                
    def set_moisture(self, client, userdata, message):
        print("command: change critical moisture, new value: %s" % str(message.payload))
        try:
            moist = int(message.payload)
            if moist >= 0 and moist <= 100:
                self.crit_moisture = moist
            else:
                print("Invalid moisture value %s" % str(message.payload))
                print("Moisture can be between 0 and 100")
        except:
            print("can't change critical moisture to %s" % str(message.payload))
        self.publish_data()
    
    def water_callback(self, client, usserdata, message):
        print("manual switch" )
        if self.status == "on":
            self.status = "off"
        else:
            self.mode = 1
        self.publish_data()
    
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
def run(client, host="127.0.0.1", port=1883):
    client.connect(host, port, 60)
    client.loop_start()
    
# body of emulator
def main():
    # create mqtt connection
    mqtt_client = init("123_client_id")
    run(mqtt_client)
    
    # init machine and read config
    machine=watering_machine(mqtt_client)
    argv = sys.argv
    try:
        path_to_config = argv[1] if len(argv) > 1 else "./config.txt"
        f = open(path_to_config, 'r')
        file = f.read()
        config = json.loads(file)
        f.close()
        machine.crit_moisture = int(config["crit_moisture"])
        machine.duration = int(config["duration"])
        machine.water_level = float(config["water_level"])
        machine.Q = float(config["consumption"])
        machine.last_watering = str(config["last_watering"])
        print("read config %s" % config)
    except:
        pass
    
    # check moisture and start/stop watering
    while True:
        time.sleep(dt)
        machine.moisture = machine.moisture_vary()
        machine.update_config()
        machine.publish_data()
        if machine.mode == 1 and machine.status == "off":
            machine.watering()
            machine.mode = 0
        if machine.moisture < machine.crit_moisture:
            machine.watering()
        
if __name__ == '__main__':
    main()
        
        