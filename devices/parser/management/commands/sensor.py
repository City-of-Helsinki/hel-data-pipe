from fvhiot.parsers import sensornode
#from fvhiot.parsers import ultrasonic


class UltrasonicParser:
    def __init__(self):
        pass

    def _parse_payload_hex(self, payload, port):
        # TODO !!!
        return None
        #return sensornode.parse_sensornode(payload, port)

    def parse_payload(self, payload):
        """ This is common parsing method, implemented by all parsers. """
        parsed_data = self._parse_payload_hex(payload["payload_hex"], payload["fport"])
        return parsed_data


class SensornodeParser:
    def __init__(self):
        pass

    def _parse_payload_hex(self, payload, port):
        return sensornode.parse_sensornode(payload, port)

    def parse_payload(self, payload):
        """ This is common parsing method, implemented by all parsers. """
        parsed_data = self._parse_payload_hex(payload["payload_hex"], payload["fport"])
        return parsed_data


# Available parsers. "name" field corresponds to "Parser" field in sensor types admin panel.
PARSERS = [
    { "name": "sensornode", "parser": SensornodeParser() },
    { "name": "ultrasonic", "parser": UltrasonicParser() },
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
