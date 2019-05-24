import json
import os
import pprint
import sys

try:
    import requests
except:
    from botocore.vendored import requests

class ExistClient:

    EXIST_UPDATE_URL = 'https://exist.io/api/1/attributes/update/'

    def __init__(self):
        self.__token = self._get_token()

    def _get_token(self):
        "Fail badly if token not there"
        return os.environ["EXIST_AW_TOKEN"]

    def send_productivity(self, date, productivity_min_map):
        create_attribute = lambda key, value: {"name": key + "_min", "value": value/60, "date": date}
        attributes = [create_attribute(key, value) for (key, value) in productivity_min_map.items()]
        return self._send(self.EXIST_UPDATE_URL, attributes)

    def _send(self, url, attributes):
        return requests.post(url,
            headers={'Authorization': "Bearer " + self.__token},
            json=attributes
        )
