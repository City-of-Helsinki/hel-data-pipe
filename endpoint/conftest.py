import pytest
from app import app as flask_app


class KafkaMockProducer(object):
    """A mock Kafka client implementing just send() method.
    """

    def __init__(self, **configs):
        print(f'Initialised Kafka mock producer')

    def send(self, topic, value=None, key=None, headers=None, partition=None, timestamp_ms=None):
        print(f'KafkaMockProduser is pretending to send to {topic} a message: {value}')


@pytest.fixture
def app():
    flask_app.producer = KafkaMockProducer()
    return flask_app
