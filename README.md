# IOT25 – Wireless telemetry with ESP32, MQTT and Azure IoT Hub

ESP32 sensor nodes publish telemetry over MQTT to Mosquitto on a Raspberry Pi. A gateway on the Pi forwards it to Azure IoT Hub, and a consumer reads it back from Azure.

```
ESP32 + DHT11 (x2) -> Mosquitto (Raspberry Pi) -> gateway -> Azure IoT Hub -> Azure consumer
```

## Parts
| Folder | What |
|---|---|
| `esp32/sensor_node` | ESP32 sketch: DHT11 temperature + humidity -> MQTT (`iot25/<deviceId>/telemetry`) |
| `gateway` | Python gateway on the Pi: MQTT in, Azure IoT Hub out. Also prints every MQTT message (local consumer) |
| `consumer` | Azure consumer: reads the IoT Hub's Event Hub-compatible endpoint and shows each device's values live |

Message format (MQTT and Azure): `{"deviceId": "mhmood-esp32-01", "value": 24.6, "unit": "°C"}`. Humidity is sent as its own device, `<deviceId>-humidity`.

## Setup
**ESP32**
1. Copy `esp32/sensor_node/secrets.example.h` to `secrets.h` and fill in Wi-Fi, the Pi's IP and a unique `DEVICE_ID`.
2. Libraries: PubSubClient, DHT sensor library (Adafruit). Upload to each board.

**Raspberry Pi**
1. `sudo apt install mosquitto mosquitto-clients`, with `listener 1883` and `allow_anonymous true` in `/etc/mosquitto/conf.d/`.
2. `python3 -m venv .venv && .venv/bin/pip install -r gateway/requirements.txt`
3. Register a device for the gateway in IoT Hub and put its connection string in an env file (`IOTHUB_DEVICE_CONNECTION_STRING=...`, not committed).
4. Run `.venv/bin/python gateway/gateway.py` (or as a systemd service).

**Local consumer:** the gateway's output, or `mosquitto_sub -h <pi-ip> -t "iot25/#" -v`.

**Azure consumer**
```
pip install -r consumer/requirements.txt
set EVENTHUB_CONNECTION_STRING=<IoT Hub > Built-in endpoints > Event Hub-compatible endpoint>
python consumer/azure_consumer.py
```

## Status
- [x] ESP32 publishes temperature and humidity to MQTT
- [x] Separate topic per device
- [x] Gateway forwards to Azure IoT Hub (own device identity, every 45 s to stay within the free tier)
- [x] Local consumer + Azure consumer
- [x] Tested end to end with a real DHT11 sensor
- [ ] Second ESP32
- [ ] Bluetooth LE configuration (VG)

## Notes
- The free IoT Hub tier allows 8,000 messages a day, so the gateway sends only the latest value per device every 45 seconds.
- `azure-iot-device` requires `paho-mqtt` 1.x, so the gateway uses that API.
