import pytest
from app import app as flask_app


class KafkaMockProducer:
    """A mock Kafka client implementing just send() method."""

    def __init__(self, **configs):
        print("Initialised Kafka mock producer")

    def send(
        self,
        topic,
        value=None,
        key=None,
        headers=None,
        partition=None,
        timestamp_ms=None,
    ):
        print(f"Pretending to send to {topic} a message: {value}")


@pytest.fixture
def app():
    flask_app.producer = KafkaMockProducer()
    return flask_app
