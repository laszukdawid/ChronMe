import datetime

from chronme.discovery import Discovery


def test_add_same_events():
    # Assign
    discovery = Discovery()
    event1 = create_event(update_data={'title': 'Page 1'})
    event2 = create_event(update_data={'title': 'Page 1'})

    # Act
    discovery.add_event(event1)
    discovery.add_event(event2)
    all_events = discovery.get_all_unique_events()

    # Assert
    assert len(all_events) == 1

def test_add_unique_events():
    # Assign
    discovery = Discovery()
    event1 = create_event(update_data={'title': 'Page 1'})
    event2 = create_event(update_data={'title': 'Page 2'})

    # Act
    discovery.add_event(event1)
    discovery.add_event(event2)
    all_events = discovery.get_all_unique_events()

    # Assert
    assert len(all_events) == 2

def test_total_duration_per_event():
    # Assign
    discovery = Discovery()
    event1 = create_event(update_event={'duration': datetime.timedelta(seconds=10)})
    event2 = create_event(update_event={'duration': datetime.timedelta(seconds=50)})

    # Act
    discovery.add_event(event1)
    discovery.add_event(event2)
    all_unique_events = discovery.get_all_unique_events()
    total_duration_events = discovery.get_agg_duration_events()

    # Assert
    assert len(all_unique_events) == 1
    assert len(total_duration_events) == 1
    any_key = list(total_duration_events.keys())[0]
    assert total_duration_events[any_key] == 60

def test_total_duration_per_event_sorted():
    # Assign
    discovery = Discovery()

    # Act
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=10)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)},
                          update_data={'title': 'Fantastic choice!'}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=20)},
                          update_data={'title': 'YES! choice!'}))

    all_unique_events = discovery.get_all_unique_events()
    total_duration_events = discovery.get_agg_duration_events()
    sorted_total_duration_events = discovery.get_agg_duration_events_sorted()

    # Assert
    assert len(all_unique_events) == 3
    assert len(total_duration_events) == 3

    assert 'Amazing page' in str(sorted_total_duration_events[0][0])
    assert sorted_total_duration_events[0][1] == 60
    assert 'Fantastic' in str(sorted_total_duration_events[1][0])
    assert sorted_total_duration_events[1][1] == 50
    assert 'YES!' in str(sorted_total_duration_events[2][0])
    assert sorted_total_duration_events[2][1] == 20

def test_total_duration_per_event_sorted_cached():
    # Assign
    discovery = Discovery()
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=10)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)},
                          update_data={'title': 'Fantastic choice!'}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=20)},
                          update_data={'title': 'YES! choice!'}))

    # Act
    sorted_total_duration_events_1 = discovery.get_agg_duration_events_sorted()
    sorted_total_duration_events_2 = discovery.get_agg_duration_events_sorted()

    # Assert
    assert len(sorted_total_duration_events_1) == len(sorted_total_duration_events_2)
    assert sorted(sorted_total_duration_events_1) == sorted(sorted_total_duration_events_2)
    assert sorted_total_duration_events_1 is not sorted_total_duration_events_2

def test_total_duration_per_event_sorted_updated():
    # Assign
    discovery = Discovery()

    # Act
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=10)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)},
                          update_data={'title': 'Fantastic choice!'}))
    sorted_total_duration_events_1 = discovery.get_agg_duration_events_sorted()

    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=50)}))
    discovery.add_event(create_event(update_event={'duration': datetime.timedelta(seconds=20)},
                          update_data={'title': 'YES! choice!'}))
    sorted_total_duration_events_2 = discovery.get_agg_duration_events_sorted()

    # Assert
    assert len(sorted_total_duration_events_1) != len(sorted_total_duration_events_2)
    assert sorted(sorted_total_duration_events_1) != sorted(sorted_total_duration_events_2)
    assert sorted_total_duration_events_1 is not sorted_total_duration_events_2

def test_total_duration_per_event_sorted_top_n():
    # Assign
    discovery = Discovery()
    top_n = 3

    # Act
    discovery.add_event(create_event(update_data={'title': 'Fantastic choice!'}))
    discovery.add_event(create_event(update_data={'title': 'This is great'}))
    discovery.add_event(create_event(update_data={'title': 'YES! choice!'}))
    discovery.add_event(create_event(update_data={'title': 'If not for others, I would definitely'}))
    discovery.add_event(create_event(update_data={'title': 'Maybe or not maybe, there is not try'}))
    sorted_total_duration_events = discovery.get_agg_duration_events_sorted(top_n=top_n)

    # Assert
    assert len(sorted_total_duration_events) == top_n

def create_event(update_event={}, update_data={}):
    default_event = {
        'data': {
            'status': 'not-afk',
            'app': 'Firefox',
            'title': 'Amazing page - Mozilla Firefox',
            'url': 'https://amazing.page',
        },
        'id': 12345,
        'duration': datetime.timedelta(seconds=1),
        'timestamp': datetime.datetime.now(),
    }
    event = {**default_event, **update_event}
    event['data'] = {**default_event['data'], **update_data}
    return event
