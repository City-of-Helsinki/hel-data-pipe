import json
import pytz
from dateutil.parser import parse as parse_time


class DigitaLorawan:
    """ Expose relevant fields out of HTTP request """

    def __init__(self, request):
        self._request = request
        self._parse()

    def _parse(self):
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
