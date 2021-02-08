from dateutil.parser import parse
import logging
import pytz

from fvhiot.parsers import sensornode


class SensornodeParser:
    def __init__(self):
        pass

    def _parse_payload_hex(self, payload, port):
        return sensornode.parse_sensornode(payload, port)

    def _get_uplink(self, body):
        ul = body.get("DevEUI_uplink")
        if ul is None:
            logging.warning("DevEUI_uplink exists no :-(")
        return ul

    def parse_payload(self, body):
        ul = self._get_uplink(body)
        if not ul:
            return None
        payload = ul["payload_hex"]
        port = int(ul["FPort"])
        parsed_data = self._parse_payload_hex(payload, port)
        return parsed_data

    def parse_timestamp(self, body):
        ul = self._get_uplink(body)
        if not ul:
            return None
        timestamp = parse(ul["Time"]).astimezone(pytz.UTC).isoformat()
        return timestamp


class DummyParser:
    """ Just return the payload from DevEUI_uplink. """

    def __init__(self):
        pass

    def parse_payload(self, body):
        ul = body.get("DevEUI_uplink")
        if ul is None:
            logging.warning("DevEUI_uplink exists no :-(")
            return None
        return ul["payload_hex"]

PARSERS = [
    { "sensor_type": "sensornode", "parser": SensornodeParser() }
    #{ "sensor_type": "sensornode", "parser": DummyParser() }
]

def get_parser(sensor_type):
    """ Get entry from device database according to device id. """
    for parser in PARSERS:
        if parser["sensor_type"] == sensor_type:
            return parser["parser"]
    return None
