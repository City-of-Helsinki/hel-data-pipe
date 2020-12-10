import json

from app import consume_message


def test_consume_message_returns_parsed_message():
    # some fake body data, unnecessary fields are omitted
    body = {
        "DevEUI_uplink": {
            "FPort": "20",
            "Time": "2020-10-15T13:20:39.141+02:00",
            "payload_hex": "ce14290e0928200a",
        }
    }
    message = {
        "request": {"get": {"LrnDevEui": "123"}, "body": json.dumps(body).encode()}
    }
    result = consume_message(message)
    assert "meta" in result
    assert "data" in result
