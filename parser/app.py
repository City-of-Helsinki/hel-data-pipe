import datetime
import json
import logging
import os
import sys

from fvhiot.utils.data import data_pack, data_unpack
from kafka import KafkaConsumer, KafkaProducer

from devices import devices, parsers


logging.basicConfig(stream=sys.stdout)

logger = logging.getLogger("logger")
logger.setLevel(
    logging.DEBUG if os.getenv("DEBUG") in [True, 1, "1"] else logging.INFO
)


def create_dataline(timestamp: datetime.datetime, data: dict):
    measurement = {"measurement": data}
    return [{"time": timestamp}, measurement]


def create_meta(devid, devtype, timestamp, message, request_data):
    return {
        "timestamp.received": timestamp,
        "dev-id": devid,
        "dev-type": devtype,
        "trusted": True,
        "source": {
            "sourcename": "Acme inc. Kafka",  # TODO: Placeholder
            "topic": os.environ["KAFKA_RAW_DATA_TOPIC_NAME"],
            "endpoint": "/dummy-sensor/v2",  # TODO: placeholder
        },
    }


try:
    logger.debug("Booting up parser")

    open("/app/ready.txt", "w")

    consumer = KafkaConsumer(
        os.environ["KAFKA_RAW_DATA_TOPIC_NAME"],
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","),
        security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
        ssl_cafile=os.getenv("KAFKA_CA"),
        ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
        ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
    )

    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS").split(","),
        security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
        ssl_cafile=os.getenv("KAFKA_CA"),
        ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
        ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
    )

    for message in consumer:
        message_value = data_unpack(message.value)
        devid = message_value["request"]["get"].get("LrnDevEui")
        if devid is None:
            logger.error("ERROR: no LrnDevEui in request! False request in Kafka?")
            continue

        logger.info(f"Receiced data from device id {devid}")

        device = devices.get_device(devid)
        if not device:
            logger.warning("Device missing from device database, ignored")
            # TODO: push to DLQ
            continue

        logger.debug(f"device entry: {device}")

        request_body: bytes = message_value["request"]["body"]
        # TODO: catch json exceptions
        data = json.loads(request_body.decode())

        parser = parsers.get_parser(device["parser"])
        logger.debug(f"parser: {parser}")
        if not parser:
            logger.warning(f"Parser not found for device {devid}")
            #TODO: push to DLQ
            continue

        parsed_data = parser.parse_payload(data)
        timestamp = parser.parse_timestamp(data)
        devtype = device["dev-type"]

        dataline = create_dataline(timestamp, parsed_data)
        meta = create_meta(devid, devtype, timestamp, message_value, data)
        parsed_data_message = {"meta": meta, "data": [dataline]}
        logger.debug(json.dumps(parsed_data_message, indent=1))
        parsed_topic_name = os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME")
        logger.info(f"Sending data to {parsed_topic_name}")
        producer.send(
            parsed_topic_name,
            value=data_pack(parsed_data_message),
        )


except Exception as e:
    logger.error(e)
    raise
