import json
import os
import pprint
import requests
import sys

token_param = "Bearer " + os.environ["EXIST_TOKEN"]

url = 'https://exist.io/api/1/attributes/acquire/'

attributes = [
    {"name": "productive_min", "active":True},
    {"name": "neutral_min", "active":True},
    {"name": "distracting_min", "active":True},
    ]

print(token_param)
response = requests.post(url,
        headers={'Authorization': token_param},
        json=attributes
        )

update = response.json()
pprint.pprint(update)
