import operator
from wheremi_app import Beacon, app

# CONFIGS
from wheremi_app.helpers.precision_location import get_precision_location

CONFIG_PRECISION_SEND_TIMER        = 7200
CONFIG_PROXIMITY_SEND_TIMER        = 900
CONFIG_MOVEMENT_START_TIMER        = 30
CONFIG_MOVEMENT_INQUIRY_TIMER      = 30
CONFIG_MOVEMENT_STOP_TIMER         = 900
CONFIG_NUMBER_ACC_WAKEUPS_CRITERIA = 5
CONFIG_TIME_ACC_WAKEUPS_CRITERIA   = 15
CONFIG_ACC_TIME_NUM_BIT            = 12
CONFIG_BEACON_TIME_RESOLUTION      = 16

# STATES
STATE_TURNED_ON               = 0
STATE_STARTED_MOVING          = 1
STATE_MOVING                  = 2
STATE_STOPPED                  = 3
STATE_RESTING                 = 4

# MESSAGE TYPES
MESSAGE_TURNED_ON          = 0
MESSAGE_PERIODIC_LOCATION  = 1
MESSAGE_PROXIMITY_LOCATION = 2
MESSAGE_STARTED_MOVING	   = 3
MESSAGE_STOPPED_MOVING 	   = 4
MESSAGE_MOVING             = 5

# LOCATION TYPES
LOCATION_TYPE_PRECISION = 0
LOCATION_TYPE_PROXIMITY = 1
LOCATION_TYPE_UNKNOWN   = 3


def get_location_based_on_last_scans(device, num_scans):
    data = device.retrieve_last(num_scans)
    result = dict()

    try:
        for entry in data:
            for beacon in entry['data']['reading']:
                if beacon['id'] in result:
                    result[beacon['id']].append(beacon['rssi'])
                else:
                    result[beacon['id']] = list()
                    result[beacon['id']].append(beacon['rssi'])
    except:
        return None

    mean = dict()
    for beacon_id, beacon_rssi in result.iteritems():
        mean[beacon_id] = sum(beacon_rssi)/num_scans
    try:
        beacon_id = max(mean.iteritems(), key=operator.itemgetter(1))[0]
    except ValueError:
        return None

    return Beacon.query.filter_by(identifier=beacon_id).first()


def decode_proximity_location_timestamp(send_timestamp, relative_timestamp):

    time_interval = CONFIG_PROXIMITY_SEND_TIMER/CONFIG_BEACON_TIME_RESOLUTION
    return send_timestamp - time_interval * relative_timestamp + time_interval/2


def decode_accelerometer_event_timestamp(send_timestamp, relative_timestamp):

    time_interval = CONFIG_PROXIMITY_SEND_TIMER/CONFIG_ACC_TIME_NUM_BIT
    return send_timestamp - (12-relative_timestamp)*time_interval + time_interval/2


def get_n_location(device, n):

    data = device.retrieve_last_location(n)
    home_floor = device.home_floor
    if data != None:
        timestamp = data['timestamp']
        location = data['location']

        if location['type'] == LOCATION_TYPE_UNKNOWN:
            return {
                'type': 'Unknown',
                'exists': True,
                'timestamp': timestamp,
                'error': False,
                'message': 'Beacon unknown or no beacon seen'
            }

        if location['type'] == LOCATION_TYPE_PROXIMITY:

            try:
                beacon_id = location['id']
                beacon = Beacon.query.filter_by(identifier=beacon_id, home_floor=home_floor).first()
            except:
                return {
                    'type': 'Unknown',
                    'exists': True,
                    'timestamp': timestamp,
                    'error': True,
                    'message': 'Error calculating proximity location'
                }
            if beacon:
                return {
                    'type': 'Proximity',
                    'exists': True,
                    'beacon': beacon,
                    'beacon_info': beacon.serialize_for_map(),
                    'timestamp': timestamp,
                    'floor_id': home_floor.id,
                    'x_real': beacon.x,
                    'y_real': beacon.y,
                    'x': home_floor.get_x_coordinate_on_map(beacon.x),
                    'y': home_floor.get_x_coordinate_on_map(beacon.y)
                }
            return {
                'type': 'Unknown',
                'exists': True,
                'timestamp': timestamp,
                'error': True,
                'message': 'Error calculating proximity location'
            }

        if location['type'] == LOCATION_TYPE_PRECISION:

            max = -100
            id = 0

            for entry in location['beacons']:
                if max < entry['rssi']:
                    id = entry['id']
                    max = entry['rssi']

            beacon_strong = Beacon.query.filter_by(identifier=id, home_floor=home_floor).first()
            if beacon_strong:
                measurement = []

                for entry in location['beacons']:
                    beacon = Beacon.query.filter_by(identifier=entry['id'], home_floor=home_floor).first()
                    if beacon:
                        measurement.append({
                            'rssi': entry['rssi'],
                            'beacon':beacon
                        })
                if len(measurement) != 0:
                    location = get_precision_location(measurement)
                    x = location['x']
                    y = location['y']
                    map_zone = []
                    for zone in location['zone']:
                        map_zone.append(
                            {
                                'x': home_floor.get_x_coordinate_on_map(zone['x']),
                                'y': home_floor.get_y_coordinate_on_map(zone['y']),
                                'radius': home_floor.get_x_coordinate_on_map(zone['radius']),
                            }
                        )


                    return {
                        'type': 'Precision',
                        'exists': True,
                        'beacon': beacon_strong,
                        'beacon_info': beacon_strong.serialize_for_map(),
                        'timestamp': timestamp,
                        'floor_id': home_floor.id,
                        'x_real': x,
                        'y_real': y,
                        'x': home_floor.get_x_coordinate_on_map(x),
                        'y': home_floor.get_x_coordinate_on_map(y),
                        'zone': map_zone,

                    }
            return {
                'type': 'Unknown',
                'exists': True,
                'timestamp': timestamp,
                'error': True,
                'message': 'Error calculating precision location'
            }


    return {
        'type': 'Unknown',
        'exists': False,
        'error': False,
        'message': 'No registered location'
    }





