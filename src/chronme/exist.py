import os
from typing import Dict

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
        return os.environ["EXIST_TOKEN"]

    def send_productivity(self, date, productivity_min_map):
        create_attribute = lambda key, value: {"name": key + "_min", "value": value/60, "date": date}
        attributes = [create_attribute(key, value) for (key, value) in productivity_min_map.items()]
        print(f"Sending productivity attributes:\n{attributes}")
        return self._send(self.EXIST_UPDATE_URL, attributes)

    def _send(self, url, attributes):
        return requests.post(url,
            headers={'Authorization': "Bearer " + self.__token},
            json=attributes
        )

    def validate_response(self, response: requests.Response):
        if response.status_code >= 300:
            raise ValueError(f"Failed to update the Exist data. Reason:\n{response.content}")
