# Для масштабируемости: реальная 1 секунда = 1 минуте эмулятора

from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import time # for sleep

import bus_stop
import bus
import emulators

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
    
# body of emulator
def main():
    # create mqtt connection
    mqtt_client1 = init("mqtt-lenademi52732-l4qj1i", clientUsername="123", clientPassword="123")
    run(mqtt_client1)
    
    mqtt_client2 = init("mqtt-lenademi52732-w9110v", clientUsername="456", clientPassword="456")
    run(mqtt_client2)
    
    bus_obj = bus.Bus(mqtt_client1)
    stop = bus_stop.Stop(mqtt_client2)
    
    print("Тут будет основная логика программы")
    i=0
    while True:
       i = i  + 1
    
        
if __name__ == '__main__':
    main()