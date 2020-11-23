import os

from django.core.management.base import BaseCommand
from fvhiot.utils.data import data_unpack
from kafka import KafkaConsumer
from observations.models import save_data


class Command(BaseCommand):

    def handle(self, *args, **options):
        parsed_data_topic = os.environ.get("KAFKA_PARSED_DATA_TOPIC_NAME")
        consumer = KafkaConsumer(
            parsed_data_topic,
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
        )
        print(f"Listening to topic {parsed_data_topic}")
        for message in consumer:
            save_data(data_unpack(message.value))