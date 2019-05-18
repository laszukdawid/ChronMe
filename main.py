import datetime
import json
import pprint

from collections import defaultdict

from aw_core import Event

from src.config_parser import ConfigParser
from src.classificator import Classificator
from src.discovery import Discovery
from src.event_extractor import EventExtractor
from src.exist import ExistClient
from src.uploader import upload_data


def extract_duration(event: Event):
    "Extract duration information in seconds. Always returns at least 1 second, even if non provided"
    DURATION_KEY = "duration"
    min_duration = 1
    if DURATION_KEY not in event:
        return min_duration
    
    return event[DURATION_KEY].total_seconds() or min_duration

def main():
    config_parser = ConfigParser('config.json')
    discovery = Discovery()
    classificator = Classificator()
    event_extractor = EventExtractor()
    exist_client = ExistClient()

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    events = event_extractor.get_events_for_day(yesterday)

    category_counter = defaultdict(int)
    category_duration = defaultdict(float)
    for event in events:

        category = classificator.check_productivity(event)
        category_counter[category] += 1
        category_duration[category] += extract_duration(event)

        if category == classificator.UNKNOWN_CATEGORY:
            discovery.add_event(event)

    print("Counter: ", category_counter)
    print("Duration: ", category_duration)

    for unknown_event in discovery.get_all_unique_events():
        print(unknown_event)

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    response = exist_client.send_productivity(yesterday.isoformat()[:10], productivity_data)
    print(response.json())

    # Backup data in AWS S3
    all_buckets_events = event_extractor.get_all_buckets_events()
    upload_data(config_parser, all_buckets_events, yesterday)


if __name__ == "__main__":
    main()