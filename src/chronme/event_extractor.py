import datetime
from enum import unique
import re
from aw_client import ActivityWatchClient
from aw_core.models import Event
from typing import Dict, List, Optional

from .utils import merge_events

class EventExtractor:

    def __init__(self):
        self.aw_client = ActivityWatchClient()

        self.all_buckets = {}
        self.bucket = self._get_main_bucket()
        self.aw_watcher_window_id = self.bucket['id']

        self._all_buckets_events = {}

    def _get_main_bucket(self):
        if not self.all_buckets:
            self.all_buckets = self.aw_client.get_buckets()
        return [bucket for (name, bucket) in self.all_buckets.items() if 'window' in name][0]

    def _get_events_for_all_buckets(
            self, start_date: datetime.date, end_date: Optional[datetime.date]=None, duration: int=86400, limit: int=9999
    ) -> Dict[str, List[Event]]:
        """Gets all events for each bucket (host) within specified time window [start_date, end_date].
        If `end_date` is not defined then it returns events based on duration, i.e. [start_date, start_date+duration].
        Duration is in seconds so the default value is a day.
        """
        if end_date is None:
            end_date = start_date + datetime.timedelta(seconds=duration)

        # Wipe previous data
        self._all_buckets_events = {}
        for bucket_name in self.all_buckets:
            self._all_buckets_events[bucket_name] = self.aw_client.get_events(
                bucket_name, limit=limit, start=start_date, end=end_date
            )

        return self._all_buckets_events

    @staticmethod
    def _aggregate_events(all_buckets_events) -> List[Event]:
        return list(merge_events(*all_buckets_events.values()))

    @staticmethod
    def _find_overlapping_event(bucket_events, ref_event):
        beg_time = ref_event['timestamp']
        end_time = beg_time + ref_event['duration']
        for event in bucket_events:
            if event['timestamp'] >= beg_time and event['timestamp'] <= end_time:
                return event
        return None

    @staticmethod
    def is_afk(event: Event):
        return "data" in event and "status" in event["data"] and event["data"]["status"] == 'afk'
    
    @staticmethod
    def _clean_data(event: Event):
        data = event['data']
        for key, value in data.items():
            data[key] = re.sub(u"\u2013", "-", value)
        return event

    def get_events_between_dates(
        self, start_date: datetime.date, end_date: datetime.date, limit: int=99999
    ) -> List[Dict]:
        """Gets all ActivityWatch events that happened between start_date and end_date.
        The number of events is limitted to `limit` to avoid to large overflows.
        """
        self._all_buckets_events = self._get_events_for_all_buckets(start_date=start_date, end_date=end_date, limit=limit)

        all_hosts = [bucket_name.rsplit('_', 1)[1] for bucket_name in self._all_buckets_events.keys() if '_' in bucket_name]
        unique_hosts = list(set(all_hosts))

        agg_host_events = {}
        for host in unique_hosts:
            # Aggregate events per host
            host_events = {k:v for (k, v) in self._all_buckets_events.items() if host in k}
            _agg_host_events = self._aggregate_events(host_events)

            # Filter out afk events
            not_afk_events = [event for event in _agg_host_events if not self.is_afk(event)]
            clean_events = [self._clean_data(event) for event in not_afk_events]
            agg_host_events[host] = clean_events
        events = self._aggregate_events(agg_host_events)
        return events

    def get_events_for_day(
        self, start_date: datetime.date, end_date: Optional[datetime.date]=None, limit: int=99999
    ):
        self._all_buckets_events = self._get_events_for_all_buckets(start_date=start_date, end_date=end_date, limit=limit)
        hosts = list(set(_[1] for _ in (key.split("_") for key in self._all_buckets_events.keys() if "_" in key)))
        agg_host_events = {}
        for host in hosts:
            # Aggregate events per host
            host_events = {k:v for (k, v) in self._all_buckets_events.items() if host in k}
            _agg_host_events = self._aggregate_events(host_events)

            # Filter out afk events
            not_afk_events = [event for event in _agg_host_events if not self.is_afk(event)]
            clean_events = [self._clean_data(event) for event in not_afk_events]
            agg_host_events[host] = clean_events
        events = self._aggregate_events(agg_host_events)
        return events

    def get_main_bucket_id(self):
        return self.aw_watcher_window_id

    def get_all_buckets_events(self):
        return self._all_buckets_events
