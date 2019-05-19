
class Discovery:

    def __init__(self):
        self.all_unknown = set()
    
    def add_event(self, event):
        self.all_unknown.add(frozenset(event['data'].items()))
    
    def get_all_unique_events(self):
        return list(map(dict, self.all_unknown))
