"""
This is the core of the AWS lambda function.
It's meant to run on every S3 bucket update (cron job sync from local).
The script will fetch data from defined s3 bucket, parse them according to rules
and then update the Exist service. By default the data is loaded
from midnight today (UTC) until midnight tomorrow (UTC).
"""
import datetime
import pprint
import os

from collections import defaultdict
from typing import Optional, Tuple

from chronme.config_parser import ConfigParser
from chronme.classificator import Classificator
from chronme.discovery import Discovery
from chronme.event_extractor import EventExtractor
from chronme.exist import ExistClient
from chronme.uploader import upload_data
from chronme.utils import extract_duration

def process_dates(start_date_str: Optional[str]=None, end_date_str: Optional[str]=None) -> Tuple[datetime.date, datetime.date]:
    """Process dates in strings and return proper format.
    Dates are expected in format `%Y-%m-%d`, e.g. "2020-11-24".
    The default return for the `start_date` is today utc midnight, i.e. same day utc but with hours=0.
    The default return for the `end_date` is the `start_date` + 1 day.
    """
    if start_date_str is not None:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    else:
        utc_now = datetime.datetime.utcnow()
        utc_midnight = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = utc_midnight
    
    if end_date_str is not None:
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        end_date = start_date + datetime.timedelta(days=1)

    return (start_date, end_date)

def main():
    config_parser = ConfigParser('config.json')
    discovery = Discovery()
    classificator = Classificator()
    event_extractor = EventExtractor()

    start_date_str = os.getenv("START_DATE")
    end_date_str = os.getenv("END_DATE")
    start_date_utc, end_date_utc = process_dates(start_date_str, end_date_str)
    events = event_extractor.get_events_between_dates(start_date_utc, end_date_utc)

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

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    ## Upload results to the Exist client
    exist_client = ExistClient()
    response = exist_client.send_productivity(start_date_utc.isoformat()[:10], productivity_data)
    print("Respone from the Exist.io:")
    exist_client.validate_response(response)
    pprint.pprint(response.json())

    # Upload events data to S3
    all_buckets_events = event_extractor.get_all_buckets_events()

    upload_data(config_parser, all_buckets_events, start_date_utc)


if __name__ == "__main__":
    main()
