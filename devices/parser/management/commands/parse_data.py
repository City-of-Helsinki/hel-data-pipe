import datetime
import json
import logging
import os

from django.core.management.base import BaseCommand
from fvhiot.parsers import sensornode
from fvhiot.utils.data import data_pack, data_unpack

from .sensor_network import DigitaLorawan
from .topics import Topics

from parser.models import SensorType, Device


def create_data_field(timestamp, data):
    measurement = {"measurement": data}
    return [{"time": timestamp}, measurement]

def create_meta_field(timestamp, devid):
    return {
        "timestamp.received": timestamp,
        "dev-id": devid,
        "dev-type": "Digital Matter Sensornode LoRaWAN",
        "trusted": True,
        "source": {
            "topic": os.environ["KAFKA_RAW_DATA_TOPIC_NAME"],
        },
    }

def create_message(meta, dataline):
    return {"meta": meta, "data": [dataline]}


class Command(BaseCommand):
    def handle(self, *args, **options):
        topics = Topics()

        # Kubernetes liveness check
        open("/app/ready.txt", "w")

        for message in topics.raw_data:
            data = data_unpack(message.value)

            logging.info(data)

            # Hard coded sensor network
            try:
                network_data = DigitaLorawan(data["request"])
            except Exception as e:
                logging.error(e)
                #TODO: store unknown data
                continue

            devid = network_data.device_id
            logging.info(f"Reveiced data from device id {devid}")

            registered_device = Device.objects.get(devid=devid)
            if not registered_device:
                logging.warning("Device not found, ID: {devid}")
                #TODO: store unknown data
                continue

            logging.info(f"Found device {registered_device}")

            sensortype = registered_device.sensortype
            logging.info(f"{registered_device} has sensor type {sensortype.name} with parser {sensortype.parser}")

            try:
                parsed_data = sensornode.parse_sensornode(
                    network_data.payload_hex, network_data.fport
                )
            except Exception as e:
                logging.error(e)
                #TODO: store unknown data
                continue

            meta = create_meta_field(network_data.timestamp, devid)
            dataline = create_data_field(network_data.timestamp, parsed_data)
            parsed_data_message = create_message(meta, dataline)
            logging.info(json.dumps(parsed_data_message, indent=1))

            parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
            logging.info(f"Sending data to {parsed_topic_name}")

            topics.send_to_parsed_data(
                parsed_topic_name,
                value=data_pack(parsed_data_message),
            )
