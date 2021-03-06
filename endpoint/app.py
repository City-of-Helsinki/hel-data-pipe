import logging
import os
from logging.config import dictConfig

from flask import Flask, abort, request
from fvhiot.utils.data import data_pack
from fvhiot.utils.http import extract_data_from_flask_request
from kafka import KafkaProducer

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {"class": "logging.StreamHandler", "formatter": "default"}
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)


@app.route("/readiness")
def readiness():
    return "OK"


@app.route("/healthz")
def healthz():
    return "OK"


app.producer = None


def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
        security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
        ssl_cafile=os.getenv("KAFKA_CA"),
        ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
        ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
    )


# Wild-card catch-all handler
@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "HEAD"])
def catchall(path: str):
    """
    Endpoint for remote IoT sensors.

    Check that request path matches ENDPOINT_PATH
    and optionally validate request credentials, device id etc.
    and if everything is ok send serialised request to a kafka topic.

    :param path: request path
    :return:
    """
    # Allow testing using root path
    if path == "":
        return "Test OK", 200
    endpoint_path = os.getenv("ENDPOINT_PATH")

    # Reject requests not matching the one defined in env
    if path not in [endpoint_path, "cesva"]:
        logging.warning(
            f"{endpoint_path} did not match {path}. Rejecting this request."
        )
        abort(404, description="Resource not found")

    if app.producer is None:
        app.producer = get_kafka_producer()
    # TODO: Validate request here
    # - from allowed IP address?
    # - request contains valid token or similar?
    data = extract_data_from_flask_request(request)

    data["path"] = path
    body_max_size = app.config.get("REQUEST_BODY_MAX_SIZE", 4096)
    if len(data["request"]["body"]) > body_max_size:
        return f"Request body too large (>{body_max_size}B)", 400
    topic_name = os.getenv("KAFKA_RAW_DATA_TOPIC_NAME")
    logging.info(f"Sending {endpoint_path} data to {topic_name}")

    def on_send_success(record_metadata):
        logging.info(
            "Successfully sent to topic {}, partition {}, offset {}".format(
                record_metadata.topic, record_metadata.partition, record_metadata.offset
            )
        )

    def on_send_error(excp):
        logging.error("Error on Kafka producer", exc_info=excp)

    app.producer.send(topic_name, value=data_pack(data)).add_callback(
        on_send_success
    ).add_errback(on_send_error)
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG", False))
