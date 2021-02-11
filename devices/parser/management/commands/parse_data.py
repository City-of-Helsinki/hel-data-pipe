import datetime
import json
import logging
import os

from django.core.management.base import BaseCommand
from fvhiot.parsers import sensornode
from fvhiot.utils.data import data_pack, data_unpack

from .sensor_network import DigitaLorawan
from .topics import Topics

# from parser.models import SensorType, Device


def create_dataline(timestamp: datetime.datetime, data: dict):
    measurement = {"measurement": data}
    return [{"time": timestamp}, measurement]


def create_meta(devid, timestamp, message, request_data):
    return {
        "timestamp.received": timestamp,
        "dev-id": devid,
        "dev-type": "Digital Matter Sensornode LoRaWAN",
        "trusted": True,
        "source": {
            "sourcename": "Acme inc. Kafka",  # TODO: Placeholder
            "topic": os.environ["KAFKA_RAW_DATA_TOPIC_NAME"],
            "endpoint": "/dummy-sensor/v2",  # TODO: placeholder
        },
    }


class Command(BaseCommand):
    def handle(self, *args, **options):
        topics = Topics()

        # Kubernetes liveness check
        open("/app/ready.txt", "w")

        for message in topics.raw_data:
            message_value = data_unpack(message.value)

            # Hard coded sensor network
            try:
                network_data = DigitaLorawan(message_value["request"])
            except Exception as e:
                logging.error(e)
                #TODO: store unknown data
                continue

            devid = network_data.device_id
            logging.info(f"Reveiced data from device id {devid}")

            parsed_data = sensornode.parse_sensornode(
                network_data.payload_hex, network_data.fport
            )

            dataline = create_dataline(network_data.timestamp, parsed_data)
            meta = create_meta(devid, network_data.timestamp, message_value, network_data.body_json)
            parsed_data_message = {"meta": meta, "data": [dataline]}
            logging.info(json.dumps(parsed_data_message, indent=1))

            parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
            logging.info(f"Sending data to {parsed_topic_name}")

            topics.send_to_parsed_data(
                parsed_topic_name,
                value=data_pack(parsed_data_message),
            )
