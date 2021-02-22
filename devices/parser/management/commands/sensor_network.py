import json
import pytz
from dateutil.parser import parse as parse_time

import logging


class DigitaLorawan:
    """ Expose relevant fields out of HTTP request """

    def __init__(self):
        pass

    def parse(self, request):
        self._request = request
        self._parse()

    def _parse(self):
        # device_id and payload are lists
        self.device_id = self._request["get"].get("LrnDevEui")
        self.body_json = json.loads(self._request["body"].decode())
        self.ul = self.body_json["DevEUI_uplink"]
        self.payload_hex = self.ul["payload_hex"]
        self.fport = int(self.ul["FPort"])

        # Po parse payload, both payload_hex and fport are required.
        # To make parser generic, expose these via single payload attribute.
        self.payload = {"payload_hex": self.payload_hex, "fport": self.fport}

        self.time = self.ul["Time"]
        self.timestamp = parse_time(self.time).astimezone(pytz.UTC).isoformat()
        self.devtype = "Digital Matter Sensornode LoRaWAN"


class Cesva:
    """ Expose relevant fields out of HTTP request """

    def __init__(self):
        pass

    def parse(self, request):
        self._request = request
        self._parse()

    def _get_device_id(self):
        # ID contains device number and virtual sub device. Virtual device is identified
        # with postfix N, O, U or S.
        # Example: TA120-T246183-N, TA120-T246183-O, TA120-T246183-U, TA120-T246183-S
        device_ids = [sensor["sensor"][:-2] for sensor in self.body_json["sensors"]]

        if len(set(device_ids)) > 1:
            logging.warning("Data for multiple different sensors inside payload. Not supported.")
        return device_ids[0]

    def _parse(self):
        self.body_json = json.loads(self._request["body"].decode())

        # Multiple sensors
        self.device_id = self._get_device_id()
        self.payload = self.body_json["sensors"]
        self.devtype = "CESVA T120"


NETWORKS  = [
    { "name": "sensornode", "parser": DigitaLorawan() },
    { "name": "cesva", "parser": Cesva() },
]

def get_parser(name):
    """ Get parser based on name. """
    for parser in NETWORKS:
        if parser["name"] == name:
            return parser["parser"]
    return None
