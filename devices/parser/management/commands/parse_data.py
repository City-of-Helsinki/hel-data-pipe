import json
import logging
import os

from django.core.management.base import BaseCommand
from fvhiot.utils.data import data_pack, data_unpack

from .sensor_network import DigitaLorawan
from . import sensor
from .topics import Topics

from parser.models import SensorType, Device, RawMessage, RAW_MESSAGE_STATUS


def create_data_field(timestamp, data):
    measurement = {"measurement": data}
    return [{"time": timestamp}, measurement]

def create_meta_field(timestamp, devid, devtype):
    return {
        "timestamp.received": timestamp,
        "dev-id": devid,
        "dev-type": devtype,
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

            # Hard coded sensor network
            try:
                network_data = DigitaLorawan(data["request"])
            except Exception as e:
                logging.error(e)
                unknown_message = RawMessage(data=message, status=RAW_MESSAGE_STATUS.NW_DATA_ERROR)
                unknown_message.save()
                continue

            devid = network_data.device_id
            logging.info(f"Reveiced data from device id {devid}")

            try:
                registered_device = Device.objects.get(devid=devid)
            except Device.DoesNotExist:
                registered_device = None

            if not registered_device:
                logging.warning(f"Device not found, ID: {devid}")

                logging.warning(f"Using default parser: sensornode")
                parser = sensor.get_parser("sensornode")

                unknown_message = RawMessage(data=message, status=RAW_MESSAGE_STATUS.DEVICE_ID_NOT_FOUND, devid=devid)
                unknown_message.save()
                continue
            else:
                logging.debug(f"Found device: {registered_device}")
                sensortype = registered_device.sensortype
                logging.debug(f"{registered_device} has sensor type {sensortype.name} with parser {sensortype.parser}")
                parser = sensor.get_parser(sensortype.parser)

            if not parser:
                logging.warning(f"Parser {sensortype.parser} not found for device {devid}")
                unknown_message = RawMessage(data=message, status=RAW_MESSAGE_STATUS.PARSER_NOT_FOUND, devid=devid)
                unknown_message.save()
                continue

            try:
                parsed_data = parser.parse_payload(network_data.payload)
            except Exception as e:
                logging.error(f"Hex payload parser failed for device ID {devid}")
                logging.error(e)
                unknown_message = RawMessage(data=message, status=RAW_MESSAGE_STATUS.PARSER_ERROR, devid=devid)
                unknown_message.save()
                continue

            meta = create_meta_field(network_data.timestamp, devid, network_data.devtype)
            dataline = create_data_field(network_data.timestamp, parsed_data)
            parsed_data_message = create_message(meta, dataline)
            logging.debug(json.dumps(parsed_data_message, indent=1))

            parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
            logging.info(f"Sending data to {parsed_topic_name}")

            topics.send_to_parsed_data(
                parsed_topic_name,
                value=data_pack(parsed_data_message),
            )
