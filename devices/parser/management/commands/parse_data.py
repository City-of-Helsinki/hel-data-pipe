import datetime
import logging
import os
import json

import pytz
from dateutil.parser import parse
from django.core.management.base import BaseCommand
from fvhiot.parsers import sensornode
from fvhiot.utils.data import data_pack, data_unpack

from .topics import Topics
from .sensor_network import DigitaLorawan

# from parser.models import SensorType, Device


def create_dataline(timestamp: datetime.datetime, data: dict):
    timestr = timestamp.astimezone(pytz.UTC).isoformat()
    measurement = {"measurement": data}
    return [{"time": timestr}, measurement]


def create_meta(devid, timestamp, message, request_data):
    return {
        "timestamp.received": timestamp.astimezone(pytz.UTC).isoformat(),
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

            # Hard coded sensor network for now
            network_data = DigitaLorawan(message_value["request"])
            devid = network_data.device_id

            if devid is None:
                logging.error("ERROR: no LrnDevEui in request! False request in Kafka?")
                continue

            logging.info(f"Reveiced data from device id {devid}")

            data = network_data.body_as_json
            ul = data.get("DevEUI_uplink")
            if ul is None:
                logging.warning("DevEUI_uplink exists no :-(")
                continue
            payload = ul["payload_hex"]
            port = int(ul["FPort"])
            parsed_data = sensornode.parse_sensornode(payload, port)
            timestamp = parse(ul["Time"]).astimezone(pytz.UTC)
            dataline = create_dataline(timestamp, parsed_data)
            meta = create_meta(devid, timestamp, message_value, data)
            parsed_data_message = {"meta": meta, "data": [dataline]}
            logging.info(json.dumps(parsed_data_message, indent=1))

            parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
            logging.info(f"Sending data to {parsed_topic_name}")

            topics.send_to_parsed_data(
                parsed_topic_name,
                value=data_pack(parsed_data_message),
            )
