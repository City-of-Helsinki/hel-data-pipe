import os

from django.core.management.base import BaseCommand
from fvhiot.utils.data import data_unpack
from kafka import KafkaConsumer

from observations.models import save_data

# group id to enable multiple parallel instances
KAFKA_GROUP_ID = "persister"


class Command(BaseCommand):
    def handle(self, *args, **options):
        parsed_data_topic = os.environ.get("KAFKA_PARSED_DATA_TOPIC_NAME")
        consumer = KafkaConsumer(
            parsed_data_topic,
            group_id=KAFKA_GROUP_ID,
            bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_CA"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
        )
        print(f"Listening to topic {parsed_data_topic}")
        open("/app/ready.txt", "w")

        for message in consumer:
            save_data(data_unpack(message.value))
