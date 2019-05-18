import collections
import copy
import datetime

from functools import reduce


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def extract_time_and_duration(event):
    timestamp = datetime.datetime.strptime(event['timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
    duration = datetime.timedelta(seconds=float(event['duration']))
    return {"timestamp": timestamp, "duration": duration}

def parse_event(event):
    event.update(extract_time_and_duration(event))
    return event

def order_events(events):
    return sorted(events, key=lambda k: k['timestamp']) 

def parse_and_order_events(events):
    return order_events(list(map(parse_event, events)))
    #return order_events(list(map(extract_time_and_duration, events)))
    
def del_timestamp_duration(e):
    del e['timestamp']
    del e['duration']
    return e

def copy_all_except_time(e_to, e_from):
    new_e_from = del_timestamp_duration(e_from.copy())
    return deep_update(e_to, new_e_from)

def compare_events(e1, e2):
    "Returns (ordered_new_event, all_previous_events_but_updated)"
    if e1 is None:
        return e2, [None, None]
    if e2 is None:
        return e1, [None, None]
    
    if e1['timestamp'] == e2['timestamp']:
        if e1['duration'] == e2['duration']:
            e_m = copy_all_except_time(e1, e2)
            e_old = [None, None]
            return e_m, e_old

        elif e1['duration'] > e2['duration']:
            e_m = copy_all_except_time(e2, e1)
            
            new_e1 = e1.copy()
            new_e1['timestamp'] = e2['timestamp'] + e2['duration']
            new_e1['duration'] = e1['duration'] - e2['duration']
            e_old = [new_e1, None]
            
            return e_m, e_old

        else:
            e_m = copy_all_except_time(e1, e2)
            
            new_e2 = e2.copy()
            new_e2['timestamp'] = e1['timestamp'] + e1['duration']
            new_e2['duration'] = e2['duration'] - e1['duration']
            e_old = [None, new_e2]
            
            return e_m, e_old

    elif e1['timestamp'] < e2['timestamp']: # All cases do the same thing
        if (e1['timestamp'] + e1['duration']) <= e2['timestamp']:
            e_m = e1.copy()
            e_old = [None, e2.copy()]
            return e_m, e_old
        
        else:
            e_m = e1.copy()
            e_m['duration'] = e2['timestamp'] - e1['timestamp']
            
            new_e1 = e1.copy()
            new_e1['timestamp'] = e2['timestamp']
            new_e1['duration'] = e1['duration'] - e_m['duration']
            new_e2 = e2.copy()
            e_old = [new_e1, new_e2]
            
            return e_m, e_old
    # 7 -- 9
    elif e1['timestamp'] > e2['timestamp']: # All cases do the same thing
        if e1['timestamp'] >= (e2['timestamp'] + e2['duration']):
            e_m = e2.copy()
            e_old = [e1.copy(), None]
            return e_m, e_old
        
        else:
            e_m = e2.copy()
            e_m['duration'] = e1['timestamp'] - e2['timestamp']
            
            new_e1 = e1.copy()
            new_e2 = e2.copy()
            new_e2['timestamp'] = e1['timestamp']
            new_e2['duration'] = e2['duration'] - e_m['duration']

            e_old = [new_e1, new_e2]
            
            return e_m, e_old

def merge_events(*all_events):
    """
    Merges lists of events based on overlapping time windows.
    """
    return reduce(_merge_two_event_lists, map(order_events, all_events))

def _merge_two_event_lists(*all_events):
    """
    Mergers two lists of events based on overlapping time windows.
    """
    if len(all_events) != 2:
        raise AttributeError("Expected only two lists")
    
    # If either is empty, return one that's not empty. If both empty, return any.
    #if len(all_events[0]) == 0 or len(all_events[1]) == 0:
    if not all(all_events):
        return all_events[len(all_events[0]) == 0]

    events = [_events.pop(0) for _events in all_events]
    merged_events = []
    while(any(events)):
        new_e, events = compare_events(*events)
        events = list(events)
        merged_events.append(new_e)

        for n, e in enumerate(events):
            if e is None and len(all_events[n]) > 0:
                events[n] = all_events[n].pop(0)
    return merged_events