import json
import logging
import os

from django.core.management.base import BaseCommand
from fvhiot.utils.data import data_pack, data_unpack

from .sensor_network import DigitaLorawan
from . import sensor
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
                # TODO: store unknown data, not valid network_data
                continue

            devid = network_data.device_id
            logging.info(f"Reveiced data from device id {devid}")

            registered_device = Device.objects.get(devid=devid)
            if not registered_device:
                logging.warning("Device not found, ID: {devid}")
                # TODO: store unknown data, device not found

                # TODO: uncomment after the device registry is configured, to skip unknown devices
                #continue

            logging.info(f"Found device {registered_device}")

            sensortype = registered_device.sensortype
            logging.info(f"{registered_device} has sensor type {sensortype.name} with parser {sensortype.parser}")

            parser = sensor.get_parser(sensortype.parser)

            # TODO: This is temporarily overwritten, later device registry sets parser for each device
            parser = sensor.get_parser("sensornode")

            if not parser:
                logging.warning(f"Parser {sensortype.parser} not found for device {devid}")
                # TODO: store unknown data, parser not found
                continue

            try:
                parsed_data = parser.parse_payload(network_data.payload)
            except Exception as e:
                logging.error("Hex payload parser failed for device ID {devid}")
                logging.error(e)
                # TODO: store unknown data, error in hex payload parsing
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
