from abc import ABC, abstractmethod
import json
  

class SensorNetworkMetaData(ABC):

    @property
    @abstractmethod
    def device_id(self):
        pass

    @property
    @abstractmethod
    def body_as_json(self):
        pass


class DigitaLorawan(SensorNetworkMetaData): 
  
    def __init__(self, request):
        self._request = request

    @property
    def device_id(self):
        return self._request["get"].get("LrnDevEui")
    
    @property
    def body_as_json(self):
        request_body= self._request["body"]
        return json.loads(request_body.decode())
