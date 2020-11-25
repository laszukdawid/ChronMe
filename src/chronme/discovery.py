import operator
from aw_core.models import Event
from collections import defaultdict
from typing import Any, List, Tuple


class Discovery:
    """Servers purpose of discovering insights from the data."""

    def __init__(self):
        self.events_duration = defaultdict(float)
        self._events_duration_sorted = []
        self._refresh_cache = False
    
    @staticmethod
    def _lean_data(data):
        c_data = data.copy()
        if "status" in c_data:
            del c_data['status']
        return c_data
    
    def add_event(self, event: Event):
        data = self._lean_data(event['data'])
        duration_seconds: float = event['duration'].total_seconds()
        key = str(sorted(frozenset(data.items()), key=operator.itemgetter(0)))
        self.events_duration[key] += duration_seconds

        self._refresh_cache = True
    
    def get_all_unique_events(self):
        return list(map(dict, self.events_duration.keys()))

    def get_agg_duration_events(self):
        return self.events_duration
    
    def get_agg_duration_events_sorted(self, top_n=-1) -> List[Tuple[Any, float]]:
        """
        """
        if self._refresh_cache:
            self._events_duration_sorted = sorted(self.get_agg_duration_events().items(),
                                                  key=operator.itemgetter(1),
                                                  reverse=True)
            self._refresh_cache = False
        
        _top_n = top_n if top_n > 0 else len(self._events_duration_sorted)
        
        return self._events_duration_sorted.copy()[:_top_n]
