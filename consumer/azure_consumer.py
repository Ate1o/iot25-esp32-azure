"""Azure consumer: prints telemetry from IoT Hub in real time (the hub's Event Hub-compatible endpoint).

  set EVENTHUB_CONNECTION_STRING=<IoT Hub > Built-in endpoints > Event Hub-compatible endpoint>
  python consumer/azure_consumer.py
"""
import json
import os

from azure.eventhub import EventHubConsumerClient


def on_event(partition_context, event):
    body = event.body_as_str(encoding="UTF-8")
    try:
        d = json.loads(body)
        print(f"{event.enqueued_time:%H:%M:%S}  {d.get('deviceId'):<20} {d.get('value')} {d.get('unit', '')}", flush=True)
    except (ValueError, AttributeError):
        print("raw:", body, flush=True)


client = EventHubConsumerClient.from_connection_string(os.environ["EVENTHUB_CONNECTION_STRING"], consumer_group="$Default")
print("Listening to Azure IoT Hub (Ctrl+C to stop)...", flush=True)
with client:
    client.receive(on_event=on_event, starting_position="-1")  # "-1" = from the start of the retained stream
