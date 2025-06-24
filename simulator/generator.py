from azure.eventhub import EventHubProducerClient, EventData
from faker import Faker
import time, json, random

fake = Faker()
producer = EventHubProducerClient.from_connection_string(
    conn_str="EVENT_HUB_CONN_STR",
    eventhub_name="spark-topic"
)

def generate_event():
    return json.dumps({
        "user_id": fake.uuid4(),
        "movie_id": random.randint(1000, 9999),
        "watch_time": random.randint(1, 180),
        "timestamp": fake.date_time().isoformat()
    })

while True:
    event_data = EventData(generate_event())
    with producer:
        producer.send_batch([event_data])
    time.sleep(1)
