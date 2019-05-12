import datetime
from aw_client import ActivityWatchClient

class EventExtractor:

    def __init__(self):
        self.awc = ActivityWatchClient()

        self.all_buckets = {}
        self.bucket = self._get_bucket()

    def _get_bucket(self):
        if not self.all_buckets:
            self.all_buckets = self.awc.get_buckets()
        return [bucket for (name, bucket) in self.all_buckets.items() if 'window' in name][0]

    def get_events_for_day(self, date: datetime, limit: int=99999):
        start_date = date
        end_date = start_date + datetime.timedelta(days=1)
        events = self.awc.get_events(self.bucket['id'], limit=limit, start=start_date, end=end_date)
        return events


