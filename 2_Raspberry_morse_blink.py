import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global isConnected
    print("Connected with result code " + str(rc))
    if rc == 0:
        isConnected = 1
        client.publish("connect", "true", 1)

# When the client has sent the disconnect message it generates an on_disconnect() callback.
def on_disconnect(client, userdata, rc):
    global isConnected
    print("Unexpected disconnection")
    isConnected = 0

isConnected = 0
client = mqtt.Client(client_id="mqtt-lenademi52732-0ydm4w")
client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.username_pw_set("Raspberry_Lena", password='527')
client.loop_start()
client.connect(' dev.rightech.io', 1883, 60)
client.subscribe("base/state/+")
#client.loop_stop()
