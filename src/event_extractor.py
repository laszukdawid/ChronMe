import datetime
from aw_client import ActivityWatchClient

class EventExtractor:

    AW_WATCHER_WEB_FIREFOX = "aw-watcher-web-firefox" 

    def __init__(self):
        self.awc = ActivityWatchClient()

        self.all_buckets = {}
        self.bucket = self._get_main_bucket()
        self.aw_watcher_window_id = self.bucket['id']

    def _get_main_bucket(self):
        if not self.all_buckets:
            self.all_buckets = self.awc.get_buckets()
        return [bucket for (name, bucket) in self.all_buckets.items() if 'window' in name][0]
    
    def _get_events_for_all_buckets(self, date: datetime, limit: int=9999):
        start_date = date
        end_date = start_date + datetime.timedelta(days=1)
        all_buckets_events = {}
        for bucket_name in self.all_buckets:
            all_buckets_events[bucket_name] = self.awc.get_events(bucket_name, limit=limit, start=start_date, end=end_date)
        return all_buckets_events
    
    def _aggregate_events(self, all_buckets_events):
        # The 'window' is the main bucket
        window_bucket_events = all_buckets_events[self.aw_watcher_window_id]
        # TODO: AGGREGATE
        return window_bucket_events

    def _find_overlapping_event(self, bucket_events, ref_event):
        beg_time = ref_event['timestamp']
        end_time = beg_time + ref_event['duration']
        for event in bucket_events:
            if event['timestamp'] >= beg_time and event['timestamp'] <= end_time:
                return event
        return None

    def get_events_for_day(self, date: datetime, limit: int=99999):
        all_buckets_events = self._get_events_for_all_buckets(date, limit)
        events = self._aggregate_events(all_buckets_events)
        return events

    def get_main_bucket_id(self):
        return self.aw_watcher_window_id
