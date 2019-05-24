from collections import defaultdict
import operator

class Discovery:
    """Servers purpose of discovering insights from the data."""

    def __init__(self):
        self.events_duration = defaultdict(int)
        self._events_duration_sorted = []

        ## TODO: Introduce 'dirty' notion that will recompute aggregates once, otherwise serve from cache.
    
    def _lean_data(self, data):
        c_data = data.copy()
        del c_data['status']
        return c_data
    
    def add_event(self, event):
        data = self._lean_data(event['data'])
        duration_seconds = event['duration'].total_seconds()
        key = frozenset(data.items())
        self.events_duration[key] += duration_seconds
    
    def get_all_unique_events(self):
        return list(map(dict, self.events_duration.keys()))

    def get_agg_duration_events(self):
        return self.events_duration
    
    def get_agg_duration_events_sorted(self):
        return sorted(self.get_agg_duration_events().items(), key=operator.itemgetter(1), reverse=True)
