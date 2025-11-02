# ===== pi_publisher.py =====
import time, random, json
import paho.mqtt.client as mqtt

BROKER = "192.168.1.105"   # <- your MacBook’s local IP (or host name)
PORT   = 1884
TOPIC  = "edge/sensors"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("[Pi] Connected to broker:", BROKER)

def generate_sensor_values():
   # Simulate two sensors: smooth + noisy
   sensor1 = 20 + random.uniform(-0.5, 0.5)          # temperature-like
   sensor2 = 0.5 + random.uniform(-0.05, 0.05)       # vibration baseline

   # Random outlier 2% of the time
   if random.random() < 0.02:
       sensor2 += random.uniform(2, 3)
   return sensor1, sensor2

while True:
   sensor1, sensor2 = generate_sensor_values()
   payload = {
       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
       "sensor1": round(sensor1, 3),
       "sensor2": round(sensor2, 3)
   }
   client.publish(TOPIC, json.dumps(payload))
   print("[Pi] Published:", payload)
   time.sleep(1)