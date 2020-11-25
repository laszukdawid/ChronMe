"""
This script is used to run locally on your machine.
It fetches data from local ActvivityWatch server, parses them,
uploads parsed data into an S3 bucket and then updates the Exist service
with your insights (productivty values).
By default, if no values are provided, the time range is today midnight (UTC)
to tomorrow midnight (UTC).
"""
import datetime
from datetime import date
import logging

from collections import defaultdict
from pathlib import Path

from chronme.config_parser import ConfigParser
from chronme.classificator import Classificator
from chronme.discovery import Discovery
from chronme.event_extractor import EventExtractor
from chronme.exist import ExistClient
from chronme.uploader import upload_data
from chronme.utils import extract_duration

logger = logging.getLogger(Path(__file__).stem)

def get_today_utc():
    local_now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    utc_midnight = local_midnight.astimezone(datetime.timezone.utc)
    return local_midnight, utc_midnight

def save_report_to_disk(date: datetime.date, category, events):
    try:
        with open(f"{category}-{date}", 'w') as f:
            for event in events:
                f.write(f"{int(event[1])} sec - {event[0]}\n")
    except:
        # TODO: Nasty hack to not run on lambda
        pass

def main():
    config_parser = ConfigParser('config.json')

    # Shhh... I know. But don't tell anyone. This is going to be our own little secret, Ok? ;-)
    discovery = Discovery()
    prod_discovery = Discovery()
    neur_discovery = Discovery()
    dist_discovery = Discovery()
    classificator = Classificator()
    logger.info("Pass classifcator")
    event_extractor = EventExtractor()

    _, today_start_day_utc = get_today_utc()
    end_date_utc = today_start_day_utc - datetime.timedelta(days=3)
    start_date_utc = end_date_utc - datetime.timedelta(days=1)
    events = event_extractor.get_events_between_dates(start_date=start_date_utc, end_date=end_date_utc)

    category_counter = defaultdict(int)
    category_duration = defaultdict(float)
    for event in events:

        category = classificator.check_productivity(event)
        category_counter[category] += 1
        category_duration[category] += extract_duration(event)

        if category == classificator.UNKNOWN_CATEGORY:
            discovery.add_event(event)
        elif category == 'productive':
            prod_discovery.add_event(event)
        elif category == 'neutral':
            neur_discovery.add_event(event)
        elif category == 'distracting':
            dist_discovery.add_event(event)
        else:
            raise ValueError("Something went wrong")

    save_report_to_disk(start_date_utc.date(), 'unknown', discovery.get_agg_duration_events_sorted())
    save_report_to_disk(start_date_utc.date(), 'productive', prod_discovery.get_agg_duration_events_sorted())
    save_report_to_disk(start_date_utc.date(), 'neutral', neur_discovery.get_agg_duration_events_sorted())
    save_report_to_disk(start_date_utc.date(), 'distracting', dist_discovery.get_agg_duration_events_sorted())

    logger.info("Counter: %s", category_counter)
    logger.info("Duration: %s", category_duration)

    for unknown_event in discovery.get_agg_duration_events_sorted(top_n=20):
        logger.debug("Total duration: %f", unknown_event[1])
        logger.debug(dict(eval(unknown_event[0])))

    productivity_data = category_duration
    if classificator.UNKNOWN_CATEGORY in productivity_data:
        productivity_data.pop(classificator.UNKNOWN_CATEGORY)

    ## Upload results to the Exist client
    print("Sending request to the Exist")
    exist_client = ExistClient()
    response = exist_client.send_productivity(start_date_utc.isoformat()[:10], productivity_data)
    print("Respone from the Exist.io:")
    exist_client.validate_response(response)
    print(response.json())

    # Upload events data to S3
    all_buckets_events = event_extractor.get_all_buckets_events()
    upload_data(config_parser, all_buckets_events, start_date_utc)


if __name__ == "__main__":
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('nose').setLevel(logging.CRITICAL)
    logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.DEBUG)
    main()
