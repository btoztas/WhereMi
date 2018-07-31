import operator
from datetime import datetime

from wheremi_app import Beacon

SEND_PERIODICITY = 600
LOCATION_TIME_INTERVALS = 16
ACC_TIME_INTERVALS = 12

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


def decode_location_timestamp(send_timestamp, relative_timestamp):

    time_interval = SEND_PERIODICITY/LOCATION_TIME_INTERVALS
    return send_timestamp - time_interval * relative_timestamp + time_interval/2


def decode_accelerometer_event_timestamp(send_timestamp, relative_timestamp):

    time_interval = SEND_PERIODICITY/ACC_TIME_INTERVALS
    return send_timestamp - (12-relative_timestamp)*time_interval + time_interval/2


def get_last_location(device):

    if device.location_mode == "proximity":
        last_location_info = device.retrieve_last_beacon_location()
        try:
            beacon_id = last_location_info['location']['id']
            beacon = Beacon.query.filter_by(identifier=beacon_id).first()
        except:
            return None

        return {
            'type': 'proximity',
            'beacon': beacon,
            'timestamp': last_location_info['location']['timestamp']
        }

def save_message(device, data):

    send_timestamp = data['timestamp']

    # saving message
    device.save_message(data)

    if data['header'] == 0:
        device.save_device_info(send_timestamp, data['payload']['battery'], data['payload']['temperature'])

    elif data['header'] <= 4:

        # saving location data
        for beacon in data['payload']['beacons']:
            device.save_proximity_location(beacon['id'], decode_location_timestamp(send_timestamp, beacon['diff_time']))

        binary_acc_history = bin(data['payload']['acc_history'])
        for i, x in enumerate(binary_acc_history[2:]):
            if int(x) == 1:
                # we have an acc event
                device.save_accelerometer_event_location(decode_accelerometer_event_timestamp(send_timestamp, i))
