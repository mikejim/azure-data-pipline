import json
import os
import time
import uuid
from azure.eventhub import EventHubProducerClient, EventData

# Load env vars
connection_str = os.getenv("EVENT_HUB_CONNECTION_STRING")
eventhub_name = os.getenv("EVENT_HUB_NAME", "spark-topic")

producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=eventhub_name)

def generate_event():
    return {
        "user_id": str(uuid.uuid4()),
        "movie_id": str(uuid.uuid4())[:8],
        "watch_time": int(5 + 55 * time.time() % 1),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

print("🟢 Starting Netflix event simulator...")
while True:
    batch = producer.create_batch()
    for _ in range(5):
        event = generate_event()
        batch.add(EventData(json.dumps(event)))
    producer.send_batch(batch)
    print(f"✅ Sent batch at {time.strftime('%X')}")
    time.sleep(2)