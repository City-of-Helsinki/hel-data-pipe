import datetime
import logging
import os
import json
import pytz
import sys

from django.core.management.base import BaseCommand
from fvhiot.utils.data import data_unpack, data_pack
from fvhiot.parsers import sensornode
from kafka import KafkaConsumer, KafkaProducer
from dateutil.parser import parse

#from parser.models import SensorType, Device

# group id to enable multiple parallel instances
KAFKA_GROUP_ID = "parser"


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
        topic = os.environ.get("KAFKA_RAW_DATA_TOPIC_NAME")
        consumer = KafkaConsumer(
            topic,
            group_id=KAFKA_GROUP_ID,
            bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_CA"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
        )
        logging.info(f"Listening to topic {topic}")

        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_CA"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),)

        logging.info(f"Creating liveness file")
        # Kubernetes liveness check
        open("/app/ready.txt", "w")

        for message in consumer:
            message_value = data_unpack(message.value)
            devid = message_value["request"]["get"].get("LrnDevEui")
            if devid is None:
                logging.error("ERROR: no LrnDevEui in request! False request in Kafka?")
                continue
            logging.info(f"Reveiced data from device id {devid}")
            request_body: bytes = message_value["request"]["body"]
            # TODO: catch json exceptions
            data = json.loads(request_body.decode())
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
            logging.debug(json.dumps(parsed_data_message, indent=1))
            parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
            logging.info(f"Sending data to {parsed_topic_name}")

            producer.send(
                parsed_topic_name,
                value=data_pack(parsed_data_message),
            )
