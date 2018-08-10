import operator
from wheremi_app import Beacon, app

# CONFIGS
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
STATE_RESTING                 = 3

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


def get_last_location(device):

    data = device.retrieve_last_location()
    if data:
        timestamp = data['timestamp']
        location = data['location']

        if location['type'] == LOCATION_TYPE_UNKNOWN:
            return None

        if location['type'] == LOCATION_TYPE_PROXIMITY:

            try:
                beacon_id = location['id']
                beacon = Beacon.query.filter_by(identifier=beacon_id).first()
            except:
                return None
            return {
                'type': 'Proximity',
                'beacon': beacon,
                'timestamp': timestamp
            }

        if location['type'] == LOCATION_TYPE_PRECISION:

            max = -100
            id = 0

            for entry in location['beacons']:
                if max < entry['rssi']:
                    id = entry['id']
                    max = entry['rssi']
            try:
                beacon = Beacon.query.filter_by(identifier=id).first()

            except:
                return None

            return {
                'type': 'Proximity',
                'beacon': beacon,
                'timestamp': timestamp
            }


def get_precision_location_from_payload(payload):

    return { 'type': LOCATION_TYPE_UNKNOWN } if payload['num_beacons'] == 0 else \
        { 'type': LOCATION_TYPE_PRECISION, 'num_beacons': payload['num_beacons'], 'beacons': payload['beacons'] }

def get_proximity_locations_from_payload(payload, timestamp):

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


    elif message_type == MESSAGE_MOVING:

        device.save_status(timestamp, STATE_MOVING)

        location = get_precision_location_from_payload(payload)
        device.save_location(LOCATION_TYPE_PRECISION, timestamp, location)

        accelerometer_events = get_accelerometer_events_from_payload(payload, timestamp)
        for event in accelerometer_events:
            device.save_accelerometer_event(event)


    elif message_type == MESSAGE_PROXIMITY_LOCATION:

        device.save_status(timestamp, STATE_MOVING)

        accelerometer_events = get_accelerometer_events_from_payload(payload, timestamp)
        for event in accelerometer_events:
            device.save_accelerometer_event(event)

        locations = get_proximity_locations_from_payload(payload, timestamp)
        for entry in locations:
                device.save_location(entry['timestamp'], entry['location'])


def find_location(data):

    type = data['location']['type']

    # CASE UNKNOWN
    if type == LOCATION_TYPE_UNKNOWN:
        return

    # CASE PROXIMITY

    # CASE PRECISION



@app.template_filter('decode_status')
def decode_status(status):

    if status == STATE_TURNED_ON:
        return 'Turned on'

    elif status == STATE_STARTED_MOVING:
        return 'Started Moving'

    elif status == STATE_MOVING:
        return 'Moving'

    elif status == STATE_RESTING:
        return 'Resting'



