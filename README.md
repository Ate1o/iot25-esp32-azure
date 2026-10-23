# IOT25 – Wireless telemetry with ESP32, MQTT and Azure IoT Hub

Two ESP32 sensor nodes publish telemetry over MQTT to Mosquitto on a Raspberry Pi. A gateway on the Pi forwards it to Azure IoT Hub, and consumers show it locally and from Azure.

```
ESP32 + DHT11 (x2) > Mosquitto (Raspberry Pi) > gateway > Azure IoT Hub > Azure consumer
                                       \> local consumer (gateway output / mosquitto_sub)
```

## Parts
| Folder | What |
|---|---|
| `esp32/sensor_node` | ESP32 sketch (both boards): DHT11 temperature + humidity > MQTT |
| `gateway` | Python gateway on the Pi: MQTT in, Azure IoT Hub out. Prints every MQTT message (local consumer). Includes a systemd unit |
| `consumer` | Azure consumer: reads the IoT Hub's Event Hub-compatible endpoint and shows each device's values live |

## Message format
- MQTT topic per device: `iot25/<deviceId>/telemetry`
- JSON (MQTT and Azure): `{"deviceId": "mhmood-esp32-01", "value": 24.6, "unit": "°C"}`
- Humidity is published as its own device, `<deviceId>-humidity`, so every deviceId has one value.

## Setup

### ESP32 (both boards)
1. Copy `esp32/sensor_node/secrets.example.h` to `secrets.h` and fill in Wi-Fi, the Pi's IP and the device id.
2. Board 1: `DEVICE_ID "mhmood-esp32-01"`. Board 2: `DEVICE_ID "mhmood-esp32-02"`. Everything else is the same.
3. Libraries: PubSubClient, DHT sensor library (Adafruit). Board: Arduino Nano ESP32, DHT11 data on D4.

### Raspberry Pi
```bash
sudo apt install mosquitto mosquitto-clients
printf "listener 1883\nallow_anonymous true\n" | sudo tee /etc/mosquitto/conf.d/iot25.conf
sudo systemctl restart mosquitto

mkdir -p ~/iot25 && cp gateway/gateway.py ~/iot25/ && cd ~/iot25
python3 -m venv .venv && .venv/bin/pip install -r <repo>/gateway/requirements.txt
cp <repo>/gateway/gateway.env.example gateway.env   # fill in the IoT Hub connection string
chmod 600 gateway.env

sudo cp <repo>/gateway/iot25-gateway.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now iot25-gateway
journalctl -u iot25-gateway -f                      # local consumer: shows every MQTT message
```
The gateway has its own device identity in IoT Hub. Its connection string lives only in `gateway.env` on the Pi.

### Local consumer
Either the gateway's log above, or:
```bash
mosquitto_sub -h <pi-ip> -t "iot25/#" -v
```

### Azure consumer
```bash
pip install -r consumer/requirements.txt
set EVENTHUB_CONNECTION_STRING=<IoT Hub > Built-in endpoints > Event Hub-compatible endpoint>
python consumer/azure_consumer.py
```

## Test results
Tested end to end with a real Arduino Nano ESP32 and DHT11:
- On the Pi (`mosquitto_sub`): `iot25/mhmood-esp32-01/telemetry {"deviceId":"mhmood-esp32-01","sensor":"temperature","value":24.60,"unit":"°C"}` and `iot25/mhmood-esp32-01-humidity/telemetry {... "value":53.00,"unit":"%"}`
- In Azure IoT Hub (`az iot hub monitor-events`), sent by device `mhmood-gateway`: `{"deviceId": "mhmood-esp32-01", "value": 24.6, "unit": "°C"}`
- Azure consumer output (test run with two simulated devices on the same MQTT topics): `mhmood-esp32-01  23.08 °C` and `mhmood-esp32-02  47.11 %`, each line showing which device sent the value.

## Notes
- The free IoT Hub tier allows 8,000 messages a day. The gateway sends only the latest value per device every 45 seconds: 2 boards x 2 readings x 1,920 rounds = 7,680 messages/day.
- `azure-iot-device` requires `paho-mqtt` 1.x, so the gateway uses that API.
- No secrets are committed: `secrets.h` and `gateway.env` are git-ignored; only example files are in the repo.

## Status
- [x] ESP32 publishes temperature and humidity to MQTT, one topic per device
- [x] Gateway forwards to Azure IoT Hub with its own device identity
- [x] Local consumer and Azure consumer
- [ ] Bluetooth LE configuration (VG)
