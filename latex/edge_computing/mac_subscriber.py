# mac_subscriber.py — Edge Cloud AI Subscriber
import os, json, time
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt

# AWS IoT Core configuration
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT", "akzdc7a60ugm9-ats.iot.eu-north-1.amazonaws.com")
AWS_PORT = 8883
AWS_TOPIC = "edgecloud/alerts"
AWS_CERT_DIR = os.path.join(os.path.dirname(__file__), "aws_certs")

AWS_CERT = os.path.join(AWS_CERT_DIR, "664ca5debe852d4e4b57ebe0688388694278de7c350202d2ed0d7a9c60d8133b-certificate.pem.crt")
AWS_KEY  = os.path.join(AWS_CERT_DIR, "664ca5debe852d4e4b57ebe0688388694278de7c350202d2ed0d7a9c60d8133b-private.pem.key")
AWS_ROOT_CA = os.path.join(AWS_CERT_DIR, "AmazonRootCA1.pem")

aws_client = mqtt.Client(client_id="EdgeCloudAWS", protocol=mqtt.MQTTv311)
aws_client.tls_set(ca_certs=AWS_ROOT_CA, certfile=AWS_CERT, keyfile=AWS_KEY)
aws_client.connect(AWS_ENDPOINT, AWS_PORT, keepalive=60)
aws_client.loop_start()

# MQTT configuration
BROKER = os.getenv("MQTT_BROKER", "host.docker.internal")
PORT = int(os.getenv("MQTT_PORT", "1884"))
TOPIC = os.getenv("MQTT_TOPIC", "sensor/data")

# Buffer for recent sensor2 values
window_size = 100
buffer_s2 = deque(maxlen=window_size)

# Isolation Forest model for anomaly detection
model = IsolationForest(contamination=0.05, random_state=42)

def train_model():
    """Retrains the model with the current buffer data."""
    if len(buffer_s2) >= 20:
        data = np.array(buffer_s2).reshape(-1, 1)
        model.fit(data)
        print(f"[EdgeCloud] Model retrained on {len(buffer_s2)} samples")

def detect_anomaly(value):
    """Returns True if an anomaly is detected."""
    data = np.array([[value]])
    pred = model.predict(data)[0]  # 1 = normal, -1 = anomaly
    return pred == -1

def on_connect(client, userdata, flags, rc):
    print(f"[EdgeCloud] Connected with result code {rc}, subscribing to '{TOPIC}'")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global model
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        sensor2 = payload.get("sensor2", None)
        timestamp = payload.get("timestamp", "?")
        if sensor2 is None:
            return

        # Add to buffer and retrain periodically
        buffer_s2.append(sensor2)
        if len(buffer_s2) % 20 == 0:
            train_model()

        # Detect anomalies when trained
        if len(buffer_s2) >= 20:
            is_anomaly = detect_anomaly(sensor2)
            status = "⚠️ ANOMALY" if is_anomaly else "✅ OK"
            print(f"[EdgeCloud] {timestamp} | s2={sensor2:.3f} -> {status}")

            # Publish anomaly results to AWS IoT Core with safe serialization
            try:
                result_payload = {
                    "timestamp": str(timestamp),
                    "sensor2": float(sensor2),
                    "anomaly": bool(is_anomaly)
                }
                payload_json = json.dumps(result_payload, default=str)
                aws_client.publish(AWS_TOPIC, payload_json)
                print(f"[EdgeCloud] Published anomaly result to AWS IoT Core: {payload_json}")
            except Exception as e:
                print("[EdgeCloud] Error publishing to AWS:", e)

    except Exception as e:
        print("[EdgeCloud] Error parsing message:", e)

# MQTT setup
client = mqtt.Client(client_id="EdgeCloudSubscriber", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

print(f"[EdgeCloud] Connecting to {BROKER}:{PORT}")
client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()