def get_precision_location_from_payload(payload):

    if payload['num_beacons'] == 0:
        return {'type': LOCATION_TYPE_UNKNOWN}

    return { 'type': LOCATION_TYPE_PRECISION, 'num_beacons': payload['num_beacons'], 'beacons': payload['beacons'] }

def get_proximity_locations_from_payload(payload, timestamp):

    if payload['num_beacons'] == 0:
        return { 'type': LOCATION_TYPE_UNKNOWN }

    locations = list()

    for beacon in payload['beacons']:

        if beacon['id'] == 65535:
            locations.append(
                {
                    'timestamp': decode_proximity_location_timestamp(timestamp, beacon['diff_time']),
                    'location': { 'type': LOCATION_TYPE_UNKNOWN }
                }
            )
        else:
            locations.append(
                {
                    'location': { 'type': LOCATION_TYPE_PROXIMITY, 'id': beacon['id'] },
                    'timestamp': decode_proximity_location_timestamp(timestamp, beacon['diff_time']),
                }
            )

    return locations


def get_battery_from_payload(payload):
    return payload['vbat']


def get_temperature_from_payload(payload):
    return payload['temp']


def get_accelerometer_events_from_payload(payload, timestamp):
    binary_acc_history = bin(payload['acc_history'])
    acc_events = list()
    for i, x in enumerate(binary_acc_history[2:]):
        if int(x) == 1:
            acc_events.append(decode_accelerometer_event_timestamp(timestamp, i))
    return acc_events

def save_message(device, data):

    timestamp = data['timestamp']
    message_type = data['header']
    if 'payload' in data: payload = data['payload']

    # Saving Message
    device.save_message(data)


    if message_type == MESSAGE_TURNED_ON or\
            message_type == MESSAGE_PERIODIC_LOCATION or\
            message_type == MESSAGE_STOPPED_MOVING:

        if (message_type == MESSAGE_TURNED_ON):
            device.save_status(timestamp, STATE_TURNED_ON)

        if (message_type == MESSAGE_PERIODIC_LOCATION):
            device.save_status(timestamp, STATE_RESTING)

        if (message_type == MESSAGE_STOPPED_MOVING):
            device.save_status(timestamp, STATE_RESTING)

        location = get_precision_location_from_payload(payload)
        device.save_location(timestamp, location)

        temperature = get_temperature_from_payload(payload)
        device.save_temperature(timestamp, temperature)

        battery = get_battery_from_payload(payload)
        device.save_battery(timestamp, battery)


    elif message_type == MESSAGE_STARTED_MOVING:

        device.save_status(timestamp, STATE_STARTED_MOVING)
        device.save_accelerometer_event(timestamp)


    elif message_type == MESSAGE_MOVING:

        device.save_status(timestamp, STATE_MOVING)

        location = get_precision_location_from_payload(payload)
        device.save_location(timestamp, location)

        accelerometer_events = get_accelerometer_events_from_payload(payload, timestamp)
        for event in accelerometer_events:
            device.save_accelerometer_event(event)


    elif message_type == MESSAGE_PROXIMITY_LOCATION:

        accelerometer_events = get_accelerometer_events_from_payload(payload, timestamp)
        for event in accelerometer_events:
            device.save_accelerometer_event(event)
            device.save_status(event, STATE_MOVING)

        locations = get_proximity_locations_from_payload(payload, timestamp)
        for entry in locations:
                device.save_location(entry['timestamp'], entry['location'])
                device.save_status(entry['timestamp'], STATE_STOPPED)



@app.template_filter('decode_status')
def decode_status(status):

    if status == STATE_TURNED_ON:
        return 'Turned on'

    elif status == STATE_STARTED_MOVING:
        return 'Started Moving'

    elif status == STATE_MOVING:
        return 'Moving'

    elif status == STATE_STOPPED:
        return 'Stopped'

    elif status == STATE_RESTING:
        return 'Resting'



