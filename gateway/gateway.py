"""Gateway on the Raspberry Pi: listens to the local Mosquitto broker.

Next step: forward each message to Azure IoT Hub.
"""
import json
import os

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(msg.topic, data)
    # TODO: send to Azure IoT Hub


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(MQTT_HOST, 1883)
client.subscribe("telemetry")
client.loop_forever()
