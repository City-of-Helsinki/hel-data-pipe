import datetime
import json
import logging
import os
import sys

import pytz
from dateutil.parser import parse
from fvhiot.parsers import sensornode
from fvhiot.utils.data import data_pack, data_unpack
from kafka import KafkaConsumer, KafkaProducer

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG if os.getenv("DEBUG") else logging.ERROR
)
logger = logging.getLogger("logger")


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
            print("ERROR: no LrnDevEui in request! False request in Kafka?")
            continue
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
        print(json.dumps(parsed_data_message, indent=1))
        producer.send(
            os.getenv("KAFKA_PARSED_DATA_TOPIC_NAME"),
            value=data_pack(parsed_data_message),
        )


except Exception as e:
    print(e)
    raise
