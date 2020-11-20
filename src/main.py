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


def save_unknown_to_disk(date, unknown_events):
    try:
        with open(f"unknown-{date}", 'w') as f:
            for unknown_event in unknown_events:
                f.write(f"{int(unknown_event[1])} sec - {unknown_event[0]}\n")
    except:
        # TODO: Nasty hack to not run on lambda
        pass


def main():
    config_parser = ConfigParser('config.json')
    discovery = Discovery()
    classificator = Classificator()
    event_extractor = EventExtractor()

    yesterday = datetime.date.today() - datetime.timedelta(days=7)
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

    for unknown_event in discovery.get_agg_duration_events_sorted(top_n=20):
        pprint.pprint(unknown_event)

    save_unknown_to_disk(yesterday, discovery.get_agg_duration_events_sorted())

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    ## Upload results to the Exist client
    exist_client = ExistClient()
    response = exist_client.send_productivity(yesterday.isoformat()[:10], productivity_data)
    print("Respone from the Exist.io:")
    exist_client.validate_response(response)
    pprint.pprint(response.json())

    # Upload events data to S3
    all_buckets_events = event_extractor.get_all_buckets_events()

    upload_data(config_parser, all_buckets_events, yesterday)


if __name__ == "__main__":
    main()
