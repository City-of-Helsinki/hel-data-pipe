from . import parsers


DEV_TYPE_LORAWAN = "Digital Matter Sensornode LoRaWAN"

# Device database

DEVICES = [
    { "devid": "70B3D57050005037", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050001AB9", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050001BA6", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050004D86", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},

    # Device for testing purposes
    { "devid": "123", "parser": None, "dev-type": None }
]

class Device:
    def __init__(self, devid=None, parser=None, devtype=None):
        self.devid = devid
        self.parser = parser
        self.devtype = devtype

    @classmethod
    def from_device_entry(self, entry):
        return Device(entry["devid"], entry["parser"], entry["dev-type"])

    def __str__(self):
        return f"Device devid: {self.devid}, parser: {self.parser}, devtype: {self.devtype}"

    def get_parser(self):
        return parsers.get_parser(self.parser)


def get_device(devid):
    """ Get entry from device database according to device id. """
    for device in DEVICES:
        if device["devid"] == devid:
            return Device.from_device_entry(device)
    return None
