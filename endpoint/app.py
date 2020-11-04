import os

import certifi
from flask import Flask, request, abort
from fvhiot.utils.data import data_pack
from fvhiot.utils.http import extract_data_from_flask_request
from kafka import KafkaProducer

# TODO: figure out how to use logging instead of print in docker
# import logging


app = Flask(__name__)


@app.route("/readiness")
def readiness():
    return "OK"


@app.route("/healthz")
def healthz():
    return "OK"


producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS').split(','),
    security_protocol=os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
    ssl_cafile=certifi.where(),
    sasl_mechanism=os.getenv('KAFKA_SASL_MECHANISM'),
    sasl_plain_username=os.getenv('KAFKA_USERNAME'),
    sasl_plain_password=os.getenv('KAFKA_PASSWORD')
)


# Wild-card catch-all handler
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'HEAD'])
def catchall(path: str):
    """
    Endpoint for remote IoT sensors.

    Check that request path matches ENDPOINT_PATH
    and optionally validate request credentials, device id etc.
    and if everything is ok send serialised request to a kafka topic.

    :param path: request path
    :return:
    """
    endpoint_path = os.getenv('ENDPOINT_PATH')
    if endpoint_path != path:
        print(f'{endpoint_path} did not match {path}. Rejecting this request.')
        abort(404, description="Resource not found")
    # TODO: Validate request here
    # - from allowed IP address?
    # - request contains valid token or similar?
    data = extract_data_from_flask_request(request)
    data['path'] = path
    body_max_size = app.config.get('REQUEST_BODY_MAX_SIZE', 4096)
    if len(data['request']['body']) > body_max_size:
        return f'Request body too large (>{body_max_size}B)', 400
    topic_name = os.getenv('KAFKA_RAW_DATA_TOPIC_NAME')
    print(f'Sending stuff to {topic_name}')
    producer.send(topic_name, value=data_pack(data))
    return 'OK'


if __name__ == "__main__":
    app.run()
