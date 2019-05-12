import datetime
import json
import pprint

from collections import defaultdict

from classificator import Classificator
from discovery import Discovery
from event_extractor import EventExtractor


def extract_duration(event):
    "Extract duration information in seconds. Always returns at least 1 second, even if non provided"
    DURATION_KEY = "duration"
    min_duration = 1
    if DURATION_KEY not in event:
        return min_duration
    
    return event[DURATION_KEY].total_seconds() or min_duration


if __name__ == "__main__":

    discovery = Discovery()
    classificator = Classificator()
    event_extractor = EventExtractor()

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    events = event_extractor.get_events_for_day(yesterday)

    category_counter = defaultdict(int)
    category_duration = defaultdict(float)
    for event in events:
        # pprint.pprint(event)

        duration = extract_duration(event)
        category = classificator.check_productivity(event)

        category_counter[category] += 1
        category_duration[category] += duration
        if category == classificator.UNKNOWN_CATEGORY:
            discovery.add_event(event)
            print(category, ' -- ', event['data'])

    print("Counter: ", category_counter)
    print("Duration: ", category_duration)

    pprint.pprint(discovery.get_all_unique_events())
