# IOT25 – Wireless telemetry with ESP32, MQTT and Azure IoT Hub

Two ESP32 sensor nodes publish telemetry over MQTT to Mosquitto on a Raspberry Pi. A gateway on the Pi forwards it to Azure IoT Hub.

```
ESP32 (x2) -> Mosquitto (Raspberry Pi) -> gateway -> Azure IoT Hub -> consumer
```

## Parts
| Folder | What |
|---|---|
| `esp32/sensor_node` | ESP32 sketch (DHT sensor -> MQTT) |
| `gateway` | Python gateway on the Pi |

## Setup
1. Copy `esp32/sensor_node/secrets.example.h` to `secrets.h` and fill in Wi-Fi/MQTT settings.
2. Upload the sketch to each ESP32 (different `DEVICE_ID`).
3. On the Pi: `pip install paho-mqtt`, then `python3 gateway/gateway.py`.

## Status
- [x] ESP32 publishes JSON to MQTT
- [x] Gateway receives messages
- [ ] Separate topic per device
- [ ] Forward to Azure IoT Hub
- [ ] Local consumer + Azure consumer
- [ ] Bluetooth LE configuration (VG)
