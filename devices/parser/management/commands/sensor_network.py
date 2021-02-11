import json
import pytz
from dateutil.parser import parse


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
        self.time = self.ul["Time"]
        self.timestamp = parse(self.time).astimezone(pytz.UTC).isoformat()
