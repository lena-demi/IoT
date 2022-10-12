
from random import uniform
from threading import Timer
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("on_connect rc: [%d]" % (rc))


def on_disconnect(client, userdata, rc):
    print("disconnected with rtn code [%d]" % (rc))

def publish():
    temp = round(uniform(15, 35), 2)
    client.publish("base/state/temperature", temp, qos=0)
    Timer(10, publish).start()


client = mqtt.Client("mqtt-lenademi52732-bi5gvw")
client.username_pw_set(username = "bi5gvw", password = "password")

client.tls_set("isrgrootx1.pem",
                certfile="cert.pem",
                keyfile="key.pem"
              )

client.on_connect = on_connect
client.on_disconnect = on_disconnect


client.connect("dev.rightech.io", 8883, 60)


Timer(1, publish).start()

client.loop_forever()