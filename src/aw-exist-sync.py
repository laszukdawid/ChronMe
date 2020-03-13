import datetime
import json
import pprint

from collections import defaultdict

from aw_core import Event

from chronme.config_parser import ConfigParser
from chronme.classificator import Classificator
from chronme.discovery import Discovery
from chronme.event_extractor import EventExtractor
from chronme.exist import ExistClient
from chronme.uploader import upload_data
from chronme.utils import extract_duration

def get_today_utc():
    local_now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_midnight = local_midnight.astimezone(datetime.timezone.utc)
    return local_midnight, utc_midnight

def main():
    config_parser = ConfigParser('config.json')
    discovery = Discovery()
    classificator = Classificator()
    print("Pass classifcator")
    event_extractor = EventExtractor()

    _, today_utc = get_today_utc()
    tomorrow_utc = today_utc + datetime.timedelta(days=1)
    events = event_extractor.get_events_for_day(today_utc, end_date=tomorrow_utc)

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

    for unknown_event in discovery.get_agg_duration_events_sorted(top_n=20):
        print("Total duration: ", unknown_event[1])
        pprint.pprint(dict(unknown_event[0]))

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    # Upload events data to S3
    all_buckets_events = event_extractor.get_all_buckets_events()
    upload_data(config_parser, all_buckets_events, today_utc)


if __name__ == "__main__":
    main()
