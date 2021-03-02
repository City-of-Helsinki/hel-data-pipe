import datetime
import logging

import pytz
from dateutil.parser import parse as parse_time
from fvhiot.parsers import dlmbx, sensornode


class UltrasonicParser:
    def __init__(self):
        pass

    def _parse_payload_hex(self, payload, port):
        return dlmbx.decode_hex(payload, port)

    def parse_payload(self, payload):
        """ This is common parsing method, implemented by all parsers. """
        parsed_data = self._parse_payload_hex(payload["payload_hex"], payload["fport"])
        return parsed_data


class SensornodeParser:
    def __init__(self):
        pass

    def _parse_payload_hex(self, payload, port):
        return sensornode.decode_hex(payload, port)

    def parse_payload(self, payload):
        """ This is common parsing method, implemented by all parsers. """
        parsed_data = self._parse_payload_hex(payload["payload_hex"], payload["fport"])
        return parsed_data


class CesvaParser:
    def __init__(self):
        pass

    def parse_payload(self, payload):
        """ This is common parsing method, implemented by all parsers. """

        parsed_data = []
        for meas in payload:
            postfix = meas["sensor"][-1:]

            time = parse_time(meas["observations"][0]["timestamp"], dayfirst=False).astimezone(pytz.UTC)

            if postfix == "N":
                meas_type = "LAeq"
                value = meas["observations"][0]["value"]
                parsed_data.append({meas_type: value, "time": time.isoformat()})
            elif postfix == "S":
                meas_type = "LAeq1s"
                # Multiple values, each has own time stamp
                values_str = meas["observations"][0]["value"]
                # Each element has format '044.9,0,0' separated by ';'
                # Take only the first value (before ',') from each
                val_count = len(values_str.split(";"))
                if val_count != 60:
                    logging.error(f"Assuming 60 entries for LAea1s, found {val_count}")
                    continue
                for i, entry in enumerate(values_str.split(";")):
                    value = entry.split(",", 1)[0]
                    # 60 values, timestamp only for the last one. Calculate entry specific times.
                    time_delta_s = val_count - i - 1
                    entry_time = time - datetime.timedelta(seconds=time_delta_s)
                    parsed_data.append(
                        {meas_type: value, "time": entry_time.isoformat()}
                    )

            else:
                # Code not implemented
                continue

        return parsed_data


# Available parsers. "name" field corresponds to "Parser" field in sensor types admin panel.
PARSERS = [
    {"name": "sensornode", "parser": SensornodeParser()},
    {"name": "dlmbx", "parser": UltrasonicParser()},
    {"name": "cesva", "parser": CesvaParser()},
]


def get_parser(name):
    """ Get parser based on name. """
    for parser in PARSERS:
        if parser["name"] == name:
            return parser["parser"]
    return None


def get_parser_choices():
    """ Get available parsers to be used as choices in models. """

    # ( <model field>, <visible name> )
    return [(p["name"], p["name"]) for p in PARSERS]
