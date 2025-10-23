# mac_subscriber.py
import os, json
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "host.k3d.internal")
PORT = int(os.getenv("MQTT_PORT", "1884"))
TOPIC = os.getenv("MQTT_TOPIC", "sensor/data")

def on_connect(client, userdata, flags, rc):
    print(f"[subscriber] Connected with result code {rc}, subscribing to '{TOPIC}'")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8", errors="ignore")
        data = json.loads(payload)
    except Exception:
        data = payload
    print(f"[subscriber] {msg.topic} -> {data}")

client = mqtt.Client(client_id="K3dSubscriber", protocol=mqtt.MQTTv311)  # paho 1.6 friendly
client.on_connect = on_connect
client.on_message = on_message

print(f"[subscriber] Connecting to {BROKER}:{PORT}")
client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()