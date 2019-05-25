from collections import defaultdict
import operator

class Discovery:
    """Servers purpose of discovering insights from the data."""

    def __init__(self):
        self.events_duration = defaultdict(int)
        self._events_duration_sorted = []

        self._refresh_cache = False
    
    def _lean_data(self, data):
        c_data = data.copy()
        if "status" in c_data:
            del c_data['status']
        return c_data
    
    def add_event(self, event):
        data = self._lean_data(event['data'])
        duration_seconds = event['duration'].total_seconds()
        key = frozenset(data.items())
        self.events_duration[key] += duration_seconds

        self._refresh_cache = True
    
    def get_all_unique_events(self):
        return list(map(dict, self.events_duration.keys()))

    def get_agg_duration_events(self):
        return self.events_duration
    
    def get_agg_duration_events_sorted(self, top_n=-1):
        if self._refresh_cache:
            self._events_duration_sorted = sorted(self.get_agg_duration_events().items(),
                                                  key=operator.itemgetter(1),
                                                  reverse=True)
            self._refresh_cache = False
        
        _top_n = top_n if top_n > 0 else len(self._events_duration_sorted)
        
        return self._events_duration_sorted.copy()[:_top_n]
