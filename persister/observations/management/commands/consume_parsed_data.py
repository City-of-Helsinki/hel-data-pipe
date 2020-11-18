import os

from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from fvhiot.utils.data import data_unpack


class Command(BaseCommand):

    def handle(self, *args, **options):
        parsed_data_topic = os.environ.get("KAFKA_PARSED_DATA_TOPIC_NAME")
        consumer = KafkaConsumer(
            parsed_data_topic,
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
        )
        print(f"Listening to topic {parsed_data_topic}")
        for message in consumer:
            print(f"{message.topic}: {data_unpack(message.value)}")

            # TODO: Example how we could actually save the data when models
            #       are present

            # serializer = ObservationSerializer(
            #     data=json.loads(msg.value.decode())["data"]
            # )
            # serializer.is_valid()
            # serializer.save()
