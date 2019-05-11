import json
import pprint

from aw_client import ActivityWatchClient

from classificator import Classificator


awc = ActivityWatchClient()
classificator = Classificator()

buckets = awc.get_buckets()
bucket_name = [k for k in buckets.keys() if 'window' in k][0]
bucket = buckets[bucket_name]

print("Bucket: ", bucket)
events = awc.get_events(bucket['id'], limit=1000)

counter = {}
for event in events:
    category = classificator.check_productivity(event)
    print(category, ' -- ', event['data'])
    if category not in counter:
        counter[category] = 0
    counter[category] += 1

print(counter)
