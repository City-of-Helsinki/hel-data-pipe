import logging
import os

from kafka import KafkaConsumer, KafkaProducer


class Topics:

    # group id to enable multiple parallel instances
    KAFKA_GROUP_ID = "parser"

    def __init__(self):
        self._consumer = KafkaConsumer(
            os.environ.get("KAFKA_RAW_DATA_TOPIC_NAME"),
            group_id=Topics.KAFKA_GROUP_ID,
            bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_CA"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
        )

        self._producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_CA"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
        )

    @property
    def raw_data(self):
        """ Return default consumer for RAW data. """
        return self._consumer

    def send_to_parsed_data(self, topic, value):
        """ Send data to given topic in PARSED data topic. """

        def on_send_success(record_metadata):
            logging.info(
                "Successfully sent to topic {}, partition {}, offset {}".format(
                    record_metadata.topic,
                    record_metadata.partition,
                    record_metadata.offset,
                )
            )

        def on_send_error(excp):
            logging.error("Error on Kafka producer", exc_info=excp)

        self._producer.send(topic, value).add_callback(on_send_success).add_errback(
            on_send_error
        )
