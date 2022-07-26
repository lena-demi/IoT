
#include "Arduino.h"
#include "EspMQTTClient.h" /* https://github.com/plapointe6/EspMQTTClient */
                           /* https://github.com/knolleary/pubsubclient */
#define PUB_DELAY (15 * 1000) /* 15 seconds */
// Create wifi connection  and initialize mqtt client
EspMQTTClient client(
  "<wifi>",
  "<wifi-password>",

  "dev.rightech.io",
  "Node_MCU_Lena",
  "527",
  "mqtt-lenademi52732-0265of"
);

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0)); // For more random randomizer :)
  client.enableLastWillMessage("connect/arduino", "Arduino is lost :(", true);  
}

// On connection: to publish, that arduino online and learn who else is online
void onConnectionEstablished() {
  client.publish("connect/arduino", "Arduino is here!", true);
  client.subscribe("connect/+", [] (const String &payload)  {
    Serial.println(payload);
  });
}

// Create random message
String createMessage(){
  int msg_length = random(1,10);
  String message;
  String alphabet="abcdefghijklmnopqrstuvwxyz0123456789 ";
  for (int i=0; i<=msg_length; i++){
    int j = random(36);
    message+=alphabet[j];
   }
   return message;
}

//Every 15 seconds publish message
long last = 0;
void publish_message(String msg) {
  long now = millis();
  if (client.isConnected() && (now - last > PUB_DELAY)) {
    client.publish("led/morze", msg);
    Serial.println(msg);
    last = now;
  }
}

void loop() {
  client.loop();
  String msg=createMessage();
  publish_message(msg);
}
