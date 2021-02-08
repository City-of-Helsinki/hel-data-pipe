# Device database

DEV_TYPE_LORAWAN = "Digital Matter Sensornode LoRaWAN"

DEVICES = [
    { "devid": "70B3D57050005037", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050001AB9", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050001BA6", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},
    { "devid": "70B3D57050004D86", "parser": "sensornode", "dev-type": DEV_TYPE_LORAWAN},

    # Device for testing purposes
    { "devid": "123", "parser": None, "dev-type": None }
]

def get_device(devid):
    """ Get entry from device database according to device id. """
    for device in DEVICES:
        if device["devid"] == devid:
            return device
    return None
