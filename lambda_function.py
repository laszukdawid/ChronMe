import boto3
import datetime
import json
import os
import pprint

from collections import defaultdict

from chronme.classificator import Classificator
from chronme.discovery import Discovery
from chronme.exist import ExistClient
from chronme.utils import extract_duration, parse_merge_events


BUCKET_NAME = os.environ["AW_BUCKET"]
s3 = boto3.client("s3")

def get_all_data(isodate):
    prefix = "data/" + isodate
    all_files = s3.list_objects(Bucket=BUCKET_NAME, Prefix=prefix)
    file_paths = [obj["Key"] for obj in all_files["Contents"]]

    all_events = {}
    for file_path in file_paths:
        print(f"Downloading: {file_path}")
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_path)
        key = file_path.rsplit('/', 1)[1]
        all_events[key] = json.loads(obj['Body'].read())

    return all_events

def get_rules():
    objects = s3.list_objects(Bucket=BUCKET_NAME, Prefix="rules")
    rules = {}
    for s3_rules_file in objects["Contents"]:
        key = s3_rules_file["Key"]
        print(key)
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        rules.update(json.loads(obj["Body"].read()))
    return rules

def merge_all_events(all_buckets_events):
    return list(parse_merge_events(*all_buckets_events.values()))

def categorize_data(merged_events, rules):
    classificator = Classificator(productivity_map=rules)
    discovery = Discovery()

    category_counter = defaultdict(int)
    category_duration = defaultdict(float)
    for event in merged_events:

        category = classificator.check_productivity(event)
        category_counter[category] += 1
        category_duration[category] += extract_duration(event)

        if category == classificator.UNKNOWN_CATEGORY:
            discovery.add_event(event)

    print("Counter: ", category_counter)
    print("Duration: ", category_duration)

    for unknown_event in discovery.get_agg_duration_events_sorted(top_n=20):
        print("Total duration: ", unknown_event[1])
        pprint.pprint(dict(unknown_event[0]))

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    return productivity_data

def update_exist(isodate, productivity_data):
    exist_client = ExistClient()
    return exist_client.send_productivity(isodate, productivity_data)

def lambda_handler(event, context):
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    isodate = yesterday.isoformat()[:10]
    all_bucket_events = get_all_data(isodate)
    rules = get_rules()
    merged_events = merge_all_events(all_bucket_events)

    productivity_data = categorize_data(merged_events, rules)
    response = update_exist(isodate, productivity_data)

    return "All good! Fuck-tastic!\n" + str(response.json())